"""Ilustração animada de sarcopenia: coxa em corte, jovem × idosa.

Padrão: fotos realistas da coxa em corte (geradas no Canva, em
modelos/estilo-referencia/assets/sarcopenia/); a da direita vira, no meio do
clipe, a coxa com o músculo tomado de gordura. O usuário pediu "mais próximo do
real". Com --desenho, usa a versão desenhada abaixo.

Desenha dois cortes transversais de coxa (pele, gordura, músculo, osso). O da
esquerda fica jovem; o da direita "envelhece" no meio do clipe: o músculo
encolhe, a gordura engrossa e aparecem manchas de gordura dentro do músculo.
É a imagem clássica da perda de músculo com a idade, para usar no cartão
(formato menor) quando o vídeo fala de sarcopenia.

Uso:
    python3 ferramentas/secao_musculo.py -o hf/assets/sarcopenia.mp4
    python3 ferramentas/secao_musculo.py -o x.mp4 --dur 2.2 --muda 0.5 --largura 840 --altura 800 \\
        --esquerda "30 anos" --direita "70 anos" --titulo "sarcopenia" --sub "perda de músculo com a idade"
Depois aplique o filtro do cartão: ferramentas/filtro_clipe.py tv x.mp4 -o x_fx.mp4
"""

from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTES = Path(__file__).resolve().parent.parent / "modelos/estilo-referencia/assets"
PELE, GORDURA, MUSCULO, FASCIA = "#E8C3A0", "#F2D58C", "#B8473E", "#86302A"
OSSO, MEDULA, TEXTO, DOURADO = "#F5F2EA", "#E2B062", "#F5F2EA", "#F2C94C"


def suave(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def manchas(n: int, semente: int = 5) -> list[tuple[float, float, float]]:
    """Posições fixas (ângulo, fração do raio, tamanho) das manchas de gordura."""
    rng = np.random.default_rng(semente)
    return [
        (rng.uniform(0, 2 * math.pi), rng.uniform(0.45, 0.92), rng.uniform(5, 11))
        for _ in range(n)
    ]


def corte(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, idade: float, pts) -> None:
    """idade 0 = jovem, 1 = sarcopenia."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PELE)
    rg = r - 6
    d.ellipse([cx - rg, cy - rg, cx + rg, cy + rg], fill=GORDURA)
    rm = rg * (0.9 - 0.32 * idade)  # o músculo encolhe
    d.ellipse([cx - rm, cy - rm, cx + rm, cy + rm], fill=MUSCULO)
    # divisões entre os grupos musculares
    for k in range(7):
        a = 2 * math.pi * k / 7 + 0.3
        d.line(
            [cx + 36 * math.cos(a), cy + 36 * math.sin(a), cx + rm * math.cos(a), cy + rm * math.sin(a)],
            fill=FASCIA,
            width=3,
        )
    # gordura entrando no músculo
    for a, f, s in pts:
        s2 = s * suave((idade - 0.15) / 0.85)
        if s2 > 0.5:
            x, y = cx + rm * f * math.cos(a), cy + rm * f * math.sin(a)
            d.ellipse([x - s2, y - s2 * 0.7, x + s2, y + s2 * 0.7], fill=GORDURA)
    # fêmur
    d.ellipse([cx - 34, cy - 30, cx + 34, cy + 38], fill=OSSO)
    d.ellipse([cx - 17, cy - 13, cx + 17, cy + 21], fill=MEDULA)


FOTOS = FONTES / "sarcopenia"


def carregar_fotos(diam: int) -> tuple[Image.Image, Image.Image, Image.Image]:
    """Coxa saudável e com sarcopenia (fotos realistas geradas no Canva, 200 px),
    ampliadas com lanczos e um leve realce, mais a máscara redonda."""
    from PIL import ImageFilter

    def abre(nome: str) -> Image.Image:
        im = Image.open(FOTOS / nome).convert("RGB").resize((diam, diam), Image.LANCZOS)
        return im.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))

    yy, xx = np.mgrid[0:diam, 0:diam]
    r = np.hypot(xx - diam / 2, yy - diam / 2) / (diam / 2)
    masc = Image.fromarray((np.clip((1.0 - r) / 0.04, 0, 1) * 255).astype(np.uint8), "L")
    return abre("coxa_saudavel.jpg"), abre("coxa_sarcopenia.jpg"), masc


def quadro_foto(w: int, h: int, t: float, a: argparse.Namespace, fotos, f) -> Image.Image:
    jovem, velho, masc = fotos
    diam = jovem.size[0]
    im = Image.new("RGB", (w, h), "#000000")
    d = ImageDraw.Draw(im)
    entra = suave(t / 0.3)
    idade = suave((t - a.muda) / 0.9)
    zoom = 1.0 + 0.04 * t / max(a.dur, 0.1)  # leve aproximação, para não ficar parado
    dz = int(diam * zoom)
    cy = int(h * 0.5)
    for cx, mistura, rot, cor in (
        (int(w * 0.265), 0.0, a.esquerda, TEXTO),
        (int(w * 0.735), idade, a.direita, DOURADO),
    ):
        foto = Image.blend(jovem, velho, mistura) if mistura > 0 else jovem
        foto = foto.resize((dz, dz), Image.LANCZOS)
        im.paste(foto, (cx - dz // 2, cy - dz // 2), masc.resize((dz, dz)))
        tw = d.textlength(rot, font=f["rot"])
        d.text((cx - tw / 2, cy + dz / 2 + 22), rot, font=f["rot"], fill=cor)
    tw = d.textlength(a.titulo, font=f["tit"])
    d.text((w / 2 - tw / 2, h * 0.07), a.titulo, font=f["tit"], fill=DOURADO)
    tw = d.textlength(a.sub, font=f["sub"])
    d.text((w / 2 - tw / 2, h * 0.07 + 70), a.sub, font=f["sub"], fill=TEXTO)
    if entra < 1:
        im = Image.blend(Image.new("RGB", (w, h), "#000000"), im, entra)
    return im


def quadro(w: int, h: int, t: float, a: argparse.Namespace, pts, f) -> Image.Image:
    im = Image.new("RGB", (w, h), "#0B100D")
    d = ImageDraw.Draw(im)
    # luz suave no meio
    yy, xx = np.mgrid[0:h, 0:w]
    luz = np.exp(-(((xx - w / 2) / (0.6 * w)) ** 2 + ((yy - h * 0.45) / (0.55 * h)) ** 2))
    base = np.array([11, 16, 13]) + (np.array([36, 53, 42]) - np.array([11, 16, 13])) * luz[..., None]
    im = Image.fromarray(base.astype(np.uint8))
    d = ImageDraw.Draw(im)
    entra = suave(t / 0.3)
    idade = suave((t - a.muda) / 0.9)
    r = min(w * 0.21, h * 0.24)
    cy = h * 0.5
    for cx, idd, rot, cor in (
        (w * 0.27, 0.0, a.esquerda, TEXTO),
        (w * 0.73, idade, a.direita, DOURADO),
    ):
        corte(d, cx, cy, r * (0.92 + 0.08 * entra), idd, pts)
        tw = d.textlength(rot, font=f["rot"])
        d.text((cx - tw / 2, cy + r + 26), rot, font=f["rot"], fill=cor)
    tw = d.textlength(a.titulo, font=f["tit"])
    d.text((w / 2 - tw / 2, h * 0.07), a.titulo, font=f["tit"], fill=DOURADO)
    tw = d.textlength(a.sub, font=f["sub"])
    d.text((w / 2 - tw / 2, h * 0.07 + 70), a.sub, font=f["sub"], fill=TEXTO)
    # legenda de cores
    lx, ly = w / 2 - 170, h * 0.9
    for i, (cor, nome) in enumerate(((MUSCULO, "músculo"), (GORDURA, "gordura"))):
        x = lx + i * 200
        d.rounded_rectangle([x, ly, x + 26, ly + 26], 5, fill=cor)
        d.text((x + 36, ly - 2), nome, font=f["leg"], fill=TEXTO)
    if entra < 1:
        im = Image.blend(Image.new("RGB", (w, h), "#0B100D"), im, entra)
    return im


def main() -> None:
    ap = argparse.ArgumentParser(description="Coxa em corte: músculo encolhendo com a idade")
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--largura", type=int, default=840)
    ap.add_argument("--altura", type=int, default=800)
    ap.add_argument("--dur", type=float, default=2.2)
    ap.add_argument("--muda", type=float, default=0.5, help="segundo em que o corte da direita começa a envelhecer")
    ap.add_argument("--esquerda", default="30 anos")
    ap.add_argument("--direita", default="70 anos")
    ap.add_argument("--titulo", default="sarcopenia")
    ap.add_argument("--sub", default="perda de músculo com a idade")
    ap.add_argument("--desenho", action="store_true", help="usa o desenho simples em vez das fotos realistas")
    a = ap.parse_args()
    w, h, fps = a.largura, a.altura, 30
    f = {
        "tit": ImageFont.truetype(str(FONTES / "Inter-Black.otf"), 58),
        "sub": ImageFont.truetype(str(FONTES / "Inter-Bold.otf"), 30),
        "rot": ImageFont.truetype(str(FONTES / "Inter-Bold.otf"), 38),
        "leg": ImageFont.truetype(str(FONTES / "Inter-Bold.otf"), 26),
    }
    pts = manchas(26)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(a.output)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fotos = None if a.desenho else carregar_fotos(int(min(w * 0.45, h * 0.5)))
    for i in range(int(round(a.dur * fps))):
        q = quadro(w, h, i / fps, a, pts, f) if a.desenho else quadro_foto(w, h, i / fps, a, fotos, f)
        p.stdin.write(q.tobytes())
    p.stdin.close()
    p.wait()
    print(f"ilustração: {a.output} ({a.dur:.2f}s, {w}x{h})")


if __name__ == "__main__":
    main()
