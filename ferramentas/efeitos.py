"""Efeitos sonoros sintetizados (sem direitos autorais: tudo é gerado aqui).

Cada efeito devolve um array estéreo float32 (n, 2) a 48 kHz, com pico em
-1 dBFS, e tem um "ponto de impacto" (âncora): o instante, dentro do som, que
deve coincidir com o evento na tela. Um whoosh, por exemplo, cresce antes do
impacto; um clique não tem preparo.

Uso:
    from efeitos import efeito, EFEITOS
    som, ancora = efeito("whoosh_suave")
    python3 ferramentas/efeitos.py pasta/   # grava todos em WAV para ouvir
"""

from __future__ import annotations

import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000


def _env(n: int, ataque: float, queda: float, curva: float = 3.0) -> np.ndarray:
    """Envelope ataque linear + queda exponencial (em segundos)."""
    a = max(1, int(ataque * SR))
    t = np.arange(n - a) / SR
    return np.concatenate(
        [np.linspace(0, 1, a), np.exp(-curva * t / max(queda, 1e-3))]
    )[:n]


def _norm(x: np.ndarray, pico_db: float = -1.0) -> np.ndarray:
    return (x / (np.max(np.abs(x)) + 1e-9) * 10 ** (pico_db / 20)).astype(np.float32)


def _estereo(m: np.ndarray, pan_ini: float = 0.0, pan_fim: float = 0.0) -> np.ndarray:
    """Mono -> estéreo com pan que pode andar (de -1 esquerda a 1 direita)."""
    pan = np.linspace(pan_ini, pan_fim, len(m))
    ang = (pan + 1) * np.pi / 4
    return np.stack([m * np.cos(ang), m * np.sin(ang)], axis=1)


def _ruido(n: int, semente: int) -> np.ndarray:
    return np.random.default_rng(semente).standard_normal(n)


def _varredura(
    ruido: np.ndarray, f_ini: float, f_meio: float, f_fim: float, q: float
) -> np.ndarray:
    """Passa-faixa que varre f_ini -> f_meio -> f_fim (em blocos de 10 ms)."""
    n, bloco = len(ruido), int(0.01 * SR)
    out = np.zeros(n)
    meio = n // 2
    zi = None
    for i in range(0, n, bloco):
        f = (
            f_ini * (f_meio / f_ini) ** (i / meio)
            if i < meio
            else f_meio * (f_fim / f_meio) ** ((i - meio) / (n - meio))
        )
        b, a = signal.iirpeak(min(f, SR / 2 - 100), q, fs=SR)
        if zi is None:
            zi = signal.lfilter_zi(b, a) * 0
        out[i : i + bloco], zi = signal.lfilter(b, a, ruido[i : i + bloco], zi=zi)
    return out


def whoosh(suave: bool = False) -> tuple[np.ndarray, float]:
    dur = 0.9 if suave else 0.65
    n = int(dur * SR)
    pico = 0.55 if suave else 0.4
    x = _varredura(
        _ruido(n, 11),
        350 if suave else 500,
        1800 if suave else 3200,
        600 if suave else 900,
        1.2,
    )
    t = np.arange(n) / SR
    env = np.where(
        t < pico, (t / pico) ** 2, np.exp(-(t - pico) / (0.12 if suave else 0.08))
    )
    x = x * env
    if suave:
        b, a = signal.butter(2, 5000, fs=SR)
        x = signal.lfilter(b, a, x)
    return _norm(_estereo(x, -0.6, 0.6)), pico


def impacto() -> tuple[np.ndarray, float]:
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 62 * np.exp(-t * 2.5) + 38  # queda de pitch: "tum"
    corpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28)
    clique = _ruido(n, 3) * np.exp(-t / 0.006) * 0.5
    b, a = signal.butter(2, 3000, fs=SR)
    x = np.tanh(1.6 * (corpo + signal.lfilter(b, a, clique)))
    return _norm(_estereo(x)), 0.0


def pop(suave: bool = False) -> tuple[np.ndarray, float]:
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    if suave:  # "bolha": seno agudo que desce rápido, ataque macio
        f = 1150 * np.exp(-t * 18) + 520
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.003, 0.05, 4)
    else:
        f = 700 * np.exp(-t * 30) + 260
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, 0.04, 4)
        x += _ruido(n, 5) * np.exp(-t / 0.003) * 0.25
    return _norm(_estereo(x)), 0.0


def tick() -> tuple[np.ndarray, float]:
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    x = (
        np.sin(2 * np.pi * 2600 * t) * 0.6 + np.sin(2 * np.pi * 4100 * t) * 0.3
    ) * np.exp(-t / 0.012)
    return _norm(_estereo(x, 0.15, 0.15)), 0.0


def respiro() -> tuple[np.ndarray, float]:
    """Sopro de ar que cresce e some: transição delicada."""
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    b, a = signal.butter(2, [1500, 9000], btype="band", fs=SR)
    x = signal.lfilter(b, a, _ruido(n, 21))
    pico = 0.45
    env = np.where(
        t < pico, np.sin(np.pi / 2 * t / pico) ** 2, np.exp(-(t - pico) / 0.18)
    )
    return _norm(_estereo(x * env, -0.3, 0.3)), pico


def sino() -> tuple[np.ndarray, float]:
    """Sino suave: parciais inarmônicas de sino, com uma quinta por cima."""
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f0, ganho in ((880.0, 1.0), (1318.5, 0.45)):
        for razao, g, dec in (
            (1.0, 1.0, 1.4),
            (2.76, 0.35, 0.6),
            (5.4, 0.15, 0.3),
            (0.5, 0.25, 1.8),
        ):
            x += (
                ganho
                * g
                * np.sin(2 * np.pi * f0 * razao * t + razao)
                * np.exp(-t / dec)
            )
    x *= _env(n, 0.004, 10, 0.1)
    return _norm(_estereo(x, -0.1, 0.1)), 0.0


EFEITOS = {
    "whoosh": lambda: whoosh(False),
    "whoosh_suave": lambda: whoosh(True),
    "impacto": impacto,
    "pop": lambda: pop(False),
    "pop_suave": lambda: pop(True),
    "tick": tick,
    "respiro": respiro,
    "sino": sino,
}
# Volume de cada efeito na mixagem, em dB relativos ao pico da voz.
# Efeito bom é sentido, não notado: fica bem abaixo da fala.
GANHO_DB = {
    "whoosh": -15,
    "whoosh_suave": -17,
    "impacto": -13,
    "pop": -17,
    "pop_suave": -18,
    "tick": -21,
    "respiro": -19,
    "sino": -15,
}


def efeito(nome: str) -> tuple[np.ndarray, float]:
    if nome not in EFEITOS:
        raise KeyError(
            f"efeito desconhecido: {nome} (disponíveis: {', '.join(EFEITOS)})"
        )
    return EFEITOS[nome]()


def gravar_wav(path: Path, x: np.ndarray, sr: int = SR) -> None:
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(pcm.shape[1] if pcm.ndim > 1 else 1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    destino = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    destino.mkdir(parents=True, exist_ok=True)
    for nome in EFEITOS:
        som, ancora = efeito(nome)
        gravar_wav(destino / f"{nome}.wav", som)
        print(f"{nome:13s} {len(som) / SR:.2f}s  impacto em {ancora:.2f}s")
