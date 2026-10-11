"""Trilhas sonoras geradas por síntese (sem direitos autorais: tudo é criado aqui).

Três humores, todos discretos e elegantes, para ficar por baixo da voz:
    calma    pad suave + arpejo esparso + baixo (84 BPM, Ré maior)
    leve     pad + arpejo em colcheias + chocalho + bumbo leve (96 BPM, Fá maior)
    inspira  pad brilhante + arpejo + bumbo e palma suaves (102 BPM, Lá maior)

Uma trilha é feita de seções (uma por capítulo do vídeo). Na virada de seção a
música cai e volta em outro humor, como no vídeo de referência. Depois da
última fala entra um encerramento: acorde da tônica que se abre e some.

Uso:
    from trilha import gerar_trilha
    audio = gerar_trilha([{"inicio": 0, "fim": 20, "humor": "calma"}, ...], duracao=30, final=27)
    python3 ferramentas/trilha.py saida.wav   # demo de 45 s com os três humores
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000

HUMORES = {
    "calma": {
        "bpm": 84,
        "acordes": [
            [50, 57, 61, 64, 66],
            [47, 54, 57, 61, 62],
            [43, 50, 54, 59, 61],
            [45, 52, 59, 64, 66],
        ],
        "arpejo": [
            0,
            2,
            3,
            None,
            4,
            3,
            None,
            None,
        ],  # índices nas notas do acorde (+1 oitava)
        "passo": 0.5,  # em tempos
        "bumbo": [],
        "chocalho": False,
        "palma": [],
        "brilho": 1800,
    },
    "leve": {
        "bpm": 96,
        "acordes": [
            [53, 57, 60, 64],
            [45, 52, 55, 60],
            [50, 53, 57, 60, 64],
            [46, 53, 57, 62],
        ],
        "arpejo": [0, 1, 2, 3, 2, 1, 2, 3],
        "passo": 0.5,
        "bumbo": [0],
        "chocalho": True,
        "palma": [],
        "brilho": 2400,
    },
    "inspira": {
        "bpm": 102,
        "acordes": [
            [45, 52, 57, 59, 61],
            [44, 52, 59, 64],
            [42, 49, 52, 57],
            [50, 57, 61, 64, 66],
        ],
        "arpejo": [0, 2, 4, 2, 3, 2, 4, 3],
        "passo": 0.5,
        "bumbo": [0, 2],
        "chocalho": True,
        "palma": [1, 3],
        "brilho": 3200,
    },
}
# Humores sombrios para vídeos sérios ("tom": "tenso" no roteiro): menor,
# grave, pouca melodia, pulso no baixo.
HUMORES["tensa"] = {
    "bpm": 70,
    "acordes": [
        [38, 45, 50, 53],
        [34, 41, 46, 50, 53],
        [36, 43, 48, 51],
        [33, 45, 49, 52],
    ],
    "arpejo": [0, None, None, None, 2, None, None, None],
    "passo": 0.5,
    "bumbo": [0],
    "chocalho": False,
    "palma": [],
    "brilho": 900,
}
HUMORES["tensa_pulso"] = {
    "bpm": 84,
    "acordes": [[38, 45, 50, 53], [39, 46, 51, 55], [38, 45, 50, 53], [36, 43, 48, 51]],
    "arpejo": [None, None, 3, None, None, None, 2, None],
    "passo": 0.5,
    "bumbo": [0, 1.5, 2],
    "chocalho": True,
    "palma": [],
    "brilho": 1100,
}
TEMPOS_POR_ACORDE = 8  # dois compassos de 4/4


def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def _pad_nota(f: float, n: int, rng: np.random.Generator) -> np.ndarray:
    """Nota de pad: harmônicos com leve desafinação (coro), timbre quente."""
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(1, 6):
        for cents in (-4, 4):
            fk = f * k * 2 ** (cents / 1200)
            x += (1 / k**1.6) * np.sin(2 * np.pi * fk * t + rng.uniform(0, 2 * np.pi))
    return x


def _envelope(n: int, ataque: float, soltura: float) -> np.ndarray:
    a, r = min(n, int(ataque * SR)), min(n, int(soltura * SR))
    env = np.ones(n)
    env[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    env[n - r :] *= np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    return env


def _pluck(f: float, dur: float) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = (
        np.sin(2 * np.pi * f * t)
        + 0.35 * np.sin(4 * np.pi * f * t)
        + 0.12 * np.sin(6 * np.pi * f * t)
    )
    return x * np.exp(-t / 0.32) * np.minimum(1, t / 0.004)


def _bumbo() -> np.ndarray:
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 75 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)


def _chocalho(rng: np.random.Generator) -> np.ndarray:
    n = int(0.06 * SR)
    b, a = signal.butter(2, 6000, btype="high", fs=SR)
    return signal.lfilter(b, a, rng.standard_normal(n)) * np.exp(
        -np.arange(n) / SR / 0.015
    )


def _palma(rng: np.random.Generator) -> np.ndarray:
    n = int(0.18 * SR)
    b, a = signal.butter(2, [900, 4000], btype="band", fs=SR)
    return signal.lfilter(b, a, rng.standard_normal(n)) * np.exp(
        -np.arange(n) / SR / 0.05
    )


def _reverb(x: np.ndarray, rng: np.random.Generator, cauda: float = 2.4) -> np.ndarray:
    n = int(cauda * SR)
    t = np.arange(n) / SR
    b, a = signal.butter(1, 5000, fs=SR)
    ir = np.stack(
        [
            signal.lfilter(b, a, rng.standard_normal(n)) * np.exp(-t / (cauda / 5))
            for _ in range(2)
        ],
        1,
    )
    ir /= np.sqrt(np.sum(ir**2, axis=0, keepdims=True))
    return np.stack(
        [signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1
    )


def _somar(dest: np.ndarray, x: np.ndarray, ini: int, pan: float = 0.0) -> None:
    if ini >= len(dest) or len(x) == 0:
        return
    x = x[: len(dest) - ini]
    ang = (pan + 1) * np.pi / 4
    dest[ini : ini + len(x), 0] += x * np.cos(ang)
    dest[ini : ini + len(x), 1] += x * np.sin(ang)


def secao(humor: str, dur: float, semente: int = 7, acorde_ini: int = 0) -> np.ndarray:
    """Gera `dur` segundos de música num humor (estéreo, pico -3 dBFS)."""
    h = HUMORES[humor]
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    seco = np.zeros((n + int(1.5 * SR), 2))
    molhado = np.zeros_like(seco)
    beat = 60 / h["bpm"]
    dur_acorde = TEMPOS_POR_ACORDE * beat
    n_acordes = int(np.ceil(dur / dur_acorde)) + 1
    b_lp, a_lp = signal.butter(2, h["brilho"], fs=SR)

    for i in range(n_acordes):
        notas = h["acordes"][(acorde_ini + i) % len(h["acordes"])]
        t0 = i * dur_acorde
        ini = int(t0 * SR)
        # pad (com soltura longa que atravessa o próximo acorde)
        npad = int((dur_acorde + 1.2) * SR)
        pad = sum(_pad_nota(hz(m), npad, rng) for m in notas) / len(notas)
        pad = signal.lfilter(b_lp, a_lp, pad) * _envelope(npad, 0.9, 1.4)
        _somar(seco, pad * 0.5, ini, -0.15)
        _somar(seco, pad * 0.5, ini, 0.15)
        _somar(molhado, pad * 0.6, ini)
        # baixo: fundamental do acorde na região grave
        raiz = notas[0]
        while raiz > 47:
            raiz -= 12
        nb = int(dur_acorde * SR)
        tb = np.arange(nb) / SR
        baixo = (
            np.sin(2 * np.pi * hz(raiz) * tb) + 0.2 * np.sin(4 * np.pi * hz(raiz) * tb)
        ) * _envelope(nb, 0.05, 0.6)
        _somar(seco, baixo * 0.55, ini)
        # arpejo + percussão, nota a nota
        passos = int(TEMPOS_POR_ACORDE / h["passo"])
        for p in range(passos):
            tp = t0 + p * h["passo"] * beat
            idx = h["arpejo"][p % len(h["arpejo"])]
            if idx is not None:
                nota = notas[idx % len(notas)] + 12
                pl = _pluck(hz(nota), 0.9) * rng.uniform(0.75, 1.0)
                pan = 0.35 if p % 2 else -0.35
                _somar(seco, pl * 0.22, int(tp * SR), pan)
                _somar(molhado, pl * 0.3, int(tp * SR), pan)
                eco = int((tp + 0.75 * beat) * SR)  # eco em colcheia pontuada
                _somar(molhado, pl * 0.12, eco, -pan)
            tempo_no_compasso = (p * h["passo"]) % 4
            if tempo_no_compasso in h["bumbo"]:
                _somar(seco, _bumbo() * 0.6, int(tp * SR))
            if tempo_no_compasso in h["palma"]:
                _somar(molhado, _palma(rng) * 0.25, int(tp * SR))
            if h["chocalho"]:
                _somar(
                    seco, _chocalho(rng) * (0.08 if p % 2 else 0.05), int(tp * SR), 0.4
                )

    x = seco + 0.55 * _reverb(molhado, rng)
    x = np.tanh(x / (np.max(np.abs(x)) + 1e-9) * 1.2)
    x = x[:n] * _envelope(n, 0.25, 0.35)[:, None]
    return (x / (np.max(np.abs(x)) + 1e-9) * 10 ** (-3 / 20)).astype(np.float32)


def encerramento(dur: float, humor: str, semente: int = 7) -> np.ndarray:
    """Acorde da tônica que se abre devagar e some: fundo da tela final."""
    h = HUMORES[humor]
    rng = np.random.default_rng(semente + 99)
    n = int(dur * SR)
    notas = h["acordes"][0] + [h["acordes"][0][-1] + 12]
    pad = sum(_pad_nota(hz(m), n, rng) for m in notas) / len(notas)
    b, a = signal.butter(2, h["brilho"] * 1.3, fs=SR)
    pad = signal.lfilter(b, a, pad) * _envelope(n, 0.6, min(1.6, dur * 0.6))
    x = np.stack([pad, pad], 1)
    x = 0.7 * x + 0.5 * _reverb(x, rng, 3.0)
    return (x / (np.max(np.abs(x)) + 1e-9) * 10 ** (-3 / 20)).astype(np.float32)


def gerar_trilha(
    secoes: list[dict], duracao: float, final: float | None = None, semente: int = 7
) -> np.ndarray:
    """Monta a trilha inteira: seções em sequência, quedas nas viradas e encerramento."""
    out = np.zeros((int(duracao * SR) + 1, 2), dtype=np.float32)
    final = duracao if final is None else final
    for k, s in enumerate(secoes):
        ini, fim = float(s["inicio"]), min(float(s["fim"]), final)
        if fim - ini < 0.3:
            continue
        trecho = secao(s.get("humor", "calma"), fim - ini, semente + k, acorde_ini=k)
        a = int(ini * SR)
        out[a : a + len(trecho)] += trecho[: len(out) - a]
    if duracao - final > 0.3:
        humor_fim = secoes[-1].get("humor", "calma") if secoes else "calma"
        fim = encerramento(duracao - final, humor_fim, semente)
        a = int(final * SR)
        out[a : a + len(fim)] += fim[: len(out) - a]
    return out


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from efeitos import gravar_wav

    demo = gerar_trilha(
        [
            {"inicio": 0, "fim": 14, "humor": "calma"},
            {"inicio": 14, "fim": 27, "humor": "leve"},
            {"inicio": 27, "fim": 40, "humor": "inspira"},
        ],
        duracao=45,
        final=40,
    )
    saida = Path(sys.argv[1] if len(sys.argv) > 1 else "trilha_demo.wav")
    gravar_wav(saida, demo)
    print(f"trilha demo: {saida} ({len(demo) / SR:.1f}s)")
