"""Cenas em tela cheia que cobrem a câmera ("cutaways" animados).

Cada cena ocupa o quadro inteiro por alguns segundos enquanto a voz continua,
ilustrando o que está sendo dito. O conteúdo fica entre y 200 e 1250 para a
legenda (y ≈ 1400) continuar legível por cima. Todas usam as cores da identidade.

Modelos (campo "modelo" do evento "cena"):
    numero        número gigante + unidade + frase          {grande, unidade, texto, tam?}
    barras        barras que sobem/descem na palavra        {titulo, itens:[{rotulo, valor 0-100, seta, t}]}
    notificacoes  celular recebendo notificações            {titulo, itens:[{titulo, sub, t}]}
    pico          gráfico de linha com pico e queda         {titulo, t_pico, rotulo_pico, t_queda, rotulo_queda}
    sol           nascer do sol + lista de hábitos          {titulo, itens:[{texto, t}]}
    frase         frase grande, palavra por palavra         {palavras:[{texto, t, destaque?, quebra?}]}
    rede          rede de neurônios que se desenha e acende {titulo, t, rotulo}
    queda         linhas retas até uma idade e depois caindo {titulo, idades, t_marco, rotulo_marco,
                  (perda com a idade: músculo, osso, …)       linhas:[{rotulo, t, t_fim, cor?, marco?}]}
    busca         celular: página de busca, frase digitada    {palavras:[{texto, t, fim}], t_logo, t_alerta,
                  letra a letra e resultados                   t_enter, resultados:[{rotulo, vivo|cor, t}], logo}
    versus        dois cartões lado a lado (✓ × ✗)            {lados:[{texto, icone, cor?, t}], t_vs}
    troca         palavra riscada e trocada por outra         {de:{texto,t}, sub:{texto,t}, t_risco, para:{texto,t,vivo}}

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
    peso = dest.get("peso", 400)
    kick = idt.get("cena_kick", {})
    return f"""
.cena-in {{ position: absolute; inset: 0; overflow: hidden; }}
.cena-bg {{ position: absolute; inset: 0; background: radial-gradient(130% 85% at 50% 32%, {fundo[0]} 0%, {fundo[1]} 72%); }}
.cena-luz {{ position: absolute; width: 1000px; height: 1000px; left: 40px; top: 160px; border-radius: 50%;
  background: radial-gradient(closest-side, {c["veu"]}, rgba(0,0,0,0)); opacity: .55; }}
.cena-kick {{ position: absolute; left: 80px; width: 920px; top: 300px; text-align: center; font-family: "Inter";
  font-weight: {kick.get("peso", 400)}; font-size: {kick.get("tam", 34)}px; letter-spacing: {kick.get("tracking", ".24em")};
  text-transform: {"none" if kick.get("caixa") == "normal" else "uppercase"}; color: {c["texto"]}; opacity: .85; }}
.cena-num {{ position: absolute; left: 0; width: {W}px; top: 470px; text-align: center; font-family: "{dest["familia"]}";
  font-style: {"italic" if dest.get("italico") else "normal"}; font-weight: {peso}; font-size: 300px; line-height: 1; color: {c["destaque"]}; }}
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
.cena-rotulo {{ position: absolute; font-family: "{dest["familia"]}"; font-weight: {peso}; font-style: {"italic" if dest.get("italico") else "normal"};
  font-size: 76px; line-height: 1; }}
.cena-sol {{ position: absolute; left: 340px; top: 0; width: 400px; height: 400px; border-radius: 50%;
  background: radial-gradient(closest-side, #FFE7A8, #F7B955 60%, rgba(247,185,85,0) 100%); }}
.cena-ceu {{ position: absolute; inset: 0; background: linear-gradient(180deg, #F2B46B 0%, #E78A5B 35%, #3A3A4F 75%, #141C24 100%); }}
.cena-item {{ position: absolute; left: 150px; width: 820px; font-family: "Inter"; font-weight: 500; font-size: 62px; color: {c["texto"]};
  text-shadow: 0 3px 14px rgba(0,0,0,.45); }}
.cena-item em {{ font-style: normal; color: {c["destaque"]}; margin-right: 22px; font-family: "{dest["familia"]}"; font-weight: {peso}; }}
.cena-frase {{ position: absolute; left: 80px; width: 920px; top: 520px; text-align: center; font-family: "{dest["familia"]}";
  font-style: {"italic" if dest.get("italico") else "normal"}; font-weight: {peso}; font-size: 120px; line-height: 1.08; color: {c["texto"]}; }}
.cena-frase span {{ display: inline-block; margin: 0 .14em; }}
.cena-rede-rot {{ position: absolute; left: 80px; width: 920px; top: 1150px; text-align: center; font-family: "Inter";
  font-weight: 500; font-size: 48px; color: {c["texto"]}; }}
{CSS_BUSCA}{CSS_VERSUS}{CSS_TROCA}"""


# --- busca: celular com a página de busca, a frase digitada e os resultados ---
CSS_BUSCA = """
.bus-cel { position: absolute; left: 150px; top: 180px; width: 780px; height: 1190px; border-radius: 72px; overflow: hidden;
  background: #fff; border: 10px solid #121417; box-shadow: 0 30px 90px rgba(0,0,0,.6); font-family: "Inter"; color: #202124; }
.bus-status { position: absolute; left: 0; right: 0; top: 0; height: 56px; padding: 16px 44px 0; display: flex; justify-content: space-between;
  font-weight: 600; font-size: 26px; }
.bus-status i { display: inline-block; width: 46px; height: 22px; border: 2px solid #202124; border-radius: 6px; position: relative; top: 2px; }
.bus-status i::after { content: ""; position: absolute; left: 2px; top: 2px; width: 30px; height: 14px; border-radius: 3px; background: #202124; }
.bus-p1, .bus-p2 { position: absolute; inset: 56px 0 0 0; }
.bus-logo { position: absolute; left: 0; width: 100%; top: 150px; text-align: center; font-weight: 600; font-size: 136px;
  letter-spacing: -0.045em; line-height: 1; }
.bus-logo span { display: inline-block; }
.bus-caixa { position: absolute; left: 36px; width: 708px; top: 360px; height: 104px; border-radius: 52px; border: 2px solid #dfe1e5;
  box-shadow: 0 4px 16px rgba(32,33,36,.18); }
.bus-caixa svg { position: absolute; left: 30px; top: 30px; width: 44px; height: 44px; }
.bus-txt { position: absolute; left: 94px; top: 27px; font-weight: 500; font-size: 40px; white-space: pre; line-height: 50px; }
.bus-txt span { display: none; }
.bus-caret { display: inline-block; width: 3px; height: 46px; background: #1a73e8; vertical-align: -9px; margin-left: 2px; }
.bus-kb { position: absolute; left: 0; right: 0; bottom: 0; height: 450px; background: #d2d5db; }
.bus-k { position: absolute; height: 84px; border-radius: 12px; background: #fff; box-shadow: 0 2px 0 #898a8d;
  text-align: center; line-height: 84px; font-weight: 400; font-size: 38px; color: #111; }
.bus-k.esc { background: #abb0ba; font-size: 28px; }
.bus-k.ir { background: #1a73e8; color: #fff; font-size: 30px; font-weight: 600; }
.bus-topo-logo { position: absolute; left: 0; width: 100%; top: 26px; text-align: center; font-weight: 600; font-size: 60px;
  letter-spacing: -0.045em; line-height: 1; }
.bus-caixa2 { position: absolute; left: 30px; width: 720px; top: 112px; height: 84px; border-radius: 42px; background: #f1f3f4;
  font-weight: 500; font-size: 32px; line-height: 84px; padding-left: 82px; white-space: nowrap; overflow: hidden; }
.bus-caixa2 svg { position: absolute; left: 26px; top: 22px; width: 38px; height: 38px; }
.bus-abas { position: absolute; left: 40px; top: 226px; display: flex; gap: 38px; font-weight: 500; font-size: 28px; color: #5f6368; }
.bus-abas b { color: #1a73e8; font-weight: 600; border-bottom: 4px solid #1a73e8; padding-bottom: 10px; }
.bus-linha { position: absolute; left: 0; top: 282px; height: 2px; width: 100%; background: #ebebeb; }
.bus-carga { position: absolute; left: 0; top: 280px; height: 5px; width: 100%; background: #1a73e8; transform-origin: 0 50%; }
.bus-res { position: absolute; left: 30px; width: 720px; height: 236px; border-radius: 26px; background: #fff;
  border: 3px solid #ececec; padding: 26px 30px; }
.bus-chip { display: inline-block; padding: 6px 22px; border-radius: 30px; font-weight: 900; font-size: 34px; color: #141414;
  letter-spacing: -0.01em; }
.bus-barra { height: 20px; border-radius: 10px; background: #e6e8eb; margin-top: 18px; }
.bus-barra.t { background: #c9d7f8; height: 26px; margin-top: 22px; }
.bus-alerta { position: absolute; inset: 0; border-radius: 62px; box-shadow: inset 0 0 0 10px #ff3b30, inset 0 0 120px rgba(255,59,48,.55); opacity: 0; }
"""

LUPA = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="#9aa0a6" stroke-width="2.4" stroke-linecap="round">'
    '<circle cx="10.5" cy="10.5" r="6.5"/><line x1="15.5" y1="15.5" x2="21" y2="21"/></svg>'
)
CORES_GOOGLE = ["#4285F4", "#EA4335", "#FBBC05", "#4285F4", "#34A853", "#EA4335"]
TECLAS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]


def _sem_acento(ch: str) -> str:
    return {"á": "a", "à": "a", "â": "a", "ã": "a", "é": "e", "ê": "e", "í": "i", "ó": "o",
            "ô": "o", "õ": "o", "ú": "u", "ç": "c"}.get(ch.lower(), ch.lower())


def _busca(ev: str, e: dict, t0: float, t1: float, c: dict, js: list[str], sons: list) -> str:
    """Celular com a página de busca. A frase é digitada letra a letra no tempo
    de cada palavra falada ("palavras": [{texto, t, fim}]); em "t_enter" a tecla
    "ir" é tocada e entram os resultados ("resultados": [{rotulo, cor, t}]), que
    são só barras cinzas: nenhuma manchete inventada. "t_alerta" acende a borda
    em vermelho e treme o celular (palavra forte da frase)."""
    vivos = c.get("vivos", [c["destaque"]])
    logo_txt = e.get("logo", "Google")
    logo = "".join(
        f'<span id="{ev}-g{i}" style="color:{CORES_GOOGLE[i % len(CORES_GOOGLE)]}">{esc(ch)}</span>'
        for i, ch in enumerate(logo_txt)
    )
    logo_peq = "".join(
        f'<span style="color:{CORES_GOOGLE[i % len(CORES_GOOGLE)]}">{esc(ch)}</span>'
        for i, ch in enumerate(logo_txt)
    )
    # letras com o instante em que cada uma aparece
    letras: list[tuple[str, float]] = []
    palavras = e["palavras"]
    for k, p in enumerate(palavras):
        txt = p["texto"] + (" " if k + 1 < len(palavras) else "")
        a, z = float(p["t"]), float(p.get("fim", float(p["t"]) + 0.4))
        for j, ch in enumerate(txt):
            letras.append((ch, a + (z - a) * j / max(1, len(txt))))
    frase = " ".join(p["texto"] for p in palavras)
    spans = "".join(f'<span id="{ev}-c{i}">{esc(ch)}</span>' for i, (ch, _) in enumerate(letras))

    # teclado
    teclas = []
    larg, alt, gap = 67, 84, 9
    for r, linha in enumerate(TECLAS):
        x0 = (780 - (len(linha) * larg + (len(linha) - 1) * gap)) / 2
        for i, ch in enumerate(linha):
            teclas.append(
                f'<div class="bus-k" id="{ev}-k{ch}" style="left:{x0 + i * (larg + gap):.0f}px;top:{22 + r * 104}px;width:{larg}px">{ch}</div>'
            )
    teclas.append(f'<div class="bus-k esc" style="left:10px;top:230px;width:96px">⇧</div>')
    teclas.append(f'<div class="bus-k esc" style="left:674px;top:230px;width:96px">⌫</div>')
    teclas.append(f'<div class="bus-k esc" style="left:10px;top:334px;width:150px">123</div>')
    teclas.append(f'<div class="bus-k" id="{ev}-kesp" style="left:170px;top:334px;width:430px;font-size:28px">espaço</div>')
    teclas.append(f'<div class="bus-k ir" id="{ev}-kir" style="left:610px;top:334px;width:160px">ir</div>')

    res = []
    for i, rs in enumerate(e.get("resultados", [])):
        cor = rs.get("cor") or (vivos[int(rs["vivo"]) - 1] if rs.get("vivo") else c["destaque"])
        borda = f"border-color:{cor};" if rs.get("borda") else ""
        res.append(
            f'<div class="bus-res" id="{ev}-r{i}" style="top:{318 + i * 262}px;{borda}">'
            f'<span class="bus-chip" style="background:{cor}">{esc(rs["rotulo"])}</span>'
            f'<div class="bus-barra t" style="width:{88 - 9 * i}%"></div><div class="bus-barra" style="width:96%"></div>'
            f'<div class="bus-barra" style="width:{70 + 8 * i}%"></div></div>'
        )

    partes = [
        f'<div class="bus-cel" id="{ev}-cel"><div class="bus-status"><span>9:41</span><i></i></div>',
        f'<div class="bus-p1" id="{ev}-p1"><div class="bus-logo">{logo}</div>',
        f'<div class="bus-caixa" id="{ev}-cx">{LUPA}<div class="bus-txt">{spans}<i class="bus-caret" id="{ev}-car"></i></div></div></div>',
        f'<div class="bus-p2" id="{ev}-p2" style="opacity:0"><div class="bus-topo-logo">{logo_peq}</div>',
        f'<div class="bus-caixa2">{LUPA}{esc(frase)}</div>',
        '<div class="bus-abas"><b>Tudo</b><span>Notícias</span><span>Vídeos</span><span>Imagens</span></div>',
        f'<div class="bus-linha"></div><div class="bus-carga" id="{ev}-ld"></div>{"".join(res)}</div>',
        f'<div class="bus-kb" id="{ev}-kb">{"".join(teclas)}</div>',
        f'<div class="bus-alerta" id="{ev}-al"></div></div>',
    ]

    js.append(_entra(f"#{ev}-cel", t0 + 0.02, "y: 260, opacity: 0", "y: 0, opacity: 1", 0.5, "power3.out"))
    tl_logo = float(e.get("t_logo", t0 + 0.3))
    for i in range(len(logo_txt)):
        js.append(_entra(f"#{ev}-g{i}", tl_logo + 0.05 * i, "opacity: 0, y: 30, scale: 0.6",
                         "opacity: 1, y: 0, scale: 1", 0.35, "back.out(2.2)"))
    sons.append((tl_logo, "busca_logo"))
    # cursor piscando até a primeira letra
    t_primeira = letras[0][1] if letras else t1
    t = t0 + 0.5
    ligado = False
    while t < t_primeira - 0.05:
        js.append(f'tl.set("#{ev}-car", {{opacity: {1 if ligado else 0}}}, {t:.3f});')
        ligado = not ligado
        t += 0.45
    js.append(f'tl.set("#{ev}-car", {{opacity: 1}}, {t_primeira:.3f});')
    for i, (ch, tc) in enumerate(letras):
        js.append(f'tl.set("#{ev}-c{i}", {{display: "inline"}}, {tc:.3f});')
        tecla = "esp" if ch == " " else _sem_acento(ch)
        if tecla == "esp" or tecla in "".join(TECLAS):
            # set + to: um fromTo deixaria a tecla "apertada" antes da hora (immediateRender)
            js.append(f'tl.set("#{ev}-k{tecla}", {{backgroundColor: "#9aa3b2", scale: 1.12}}, {tc:.3f});')
            js.append(
                f'tl.to("#{ev}-k{tecla}", {{backgroundColor: "#ffffff", scale: 1, duration: 0.14, ease: "power1.out"}}, {tc + 0.02:.3f});'
            )
        if ch != " ":
            sons.append((tc, ("tecla", "tecla2", "tecla3")[i % 3]))
    if e.get("t_alerta"):
        ta = float(e["t_alerta"])
        js.append(f'tl.set("#{ev}-al", {{opacity: 1}}, {ta:.3f});')
        js.append(f'tl.to("#{ev}-al", {{opacity: 0, duration: 0.6, ease: "power2.in"}}, {ta + 0.02:.3f});')
        js.append(
            f'tl.to("#{ev}-cel", {{keyframes: [{{x: -14, rotation: -1}}, {{x: 12, rotation: 1}}, {{x: -8}}, {{x: 6}}, {{x: 0, rotation: 0}}], '
            f'duration: 0.3, ease: "none"}}, {ta:.3f});'
        )
    te = float(e.get("t_enter", letras[-1][1] + 0.1 if letras else t0 + 1))
    js.append(f'tl.set("#{ev}-kir", {{backgroundColor: "#0b4fb3", scale: 0.92}}, {te:.3f});')
    js.append(f'tl.to("#{ev}-kir", {{backgroundColor: "#1a73e8", scale: 1, duration: 0.2}}, {te + 0.02:.3f});')
    sons.append((te, "busca_enter"))
    js.append(f'tl.to("#{ev}-p1", {{opacity: 0, duration: 0.12}}, {te + 0.06:.3f});')
    js.append(f'tl.to("#{ev}-kb", {{y: 470, duration: 0.3, ease: "power2.in"}}, {te + 0.06:.3f});')
    js.append(f'tl.to("#{ev}-p2", {{opacity: 1, duration: 0.12}}, {te + 0.1:.3f});')
    js.append(
        f'tl.fromTo("#{ev}-ld", {{scaleX: 0, opacity: 1}}, {{scaleX: 1, duration: 0.35, ease: "power2.out"}}, {te + 0.1:.3f});'
    )
    js.append(f'tl.to("#{ev}-ld", {{opacity: 0, duration: 0.15}}, {te + 0.45:.3f});')
    for i, rs in enumerate(e.get("resultados", [])):
        tr = float(rs.get("t", te + 0.4 + 0.5 * i))
        js.append(
            _entra(f"#{ev}-r{i}", tr, 'opacity: 0, y: 40, scale: 0.94', 'opacity: 1, y: 0, scale: 1', 0.4, "back.out(1.8)")
        )
        sons.append((tr, "cena_item"))
    return "".join(partes)


# --- versus: dois cartões lado a lado (ex.: VERDADE ✓ × MENTIRA ✗) ---
CSS_VERSUS = """
.vs-c { position: absolute; top: 470px; width: 460px; height: 620px; border-radius: 40px; border: 6px solid; text-align: center; }
.vs-c svg { position: absolute; left: 115px; top: 80px; width: 230px; height: 230px; }
.vs-c b { position: absolute; left: 0; width: 100%; top: 380px; font-family: "Inter"; font-weight: 900; font-size: 78px;
  letter-spacing: -0.02em; line-height: 1; }
.vs-x { position: absolute; left: 470px; top: 710px; width: 140px; height: 140px; border-radius: 50%; background: #0b0d0c;
  border: 5px solid #F5F2EA; text-align: center; line-height: 128px; font-family: "Inter"; font-weight: 900; font-size: 56px; color: #F5F2EA; }
"""
ICONES_VS = {
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="{cor}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>',
    "x": '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="{cor}" stroke-width="3.2" stroke-linecap="round"/>',
}


def _versus(ev: str, e: dict, t0: float, c: dict, js: list[str], sons: list) -> str:
    vivos = c.get("vivos", [c["destaque"]])
    partes = []
    for i, ld in enumerate(e["lados"][:2]):
        cor = ld.get("cor") or vivos[i % len(vivos)]
        icone = ICONES_VS.get(ld.get("icone", "check" if i == 0 else "x"), "").replace("{cor}", cor)
        partes.append(
            f'<div class="vs-c" id="{ev}-l{i}" style="left:{50 + i * 520}px;border-color:{cor};background:{cor}22">'
            f'<svg viewBox="0 0 24 24">{icone}</svg><b style="color:{cor}">{esc(ld["texto"])}</b></div>'
        )
        tl_ = float(ld.get("t", t0 + 0.3 + 1.2 * i))
        lado = -1 if i == 0 else 1
        js.append(
            _entra(f"#{ev}-l{i}", tl_, f"opacity: 0, x: {lado * 520}, rotation: {lado * 8}",
                   "opacity: 1, x: 0, rotation: 0", 0.45, "back.out(1.6)")
        )
        if i == 1:  # o segundo "empurra" o primeiro
            js.append(
                f'tl.to("#{ev}-l0", {{keyframes: [{{x: -26, rotation: -3}}, {{x: 0, rotation: 0}}], duration: 0.4, ease: "power2.out"}}, {tl_ + 0.12:.3f});'
            )
        sons.append((tl_, "versus_lado"))
    partes.append(f'<div class="vs-x" id="{ev}-vs">VS</div>')
    tv = float(e.get("t_vs", t0 + 0.9))
    js.append(_entra(f"#{ev}-vs", tv, "opacity: 0, scale: 0", "opacity: 1, scale: 1", 0.35, "back.out(2.5)"))
    sons.append((tv, "cena_item"))
    return "".join(partes)


# --- troca: palavra grande que é riscada e trocada por outra (opinião → torcida) ---
CSS_TROCA = """
.tr-a { position: absolute; left: 0; width: 1080px; text-align: center; font-family: "Inter"; font-weight: 900; line-height: 1;
  letter-spacing: -0.03em; text-shadow: 0 6px 30px rgba(0,0,0,.6); }
.tr-a .risco { position: absolute; left: 50%; top: 52%; height: 22px; border-radius: 11px; transform-origin: 0 50%; }
"""


def _troca(ev: str, e: dict, t0: float, c: dict, js: list[str], sons: list) -> str:
    vivos = c.get("vivos", [c["destaque"]])
    a, b = e["de"], e["para"]
    tam_a, tam_b = int(e.get("tam_de", 170)), int(e.get("tam_para", 200))
    larg_a = int(tam_a * 0.66 * len(a["texto"]))
    y = int(e.get("topo", 470))
    cor_b = vivos[int(b.get("vivo", 1)) - 1]
    partes = [
        f'<div class="tr-a" id="{ev}-a" style="top:{y}px;font-size:{tam_a}px;color:{c["texto"]}"><span style="position:relative;display:inline-block">'
        f'{esc(a["texto"])}<i class="risco" id="{ev}-x" style="left:-20px;width:{larg_a + 40}px;background:{cor_b}"></i></span></div>'
    ]
    js.append(_entra(f"#{ev}-a", float(a["t"]), 'opacity: 0, scale: 1.3, filter: "blur(12px)"',
                     'opacity: 1, scale: 1, filter: "blur(0px)"', 0.35, "power3.out"))
    js.append(f'tl.set("#{ev}-x", {{scaleX: 0}}, 0);')
    if e.get("sub"):
        partes.append(
            f'<div class="tr-a" id="{ev}-s" style="top:{y + tam_a + 30}px;font-size:76px;color:{c["destaque"]}">{esc(e["sub"]["texto"])}</div>'
        )
        js.append(_entra(f"#{ev}-s", float(e["sub"]["t"]), "opacity: 0, y: 24", "opacity: 1, y: 0", 0.35, "power3.out"))
        sons.append((float(e["sub"]["t"]), "cena_item"))
    tr = float(e["t_risco"])
    js.append(f'tl.fromTo("#{ev}-x", {{scaleX: 0}}, {{scaleX: 1, duration: 0.22, ease: "power3.out"}}, {tr:.3f});')
    js.append(f'tl.to("#{ev}-a", {{color: "rgba(245,242,234,0.4)", duration: 0.25}}, {tr + 0.15:.3f});')
    if e.get("sub"):
        js.append(f'tl.to("#{ev}-s", {{opacity: 0.35, duration: 0.25}}, {tr + 0.15:.3f});')
    sons.append((tr, "troca_risco"))
    yb = y + tam_a + (150 if e.get("sub") else 60) + 40
    partes.append(
        f'<div class="tr-a" id="{ev}-b" style="top:{yb}px;font-size:{tam_b}px;color:{cor_b}">{esc(b["texto"])}</div>'
    )
    js.append(_entra(f"#{ev}-b", float(b["t"]), "opacity: 0, scale: 2.2, rotation: -6",
                     "opacity: 1, scale: 1, rotation: -3", 0.28, "power4.out"))
    sons.append((float(b["t"]), "troca_para"))
    return "".join(partes)


def _entra(
    sel: str, t: float, de: str, para: str, dur: float = 0.6, ease: str = "expo.out"
) -> str:
    return f'tl.fromTo("{sel}", {{{de}}}, {{{para}, duration: {dur:.2f}, ease: "{ease}"}}, {t:.3f});'


def construir(
    modelo: str, ev: str, e: dict, t0: float, t1: float, idt: dict
) -> tuple[str, list[str], list[tuple[float, str]]]:
    c = idt["cores"]
    vivos = c.get("vivos", [c["destaque"]])
    html_: list[str] = []
    js: list[str] = []
    if not e.get("sobre_camera"):  # "sobre_camera": a câmera escurecida fica de fundo
        html_.append(f'<div class="cena-bg"></div><div class="cena-luz" id="{ev}-luz"></div>')
        js.append(
            f'tl.fromTo("#{ev}-luz", {{x: -120, y: 40}}, {{x: 120, y: -40, duration: {t1 - t0:.2f}, ease: "none"}}, {t0:.3f});'
        )
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
        if e.get("tam"):  # número comprido ("10–15%") precisa de letra menor
            cor += f"font-size:{int(e['tam'])}px;top:{470 + (300 - int(e['tam'])) // 2}px;"
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
            d = p.get("destaque")
            viva = vivos[min(int(d), len(vivos)) - 1] if d is not True and d else vivos[0]
            cor = f"color:{viva if d else c['texto']};"
            partes.append(
                f'<span id="{ev}-w{i}" style="{cor}">{esc(p["texto"])}</span>'
                + ("<br>" if p.get("quebra") else "")
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

    elif modelo == "queda":
        # Gráfico por idade: cada linha fica reta até a idade do marco e cai
        # (desenhada entre "t" e "t_fim"). Até 3 linhas.
        idades = [str(i) for i in e.get("idades", [30, 40, 50, 60, 70])]
        marco = int(e.get("marco", 1))  # índice da idade onde começa a queda
        xs = [60 + i * (780 / (len(idades) - 1)) for i in range(len(idades))]
        xm = xs[marco]
        eixo = 640
        tm = float(e.get("t_marco", t0 + 0.4))
        cores_linha = [c["destaque"], c.get("voz", c["texto"]), vivos[0]]
        svg = [
            '<svg class="cena-svg" viewBox="0 0 900 700">',
            f'<line x1="0" y1="{eixo}" x2="900" y2="{eixo}" stroke="rgba(245,242,234,.25)" stroke-width="2"/>',
            f'<line id="{ev}-m" x1="{xm:.0f}" y1="40" x2="{xm:.0f}" y2="{eixo}" stroke="rgba(245,242,234,.55)"'
            ' stroke-width="3" stroke-dasharray="10 12"/>',
        ]
        rotulos = []
        for i, ln in enumerate(e["linhas"][:3]):
            y0 = 140 + 95 * i
            y1 = y0 + 280 + 20 * i
            # cada linha pode cair numa idade diferente ("marco" da linha)
            xl = xs[int(ln["marco"])] if "marco" in ln else xm
            larg = 840 - xl
            reta = f"M 60 {y0} L {xl:.0f} {y0}"
            curva = f"M {xl:.0f} {y0} C {xl + 0.27 * larg:.0f} {y0 + 10} {xl + 0.56 * larg:.0f} {y1 - 120} 840 {y1}"
            cor = ln.get("cor") or cores_linha[i]
            svg.append(
                f'<path id="{ev}-r{i}" d="{reta}" fill="none" stroke="{cor}" stroke-width="10" stroke-linecap="round"'
                f' stroke-dasharray="{max(xl, 1):.0f}" stroke-dashoffset="{max(xl, 1):.0f}"/>'
                f'<path id="{ev}-q{i}" d="{curva}" fill="none" stroke="{cor}" stroke-width="10" stroke-linecap="round"'
                ' stroke-dasharray="900" stroke-dashoffset="900"/>'
            )
            ti = float(ln.get("t", tm + 0.6 + 0.9 * i))
            tf = float(ln.get("t_fim", ti + 1.2))
            js.append(
                f'tl.fromTo("#{ev}-r{i}", {{strokeDashoffset: {max(xl, 1):.0f}}}, {{strokeDashoffset: 0, duration: {max(0.3, tm - t0 - 0.2):.2f}, ease: "none"}}, {t0 + 0.15:.3f});'
            )
            js.append(
                f'tl.fromTo("#{ev}-q{i}", {{strokeDashoffset: 900}}, {{strokeDashoffset: 0, duration: {max(0.6, tf - ti):.2f}, ease: "power1.in"}}, {ti:.3f});'
            )
            # rótulo: a 1ª linha leva acima da curva; as outras, abaixo do fim da linha
            if i == 0:
                pos = f"left:{90 + xl + 300:.0f}px;top:{420 + y0 - 150:.0f}px"
            else:
                pos = f"right:80px;text-align:right;top:{420 + y1 + 30:.0f}px"
            rotulos.append(
                f'<div class="cena-rotulo" id="{ev}-l{i}" style="{pos};color:{cor};font-size:{int(ln.get("tam", 60))}px">'
                f"{esc(ln['rotulo'])}</div>"
            )
            js.append(
                _entra(f"#{ev}-l{i}", ti + 0.1, "opacity: 0, y: 18", "opacity: 1, y: 0", 0.5)
            )
            sons.append((ti, "cena_item"))
        for i, (x, idade) in enumerate(zip(xs, idades)):
            peso = 600 if i == marco else 400
            rotulos.append(
                f'<div style="position:absolute;left:{90 + x - 60:.0f}px;width:120px;top:{420 + eixo + 24}px;text-align:center;'
                f'font-family:Inter;font-weight:{peso};font-size:34px;color:{c["texto"]};opacity:.75">{esc(idade)}</div>'
            )
        if e.get("rotulo_marco"):
            rotulos.append(
                f'<div class="cena-rotulo" id="{ev}-lm" style="left:{90 + xm - 200:.0f}px;width:400px;top:{420 + eixo + 80}px;'
                f'text-align:center;color:{c["texto"]};font-size:52px">{esc(e["rotulo_marco"])}</div>'
            )
        svg.append("</svg>")
        html_.append("".join(svg) + "".join(rotulos))
        js.append(
            _entra(f"#{ev}-m", tm - 0.1, "opacity: 0", "opacity: 1", 0.4, "power2.out")
        )
        if e.get("rotulo_marco"):
            js.append(
                _entra(f"#{ev}-lm", tm, "opacity: 0, y: 16", "opacity: 1, y: 0", 0.5)
            )
        sons.append((tm, "cena_item"))

    elif modelo == "rede":
        html_.append(_rede(ev, e, t0, t1, c, js, sons))

    elif modelo == "busca":
        html_.append(_busca(ev, e, t0, t1, c, js, sons))

    elif modelo == "versus":
        html_.append(_versus(ev, e, t0, c, js, sons))

    elif modelo == "troca":
        html_.append(_troca(ev, e, t0, c, js, sons))

    else:
        raise ValueError(f"modelo de cena desconhecido: {modelo}")

    return "".join(html_), js, sons


def _nos_rede(n: int = 24, semente: int = 11) -> list[tuple[float, float]]:
    """Pontos fixos (determinísticos) dentro de dois "lobos", no viewBox 900×700."""
    x = semente
    pts: list[tuple[float, float]] = []
    while len(pts) < n:
        x = (x * 1103515245 + 12345) % 2**31
        px = 60 + (x % 7800) / 10
        x = (x * 1103515245 + 12345) % 2**31
        py = 60 + (x % 5800) / 10
        dentro = any(
            ((px - cx) / 300) ** 2 + ((py - 330) / 270) ** 2 <= 1 for cx in (300, 600)
        )
        if dentro and all((px - a) ** 2 + (py - b) ** 2 > 105**2 for a, b in pts):
            pts.append((px, py))
    return pts


def _rede(ev: str, e: dict, t0: float, t1: float, c: dict, js: list[str], sons: list) -> str:
    """Rede de neurônios: as ligações se desenham da esquerda para a direita e,
    em `t`, uma onda de luz atravessa os neurônios (repete se houver tempo)."""
    pts = _nos_rede()
    arestas: set[tuple[int, int]] = set()
    for i, (x, y) in enumerate(pts):
        perto = sorted(
            range(len(pts)), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2
        )
        for j in perto[1:3]:
            arestas.add((min(i, j), max(i, j)))
    arestas_ord = sorted(arestas, key=lambda a: pts[a[0]][0] + pts[a[1]][0])
    partes = ['<svg class="cena-svg" viewBox="0 0 900 700">']
    inicio_no = {}
    for k, (i, j) in enumerate(arestas_ord):
        (x1, y1), (x2, y2) = pts[i], pts[j]
        comp = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        ta = t0 + 0.15 + 1.1 * k / max(1, len(arestas_ord))
        partes.append(
            f'<line id="{ev}-a{k}" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="{c["texto"]}" stroke-opacity=".35" stroke-width="3" '
            f'stroke-dasharray="{comp:.0f}" stroke-dashoffset="{comp:.0f}"/>'
        )
        js.append(
            f'tl.fromTo("#{ev}-a{k}", {{strokeDashoffset: {comp:.0f}}}, {{strokeDashoffset: 0, duration: 0.5, ease: "power2.out"}}, {ta:.3f});'
        )
        for n in (i, j):
            inicio_no[n] = min(inicio_no.get(n, ta), ta)
    for n, (x, y) in enumerate(pts):
        partes.append(
            f'<circle id="{ev}-n{n}" cx="{x:.0f}" cy="{y:.0f}" r="13" fill="{c["destaque"]}"/>'
        )
        js.append(
            f'tl.fromTo("#{ev}-n{n}", {{opacity: 0, scale: 0, transformOrigin: "50% 50%"}}, '
            f'{{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)"}}, {inicio_no.get(n, t0 + 0.2):.3f});'
        )
    partes.append("</svg>")
    # onda de luz: cada neurônio acende quando a frente da onda passa por ele
    tp = float(e.get("t", t0 + 1.3))
    ondas = [tp] + ([tp + 1.1] if tp + 1.1 + 0.9 < t1 - 0.3 else [])
    for ti in ondas:
        for n, (x, _) in enumerate(pts):
            tn = ti + 0.6 * x / 900
            js.append(
                f'tl.to("#{ev}-n{n}", {{keyframes: [{{scale: 1.9, fill: "{c["texto"]}", duration: 0.12}}, '
                f'{{scale: 1, fill: "{c["destaque"]}", duration: 0.35}}], ease: "power2.out"}}, {tn:.3f});'
            )
        sons.append((ti, "cena_item"))
    if e.get("rotulo"):
        partes.append(f'<div class="cena-rede-rot" id="{ev}-r">{esc(e["rotulo"])}</div>')
        js.append(_entra(f"#{ev}-r", tp + 0.2, "opacity: 0, y: 20", "opacity: 1, y: 0", 0.5))
    return "".join(partes)
