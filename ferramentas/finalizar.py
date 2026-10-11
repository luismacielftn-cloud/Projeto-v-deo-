"""Etapa final: imagem do HyperFrames + áudio do Video Use (+ legenda por último).

O HyperFrames remasteriza o áudio por conta própria (sobe ~3 dB e comprime).
Como a composição usa o vídeo cortado inteiro, do início ao fim, as duas
linhas do tempo são idênticas: aqui mantemos a imagem renderizada e
devolvemos o áudio já normalizado pelo Video Use (-14 LUFS, -1 dBTP).

Legendas, se pedidas, entram por último, por cima das animações (regra 1 do
Video Use). O .srt é gerado com o próprio build_master_srt do Video Use, a
partir do edl.json e das transcrições das fontes.

Com --mix (mix.json do modelo), o áudio final é a mixagem completa do
ferramentas/mixar.py: voz + efeitos sonoros + insertos com som + trilha com
ducking, normalizada em -14 LUFS.

Uso:
    python3 ferramentas/finalizar.py --video <render_hf.mp4> --audio <edit>/cortado.mp4 -o <edit>/final.mp4
    python3 ferramentas/finalizar.py ... --mix <edit>/hf/mix.json --crf 20 --entrega <edit>/entrega/<nome>.mp4
    python3 ferramentas/finalizar.py ... --legenda-edl <edit>/edl.json
    python3 ferramentas/finalizar.py ... --srt <arquivo.srt>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HELPERS = Path(__file__).resolve().parent.parent / ".claude/skills/video-use/helpers"

# Estilo "bold-overlay" do Video Use, trocando Helvetica (ausente no Linux) por Inter.
ESTILO_PADRAO = (
    "FontName=Inter,FontSize=18,Bold=1,"
    "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H00000000,"
    "BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=35"
)


def duracao(path: Path) -> float:
    out = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return float(out.strip())


def copia_de_entrega(origem: Path, destino: Path, limite_mib: float = 28.0) -> None:
    """Duas passadas de x264 com a taxa que cabe no limite de envio do chat (30 MB).

    Instagram e TikTok recomprimem para taxas parecidas, então a perda no celular
    é mínima. A resolução é mantida.
    """
    dur = duracao(origem)
    audio_k = 160
    video_k = max(800, int(limite_mib * 8 * 1024 / dur - audio_k - 40))
    destino.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        log = str(Path(tmp) / "passe")
        base = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(origem),
            "-c:v",
            "libx264",
        ]
        base += ["-preset", "slow", "-b:v", f"{video_k}k", "-passlogfile", log]
        subprocess.run(
            [*base, "-pass", "1", "-an", "-f", "mp4", "/dev/null"], check=True
        )
        subprocess.run(
            [
                *base,
                "-pass",
                "2",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                f"{audio_k}k",
            ]
            + ["-movflags", "+faststart", str(destino)],
            check=True,
        )
    mib = destino.stat().st_size / 1048576
    print(f"entrega: {destino} ({mib:.1f} MB, vídeo a {video_k} kb/s)")


def gerar_srt(edl_path: Path, destino: Path) -> Path:
    sys.path.insert(0, str(HELPERS))
    from render import build_master_srt  # helper do Video Use

    edl = json.loads(edl_path.read_text())
    build_master_srt(edl, edl_path.parent, destino)
    return destino


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Junta imagem do HyperFrames com o áudio do Video Use"
    )
    ap.add_argument("--video", type=Path, required=True, help="render do HyperFrames")
    ap.add_argument(
        "--audio", type=Path, required=True, help="vídeo cortado pelo Video Use"
    )
    ap.add_argument("-o", "--output", type=Path, required=True)
    leg = ap.add_mutually_exclusive_group()
    leg.add_argument(
        "--legenda-edl", type=Path, help="gera master.srt a partir deste edl.json"
    )
    leg.add_argument("--srt", type=Path, help="usa este .srt pronto")
    ap.add_argument("--estilo", default=ESTILO_PADRAO, help="force_style do libass")
    ap.add_argument(
        "--mix", type=Path, help="mix.json do modelo: mixa efeitos e trilha"
    )
    ap.add_argument(
        "--crf", type=int, help="recomprime o vídeo (ex.: 20) para um arquivo mais leve"
    )
    ap.add_argument(
        "--entrega",
        type=Path,
        help="grava também uma cópia abaixo de 30 MB (limite de envio pelo chat)",
    )
    args = ap.parse_args()

    dv, da = duracao(args.video), duracao(args.audio)
    if abs(dv - da) > 0.15:
        sys.exit(
            f"durações diferentes (vídeo {dv:.2f}s, áudio {da:.2f}s): "
            "a composição precisa cobrir o vídeo cortado inteiro"
        )

    srt = args.srt
    if args.legenda_edl:
        srt = gerar_srt(args.legenda_edl, args.legenda_edl.parent / "master.srt")

    tmp = tempfile.TemporaryDirectory()
    fonte_audio = args.audio
    if args.mix:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from mixar import mixar

        fonte_audio = Path(tmp.name) / "mix.wav"
        info = mixar(args.audio, args.mix, fonte_audio)
        print(f"mixagem: {info}")
    audio_codec = ["-c:a", "aac", "-b:a", "192k"] if args.mix else ["-c:a", "copy"]

    cmd = [
        "ffmpeg",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(args.video),
        "-i",
        str(fonte_audio),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-shortest",
    ]
    if srt:
        caminho = (
            str(srt.resolve())
            .replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
        )
        cmd += [
            "-vf",
            f"subtitles='{caminho}':force_style='{args.estilo}'",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            *audio_codec,
            "-movflags",
            "+faststart",
        ]
    elif args.crf:
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf)]
        cmd += ["-pix_fmt", "yuv420p", *audio_codec, "-movflags", "+faststart"]
    else:
        cmd += ["-c:v", "copy", *audio_codec, "-movflags", "+faststart"]
    cmd.append(str(args.output))
    subprocess.run(cmd, check=True)
    tmp.cleanup()

    print(
        f"final: {args.output} ({duracao(args.output):.2f}s"
        + (f", legenda {srt.name}" if srt else ", sem legenda")
        + ")"
    )
    if args.entrega:
        copia_de_entrega(args.output, args.entrega)


if __name__ == "__main__":
    main()
