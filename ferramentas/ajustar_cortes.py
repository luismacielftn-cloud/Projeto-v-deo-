"""Encosta as bordas de corte de um edl.json no silêncio real do áudio.

O Whisper costuma marcar o fim da última palavra antes de uma pausa cedo
demais (até ~0,7 s), e um corte feito nesse tempo come o fim da palavra.
Este script mede o silêncio direto no áudio de cada fonte e:

  - fim do trecho caindo em fala  → avança até o início do silêncio seguinte
  - início caindo em fala         → recua até o fim do silêncio anterior
  - borda caindo em silêncio longo → aperta, deixando só uma folga curta
    (assim não sobra "ar morto" no corte)

Trechos com "manter": true no edl.json ficam como estão: use para silêncios
intencionais, como o respiro da tela final ou o espaço de um inserto com som.

O limiar de silêncio é adaptativo: piso de ruído da fonte + 10 dB.

Uso:
    python3 ferramentas/ajustar_cortes.py <edit>/edl.json            # ajusta no lugar (backup .orig.json)
    python3 ferramentas/ajustar_cortes.py <edit>/edl.json --simular  # só mostra o que mudaria
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np

SR = 16000
JANELA = 0.02  # 20 ms por quadro de RMS
SIL_MIN = 0.12  # silêncio mais curto que isso não conta
BUSCA_FIM = 0.9  # quanto o fim pode avançar procurando silêncio
BUSCA_INICIO = 0.6  # quanto o início pode recuar procurando silêncio
FOLGA_FIM = 0.08  # folga mantida depois da última palavra
FOLGA_INICIO = 0.06  # folga mantida antes da primeira palavra


def carregar_audio(path: Path) -> np.ndarray:
    pcm = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-f",
            "s16le",
            "-ac",
            "1",
            "-ar",
            str(SR),
            "-",
        ],
        check=True,
        capture_output=True,
    ).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0


def silencios(audio: np.ndarray) -> tuple[list[tuple[float, float]], float]:
    n = int(SR * JANELA)
    q = len(audio) // n
    rms = np.sqrt(np.mean(audio[: q * n].reshape(q, n) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    piso = float(np.percentile(db, 10))
    limiar = min(max(piso + 10, -55.0), -25.0)
    quieto = db < limiar
    out: list[tuple[float, float]] = []
    i = 0
    while i < q:
        if quieto[i]:
            j = i
            while j < q and quieto[j]:
                j += 1
            if (j - i) * JANELA >= SIL_MIN:
                out.append((i * JANELA, j * JANELA))
            i = j
        else:
            i += 1
    return out, limiar


def dentro(t: float, sils: list[tuple[float, float]]) -> tuple[float, float] | None:
    for s0, s1 in sils:
        if s0 <= t <= s1:
            return s0, s1
    return None


def ajustar_fim(t: float, sils, dur: float) -> float:
    s = dentro(t, sils)
    if s:  # já está em silêncio: só tira o ar morto em excesso
        return min(t, s[0] + FOLGA_FIM)
    for s0, s1 in sils:
        if t < s0 <= t + BUSCA_FIM:
            return min(s0 + FOLGA_FIM, s1, dur)
    return t  # não achou silêncio perto: mantém e avisa


def ajustar_inicio(t: float, sils) -> float:
    s = dentro(t, sils)
    if s:
        return max(t, s[1] - FOLGA_INICIO)
    for s0, s1 in reversed(sils):
        if t - BUSCA_INICIO <= s1 < t:
            return max(s1 - FOLGA_INICIO, s0, 0.0)
    return t


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("edl", type=Path)
    ap.add_argument("--simular", action="store_true")
    args = ap.parse_args()

    edl = json.loads(args.edl.read_text())
    cache: dict[str, tuple[list, float, float]] = {}
    avisos = 0

    for r in edl["ranges"]:
        src = r["source"]
        if src not in cache:
            audio = carregar_audio(Path(edl["sources"][src]))
            sils, limiar = silencios(audio)
            cache[src] = (sils, len(audio) / SR, limiar)
            print(f"{src}: {len(sils)} silêncios (limiar {limiar:.1f} dB)")
        sils, dur, _ = cache[src]

        ini0, fim0 = r["start"], r["end"]
        if r.get(
            "manter"
        ):  # silêncio intencional (tela final, inserto com som): não mexe
            print(f"  {ini0:7.2f}-{fim0:7.2f}   mantido  {r.get('quote', '')[:40]}")
            continue
        ini, fim = ajustar_inicio(ini0, sils), ajustar_fim(fim0, sils, dur)
        if fim <= ini:
            ini, fim = ini0, fim0
        marca = ""
        # bordas no começo ou no fim do arquivo não são cortes de verdade
        if not dentro(ini, sils) and ini == ini0 and ini > 0.05:
            marca += "  ! início em fala"
        if not dentro(fim, sils) and fim == fim0 and fim < dur - 0.05:
            marca += "  ! fim em fala"
        avisos += bool(marca)
        print(
            f"  {ini0:7.2f}-{fim0:7.2f} → {ini:7.2f}-{fim:7.2f}  {r.get('quote', '')[:40]}{marca}"
        )
        r["start"], r["end"] = round(ini, 3), round(fim, 3)

    total = sum(r["end"] - r["start"] for r in edl["ranges"])
    edl["total_duration_s"] = round(total, 2)
    print(
        f"duração total: {total:.2f}s"
        + (f"  ({avisos} borda(s) para conferir)" if avisos else "")
    )

    if not args.simular:
        shutil.copy(args.edl, args.edl.with_suffix(".orig.json"))
        args.edl.write_text(json.dumps(edl, indent=2, ensure_ascii=False))
        print(f"salvo: {args.edl}")


if __name__ == "__main__":
    main()
