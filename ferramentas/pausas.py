"""Monta o edl.json de um vídeo de uma tomada só, tirando pausas e respirações.

Para fala corrida sem repetição (o caso dos pedidos "só cortes + legenda"). Mede
o áudio em quadros de 20 ms:

  - silêncio: abaixo de -42 dB;
  - pausa: trecho sem fala (tudo abaixo de -30 dB) com silêncios de pelo
    menos 0,2 s, do primeiro silêncio de 80 ms ao último quadro silencioso
    antes da fala. A respiração entre os dois sai junto. O início exige 80 ms
    porque um silêncio mais curto pode ser o fechamento de uma consoante no
    meio da última palavra ("seguin-t-e");
  - o que fica entre a fala e o primeiro silêncio (ou entre o último silêncio
    e a fala) é mantido: pode ser o fim fraco de uma palavra ("s", "a") ou o
    começo de outra ("se", "fita").

Cada corte deixa 40 ms de folga de cada lado, com as bordas em quadros
inteiros (o render.py precisa disso para manter a voz sincronizada). Corte que
tiraria menos de 0,12 s fica de fora: só daria pulo na imagem.

O ajustar_cortes.py não serve aqui: ele trata a respiração como fala.

Uso:
    python3 ferramentas/pausas.py videos/x/fonte.mp4            # grava videos/x/edit/edl.json
    python3 ferramentas/pausas.py videos/x/fonte.mp4 --simular  # só lista as pausas
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from fractions import Fraction
from pathlib import Path

import numpy as np

SR = 16000
J = 0.02  # 20 ms por quadro de medida
FALA = -30.0  # acima disso é fala
SILENCIO = -42.0  # abaixo disso é silêncio
PAUSA_MIN = 0.2  # do começo do primeiro silêncio ao fim do último
SIL_MIN = 4  # quadros seguidos (80 ms): o fechamento de um "t" ou "p" é mais curto
FOLGA = 0.04
GANHO_MIN = 0.12


def niveis(video: Path) -> np.ndarray:
    pcm = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(video), "-map", "0:a:0",
         "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True,
    ).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    n = int(J * SR)
    k = len(x) // n
    return 20 * np.log10(np.sqrt((x[: k * n].reshape(k, n) ** 2).mean(1) + 1e-12))


def sonda(video: Path, campo: str) -> str:
    return subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", campo[0] + ":0", "-show_entries",
         "stream=" + campo[2:], "-of", "csv=p=0", str(video)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def pausas(db: np.ndarray) -> list[tuple[float, float]]:
    """(fim da fala, começo da próxima fala) de cada pausa, em segundos."""
    out, i, k = [], 0, len(db)
    while i < k:
        if db[i] >= FALA:
            i += 1
            continue
        j = i
        while j < k and db[j] < FALA:
            j += 1
        corridas, m = [], i
        while m < j:
            if db[m] < SILENCIO:
                n = m
                while n < j and db[n] < SILENCIO:
                    n += 1
                if n - m >= SIL_MIN:
                    corridas.append((m, n))
                m = n
            else:
                m += 1
        if not corridas:
            i = j
            continue
        # a pausa começa no primeiro silêncio de verdade e vai até o último
        # quadro silencioso antes da fala (aí não há fim de palavra a proteger)
        e = corridas[0][0]
        s_ = max(m for m in range(e, j) if db[m] < SILENCIO) + 1
        if (s_ - e) * J >= PAUSA_MIN:
            out.append((e * J, s_ * J))
        i = j
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="edl.json sem pausas nem respirações")
    ap.add_argument("video", type=Path)
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()

    video = a.video.resolve()
    fps = Fraction(sonda(video, "v=r_frame_rate"))
    db = niveis(video)
    fim_audio = len(db) * J
    quadros = int(fim_audio * fps)  # último quadro com áudio

    # começo: pula o silêncio antes da primeira fala
    primeiro = next(m for m in range(len(db)) if db[m] >= FALA) * J
    trechos, ini = [], max(0, math.floor((primeiro - FOLGA) * fps))
    tirado = ini / fps
    for e, s in pausas(db):
        if e < primeiro:
            continue
        q1 = math.ceil((e + FOLGA) * fps)
        q2 = math.floor((s - FOLGA) * fps)
        if s >= fim_audio or (q2 - q1) / fps < GANHO_MIN:
            continue
        print(f"  {e:6.2f} – {s:6.2f}: tira {float((q2 - q1) / fps):.2f} s")
        trechos.append((ini, q1))
        tirado += (q2 - q1) / fps
        ini = q2
    ultimo = next(m for m in range(len(db) - 1, -1, -1) if db[m] >= FALA) * J + J
    q_fim = min(quadros, math.ceil((ultimo + 0.35) * fps))  # respiro curto no fim
    trechos.append((ini, q_fim))
    tirado += (quadros - q_fim) / fps
    total = sum(b - c for c, b in trechos) / fps
    print(f"{len(trechos)} trechos: {fim_audio:.1f} s → {float(total):.1f} s")
    if a.simular:
        return

    edl = {
        "version": 1,
        "sources": {video.stem: str(video)},
        "ranges": [
            {"source": video.stem, "start": round(float(c / fps), 4), "end": round(float(b / fps), 4)}
            for c, b in trechos
        ],
        "total_duration_s": round(float(total), 3),
    }
    destino = video.parent / "edit" / "edl.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"→ {destino}")


if __name__ == "__main__":
    main()
