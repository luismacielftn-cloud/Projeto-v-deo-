"""Monta a composição HyperFrames no "estilo referência" a partir de um roteiro.json.

O estilo (ver GUIA.md) vem do vídeo de referência analisado: legenda pequena
em itálico, palavra-chave laranja gigante, capítulos numerados, janelas
flutuantes, inserto com fundo preto e branco, apartes em P&B, zoom de
ênfase, clarão laranja, marca d'água que muda de lugar e tela final com CTA.

Uso:
    python3 modelos/estilo-referencia/montar.py videos/x/edit/hf/roteiro.json

Gera index.html na pasta do roteiro e copia fontes e GSAP para assets/.
Caminhos de mídia no roteiro são relativos à pasta do roteiro.
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
W, H = 1080, 1920
LARANJA = "#E9870A"
AMARELO = "#F1F454"
FONTES = {
    "MediumItalic": ("Inter-MediumItalic.otf", 500, "italic"),
    "SemiBold": ("Inter-SemiBold.otf", 600, "normal"),
    "Bold": ("Inter-Bold.otf", 700, "normal"),
    "Black": ("Inter-Black.otf", 900, "normal"),
}
# Eventos que já mostram texto na tela: a legenda some enquanto eles estão ativos.
TIPOS_SEM_LEGENDA = {"titulo", "capitulo", "final"}
# Posições da marca d'água (left, top em px), como no vídeo de referência.
POSICOES_MARCA = [(40, 1130), (860, 300), (860, 1160), (40, 380), (40, 1650)]
TAM_MARCA = (260, 90)
POSICOES_JANELA = {
    "topo-esquerda": ("left", 50, 230),
    "topo-direita": ("right", 50, 230),
    "topo-centro": ("center", 0, 200),
    "base-esquerda": ("left", 50, 1240),
}
ICONE_IG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2">'
    '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/>'
    '<circle cx="17.3" cy="6.7" r="1.1" fill="#fff" stroke="none"/></svg>'
)

CSS_BASE = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
#root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; font-family: "InterHF", sans-serif; }}
#cam {{ position: absolute; inset: 0; transform-origin: 50% 35%; }}
#a-roll {{ position: absolute; inset: 0; width: {W}px; height: {H}px; object-fit: cover; }}
.leg {{ position: absolute; left: 60px; width: 960px; top: 1090px; text-align: center;
  font-style: italic; font-weight: 500; font-size: 44px; line-height: 1.2; color: #fff;
  text-shadow: 0 2px 8px rgba(0,0,0,.65); }}
.leg.voz {{ color: {AMARELO}; }}
.marca {{ position: absolute; width: 260px; }}
.marca svg {{ width: 46px; height: 46px; display: block; }}
.marca span {{ display: block; margin-top: 6px; color: #fff; font-weight: 600; font-size: 22px;
  letter-spacing: .02em; text-shadow: 0 1px 4px rgba(0,0,0,.6); }}
.tit {{ position: absolute; left: 70px; width: 940px; top: 1020px; }}
.tit .peq {{ color: #fff; font-weight: 700; font-size: 50px; line-height: 1.05;
  text-shadow: 0 2px 10px rgba(0,0,0,.5); }}
.tit .peq.dir {{ text-align: right; }}
.tit .big {{ color: {LARANJA}; font-weight: 900; line-height: .95; letter-spacing: -.02em;
  text-shadow: 0 4px 18px rgba(0,0,0,.35); display: block; }}
.cap {{ position: absolute; left: 70px; top: 250px; }}
.cap .num {{ color: #fff; font-weight: 900; font-size: 150px; line-height: .8; text-shadow: 0 3px 14px rgba(0,0,0,.5); }}
.cap .peq {{ color: #fff; font-weight: 600; font-size: 44px; line-height: 1; text-shadow: 0 2px 8px rgba(0,0,0,.5); }}
.cap .big {{ color: #fff; font-weight: 900; font-size: 96px; line-height: .9; letter-spacing: -.02em;
  text-shadow: 0 3px 14px rgba(0,0,0,.5); }}
.jan {{ position: absolute; border-radius: 30px; overflow: hidden; box-shadow: 0 18px 50px rgba(0,0,0,.45); }}
.jan img, .jan video {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
.ins {{ position: absolute; left: 119px; width: 842px; top: 300px; height: 1320px; border-radius: 36px;
  overflow: hidden; box-shadow: 0 24px 70px rgba(0,0,0,.6); }}
.ins img, .ins video {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
.clarao {{ position: absolute; inset: -200px; mix-blend-mode: screen;
  background: radial-gradient(closest-side at 30% 40%, rgba(255,140,30,.95), rgba(255,90,0,.55) 45%, rgba(255,60,0,0) 75%),
              radial-gradient(closest-side at 75% 65%, rgba(255,200,90,.8), rgba(255,120,20,0) 70%); }}
.fim-escuro {{ position: absolute; inset: 0; background: #000; }}
.fim-ig {{ position: absolute; left: 0; width: {W}px; top: 640px; text-align: center; }}
.fim-ig svg {{ width: 150px; height: 150px; display: inline-block; }}
.fim-ig span {{ display: block; margin-top: 18px; color: #fff; font-weight: 700; font-size: 40px; letter-spacing: .02em; }}
.cta {{ position: absolute; left: 70px; width: 940px; top: 1150px; }}
.cta .peq {{ color: #fff; font-weight: 700; font-size: 52px; line-height: 1; }}
.cta .big {{ color: {LARANJA}; font-weight: 900; font-size: 170px; line-height: .9; letter-spacing: -.03em; }}
.cta .dep {{ color: #fff; font-weight: 600; font-size: 44px; text-align: right; margin-top: 6px; }}
"""


def esc(t: str) -> str:
    return html.escape(t, quote=True)


def duracao_midia(path: Path) -> float:
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


def eh_video(nome: str) -> bool:
    return Path(nome).suffix.lower() in {".mp4", ".mov", ".webm", ".m4v", ".mkv"}


def fonte_grande(texto: str, maximo: int = 170, largura: int = 940) -> int:
    """Tamanho que faz a palavra-chave (Inter Black, caixa alta) caber na largura."""
    return max(60, min(maximo, int(largura / (0.74 * max(len(texto), 1)))))


def blocos_legenda(palavras: list[dict], max_p: int) -> list[list[dict]]:
    """Agrupa em 2–3 palavras; quebra em pontuação e pausas (lógica do chunk_words do Video Use)."""
    blocos, atual = [], []
    for i, w in enumerate(palavras):
        atual.append(w)
        prox = palavras[i + 1] if i + 1 < len(palavras) else None
        gap = prox["start"] - w["end"] if prox else 0.0
        dur = w["end"] - atual[0]["start"]
        if (
            prox is None
            or w["text"][-1] in ".,!?;:"
            or gap >= 0.3
            or len(atual) >= max_p
            or (len(atual) >= 2 and dur >= 0.35)
        ):
            blocos.append(atual)
            atual = []
    return blocos


class Composicao:
    def __init__(self, duracao: float):
        self.dur = duracao
        self.html: list[str] = []
        self.js: list[str] = []
        self.trilha = 1

    def faixa(self) -> int:
        self.trilha += 1
        return self.trilha

    def clip(
        self,
        ident: str,
        classe: str,
        t0: float,
        t1: float,
        conteudo: str,
        estilo: str = "",
    ) -> None:
        t0, t1 = max(0.0, t0), min(self.dur, t1)
        if t1 - t0 < 0.05:
            return
        st = f' style="{estilo}"' if estilo else ""
        self.html.append(
            f'<div id="{ident}" class="{classe} clip"{st} data-start="{t0:.3f}" '
            f'data-duration="{t1 - t0:.3f}" data-track-index="{self.faixa()}">{conteudo}</div>'
        )

    def entrada(
        self,
        sel: str,
        t: float,
        de: str,
        para: str,
        dur: float = 0.45,
        ease: str = "power3.out",
    ) -> None:
        self.js.append(
            f'tl.fromTo("{sel}", {{{de}}}, {{{para}, duration: {dur}, ease: "{ease}"}}, {t:.3f});'
        )

    def saida(
        self, sel: str, t1: float, para: str = "opacity: 0", dur: float = 0.25
    ) -> None:
        self.js.append(
            f'tl.to("{sel}", {{{para}, duration: {dur}, ease: "power2.in"}}, {max(0.0, t1 - dur):.3f});'
        )

    def setar(self, sel: str, t: float, props: str) -> None:
        self.js.append(f'tl.set("{sel}", {{{props}}}, {t:.3f});')


def midia_html(
    ident: str,
    src: str,
    t0: float,
    t1: float,
    comp: Composicao,
    inicio_midia: float = 0,
) -> str:
    """Imagem: vira o conteúdo do wrapper. Vídeo: <video class="clip"> com o próprio tempo (mudo)."""
    if eh_video(src):
        return (
            f'<video id="{ident}-m" class="clip" src="{esc(src)}" muted playsinline '
            f'data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-media-start="{inicio_midia:.3f}" '
            f'data-track-index="{comp.faixa()}"></video>'
        )
    return f'<img src="{esc(src)}" alt="" />'


def montar(roteiro_path: Path) -> Path:
    pasta = roteiro_path.resolve().parent
    r = json.loads(roteiro_path.read_text())

    video = r["video"]
    dur = float(r.get("duracao") or duracao_midia(pasta / video))
    comp = Composicao(dur)
    eventos = sorted(r.get("eventos", []), key=lambda e: e["inicio"])
    arroba = r.get("arroba", "@seuperfil").upper()

    # --- Eventos -----------------------------------------------------------
    janelas_sem_legenda = [
        (e["inicio"], e.get("fim", dur))
        for e in eventos
        if e["tipo"] in TIPOS_SEM_LEGENDA
    ]
    # Áreas ocupadas (tempo + retângulo) para a marca d'água não ficar por baixo/por cima.
    zonas: list[tuple[float, float, tuple[int, int, int, int]]] = []
    for k, e in enumerate(eventos):
        tipo, t0 = e["tipo"], float(e["inicio"])
        t1 = float(e.get("fim", dur))
        ev = f"ev{k}"

        if tipo == "zoom":
            foco = float(e.get("foco_y", 0.35)) * 100
            comp.setar(
                "#cam",
                t0,
                f'scale: {float(e.get("escala", 1.3))}, transformOrigin: "50% {foco:.0f}%"',
            )
            comp.setar("#cam", t1, "scale: 1")

        elif tipo == "pb":
            comp.setar("#cam", t0, 'filter: "grayscale(1) contrast(1.08)"')
            comp.setar("#cam", t1, 'filter: "none"')

        elif tipo == "titulo":
            dest = e["destaque"].upper()
            partes = []
            if e.get("antes"):
                partes.append(f'<div class="peq" id="{ev}-a">{esc(e["antes"])}</div>')
            partes.append(
                f'<span class="big" id="{ev}-b" style="font-size:{fonte_grande(dest)}px">{esc(dest)}</span>'
            )
            if e.get("depois"):
                partes.append(
                    f'<div class="peq dir" id="{ev}-d">{esc(e["depois"])}</div>'
                )
            comp.clip(ev, "tit", t0, t1, f'<div id="{ev}-in">{"".join(partes)}</div>')
            zonas.append((t0, t1, (0, 1000, W, 1440)))
            if e.get("antes"):
                comp.entrada(
                    f"#{ev}-a", t0, "opacity: 0, y: 20", "opacity: 1, y: 0", 0.3
                )
            comp.entrada(
                f"#{ev}-b",
                t0 + 0.15,
                "opacity: 0, scale: 0.6",
                "opacity: 1, scale: 1",
                0.45,
                "back.out(1.7)",
            )
            if e.get("depois"):
                comp.entrada(
                    f"#{ev}-d", t0 + 0.4, "opacity: 0, y: 16", "opacity: 1, y: 0", 0.3
                )
            comp.saida(f"#{ev}-in", t1)

        elif tipo == "capitulo":
            conteudo = (
                f'<div id="{ev}-in" style="display:flex;align-items:flex-end;gap:18px">'
                f'<div class="num" id="{ev}-n">{int(e["numero"])}.</div>'
                f'<div><div class="peq">{esc(e.get("pequeno", ""))}</div>'
                f'<div class="big" id="{ev}-g" style="font-size:{fonte_grande(e.get("grande", "").upper(), 96, 720)}px">'
                f"{esc(e.get('grande', '').upper())}</div></div></div>"
            )
            comp.clip(ev, "cap", t0, t1, conteudo)
            zonas.append((t0, t1, (0, 200, W, 440)))
            comp.entrada(f"#{ev}-n", t0, "opacity: 0, x: -40", "opacity: 1, x: 0", 0.4)
            comp.entrada(
                f"#{ev}-g", t0 + 0.15, "opacity: 0, y: 24", "opacity: 1, y: 0", 0.4
            )
            comp.saida(f"#{ev}-in", t1)

        elif tipo == "janela":
            lado, margem, topo = POSICOES_JANELA[e.get("posicao", "topo-direita")]
            larg = int(W * float(e.get("largura", 0.42)))
            alt = int(larg * float(e.get("proporcao", 1.15)))
            if lado == "center":
                pos = f"left:{(W - larg) // 2}px"
            else:
                pos = f"{lado}:{margem}px"
            estilo = f"{pos};top:{topo}px;width:{larg}px;height:{alt}px;opacity:0"
            x0 = (
                (W - larg) // 2
                if lado == "center"
                else (margem if lado == "left" else W - margem - larg)
            )
            zonas.append(
                (t0, t1, (x0 - 20, topo - 20, x0 + larg + 20, topo + alt + 20))
            )
            comp.html.append(
                f'<div id="{ev}" class="jan" style="{estilo}">'
                f"{midia_html(ev, e['midia'], t0, t1, comp, e.get('inicio_midia', 0))}</div>"
            )
            comp.setar(f"#{ev}", 0, "opacity: 0")
            comp.entrada(
                f"#{ev}",
                t0,
                "opacity: 0, scale: 0.85",
                "opacity: 1, scale: 1",
                0.4,
                "back.out(1.6)",
            )
            comp.saida(f"#{ev}", t1)

        elif tipo == "inserto":
            comp.setar("#cam", t0, 'filter: "grayscale(1) brightness(0.45) blur(6px)"')
            zonas.append((t0, t1, (119, 300, 961, 1620)))
            comp.setar("#cam", t1, 'filter: "none"')
            comp.html.append(
                f'<div id="{ev}" class="ins" style="opacity:0">'
                f"{midia_html(ev, e['midia'], t0, t1, comp, e.get('inicio_midia', 0))}</div>"
            )
            comp.setar(f"#{ev}", 0, "opacity: 0")
            comp.entrada(
                f"#{ev}",
                t0,
                "opacity: 0, scale: 0.9",
                "opacity: 1, scale: 1",
                0.4,
                "back.out(1.5)",
            )
            comp.saida(f"#{ev}", t1)

        elif tipo == "clarao":
            d = float(e.get("duracao", 0.7))
            comp.clip(
                ev,
                "clarao-host",
                t0,
                t0 + d,
                f'<div class="clarao" id="{ev}-c"></div>',
                "position:absolute;inset:0",
            )
            comp.js.append(
                f'tl.fromTo("#{ev}-c", {{opacity: 0, x: -160}}, {{opacity: 1, x: 0, duration: {d * 0.4:.2f}, '
                f'ease: "power2.out"}}, {t0:.3f});'
            )
            comp.js.append(
                f'tl.to("#{ev}-c", {{opacity: 0, x: 160, duration: {d * 0.6:.2f}, ease: "power2.in"}}, '
                f"{t0 + d * 0.4:.3f});"
            )

        elif tipo == "final":
            dest = e.get("cta_destaque", "NO LINK").upper()
            cta = (
                f'<div class="cta" id="{ev}-cta"><div class="peq" id="{ev}-p">{esc(e.get("cta_antes", "tocar"))}</div>'
                f'<div class="big" id="{ev}-b" style="font-size:{fonte_grande(dest)}px">{esc(dest)}</div>'
                f'<div class="dep" id="{ev}-d">{esc(e.get("cta_depois", "da minha bio"))}</div></div>'
            )
            escurece = float(e.get("escurecer_em", 1.2))
            ig = f'<div class="fim-ig" id="{ev}-ig">{ICONE_IG}<span>{esc(arroba)}</span></div>'
            comp.clip(
                ev,
                "fim",
                t0,
                dur,
                f'<div class="fim-escuro" id="{ev}-esc"></div>{cta}{ig}',
                "position:absolute;inset:0",
            )
            comp.setar(f"#{ev}-esc", t0, "opacity: 0")
            comp.setar(f"#{ev}-ig", t0, "opacity: 0")
            comp.entrada(f"#{ev}-p", t0, "opacity: 0, y: 16", "opacity: 1, y: 0", 0.3)
            comp.entrada(
                f"#{ev}-b",
                t0 + 0.12,
                "opacity: 0, scale: 0.6",
                "opacity: 1, scale: 1",
                0.45,
                "back.out(1.7)",
            )
            comp.entrada(f"#{ev}-d", t0 + 0.4, "opacity: 0", "opacity: 1", 0.3)
            comp.entrada(
                f"#{ev}-esc",
                t0 + escurece,
                "opacity: 0",
                "opacity: 0.68",
                0.5,
                "power2.out",
            )
            comp.entrada(
                f"#{ev}-ig",
                t0 + escurece + 0.2,
                "opacity: 0, scale: 0.7",
                "opacity: 1, scale: 1",
                0.45,
                "back.out(1.7)",
            )
            janelas_sem_legenda.append((t0, dur))

        else:
            sys.exit(f"tipo de evento desconhecido: {tipo}")

    # --- Legenda -----------------------------------------------------------
    leg = r.get("legenda", {})
    if leg.get("ativa", True) and r.get("transcricao"):
        palavras = [
            w
            for w in json.loads((pasta / r["transcricao"]).read_text())
            if w["text"].strip()
        ]
        vozes = [(v["inicio"], v["fim"]) for v in r.get("vozes", [])]
        blocos = blocos_legenda(palavras, int(leg.get("max_palavras", 3)))
        for i, b in enumerate(blocos):
            t0 = b[0]["start"]
            prox = blocos[i + 1][0]["start"] if i + 1 < len(blocos) else dur
            t1 = prox if prox - b[-1]["end"] < 0.5 else b[-1]["end"] + 0.15
            meio = (b[0]["start"] + b[-1]["end"]) / 2  # meio das palavras faladas
            if any(a <= meio <= z for a, z in janelas_sem_legenda):
                continue
            # não invade um título/capítulo/tela final que começa logo depois
            t1 = min([t1] + [a for a, _ in janelas_sem_legenda if t0 < a < t1])
            voz = " voz" if any(a <= meio <= z for a, z in vozes) else ""
            texto = " ".join(w["text"] for w in b)
            comp.clip(f"leg{i}", f"leg{voz}", t0, min(t1, dur), esc(texto))

    # --- Marca d'água ------------------------------------------------------
    marca = r.get("marca", {})
    if marca.get("ativa", True):
        passo = float(marca.get("intervalo", 6))
        fim_marca = min([e["inicio"] for e in eventos if e["tipo"] == "final"] + [dur])
        t, j = 0.0, 0
        while t < fim_marca - 0.1:
            t2 = min(t + passo, fim_marca)
            ocupado = [z for a, b, z in zonas if a < t2 and b > t]
            livre = None
            for n in range(len(POSICOES_MARCA)):
                left, top = POSICOES_MARCA[(j + n) % len(POSICOES_MARCA)]
                rx = (left, top, left + TAM_MARCA[0], top + TAM_MARCA[1])
                if not any(
                    rx[0] < z[2] and rx[2] > z[0] and rx[1] < z[3] and rx[3] > z[1]
                    for z in ocupado
                ):
                    livre = (left, top)
                    break
            if livre is None:  # nenhum lugar livre: pula este trecho
                t += passo
                j += 1
                continue
            left, top = livre
            comp.clip(
                f"marca{j}",
                "marca",
                t,
                t2,
                f"{ICONE_IG}<span>{esc(arroba)}</span>",
                f"left:{left}px;top:{top}px",
            )
            t += passo
            j += 1

    # --- Documento ---------------------------------------------------------
    font_faces = "".join(
        f'@font-face {{ font-family: "InterHF"; font-weight: {peso}; font-style: {estilo}; '
        f'src: url("assets/{arq}"); }}\n'
        for arq, peso, estilo in FONTES.values()
    )
    doc = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/gsap.min.js"></script>
    <style>
{font_faces}{CSS_BASE}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="{W}" data-height="{H}">
      <div id="cam">
        <video id="a-roll" class="clip" src="{esc(video)}" muted playsinline data-start="0" data-duration="{dur:.3f}" data-track-index="0"></video>
      </div>
      {chr(10).join("      " + h for h in comp.html).strip()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join("      " + j for j in comp.js).strip()}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    (pasta / "index.html").write_text(doc, encoding="utf-8")
    destino = pasta / "assets"
    destino.mkdir(exist_ok=True)
    for arq in [f[0] for f in FONTES.values()] + ["gsap.min.js"]:
        if not (destino / arq).exists():
            shutil.copy(AQUI / "assets" / arq, destino / arq)
    return pasta / "index.html"


def main() -> None:
    ap = argparse.ArgumentParser(description="Monta index.html no estilo referência")
    ap.add_argument("roteiro", type=Path)
    args = ap.parse_args()
    saida = montar(args.roteiro)
    print(f"composição: {saida}")


if __name__ == "__main__":
    main()
