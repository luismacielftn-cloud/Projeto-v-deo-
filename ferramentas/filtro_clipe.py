"""Filtros de "vídeo de prova" no estilo da 3ª referência do usuário (@elias.maman).

Dois visuais, aplicados ao clipe já recortado no tamanho final:

  tv     para o formato menor (cartão): parece uma TV de tubo. A imagem fica
         levemente estufada, ganha uma grade fina de pontos de tela, cantos
         escuros, um pouco de desfoque e grão.
  lente  para a tela dividida e a tela cheia: o centro fica nítido e as bordas
         ganham um borrão de zoom (radial), com cantos escuros e grão.
  desfoque  "lembrança" para a tela dividida: o clipe todo fica muito suave,
         escuro e avermelhado (print do usuário com o Beckham no topo).

Uso:
    python3 ferramentas/filtro_clipe.py tv    entrada.mp4 -o saida.mp4
    python3 ferramentas/filtro_clipe.py lente entrada.mp4 -o saida.mp4 [--forca 1.0]
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


def duracao(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return float(out.strip())


def tamanho(path: Path) -> tuple[int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


def grade_pontos(w: int, h: int, passo: int = 5, fundo: float = 0.66) -> Image.Image:
    """Máscara multiplicativa: pontos claros (1,0) num fundo mais escuro."""
    y, x = np.mgrid[0:h, 0:w]
    fx = 0.5 + 0.5 * np.cos(2 * np.pi * x / passo)
    fy = 0.5 + 0.5 * np.cos(2 * np.pi * y / passo)
    m = fundo + (1 - fundo) * (fx * fy) ** 0.6
    return Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), "L").convert("RGB")


def mascara_bordas(w: int, h: int, nitido: float = 0.30, suave: float = 0.38) -> Image.Image:
    """0 no centro (fica nítido) → 255 nas bordas (recebe o borrão)."""
    y, x = np.mgrid[0:h, 0:w]
    r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    m = np.clip((r - nitido) / suave, 0, 1) ** 1.2
    return Image.fromarray((m * 255).astype(np.uint8), "L")


def aplicar(
    estilo: str, entrada: Path, saida: Path, forca: float = 1.0, brilho: float = 1.0
) -> None:
    w, h = tamanho(entrada)
    dur = f"{duracao(entrada):.3f}"
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(entrada)]
        if estilo == "tv":
            grade = Path(tmp) / "grade.png"
            grade_pontos(w, h).save(grade)
            cmd += ["-loop", "1", "-t", dur, "-i", str(grade)]
            k1 = 0.16 * forca
            filtro = (
                f"[0:v]format=rgb24,lenscorrection=k1={k1:.3f}:k2={0.05 * forca:.3f}:i=bilinear,"
                "gblur=sigma=0.7,eq=contrast=1.08:saturation=0.88,format=gbrp,"
                # a grade escurece ~25%: compensa antes de multiplicar
                f"lutrgb=r=val*{1.3 * brilho:.2f}:g=val*{1.3 * brilho:.2f}:b=val*{1.3 * brilho:.2f}[v];"
                "[1:v]format=gbrp[g];"
                # multiplica em RGB (em YUV a grade puxaria a cor para o verde)
                "[v][g]blend=all_mode=multiply:shortest=1,"
                "vignette=angle=PI/3.2,noise=alls=9:allf=t+u,format=yuv420p[o]"
            )
        elif estilo == "lente":
            masc = Path(tmp) / "mascara.png"
            mascara_bordas(w, h).save(masc)
            cmd += ["-loop", "1", "-t", dur, "-i", str(masc)]
            # borrão de zoom: média de 4 cópias ampliadas a partir do centro
            esc = [1.0 + 0.04 * forca * i for i in range(4)]
            partes = [
                f"[0:v]format=gbrp,lutrgb=r=val*{brilho:.2f}:g=val*{brilho:.2f}:b=val*{brilho:.2f},"
                "split=5[o0][z0][z1][z2][z3]"
            ]
            for i, s in enumerate(esc):
                partes.append(
                    f"[z{i}]scale=iw*{s:.4f}:ih*{s:.4f},crop={w}:{h}[s{i}]"
                )
            partes += [
                "[s0][s1]blend=all_mode=average[a01]",
                "[s2][s3]blend=all_mode=average[a23]",
                "[a01][a23]blend=all_mode=average,gblur=sigma=2.5[zb]",
                "[1:v]format=gray,scale=" + f"{w}:{h}" + ",format=gbrp[m]",
                "[o0][zb][m]maskedmerge[mm]",
                "[mm]eq=contrast=1.06:saturation=0.92,"
                "vignette=angle=PI/4.2,noise=alls=7:allf=t+u,format=yuv420p[o]",
            ]
            filtro = ";".join(partes)
        elif estilo == "desfoque":
            # "lembrança": muito suave (imagem pequena ampliada + desfoque), escura e
            # puxada para o vermelho, como o clipe de cima do print do usuário
            pequeno = max(96, int(w / (6 * forca)) // 2 * 2)
            filtro = (
                f"[0:v]lutrgb=r=val*{brilho:.2f}:g=val*{brilho:.2f}:b=val*{brilho:.2f},"
                f"scale={pequeno}:-2:flags=area,gblur=sigma=1.4,scale={w}:{h}:flags=bicubic,"
                "eq=contrast=0.96:saturation=1.15:gamma=0.66:brightness=-0.05,"
                "colorbalance=rs=0.16:gs=-0.04:bs=-0.12:rm=0.13:gm=-0.04:bm=-0.10:rh=0.05:bh=-0.05,"
                "vignette=angle=PI/3.6,noise=alls=6:allf=t+u,format=yuv420p[o]"
            )
        else:
            raise SystemExit(f"estilo desconhecido: {estilo} (use tv, lente ou desfoque)")
        cmd += [
            "-filter_complex", filtro, "-map", "[o]", "-an",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", "30",
            "-g", "30", "-pix_fmt", "yuv420p", "-t", dur, str(saida),
        ]
        subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Filtro de TV de tubo ou lente nos clipes de prova")
    ap.add_argument("estilo", choices=["tv", "lente", "desfoque"])
    ap.add_argument("entrada", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--forca", type=float, default=1.0, help="intensidade (1,0 = como a referência)")
    ap.add_argument("--brilho", type=float, default=1.0, help="clareia (>1) clipes escuros")
    args = ap.parse_args()
    aplicar(args.estilo, args.entrada, args.output, args.forca, args.brilho)
    print(f"{args.estilo}: {args.output}")


if __name__ == "__main__":
    main()
