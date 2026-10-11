"""Mixagem final: voz do Video Use + efeitos + insertos com som + trilha.

Lê o mix.json gerado pelo montar.py e:
  - abafa a voz nos apartes em P&B (passa-baixa suave, como um pensamento) ou
    a deixa com som de rádio/celular (só a faixa média);
  - toca o som próprio dos insertos marcados com "som": true;
  - coloca cada efeito sonoro com o ponto de impacto no instante do evento;
  - põe a trilha (gerada ou do usuário) com "ducking": ela abaixa sozinha
    por baixo da fala e sobe nas pausas e na tela final;
  - normaliza em dois passes para -14 LUFS e pico real de -1,5 dBTP (folga para o AAC).

Uso (normalmente chamado pelo finalizar.py):
    python3 ferramentas/mixar.py --voz <edit>/cortado.mp4 --mix <edit>/hf/mix.json -o <edit>/mix.wav
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from efeitos import GANHO_DB, efeito, gravar_wav
from trilha import gerar_trilha

SR = 48000
MUSICA_SOZINHA_DB = -9.0  # trilha sem fala: tantos dB abaixo do nível médio da voz
DUCKING_DB = 12.0  # quanto a trilha abaixa por baixo da fala


def ler_audio(path: Path, inicio: float = 0.0, dur: float | None = None) -> np.ndarray:
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-loglevel",
        "error",
        "-ss",
        f"{inicio:.3f}",
        "-i",
        str(path),
    ]
    if dur is not None:
        cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-map", "0:a:0", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    pcm = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, 2).copy()


def rampa(n: int, fade: int) -> np.ndarray:
    """Janela 1 com bordas em cosseno (evita estalos)."""
    w = np.ones(n)
    f = min(fade, n // 2)
    if f > 0:
        r = np.sin(np.linspace(0, np.pi / 2, f)) ** 2
        w[:f], w[n - f :] = r, r[::-1]
    return w


def somar(dest: np.ndarray, x: np.ndarray, ini: int) -> None:
    if ini < 0:
        x, ini = x[-ini:], 0
    x = x[: max(0, len(dest) - ini)]
    dest[ini : ini + len(x)] += x


def envelope_fala(voz: np.ndarray) -> np.ndarray:
    """0 = silêncio, 1 = fala; suavizado (sobe em ~20 ms, desce em ~400 ms)."""
    mono = voz.mean(axis=1)
    bloco = int(0.01 * SR)
    q = len(mono) // bloco
    rms = np.sqrt(np.mean(mono[: q * bloco].reshape(q, bloco) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    alvo = np.clip((db - (np.percentile(db, 95) - 30)) / 12, 0, 1)
    env = np.zeros(q)
    sobe, desce = 1 - np.exp(-1 / 2), 1 - np.exp(-1 / 40)  # em blocos de 10 ms
    for i in range(q):
        k = sobe if alvo[i] > env[i - 1] else desce
        env[i] = env[i - 1] + k * (alvo[i] - env[i - 1]) if i else alvo[i]
    return np.interp(np.arange(len(mono)), np.arange(q) * bloco, env)


def abafar(voz: np.ndarray, trechos: list[list[float]]) -> np.ndarray:
    if not trechos:
        return voz
    # Corte suave de agudos (~ -5 dB acima de 2,5 kHz), não um passa-baixa duro:
    # soa como pensamento, não como telefone. Na referência o brilho cai ~25–30%;
    # aqui cai ~35%.
    b, a = signal.butter(2, 2500, btype="high", fs=SR)
    filtrada = (voz - 0.45 * signal.filtfilt(b, a, voz, axis=0)) * 10 ** (-1.0 / 20)
    mistura = np.zeros(len(voz))
    for t0, t1 in trechos:
        i0, i1 = int(t0 * SR), min(len(voz), int(t1 * SR))
        if i1 > i0:
            mistura[i0:i1] = rampa(i1 - i0, int(0.04 * SR))
    return voz * (1 - mistura[:, None]) + filtrada * mistura[:, None]


def radio(voz: np.ndarray, trechos: list[list[float]]) -> np.ndarray:
    """Som de rádio/celular: só a faixa média (400–3000 Hz) e um leve drive.

    Calibrada no vídeo sério do usuário (o que ele chama de "voz de rádio"):
    ~20 dB a menos de graves e ~8 dB a menos de agudos que o trecho normal.
    Aplicado à voz e à trilha juntas (como no vídeo de referência, tudo soa
    "pelo rádio"); o nível (RMS) é igualado ao original para não cair o volume.
    """
    if not trechos:
        return voz
    sos = signal.butter(4, [400, 3000], btype="band", fs=SR, output="sos")
    filtrada = signal.sosfilt(sos, voz, axis=0)
    pico = float(np.max(np.abs(filtrada))) or 1.0
    filtrada = np.tanh(0.8 * filtrada / pico) * pico / np.tanh(0.8)
    mistura = np.zeros(len(voz))
    for t0, t1 in trechos:
        i0, i1 = int(t0 * SR), min(len(voz), int(t1 * SR))
        if i1 > i0:
            mistura[i0:i1] = rampa(i1 - i0, int(0.03 * SR))
    sel = mistura > 0.5
    if np.any(sel):
        ganho = np.sqrt(np.mean(voz[sel] ** 2) / (np.mean(filtrada[sel] ** 2) + 1e-12))
        filtrada = filtrada * ganho
    return voz * (1 - mistura[:, None]) + filtrada * mistura[:, None]


def trilha_do_mix(mix: dict, n: int) -> np.ndarray | None:
    dur = n / SR
    if mix.get("musica"):  # faixas do usuário
        out = np.zeros((n, 2), np.float32)
        for m in mix["musica"]:
            ini, fim = float(m.get("inicio", 0)), float(m.get("fim", dur))
            x = ler_audio(
                Path(m["arquivo"]), float(m.get("inicio_arquivo", 0)), fim - ini
            )
            x = (
                x
                * rampa(len(x), int(0.5 * SR))[:, None]
                * 10 ** (float(m.get("volume_db", 0)) / 20)
            )
            somar(out, x, int(ini * SR))
        return out
    t = mix.get("trilha", {})
    if t.get("auto"):
        x = gerar_trilha(t["secoes"], dur, t.get("final"), int(t.get("semente", 7)))
        return x[:n] * 10 ** (float(t.get("volume_db", 0)) / 20)
    return None


def eq_trilha(x: np.ndarray) -> np.ndarray:
    """Abre espaço para a voz: corta o sub-grave e cava um pouco a região de presença."""
    b, a = signal.butter(2, 70, btype="high", fs=SR)
    x = signal.lfilter(b, a, x, axis=0)
    b, a = signal.iirpeak(2500, 0.8, fs=SR)
    presenca = signal.lfilter(b, a, x, axis=0)
    return x - 0.45 * presenca  # ~ -5 dB em torno de 2,5 kHz


def loudnorm(
    entrada: Path, saida: Path, alvo: float = -14.0, pico: float = -1.5
) -> dict:
    """Dois passes. Pico de -1,5 dBTP deixa folga para o AAC, que sobe o pico ~0,5 dB."""
    filtro = f"loudnorm=I={alvo}:TP={pico}:LRA=11"
    p1 = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-i",
            str(entrada),
            "-af",
            filtro + ":print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stderr
    m = json.loads(re.findall(r"\{[^{}]*\}", p1)[-1])
    filtro2 = (
        f"{filtro}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
        f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(entrada),
            "-af",
            filtro2,
            "-ar",
            str(SR),
            str(saida),
        ],
        check=True,
    )
    return m


def mixar(voz_path: Path, mix_path: Path, saida: Path) -> dict:
    mix = json.loads(mix_path.read_text())
    voz = ler_audio(voz_path)
    n = len(voz)

    voz = abafar(voz, mix.get("abafar", []))
    fala = envelope_fala(voz)
    nivel_voz = np.sqrt(np.mean(voz[fala > 0.6] ** 2)) if np.any(fala > 0.6) else 0.1
    pico_voz = float(np.max(np.abs(voz))) or 1.0

    # Insertos com som próprio entram no barramento da voz (também abaixam a trilha).
    for ins in mix.get("insertos", []):
        x = ler_audio(Path(ins["arquivo"]), ins.get("inicio_midia", 0), ins["dur"])
        x = x * rampa(len(x), int(0.06 * SR))[:, None]
        rms = np.sqrt(np.mean(x**2)) + 1e-9
        x = x * (nivel_voz / rms) * 10 ** (float(ins.get("ganho_db", 0)) / 20)
        somar(voz, x, int(ins["t"] * SR))
    fala = envelope_fala(voz)

    efeitos = np.zeros((n, 2), np.float32)
    extra = float(mix.get("efeitos_volume_db", 0))
    for s in mix.get("sons", []):
        som, ancora = efeito(s["som"])
        ganho = pico_voz * 10 ** ((GANHO_DB[s["som"]] + extra) / 20)
        somar(efeitos, som * ganho, int((s["t"] - ancora) * SR))

    trilha = trilha_do_mix(mix, n)
    if trilha is not None:
        trilha = eq_trilha(trilha)
        rms_t = np.sqrt(np.mean(trilha**2)) + 1e-9
        base = nivel_voz / rms_t * 10 ** (MUSICA_SOZINHA_DB / 20)
        ganho = base * 10 ** (-DUCKING_DB * fala / 20)
        trilha = trilha * ganho[:, None]
        fim = rampa(n, int(1.2 * SR))  # some no final
        trilha *= np.where(np.arange(n) > n // 2, fim, 1)[:, None]
    else:
        trilha = np.zeros_like(voz)

    total = radio(voz + trilha, mix.get("radio", [])) + efeitos
    with tempfile.TemporaryDirectory() as tmp:
        bruto = Path(tmp) / "bruto.wav"
        gravar_wav(bruto, total / max(1.0, float(np.max(np.abs(total)))))
        medida = loudnorm(bruto, saida)
    return {
        "efeitos": len(mix.get("sons", [])),
        "abafados": len(mix.get("abafar", [])),
        "radio": len(mix.get("radio", [])),
        "insertos": len(mix.get("insertos", [])),
        "trilha": "usuário"
        if mix.get("musica")
        else ("gerada" if mix.get("trilha", {}).get("auto") else "nenhuma"),
        "loudness_entrada": medida["input_i"],
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Mixa voz + efeitos + trilha a partir do mix.json"
    )
    ap.add_argument(
        "--voz", type=Path, required=True, help="vídeo/áudio cortado pelo Video Use"
    )
    ap.add_argument(
        "--mix", type=Path, required=True, help="mix.json gerado pelo montar.py"
    )
    ap.add_argument("-o", "--output", type=Path, required=True, help="WAV de saída")
    args = ap.parse_args()
    info = mixar(args.voz, args.mix, args.output)
    print(f"mixado: {args.output} {info}")


if __name__ == "__main__":
    main()
