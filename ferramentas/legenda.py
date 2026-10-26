"""Legenda em destaque queimada direto no vídeo, sem o HyperFrames.

Para quando o usuário pede só os cortes + legenda (sem animação, efeito, trilha
nem @). O visual é o da legenda "destaque" do modelo: Inter Black, 2–3 palavras,
a palavra falada acende em dourado e cresce 12 %. Os blocos saem da mesma
função do montar.py, então a quebra é igual à dos vídeos com animação.

A palavra ativa vai numa camada de cima, com as outras palavras invisíveis:
assim ela cresce sobre o próprio centro e as vizinhas não tremem.

Entrada: o vídeo cortado e a transcrição dele em lista simples (a do
`transcrever.py --flat`), com o `text` já corrigido. Texto vazio some da
legenda (útil para juntar "para" + "a" em "pra").

Uso:
    python3 ferramentas/legenda.py videos/x/edit/cortado.mp4 videos/x/edit/leg/transcript.json \
        -o videos/x/edit/final.mp4 --entrega videos/x/edit/entrega/x.mp4
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "modelos/estilo-referencia"
sys.path.insert(0, str(MODELO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from finalizar import copia_de_entrega, duracao  # noqa: E402
from montar import blocos_legenda  # noqa: E402

# No libass o tamanho é a altura ascendente + descendente; no Inter isso é
# 1,21 em. Tamanho 66 px do CSS do modelo = 80 aqui.
INTER_ASS = 1.21
# Espaço largo entre palavras (o modelo usa margem de .17em em cada lado):
# sem ele a palavra ativa, 12 % maior, encosta na vizinha.
ESPACO = " \\h"


def cor_ass(hexa: str, alfa: int = 0) -> str:
    r, g, b = hexa.lstrip("#")[0:2], hexa.lstrip("#")[2:4], hexa.lstrip("#")[4:6]
    return f"&H{alfa:02X}{b}{g}{r}".upper()


def tempo_ass(t: float) -> str:
    cs = max(0, round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def esc(texto: str) -> str:
    return texto.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def gerar_ass(palavras: list[dict], dur: float, a: argparse.Namespace) -> str:
    tam = round(a.tam * INTER_ASS)
    base, ativa = cor_ass(a.cor_base), cor_ass(a.cor)
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Inter Black,{tam},{base},{base},&H00000000,&H50000000,0,0,0,0,100,100,0,0,1,3.5,3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    linhas = []
    pos = f"\\pos(540,{a.y})"
    blocos = blocos_legenda(palavras, a.max_palavras)
    for i, b in enumerate(blocos):
        t0 = b[0]["start"]
        prox = blocos[i + 1][0]["start"] if i + 1 < len(blocos) else dur
        t1 = min(prox if prox - b[-1]["end"] < 0.5 else b[-1]["end"] + 0.15, dur)
        for k, w in enumerate(b):
            ini = t0 if k == 0 else w["start"]
            fim = b[k + 1]["start"] if k + 1 < len(b) else t1
            if fim <= ini:
                continue
            # entrada do bloco: aparece subindo 12 px em 0,14 s (menos no 0 s: o
            # quadro 0 é a capa que o celular mostra, a legenda já entra inteira)
            entra = (
                f"\\fad(80,0)\\move(540,{a.y + 12},540,{a.y},0,140)"
                if k == 0 and ini > 0.05
                else pos
            )
            some = "{\\alpha&HFF&}"
            volta = "{\\alpha&H00&}"
            fundo = ESPACO.join(
                some + esc(x["text"]) + volta if j == k else esc(x["text"])
                for j, x in enumerate(b)
            )
            cima = ESPACO.join(
                f"{{\\c{ativa}\\fscx112\\fscy112}}{esc(x['text'])}{{\\fscx100\\fscy100}}"
                if j == k
                else some + esc(x["text"]) + volta
                for j, x in enumerate(b)
            )
            for camada, texto in ((0, fundo), (1, cima)):
                linhas.append(
                    f"Dialogue: {camada},{tempo_ass(ini)},{tempo_ass(fim)},Leg,,0,0,0,,"
                    f"{{\\blur1.5{entra}}}{texto}"
                )
    return cab + "\n".join(linhas) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Queima a legenda em destaque no vídeo")
    ap.add_argument("video", type=Path, help="vídeo cortado (Video Use)")
    ap.add_argument("transcricao", type=Path, help="lista simples de palavras do vídeo")
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--y", type=int, default=1460, help="centro vertical da legenda")
    ap.add_argument("--tam", type=float, default=66, help="tamanho em px (como no CSS)")
    ap.add_argument("--cor", default="#F2C94C", help="cor da palavra falada")
    ap.add_argument("--cor-base", default="#F5F2EA")
    ap.add_argument("--max-palavras", type=int, default=3)
    ap.add_argument("--entrega", type=Path, help="cópia abaixo de 30 MB para o chat")
    a = ap.parse_args()

    palavras = [w for w in json.loads(a.transcricao.read_text()) if w["text"].strip()]
    dur = duracao(a.video)
    ass = a.output.with_suffix(".ass")
    ass.write_text(gerar_ass(palavras, dur, a), encoding="utf-8")

    caminho = str(ass.resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    fontes = str(MODELO / "assets").replace(":", "\\:")
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(a.video),
            "-vf", f"subtitles='{caminho}':fontsdir='{fontes}'",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            # O AAC do cortado.mp4 passa um pouco de -1 dBTP (medido: -0,8). Limitador
            # com sobreamostragem 4x: pico real -1,2 dBTP, sem mexer nos -14 LUFS.
            "-af", "aresample=192000,alimiter=limit=0.84:level=false:attack=1:release=50,aresample=48000",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(a.output),
        ],
        check=True,
    )
    print(f"final: {a.output} ({duracao(a.output):.2f}s, legenda {ass.name})")
    if a.entrega:
        copia_de_entrega(a.output, a.entrega)


if __name__ == "__main__":
    main()
