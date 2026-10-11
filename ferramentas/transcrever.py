"""Transcrição local e gratuita (faster-whisper) no formato do ElevenLabs Scribe.

Substitui `helpers/transcribe.py` do Video Use quando não há ELEVENLABS_API_KEY.
Grava <edit_dir>/transcripts/<nome>.json com a mesma estrutura que o Scribe
devolve (lista `words` com entradas `word` e `spacing`), então
`pack_transcripts.py`, `render.py --build-subtitles` e o resto do Video Use
funcionam sem mudança.

Com --flat grava também o formato que o talking-head-recut do HyperFrames lê:
uma lista simples [{"text", "start", "end"}, ...].

Uso:
    python3 ferramentas/transcrever.py <video>
    python3 ferramentas/transcrever.py <video> --edit-dir videos/x/edit
    python3 ferramentas/transcrever.py <video> --modelo medium
    python3 ferramentas/transcrever.py <video> --flat videos/x/transcript.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

# Prepara o Whisper para manter hesitações e repetições em vez de "limpar" a fala.
# Sem isso ele tende a omitir "é...", "hum", "tipo" e falsos começos, que são
# justamente o que o corte precisa enxergar.
PROMPT_VERBATIM = (
    "Ééé... então, tipo, hum, né? Ahn, eu, eu acho que... assim, é, "
    "o que eu quero, o que eu quero dizer é isso."
)


def audio_16k(path: Path, faixa: int) -> np.ndarray:
    """Decodifica com o ffmpeg do sistema (o PyAV 19 é incompatível com o faster-whisper)."""
    pcm = subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-map",
            f"0:a:{faixa}",
            "-f",
            "s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-",
        ],
        check=True,
        capture_output=True,
    ).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0


def transcrever(video: Path, modelo: str, idioma: str, faixa: int) -> dict:
    from faster_whisper import WhisperModel

    model = WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, info = model.transcribe(
        audio_16k(video, faixa),
        language=idioma,
        word_timestamps=True,
        initial_prompt=PROMPT_VERBATIM,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 300},
    )

    palavras: list[dict] = []
    for seg in segs:
        for w in seg.words or []:
            texto = w.word.strip()
            if not texto:
                continue
            palavras.append(
                {
                    "text": texto,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "type": "word",
                    "speaker_id": "speaker_0",
                    "logprob": round(float(np.log(max(w.probability, 1e-6))), 4),
                }
            )

    # Entradas de "spacing" entre palavras, como o Scribe faz: é delas que o
    # pack_transcripts tira os silêncios.
    words: list[dict] = []
    for i, w in enumerate(palavras):
        if i > 0 and w["start"] > palavras[i - 1]["end"]:
            words.append(
                {
                    "text": " ",
                    "start": palavras[i - 1]["end"],
                    "end": w["start"],
                    "type": "spacing",
                    "speaker_id": "speaker_0",
                }
            )
        words.append(w)

    return {
        "language_code": info.language,
        "language_probability": round(info.language_probability, 3),
        "text": " ".join(p["text"] for p in palavras),
        "words": words,
        "transcriber": f"faster-whisper/{modelo}",
        "duration": round(info.duration, 3),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcrição local no formato Scribe")
    ap.add_argument("video", type=Path)
    ap.add_argument(
        "--edit-dir", type=Path, default=None, help="padrão: <pasta do vídeo>/edit"
    )
    ap.add_argument(
        "--modelo", default="small", help="tiny, base, small (padrão), medium, large-v3"
    )
    ap.add_argument("--idioma", default="pt")
    ap.add_argument("--audio-track", type=int, default=0)
    ap.add_argument(
        "--flat",
        type=Path,
        default=None,
        help="grava também a lista simples de palavras (talking-head-recut)",
    )
    ap.add_argument("--forcar", action="store_true", help="ignora o cache")
    args = ap.parse_args()

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"vídeo não encontrado: {video}")

    edit_dir = (args.edit_dir or video.parent / "edit").resolve()
    sufixo = "" if args.audio_track == 0 else f".track{args.audio_track}"
    out = edit_dir / "transcripts" / f"{video.stem}{sufixo}.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    if out.exists() and not args.forcar:
        print(f"cache: {out}")
        dados = json.loads(out.read_text())
    else:
        t0 = time.time()
        dados = transcrever(video, args.modelo, args.idioma, args.audio_track)
        out.write_text(json.dumps(dados, indent=2, ensure_ascii=False))
        n = sum(1 for w in dados["words"] if w["type"] == "word")
        print(
            f"salvo: {out} ({n} palavras, áudio de {dados['duration']:.1f}s, "
            f"{time.time() - t0:.0f}s)"
        )

    if args.flat:
        flat = [
            {"text": w["text"], "start": w["start"], "end": w["end"]}
            for w in dados["words"]
            if w["type"] == "word"
        ]
        args.flat.parent.mkdir(parents=True, exist_ok=True)
        args.flat.write_text(json.dumps(flat, indent=2, ensure_ascii=False))
        print(f"flat: {args.flat}")


if __name__ == "__main__":
    main()
