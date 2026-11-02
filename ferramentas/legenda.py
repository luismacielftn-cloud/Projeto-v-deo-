"""Legenda em destaque queimada direto no vídeo, sem o HyperFrames.

Para quando o usuário pede só os cortes + legenda (sem animação, efeito, trilha
nem @). O visual é o da legenda "destaque" do modelo: Inter Black, 2–3 palavras,
a palavra falada acende em dourado e cresce 12 %. Os blocos saem da mesma
função do montar.py, então a quebra é igual à dos vídeos com animação.

A palavra ativa vai numa camada de cima, com as outras palavras invisíveis:
assim ela cresce sobre o próprio centro e as vizinhas não tremem.

Entrada: o vídeo cortado e a lista simples de palavras dele, com o `text` já
corrigido. Texto vazio some da legenda (útil para juntar "para" + "a" em "pra").

A lista sai de `mapear`: as palavras da transcrição da fonte levadas pelo
edl.json para a linha do tempo do cortado (trechos em quadros inteiros, como
no render.py). Transcrever o próprio cortado erra até 0,3 s logo depois dos
cortes, porque sem a pausa o Whisper se perde.

Uso:
    python3 ferramentas/legenda.py mapear videos/x/edit/edl.json videos/x/edit/leg/transcript.json
    (corrija o texto)
    python3 ferramentas/legenda.py videos/x/edit/cortado.mp4 videos/x/edit/leg/transcript.json \
        -o videos/x/edit/final.mp4 --entrega videos/x/edit/entrega/x.mp4
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from PIL import ImageFont

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "modelos/estilo-referencia"
sys.path.insert(0, str(MODELO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from finalizar import copia_de_entrega, duracao  # noqa: E402
from montar import blocos_legenda  # noqa: E402

# No libass o tamanho é a altura ascendente + descendente; no Inter isso é
# 1,21 em. Tamanho 66 px do CSS do modelo = 80 aqui.
INTER_ASS = 1.21
FONTE = MODELO / "assets/Inter-Black.otf"
CRESCE = 1.12  # a palavra falada fica 12 % maior


def separador(bloco: list[dict], fonte: ImageFont.FreeTypeFont) -> str:
    """Espaço entre palavras do bloco, largo o bastante para a palavra ativa
    crescer sem encostar na vizinha: um espaço normal + um espaço fixo (\\h)
    esticado. É o mesmo para o bloco todo, senão as palavras pulam quando a
    palavra ativa muda."""
    esp = fonte.getlength(" ")
    maior = max(fonte.getlength(w["text"]) for w in bloco)
    falta = max(esp, (CRESCE - 1) / 2 * maior + 4)  # o que o \h precisa cobrir
    return f" {{\\fscx{round(100 * falta / esp)}}}\\h{{\\fscx100}}"


def mapear(edl_path: Path, destino: Path) -> None:
    """Palavras da transcrição de cada fonte na linha do tempo do cortado.

    Cada palavra vai para o trecho com que mais se sobrepõe, com as bordas
    presas ao trecho (o Whisper às vezes estica a palavra pela pausa cortada).
    """
    edl = json.loads(edl_path.read_text())
    pasta = edl_path.parent
    fonte0 = edl["sources"][edl["ranges"][0]["source"]]
    taxa = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=r_frame_rate", "-of", "csv=p=0", str(pasta / fonte0)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    fps = Fraction(taxa)
    trechos, acc = [], 0.0
    for r in edl["ranges"]:
        trechos.append((r["source"], r["start"], r["end"], acc))
        acc += float(round((r["end"] - r["start"]) * fps) / fps)  # como o render.py

    palavras, perdidas = [], []
    for nome in dict.fromkeys(r["source"] for r in edl["ranges"]):
        fonte = json.loads((pasta / "transcripts" / f"{nome}.json").read_text())
        for w in fonte["words"]:
            if w.get("type", "word") != "word":
                continue
            sob = [
                (min(w["end"], b) - max(w["start"], a), a, b, o)
                for s, a, b, o in trechos
                if s == nome
            ]
            melhor = max(sob, default=(0, 0, 0, 0))
            if melhor[0] <= 0:
                perdidas.append(w["text"])
                continue
            _, a, b, o = melhor
            ini = max(w["start"], a) - a + o
            fim = min(w["end"], b) - a + o
            palavras.append(
                {"text": w["text"], "start": round(ini, 3), "end": round(max(fim, ini + 0.05), 3)}
            )
    palavras.sort(key=lambda w: w["start"])
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(palavras, indent=2, ensure_ascii=False))
    print(f"{len(palavras)} palavras → {destino}")
    if perdidas:
        print(f"fora dos trechos (cortadas): {' '.join(perdidas)}")


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
    fonte = ImageFont.truetype(str(FONTE), round(a.tam))
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
        sep = separador(b, fonte)
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
            fundo = sep.join(
                some + esc(x["text"]) + volta if j == k else esc(x["text"])
                for j, x in enumerate(b)
            )
            cima = sep.join(
                f"{{\\c{ativa}\\fscx{round(CRESCE * 100)}\\fscy{round(CRESCE * 100)}}}{esc(x['text'])}{{\\fscx100\\fscy100}}"
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
    if sys.argv[1:2] == ["mapear"]:
        ap = argparse.ArgumentParser(description="Palavras da fonte no tempo do cortado")
        ap.add_argument("edl", type=Path)
        ap.add_argument("saida", type=Path, help="lista simples de palavras")
        a = ap.parse_args(sys.argv[2:])
        mapear(a.edl, a.saida)
        return

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
