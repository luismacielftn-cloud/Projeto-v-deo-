# Vídeo "o infarto odeia quem para de fazer essas duas coisas"

Edição de 2026-10-23, sétimo vídeo, modelo padrão com o @. Gravado em casa (1080×1920 HEVC, 37,1 s), **camiseta branca** e parede amarelada; rosto no meio-alto do quadro (cabelo em y≈460, queixo em y≈1200).
O vídeo não fica no git: se precisar refazer, peça o link do Drive ao usuário.

| Arquivo | O que é |
| --- | --- |
| `edl.json` | Cortes (14 trechos, 37,1 s → 34,3 s + 1,5 s congelados = 36,1 s), com um `grade` **menos amarelo** (balanço para o frio) e mais contraste. |
| `transcript.json` | Transcrição do vídeo cortado ("salva" → "salve", "cardio respiratória" → "cardiorrespiratória"). |
| `roteiro.json` | Roteiro entregue (usa `base_escura`, `trio`, capítulos 01/02 e `trilha`). |
| `preparar_clipes.sh` | Mixkit 33767 + Pixabay 3171, 152203, 32937, 139472, 57691. |
| `project.md` | Diário. |

## Refazer

1. `helpers/render.py retomar/infarto-duas-coisas/edl.json -o videos/v7/edit/cortado_base.mp4` → congelar 1,5 s → `cortado.mp4`.
2. `transcript.json` e `roteiro.json` em `videos/v7/edit/hf/`; `cortado.mp4` em `hf/assets/` com `-g 30`.
3. `bash retomar/infarto-duas-coisas/preparar_clipes.sh videos/v7/edit/clipes_brutos videos/v7/edit/hf/assets`
4. `montar.py` → `lint` → `render` → `finalizar.py --mix … --entrega …`.

## O que este vídeo ensinou

- **Camiseta branca sob a legenda:** `"base_escura": {"y": 1150, "opacidade": 0.55}` no roteiro põe uma sombra suave na parte de baixo da câmera; legenda, capítulos, lista e título ficam legíveis sobre a roupa clara.
- **Tela dividida com rosto no meio-alto:** com o `descer` padrão (445) a legenda da emenda caía no cabelo; `"descer": 560` resolveu.
- **Respiros que o `ajustar_cortes.py` não pega:** ele só achou ~2 s de silêncio (respirações acima do limiar). Medindo o áudio a -42 dB, cinco respiros de 0,24–0,42 s dentro dos trechos foram encurtados para 0,12 s.
- **`capitulo` sem `humor` muda a trilha sozinho** (volta para o humor seguinte da lista, aqui "calma"). Dê o `humor` no próprio capítulo; use o evento `trilha` para voltar ao "inspira" no fechamento.
- **Cigarro na tela dividida:** com `desfoque --forca 1.2` o cigarro some; ficou `--forca 0.35 --brilho 1.3`.

## Linha do tempo

| Tempo | Fala | Na tela |
| --- | --- | --- |
| 0–2,9 | "O infarto odeia quem para de fazer essas duas coisas" | Gancho: tela dividida, senhora com a mão no peito em dor (Mixkit 33767) |
| 3,1–5,8 | "o infarto é a doença que mais mata" | Cena `numero` **nº1** / "causa de morte no mundo" / "doenças do coração · OMS" |
| 5,8–7,9 | "salve esse vídeo" | Zoom seco |
| 8,1–10,6 | "A primeira é aumentar o seu tempo de atividade física" | Capítulo **01 · atividade física** (trilha → inspira) |
| 12,4–16,2 | "caminhar mais, subir escadas, se movimentar durante o dia. Tudo isso conta" | `trio` com ✓: pernas caminhando, homem subindo a escadaria, aula de idosos |
| 17,7–22,8 | "pressão arterial, capacidade cardiorrespiratória, saúde metabólica" | Cena `barras`: pressão ↓, fôlego ↑, metabolismo ↑ |
| 23,0–24,9 | "E a segunda coisa é parar de fumar" | Transição + capítulo **02 · parar de fumar** (coral; trilha → tensa) |
| 25,0–27,0 | "O cigarro agrede os vasos sanguíneos" | Tela dividida: homem fumando → cartão: vasos sanguíneos acesos no corpo |
| 27,0–29,4 | "aumenta muito o risco de doenças cardiovasculares" | Cena `numero` **2 a 4×** "mais risco de doença do coração em quem fuma · CDC" |
| 29,6–31,1 | "Duas mudanças simples" | Lista ✓ se mexer mais / ✓ parar de fumar (trilha → inspira) |
| 32,1–34,5 | "uma diferença enorme na saúde do seu coração" | Título **diferença enorme** (lima) |
| 34,6–36,1 | — | Final "salva e manda pra / quem você ama" + @ |
