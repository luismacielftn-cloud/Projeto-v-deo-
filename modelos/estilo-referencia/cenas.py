"""Cenas em tela cheia que cobrem a câmera ("cutaways" animados).

Cada cena ocupa o quadro inteiro por alguns segundos enquanto a voz continua,
ilustrando o que está sendo dito. O conteúdo fica entre y 200 e 1250 para a
legenda (y ≈ 1400) continuar legível por cima. Todas usam as cores da identidade.

Modelos (campo "modelo" do evento "cena"):
    numero        número gigante + unidade + frase          {grande, unidade, texto}
    barras        barras que sobem/descem na palavra        {titulo, itens:[{rotulo, valor 0-100, seta, t}]}
    notificacoes  celular recebendo notificações            {titulo, itens:[{titulo, sub, t}]}
    pico          gráfico de linha com pico e queda         {titulo, t_pico, rotulo_pico, t_queda, rotulo_queda}
    sol           nascer do sol + lista de hábitos          {titulo, itens:[{texto, t}]}
    frase         frase grande, palavra por palavra         {palavras:[{texto, t, destaque?}]}

construir() devolve (html, js, sons): o HTML do conteúdo, as linhas de GSAP e
as deixas de som [(t, tipo)] — "cena_item" para cada elemento que entra.
"""

from __future__ import annotations

import html

W, H = 1080, 1920


def esc(t: str) -> str:
    return html.escape(str(t), quote=True)


def css(idt: dict) -> str:
    c = idt["cores"]
    fundo = c.get("cena_fundo", ["#24352A", "#0B100D"])
    dest = idt["destaque"]
    return f"""
.cena-in {{ position: absolute; inset: 0; overflow: hidden; }}
.cena-bg {{ position: absolute; inset: 0; background: radial-gradient(130% 85% at 50% 32%, {fundo[0]} 0%, {fundo[1]} 72%); }}
.cena-luz {{ position: absolute; width: 1000px; height: 1000px; left: 40px; top: 160px; border-radius: 50%;
  background: radial-gradient(closest-side, {c["veu"]}, rgba(0,0,0,0)); opacity: .55; }}
.cena-kick {{ position: absolute; left: 80px; width: 920px; top: 300px; text-align: center; font-family: "Inter";
  font-weight: 400; font-size: 34px; letter-spacing: .24em; text-transform: uppercase; color: {c["texto"]}; opacity: .85; }}
.cena-num {{ position: absolute; left: 0; width: {W}px; top: 470px; text-align: center; font-family: "{dest["familia"]}";
  font-style: {"italic" if dest.get("italico") else "normal"}; font-weight: 400; font-size: 300px; line-height: 1; color: {c["destaque"]}; }}
.cena-uni {{ position: absolute; left: 0; width: {W}px; top: 820px; text-align: center; font-family: "Inter";
  font-weight: 500; font-size: 72px; color: {c["texto"]}; }}
.cena-txt {{ position: absolute; left: 90px; width: 900px; top: 950px; text-align: center; font-family: "Inter";
  font-weight: 300; font-size: 44px; color: {c["texto"]}; opacity: .85; }}
.cena-col {{ position: absolute; bottom: 720px; width: 200px; }}
.cena-barra {{ position: absolute; bottom: 0; left: 0; width: 200px; height: 560px; border-radius: 14px 14px 4px 4px;
  background: {c["destaque"]}; transform-origin: 50% 100%; }}
.cena-trilho {{ position: absolute; bottom: 0; left: 0; width: 200px; height: 560px; border-radius: 14px 14px 4px 4px;
  background: rgba(245,242,234,.07); }}
.cena-seta {{ position: absolute; left: 0; width: 200px; text-align: center; font-family: "{dest["familia"]}"; font-size: 96px;
  line-height: 1; color: {c["texto"]}; }}
.cena-rot {{ position: absolute; left: -40px; width: 280px; top: 1215px; text-align: center; font-family: "Inter"; font-weight: 500;
  font-size: 44px; color: {c["texto"]}; }}
.cena-cel {{ position: absolute; left: 270px; top: 380px; width: 540px; height: 860px; border-radius: 64px;
  border: 3px solid rgba(245,242,234,.35); background: rgba(8,12,10,.65); overflow: hidden; }}
.cena-notch {{ position: absolute; left: 200px; top: 22px; width: 140px; height: 30px; border-radius: 16px; background: rgba(245,242,234,.18); }}
.cena-noti {{ position: absolute; left: 34px; width: 472px; height: 128px; border-radius: 30px; background: rgba(245,242,234,.12);
  border: 1px solid rgba(245,242,234,.18); }}
.cena-noti i {{ position: absolute; left: 24px; top: 34px; width: 60px; height: 60px; border-radius: 16px; background: {c["destaque"]}; }}
.cena-noti b {{ position: absolute; left: 104px; top: 26px; font-family: "Inter"; font-weight: 600; font-size: 34px; color: {c["texto"]}; }}
.cena-noti span {{ position: absolute; left: 104px; top: 72px; font-family: "Inter"; font-weight: 400; font-size: 26px; color: {c["texto"]}; opacity: .7; }}
.cena-badge {{ position: absolute; left: 760px; top: 340px; width: 96px; height: 96px; border-radius: 50%;
  background: {c.get("vivos", [c["destaque"]])[0]}; }}
.cena-badge span {{ position: absolute; inset: 0; text-align: center; line-height: 96px; font-family: "Inter"; font-weight: 700;
  font-size: 46px; color: #fff; }}
.cena-svg {{ position: absolute; left: 90px; top: 420px; width: 900px; height: 700px; overflow: visible; }}
.cena-rotulo {{ position: absolute; font-family: "{dest["familia"]}"; font-style: {"italic" if dest.get("italico") else "normal"};
  font-size: 76px; line-height: 1; }}
.cena-sol {{ position: absolute; left: 340px; top: 0; width: 400px; height: 400px; border-radius: 50%;
  background: radial-gradient(closest-side, #FFE7A8, #F7B955 60%, rgba(247,185,85,0) 100%); }}
.cena-ceu {{ position: absolute; inset: 0; background: linear-gradient(180deg, #F2B46B 0%, #E78A5B 35%, #3A3A4F 75%, #141C24 100%); }}
.cena-item {{ position: absolute; left: 150px; width: 820px; font-family: "Inter"; font-weight: 500; font-size: 62px; color: {c["texto"]};
  text-shadow: 0 3px 14px rgba(0,0,0,.45); }}
.cena-item em {{ font-style: normal; color: {c["destaque"]}; margin-right: 22px; font-family: "{dest["familia"]}"; }}
.cena-frase {{ position: absolute; left: 80px; width: 920px; top: 520px; text-align: center; font-family: "{dest["familia"]}";
  font-style: {"italic" if dest.get("italico") else "normal"}; font-size: 120px; line-height: 1.08; color: {c["texto"]}; }}
.cena-frase span {{ display: inline-block; margin: 0 .14em; }}
"""


def _entra(
    sel: str, t: float, de: str, para: str, dur: float = 0.6, ease: str = "expo.out"
) -> str:
    return f'tl.fromTo("{sel}", {{{de}}}, {{{para}, duration: {dur:.2f}, ease: "{ease}"}}, {t:.3f});'


def construir(
    modelo: str, ev: str, e: dict, t0: float, t1: float, idt: dict
) -> tuple[str, list[str], list[tuple[float, str]]]:
    c = idt["cores"]
    vivos = c.get("vivos", [c["destaque"]])
    html_: list[str] = [
        f'<div class="cena-bg"></div><div class="cena-luz" id="{ev}-luz"></div>'
    ]
    js: list[str] = [
        f'tl.fromTo("#{ev}-luz", {{x: -120, y: 40}}, {{x: 120, y: -40, duration: {t1 - t0:.2f}, ease: "none"}}, {t0:.3f});'
    ]
    sons: list[tuple[float, str]] = []
    if e.get("titulo"):
        html_.append(f'<div class="cena-kick" id="{ev}-k">{esc(e["titulo"])}</div>')
        js.append(
            _entra(
                f"#{ev}-k", t0 + 0.15, "opacity: 0, y: 16", "opacity: .85, y: 0", 0.5
            )
        )

    if modelo == "numero":
        cor = f"color:{vivos[0]};" if e.get("vivo") else ""
        html_.append(
            f'<div class="cena-num" id="{ev}-n" style="{cor}">{esc(e["grande"])}</div>'
        )
        html_.append(
            f'<div class="cena-uni" id="{ev}-u">{esc(e.get("unidade", ""))}</div>'
        )
        html_.append(
            f'<div class="cena-txt" id="{ev}-t">{esc(e.get("texto", ""))}</div>'
        )
        tn = float(e.get("t", t0 + 0.2))
        js.append(
            _entra(
                f"#{ev}-n",
                tn,
                'opacity: 0, scale: 0.7, filter: "blur(18px)"',
                'opacity: 1, scale: 1, filter: "blur(0px)"',
                0.7,
            )
        )
        js.append(
            _entra(f"#{ev}-u", tn + 0.35, "opacity: 0, y: 20", "opacity: 1, y: 0", 0.5)
        )
        js.append(_entra(f"#{ev}-t", tn + 0.6, "opacity: 0", "opacity: .85", 0.5))
        sons.append((tn, "cena_item"))

    elif modelo == "barras":
        itens = e["itens"]
        n = len(itens)
        largura_total = n * 200 + (n - 1) * 90
        x0 = (W - largura_total) // 2
        for i, it in enumerate(itens):
            x = x0 + i * 290
            frac = max(0.04, min(1.0, float(it["valor"]) / 100))
            cor = f"background:{vivos[int(it['vivo']) - 1]};" if it.get("vivo") else ""
            topo_seta = 560 * frac + 30
            html_.append(
                f'<div class="cena-col" style="left:{x}px;height:560px">'
                f'<div class="cena-trilho"></div><div class="cena-barra" id="{ev}-b{i}" style="{cor}"></div>'
                f'<div class="cena-seta" id="{ev}-s{i}" style="bottom:{topo_seta:.0f}px">{esc(it.get("seta", ""))}</div></div>'
                f'<div class="cena-rot" id="{ev}-r{i}" style="left:{x - 40}px">{esc(it["rotulo"])}</div>'
            )
            ti = float(it.get("t", t0 + 0.4 + 0.7 * i))
            js.append(
                _entra(f"#{ev}-b{i}", ti, "scaleY: 0", f"scaleY: {frac:.3f}", 0.8)
            )
            js.append(
                _entra(
                    f"#{ev}-s{i}",
                    ti + 0.25,
                    "opacity: 0, y: 20",
                    "opacity: 1, y: 0",
                    0.5,
                )
            )
            js.append(
                _entra(f"#{ev}-r{i}", ti, "opacity: 0", "opacity: 1", 0.4, "power2.out")
            )
            sons.append((ti, "cena_item"))

    elif modelo == "notificacoes":
        html_.append(
            f'<div class="cena-cel" id="{ev}-cel"><div class="cena-notch"></div>'
        )
        for i, it in enumerate(e["itens"]):
            html_.append(
                f'<div class="cena-noti" id="{ev}-n{i}" style="top:{110 + i * 150}px"><i></i>'
                f"<b>{esc(it['titulo'])}</b><span>{esc(it.get('sub', 'agora'))}</span></div>"
            )
        html_.append("</div>")
        html_.append(f'<div class="cena-badge" id="{ev}-bd">')
        for i in range(len(e["itens"])):
            html_.append(f'<span id="{ev}-bd{i}">{i + 1}</span>')
        html_.append("</div>")
        js.append(
            _entra(
                f"#{ev}-cel",
                t0 + 0.05,
                "opacity: 0, y: 60, scale: 0.94",
                "opacity: 1, y: 0, scale: 1",
                0.6,
            )
        )
        js.append(f'tl.set("#{ev}-bd", {{opacity: 0}}, 0);')
        for k in range(len(e["itens"])):
            js.append(f'tl.set("#{ev}-bd{k}", {{opacity: 0}}, 0);')
        for i, it in enumerate(e["itens"]):
            ti = float(it.get("t", t0 + 0.5 + 0.8 * i))
            js.append(
                _entra(
                    f"#{ev}-n{i}",
                    ti,
                    "opacity: 0, y: -50, scale: 0.92",
                    "opacity: 1, y: 0, scale: 1",
                    0.45,
                    "power3.out",
                )
            )
            # celular "vibra" a cada notificação
            js.append(
                f'tl.to("#{ev}-cel", {{keyframes: [{{x: -9}}, {{x: 9}}, {{x: -6}}, {{x: 6}}, {{x: 0}}], duration: 0.28, ease: "none"}}, {ti:.3f});'
            )
            js.append(f'tl.set("#{ev}-bd", {{opacity: 1}}, {ti:.3f});')
            js.append(f'tl.set("#{ev}-bd{i}", {{opacity: 1}}, {ti:.3f});')
            if i:
                js.append(f'tl.set("#{ev}-bd{i - 1}", {{opacity: 0}}, {ti:.3f});')
            js.append(
                _entra(f"#{ev}-bd", ti, "scale: 0.6", "scale: 1", 0.35, "back.out(2)")
            )
            sons.append((ti, "cena_item"))

    elif modelo == "pico":
        tp = float(e.get("t_pico", t0 + 1.0))
        tq = float(e.get("t_queda", tp + 1.2))
        base = "M 0 470 L 300 470 L 380 460 L 430 470"
        pico = "M 430 470 L 470 60 L 520 470 L 600 600 L 900 640"
        html_.append(
            '<svg class="cena-svg" viewBox="0 0 900 700">'
            '<line x1="0" y1="690" x2="900" y2="690" stroke="rgba(245,242,234,.25)" stroke-width="2"/>'
            f'<path id="{ev}-p1" d="{base}" fill="none" stroke="{c["destaque"]}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="440" stroke-dashoffset="440"/>'
            f'<path id="{ev}-p2" d="{pico}" fill="none" stroke="{vivos[0]}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1400" stroke-dashoffset="1400"/>'
            f'<circle id="{ev}-c" cx="470" cy="60" r="18" fill="{vivos[0]}"/></svg>'
            f'<div class="cena-rotulo" id="{ev}-lp" style="left:640px;top:520px;width:380px;font-size:64px;line-height:1.05;color:{vivos[0]}">{esc(e.get("rotulo_pico", "pico"))}</div>'
            f'<div class="cena-rotulo" id="{ev}-lq" style="left:560px;top:1090px;color:{c["texto"]};font-size:64px">{esc(e.get("rotulo_queda", "queda"))}</div>'
        )
        js.append(
            f'tl.fromTo("#{ev}-p1", {{strokeDashoffset: 440}}, {{strokeDashoffset: 0, duration: {max(0.4, tp - t0 - 0.3):.2f}, ease: "none"}}, {t0 + 0.2:.3f});'
        )
        js.append(
            f'tl.fromTo("#{ev}-p2", {{strokeDashoffset: 1400}}, {{strokeDashoffset: 0, duration: {max(0.6, tq - tp + 0.2):.2f}, ease: "power2.out"}}, {tp - 0.1:.3f});'
        )
        js.append(
            _entra(
                f"#{ev}-c",
                tp + 0.1,
                'opacity: 0, scale: 0, transformOrigin: "50% 50%"',
                "opacity: 1, scale: 1",
                0.4,
                "back.out(2.5)",
            )
        )
        js.append(
            _entra(f"#{ev}-lp", tp + 0.15, "opacity: 0, y: 20", "opacity: 1, y: 0", 0.5)
        )
        js.append(
            _entra(f"#{ev}-lq", tq, "opacity: 0, y: -20", "opacity: 1, y: 0", 0.5)
        )
        sons += [(tp, "cena_item"), (tq, "cena_item")]

    elif modelo == "sol":
        html_.insert(
            1,
            f'<div class="cena-ceu" id="{ev}-ceu"></div><div class="cena-sol" id="{ev}-sol"></div>',
        )
        js.append(
            _entra(f"#{ev}-ceu", t0, "opacity: 0", "opacity: 1", 1.4, "power1.out")
        )
        js.append(
            _entra(
                f"#{ev}-sol",
                t0,
                "y: 1300, scale: 0.8",
                "y: 470, scale: 1",
                1.8,
                "power2.out",
            )
        )
        for i, it in enumerate(e["itens"]):
            ti = float(it.get("t", t0 + 0.6 + 0.8 * i))
            html_.append(
                f'<div class="cena-item" id="{ev}-i{i}" style="top:{860 + i * 95}px"><em>→</em>{esc(it["texto"])}</div>'
            )
            js.append(
                _entra(
                    f"#{ev}-i{i}",
                    ti,
                    'opacity: 0, x: -40, filter: "blur(8px)"',
                    'opacity: 1, x: 0, filter: "blur(0px)"',
                    0.55,
                )
            )
            sons.append((ti, "cena_item"))

    elif modelo == "frase":
        partes = []
        for i, p in enumerate(e["palavras"]):
            cor = f"color:{vivos[0] if p.get('destaque') else c['texto']};"
            partes.append(
                f'<span id="{ev}-w{i}" style="{cor}">{esc(p["texto"])}</span>'
            )
            ti = float(p.get("t", t0 + 0.2 + 0.25 * i))
            js.append(
                _entra(
                    f"#{ev}-w{i}",
                    ti,
                    'opacity: 0, y: 30, filter: "blur(10px)"',
                    'opacity: 1, y: 0, filter: "blur(0px)"',
                    0.45,
                )
            )
        html_.append(f'<div class="cena-frase">{"".join(partes)}</div>')

    else:
        raise ValueError(f"modelo de cena desconhecido: {modelo}")

    return "".join(html_), js, sons
