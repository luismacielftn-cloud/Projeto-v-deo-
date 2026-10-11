"""Monta a composição HyperFrames do modelo a partir de um roteiro.json.

A estrutura (legenda, títulos, capítulos, janelas, inserto, P&B, zoom,
transição, marca d'água, tela final) vem do vídeo de referência analisado.
A aparência vem de uma identidade em identidades/<nome>.json: cores, fontes,
jeito de animar e sons. Veja GUIA.md.

Uso:
    python3 modelos/estilo-referencia/montar.py videos/x/edit/hf/roteiro.json

Gera, na pasta do roteiro:
    index.html   composição HyperFrames
    mix.json     deixas de som (efeitos, voz abafada, insertos com som, trilha)
                 que o ferramentas/finalizar.py mixa no áudio final
e copia fontes e GSAP para assets/. Caminhos de mídia são relativos ao roteiro.
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

# família -> [(arquivo, peso, estilo)]
FONTES = {
    "Inter": [
        ("Inter-Light.otf", "300", "normal"),
        ("Inter-Regular.otf", "400", "normal"),
        ("Inter-Medium.otf", "500", "normal"),
        ("Inter-MediumItalic.otf", "500", "italic"),
        ("Inter-SemiBold.otf", "600", "normal"),
        ("Inter-Bold.otf", "700", "normal"),
        ("Inter-Black.otf", "900", "normal"),
    ],
    "Fraunces": [
        ("Fraunces.ttf", "100 900", "normal"),
        ("Fraunces-Italic.ttf", "100 900", "italic"),
    ],
    "Cormorant Garamond": [
        ("CormorantGaramond.ttf", "300 700", "normal"),
        ("CormorantGaramond-Italic.ttf", "300 700", "italic"),
    ],
}
IDENTIDADE_PADRAO = "salvia"  # identidade escolhida pelo usuário
HUMORES = ["calma", "leve", "inspira"]  # trilha automática: um humor por seção
# Eventos que já mostram texto: a legenda some enquanto estão ativos.
TIPOS_SEM_LEGENDA = {"titulo", "capitulo", "final"}
POSICOES_MARCA = [(40, 1130), (860, 300), (860, 1160), (40, 380), (40, 1650)]
TAM_MARCA = (260, 90)
POSICOES_JANELA = {
    "topo-esquerda": ("left", 50, 230),
    "topo-direita": ("right", 50, 230),
    "topo-centro": ("center", 0, 200),
    "base-esquerda": ("left", 50, 1240),
}
ICONE_IG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">'
    '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/>'
    '<circle cx="17.3" cy="6.7" r="1.1" fill="currentColor" stroke="none"/></svg>'
)


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


def caixa(texto: str, modo: str) -> str:
    return texto.upper() if modo == "alta" else texto


def fonte_ajustada(texto: str, maximo: int, largura: int, fator: float) -> int:
    """Tamanho que faz o texto caber numa linha (fator = largura média do caractere em em)."""
    return max(48, min(maximo, int(largura / (fator * max(len(texto), 1)))))


def cor_viva(idt: dict, e: dict) -> str:
    """Estilo inline para um momento de destaque com cor viva ("vivo": true, 1 ou 2)."""
    nivel = e.get("vivo")
    vivos = idt["cores"].get("vivos", [])
    if not nivel or not vivos:
        return ""
    i = 0 if nivel is True else max(0, min(int(nivel) - 1, len(vivos) - 1))
    return f"color:{vivos[i]};"


def carregar_identidade(nome: str) -> dict:
    p = Path(nome)
    if not p.suffix:
        p = AQUI / "identidades" / f"{nome}.json"
    if not p.exists():
        disponiveis = ", ".join(
            sorted(x.stem for x in (AQUI / "identidades").glob("*.json"))
        )
        sys.exit(f"identidade não encontrada: {nome} (disponíveis: {disponiveis})")
    return json.loads(p.read_text())


def fonte_css(f: dict) -> str:
    """Declaração CSS de um bloco de texto a partir de {familia, peso, italico, tracking, caixa}."""
    partes = [f'font-family: "{f["familia"]}", sans-serif', f"font-weight: {f['peso']}"]
    partes.append(f"font-style: {'italic' if f.get('italico') else 'normal'}")
    if f.get("tracking"):
        partes.append(f"letter-spacing: {f['tracking']}")
    if f.get("caixa") == "alta":
        partes.append("text-transform: uppercase")
    return "; ".join(partes)


def css_identidade(idt: dict) -> str:
    c = idt["cores"]
    leg, peq, dest, num = idt["legenda"], idt["pequeno"], idt["destaque"], idt["numero"]
    capg = idt["capitulo_grande"]
    jan = idt.get("janela", {})
    voz_it = "font-style: italic;" if idt.get("voz_italico") else ""
    sombra = "0 2px 10px rgba(0,0,0,.55)"
    return f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
#root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; font-family: "Inter", sans-serif; }}
#cam {{ position: absolute; inset: 0; transform-origin: 50% 35%; }}
#a-roll {{ position: absolute; inset: 0; width: {W}px; height: {H}px; object-fit: cover; }}
.leg {{ position: absolute; left: 60px; width: 960px; top: 1090px; text-align: center; line-height: 1.2;
  {fonte_css(leg)}; font-size: {leg["tam"]}px; color: {c["texto"]}; text-shadow: 0 2px 8px rgba(0,0,0,.65); }}
.leg.voz {{ color: {c["voz"]}; {voz_it} }}
.marca {{ position: absolute; width: 260px; color: {c["texto"]}; opacity: {idt.get("marca", {}).get("opacidade", 1)}; }}
.marca svg {{ width: 44px; height: 44px; display: block; }}
.marca span {{ display: block; margin-top: 6px; font-family: "Inter"; font-weight: 600; font-size: 21px;
  letter-spacing: .08em; text-shadow: 0 1px 4px rgba(0,0,0,.6); }}
.peq {{ {fonte_css(peq)}; font-size: {peq["tam"]}px; line-height: 1.15; color: {c["texto"]}; text-shadow: {sombra}; }}
.big {{ {fonte_css(dest)}; color: {c["destaque"]}; line-height: 1; display: block; text-shadow: 0 4px 22px rgba(0,0,0,.4); }}
.tit {{ position: absolute; left: 70px; width: 940px; top: 1020px; }}
.tit .peq.dir, .cta .dep {{ text-align: right; }}
.cap {{ position: absolute; left: 70px; top: 250px; }}
.cap .num {{ font-family: "{num["familia"]}"; font-weight: {num["peso"]}; font-size: {num["tam"]}px; line-height: .8;
  font-variant-numeric: lining-nums; font-feature-settings: "lnum" 1;
  color: {c["numero"]}; text-shadow: {sombra}; }}
.cap .grande {{ {fonte_css(capg)}; color: {c["texto"]}; line-height: .95; text-shadow: {sombra}; }}
.jan {{ position: absolute; border-radius: {jan.get("raio", 26)}px; overflow: hidden; border: {jan.get("borda", "none")};
  box-shadow: 0 18px 50px rgba(0,0,0,.45); }}
.jan img, .jan video, .ins img, .ins video {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
.ins {{ position: absolute; left: 119px; width: 842px; top: 300px; height: 1320px; overflow: hidden;
  border-radius: {jan.get("raio", 26) + 6}px; border: {jan.get("borda", "none")}; box-shadow: 0 24px 70px rgba(0,0,0,.6); }}
.clarao {{ position: absolute; inset: -200px; mix-blend-mode: screen;
  background: radial-gradient(closest-side at 30% 40%, {c["veu"]}, rgba(0,0,0,0) 75%),
              radial-gradient(closest-side at 75% 65%, {c["veu"]}, rgba(0,0,0,0) 70%); }}
.veu {{ position: absolute; top: 0; left: 0; width: {W}px; height: {H}px; mix-blend-mode: screen;
  background: linear-gradient(100deg, rgba(0,0,0,0) 25%, {c["veu"]} 50%, rgba(0,0,0,0) 75%); }}
.fim-escuro {{ position: absolute; inset: 0; background: #000; }}
.fim-ig {{ position: absolute; left: 0; width: {W}px; top: 640px; text-align: center; color: {c["texto"]}; }}
.fim-ig svg {{ width: 130px; height: 130px; display: inline-block; }}
.fim-ig span {{ display: block; margin-top: 18px; font-family: "Inter"; font-weight: 600; font-size: 36px; letter-spacing: .12em; }}
.cta {{ position: absolute; left: 70px; width: 940px; top: 1150px; }}
"""


class Composicao:
    def __init__(self, duracao: float, idt: dict):
        self.dur = duracao
        self.idt = idt
        self.mov = idt["movimento"]
        self.html: list[str] = []
        self.js: list[str] = []
        self.sons: list[dict] = []
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

    def tween(
        self, sel: str, t: float, de: str, para: str, dur: float, ease: str
    ) -> None:
        self.js.append(
            f'tl.fromTo("{sel}", {{{de}}}, {{{para}, duration: {dur:.2f}, ease: "{ease}"}}, {t:.3f});'
        )

    def setar(self, sel: str, t: float, props: str) -> None:
        self.js.append(f'tl.set("{sel}", {{{props}}}, {t:.3f});')

    # Entradas no "jeito" da identidade: com quique (pop) ou suaves (desfoque + subida).
    def entra_texto(self, sel: str, t: float, fator_dur: float = 0.7) -> None:
        d = self.mov["dur"] * fator_dur
        if self.mov.get("pop"):
            self.tween(sel, t, "opacity: 0, y: 20", "opacity: 1, y: 0", d, "power3.out")
        else:
            self.tween(
                sel, t, "opacity: 0, y: 14", "opacity: 1, y: 0", d, self.mov["ease"]
            )

    def entra_destaque(self, sel: str, t: float) -> None:
        d = self.mov["dur"]
        if self.mov.get("pop"):
            self.tween(
                sel,
                t,
                "opacity: 0, scale: 0.6",
                "opacity: 1, scale: 1",
                d,
                "back.out(1.7)",
            )
        else:
            self.tween(
                sel,
                t,
                'opacity: 0, y: 24, filter: "blur(10px)"',
                'opacity: 1, y: 0, filter: "blur(0px)"',
                d,
                self.mov["ease"],
            )

    def entra_cartao(self, sel: str, t: float) -> None:
        if self.mov.get("pop"):
            self.tween(
                sel,
                t,
                "opacity: 0, scale: 0.85",
                "opacity: 1, scale: 1",
                0.4,
                "back.out(1.6)",
            )
        else:
            self.tween(
                sel,
                t,
                "opacity: 0, y: 30, scale: 0.97",
                "opacity: 1, y: 0, scale: 1",
                self.mov["dur"],
                self.mov["ease"],
            )

    def sai(self, sel: str, t1: float, dur: float = 0.3) -> None:
        extra = "" if self.mov.get("pop") else ", y: -10"
        self.js.append(
            f'tl.to("{sel}", {{opacity: 0{extra}, duration: {dur}, ease: "power2.in"}}, {max(0.0, t1 - dur):.3f});'
        )

    def som(self, tipo: str, t: float) -> None:
        for nome in self.idt.get("sons", {}).get(tipo, []):
            self.sons.append({"t": round(max(0.0, t), 3), "som": nome})


def midia_html(
    ident: str,
    src: str,
    t0: float,
    t1: float,
    comp: Composicao,
    inicio_midia: float = 0,
) -> str:
    """Imagem: conteúdo do cartão. Vídeo: <video class="clip"> mudo com o próprio tempo."""
    if eh_video(src):
        return (
            f'<video id="{ident}-m" class="clip" src="{esc(src)}" muted playsinline '
            f'data-start="{t0:.3f}" data-duration="{t1 - t0:.3f}" data-media-start="{inicio_midia:.3f}" '
            f'data-track-index="{comp.faixa()}"></video>'
        )
    return f'<img src="{esc(src)}" alt="" />'


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


def montar(roteiro_path: Path) -> Path:
    pasta = roteiro_path.resolve().parent
    r = json.loads(roteiro_path.read_text())
    idt = carregar_identidade(r.get("identidade", IDENTIDADE_PADRAO))
    dest_cfg, capg_cfg = idt["destaque"], idt["capitulo_grande"]

    video = r["video"]
    dur = float(r.get("duracao") or duracao_midia(pasta / video))
    comp = Composicao(dur, idt)
    eventos = sorted(r.get("eventos", []), key=lambda e: e["inicio"])
    arroba = r.get("arroba", "@seuperfil").upper()

    janelas_sem_legenda = [
        (e["inicio"], e.get("fim", dur))
        for e in eventos
        if e["tipo"] in TIPOS_SEM_LEGENDA
    ]
    zonas: list[tuple[float, float, tuple[int, int, int, int]]] = []
    abafar: list[list[float]] = []
    insertos_som: list[dict] = []

    for k, e in enumerate(eventos):
        tipo, t0 = e["tipo"], float(e["inicio"])
        t1 = float(e.get("fim", dur))
        ev = f"ev{k}"

        if tipo == "zoom":
            seco = e.get("estilo", comp.mov.get("zoom")) == "seco"
            escala = float(e.get("escala", 1.3 if seco else 1.12))
            origem = f'transformOrigin: "50% {float(e.get("foco_y", 0.35)) * 100:.0f}%"'
            if seco:
                comp.setar("#cam", t0, f"scale: {escala}, {origem}")
                comp.setar("#cam", t1, "scale: 1")
            else:
                comp.js.append(
                    f'tl.to("#cam", {{scale: {escala}, {origem}, duration: 0.9, ease: "power2.inOut"}}, {t0:.3f});'
                )
                comp.js.append(
                    f'tl.to("#cam", {{scale: 1, duration: 0.7, ease: "power2.inOut"}}, {max(t0 + 0.9, t1 - 0.7):.3f});'
                )
            comp.som("zoom", t0)

        elif tipo == "pb":
            comp.setar("#cam", t0, 'filter: "grayscale(1) contrast(1.08)"')
            comp.setar("#cam", t1, 'filter: "none"')
            if e.get("voz_abafada", True):
                abafar.append([round(t0, 3), round(t1, 3)])
            comp.som("pb", t0)

        elif tipo == "titulo":
            dest = caixa(e["destaque"], dest_cfg.get("caixa", "normal"))
            tam = fonte_ajustada(
                dest, dest_cfg["tam_max"], 940, dest_cfg["largura_char"]
            )
            partes = []
            if e.get("antes"):
                partes.append(f'<div class="peq" id="{ev}-a">{esc(e["antes"])}</div>')
            partes.append(
                f'<span class="big" id="{ev}-b" style="font-size:{tam}px;{cor_viva(idt, e)}">{esc(dest)}</span>'
            )
            if e.get("depois"):
                partes.append(
                    f'<div class="peq dir" id="{ev}-d">{esc(e["depois"])}</div>'
                )
            comp.clip(ev, "tit", t0, t1, f'<div id="{ev}-in">{"".join(partes)}</div>')
            zonas.append((t0, t1, (0, 1000, W, 1440)))
            if e.get("antes"):
                comp.entra_texto(f"#{ev}-a", t0)
            comp.entra_destaque(f"#{ev}-b", t0 + 0.15)
            if e.get("depois"):
                comp.entra_texto(f"#{ev}-d", t0 + 0.4)
            comp.sai(f"#{ev}-in", t1)
            comp.som("titulo", t0 + 0.15)

        elif tipo == "capitulo":
            num = idt["numero"]["formato"].replace("{n}", str(int(e["numero"])))
            grande = caixa(e.get("grande", ""), capg_cfg.get("caixa", "normal"))
            tam = fonte_ajustada(grande, 100, 700, capg_cfg["largura_char"])
            conteudo = (
                f'<div id="{ev}-in" style="display:flex;align-items:flex-end;gap:20px">'
                f'<div class="num" id="{ev}-n" style="{cor_viva(idt, e)}">{esc(num)}</div>'
                f'<div><div class="peq" id="{ev}-p">{esc(e.get("pequeno", ""))}</div>'
                f'<div class="grande" id="{ev}-g" style="font-size:{tam}px">{esc(grande)}</div></div></div>'
            )
            comp.clip(ev, "cap", t0, t1, conteudo)
            zonas.append((t0, t1, (0, 200, W, 440)))
            comp.entra_destaque(f"#{ev}-n", t0)
            comp.entra_texto(f"#{ev}-p", t0 + 0.12)
            comp.entra_destaque(f"#{ev}-g", t0 + 0.2)
            comp.sai(f"#{ev}-in", t1)
            comp.som("capitulo", t0)

        elif tipo in ("janela", "inserto"):
            if tipo == "janela":
                lado, margem, topo = POSICOES_JANELA[e.get("posicao", "topo-direita")]
                larg = int(W * float(e.get("largura", 0.42)))
                alt = int(larg * float(e.get("proporcao", 1.15)))
                x0 = (
                    (W - larg) // 2
                    if lado == "center"
                    else (margem if lado == "left" else W - margem - larg)
                )
                estilo = (
                    f"left:{x0}px;top:{topo}px;width:{larg}px;height:{alt}px;opacity:0"
                )
                classe = "jan"
                zonas.append(
                    (t0, t1, (x0 - 20, topo - 20, x0 + larg + 20, topo + alt + 20))
                )
            else:
                comp.setar(
                    "#cam", t0, 'filter: "grayscale(1) brightness(0.45) blur(6px)"'
                )
                comp.setar("#cam", t1, 'filter: "none"')
                estilo, classe = "opacity:0", "ins"
                zonas.append((t0, t1, (119, 300, 961, 1620)))
            ini_m = float(e.get("inicio_midia", 0))
            comp.html.append(
                f'<div id="{ev}" class="{classe}" style="{estilo}">{midia_html(ev, e["midia"], t0, t1, comp, ini_m)}</div>'
            )
            comp.setar(f"#{ev}", 0, "opacity: 0")
            comp.entra_cartao(f"#{ev}", t0)
            comp.sai(f"#{ev}", t1)
            comp.som(tipo, t0)
            if e.get("som") and eh_video(e["midia"]):
                insertos_som.append(
                    {
                        "arquivo": str((pasta / e["midia"]).resolve()),
                        "t": round(t0, 3),
                        "inicio_midia": ini_m,
                        "dur": round(t1 - t0, 3),
                        "ganho_db": float(e.get("ganho_db", 0)),
                    }
                )

        elif tipo in ("transicao", "clarao"):
            clarao = idt.get("transicao") == "clarao"
            d = float(e.get("duracao", 0.7 if clarao else 0.9))
            if clarao:
                comp.clip(
                    ev,
                    "fx",
                    t0,
                    t0 + d,
                    f'<div class="clarao" id="{ev}-c"></div>',
                    "position:absolute;inset:0",
                )
                comp.tween(
                    f"#{ev}-c",
                    t0,
                    "opacity: 0, x: -160",
                    "opacity: 1, x: 0",
                    d * 0.4,
                    "power2.out",
                )
                comp.js.append(
                    f'tl.to("#{ev}-c", {{opacity: 0, x: 160, duration: {d * 0.6:.2f}, ease: "power2.in"}}, {t0 + d * 0.4:.3f});'
                )
            else:
                comp.clip(
                    ev,
                    "fx",
                    t0,
                    t0 + d,
                    f'<div class="veu" id="{ev}-c"></div>',
                    "position:absolute;inset:0",
                )
                comp.tween(f"#{ev}-c", t0, f"x: {-W}", f"x: {W}", d, "power2.inOut")
                comp.js.append(
                    f'tl.to("#{ev}-c", {{opacity: 0, duration: {d * 0.35:.2f}, ease: "power1.in"}}, {t0 + d * 0.65:.3f});'
                )
            comp.som("transicao", t0 + d * 0.4)

        elif tipo == "final":
            dest = caixa(
                e.get("cta_destaque", "link da bio"), dest_cfg.get("caixa", "normal")
            )
            tam = fonte_ajustada(
                dest, dest_cfg["tam_max"], 940, dest_cfg["largura_char"]
            )
            cta = (
                f'<div class="cta" id="{ev}-cta"><div class="peq" id="{ev}-p">{esc(e.get("cta_antes", "toque no"))}</div>'
                f'<span class="big" id="{ev}-b" style="font-size:{tam}px;{cor_viva(idt, e)}">{esc(dest)}</span>'
                f'<div class="peq dep" id="{ev}-d">{esc(e.get("cta_depois", ""))}</div></div>'
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
            comp.entra_texto(f"#{ev}-p", t0)
            comp.entra_destaque(f"#{ev}-b", t0 + 0.12)
            comp.entra_texto(f"#{ev}-d", t0 + 0.4)
            comp.tween(
                f"#{ev}-esc",
                t0 + escurece,
                "opacity: 0",
                "opacity: 0.7",
                0.6,
                "power2.out",
            )
            comp.entra_destaque(f"#{ev}-ig", t0 + escurece + 0.2)
            janelas_sem_legenda.append((t0, dur))
            comp.som("final", t0 + 0.12)

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
            t1 = min([t1] + [a for a, _ in janelas_sem_legenda if t0 < a < t1])
            voz = " voz" if any(a <= meio <= z for a, z in vozes) else ""
            comp.clip(
                f"leg{i}",
                f"leg{voz}",
                t0,
                min(t1, dur),
                esc(" ".join(w["text"] for w in b)),
            )

    # --- Marca d'água: muda de lugar e desvia dos outros elementos ----------
    marca = r.get("marca", {})
    if marca.get("ativa", True):
        passo = float(marca.get("intervalo", 6))
        fim_marca = min([e["inicio"] for e in eventos if e["tipo"] == "final"] + [dur])
        t, j = 0.0, 0
        while t < fim_marca - 0.1:
            t2 = min(t + passo, fim_marca)
            ocupado = [z for a, b, z in zonas if a < t2 and b > t]
            for n in range(len(POSICOES_MARCA)):
                left, top = POSICOES_MARCA[(j + n) % len(POSICOES_MARCA)]
                rx = (left, top, left + TAM_MARCA[0], top + TAM_MARCA[1])
                if not any(
                    rx[0] < z[2] and rx[2] > z[0] and rx[1] < z[3] and rx[3] > z[1]
                    for z in ocupado
                ):
                    comp.clip(
                        f"marca{j}",
                        "marca",
                        t,
                        t2,
                        f"{ICONE_IG}<span>{esc(arroba)}</span>",
                        f"left:{left}px;top:{top}px",
                    )
                    break
            t += passo
            j += 1

    # --- Documento ---------------------------------------------------------
    font_faces = "".join(
        f'@font-face {{ font-family: "{fam}"; font-weight: {peso}; font-style: {estilo}; src: url("assets/{arq}"); }}\n'
        for fam, arquivos in FONTES.items()
        for arq, peso, estilo in arquivos
    )
    doc = f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/gsap.min.js"></script>
    <style>
{font_faces}{css_identidade(idt)}
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

    musica = [
        {**m, "arquivo": str((pasta / m["arquivo"]).resolve())}
        for m in r.get("musica", [])
    ]
    # Trilha automática: uma seção por capítulo (troca de música na virada,
    # como na referência) e fim na tela final.
    trilha = r.get("trilha", {"auto": True})
    if trilha.get("auto", True) and not musica:
        caps = [e for e in eventos if e["tipo"] == "capitulo"]
        inicios = [(0.0, r.get("humor_inicial", HUMORES[0]))]
        for n, c in enumerate(caps):
            inicios.append(
                (float(c["inicio"]), c.get("humor", HUMORES[(n + 1) % len(HUMORES)]))
            )
        fim_fala = min([e["inicio"] for e in eventos if e["tipo"] == "final"] + [dur])
        secoes = [
            {
                "inicio": round(a, 3),
                "fim": round(inicios[i + 1][0] if i + 1 < len(inicios) else dur, 3),
                "humor": h,
            }
            for i, (a, h) in enumerate(inicios)
        ]
        trilha = {
            "auto": True,
            "secoes": secoes,
            "final": round(fim_fala, 3),
            "volume_db": float(trilha.get("volume_db", 0)),
            "semente": int(trilha.get("semente", 7)),
        }
    else:
        trilha = {"auto": False}
    mix = {
        "duracao": round(dur, 3),
        "identidade": idt["nome"],
        "sons": sorted(comp.sons, key=lambda s: s["t"]),
        "abafar": abafar,
        "insertos": insertos_som,
        "musica": musica,
        "trilha": trilha,
        "efeitos_volume_db": float(r.get("efeitos_volume_db", 0)),
    }
    (pasta / "mix.json").write_text(
        json.dumps(mix, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    destino = pasta / "assets"
    destino.mkdir(exist_ok=True)
    arquivos = [arq for lista in FONTES.values() for arq, _, _ in lista] + [
        "gsap.min.js"
    ]
    for arq in arquivos:
        if not (destino / arq).exists():
            shutil.copy(AQUI / "assets" / arq, destino / arq)
    return pasta / "index.html"


def main() -> None:
    ap = argparse.ArgumentParser(description="Monta index.html + mix.json do modelo")
    ap.add_argument("roteiro", type=Path)
    args = ap.parse_args()
    saida = montar(args.roteiro)
    print(f"composição: {saida}")
    print(f"deixas de som: {saida.parent / 'mix.json'}")


if __name__ == "__main__":
    main()
