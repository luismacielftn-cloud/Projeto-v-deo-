# Vídeo "o melhor remédio para passar dos 60, 70 anos" (estudo dos idosos de 90 anos)

Edição de 2026-10-22, sexto vídeo, de volta ao tema saúde e ao modelo padrão (com o @). Gravado no carro (1440×2560 HEVC, 54,3 s), rosto no meio do quadro: `layout` do primeiro vídeo, `fim_ig_y` 380 (o @ da tela final acima da cabeça).
O usuário mandou junto **o print do estudo** (Fiatarone et al., JAMA 1990, 1290×390) e pediu: "eu falo do estudo dos idosos de 90 anos, aí você coloca essa foto".
O vídeo e o print não ficam no git: se precisar refazer, peça os dois de novo.

| Arquivo | O que é |
| --- | --- |
| `edl.json` | Cortes (18 trechos, 54,3 s → 51,2 s + 1,5 s congelados = 52,7 s), com o mesmo `grade` do `retomar/bolsonaro-lula/` (só `brightness` 0 para o rosto). |
| `transcript.json` | Transcrição do vídeo cortado ("é vende" → "te vende", "emagrecadora", "em velecer" → "envelhecer", "força" duplicado apagado). |
| `roteiro.json` | Roteiro entregue. |
| `preparar_clipes.sh` | Clipes (Pixabay + Mixkit 12866, 21273 e 4506), coxa em corte e o **cartão do estudo** com marca-texto e tradução (3º argumento: o print). |
| `project.md` | Diário. |

## Refazer

1. `helpers/render.py retomar/estudo-90-anos/edl.json -o videos/estudo-90-anos/edit/cortado_base.mp4` → congelar 1,5 s (`tpad`/`apad`) → `cortado.mp4`.
2. `transcript.json` e `roteiro.json` em `videos/estudo-90-anos/edit/hf/`; `cortado.mp4` em `hf/assets/` com `-g 30`.
3. `bash retomar/estudo-90-anos/preparar_clipes.sh videos/estudo-90-anos/edit/clipes_brutos videos/estudo-90-anos/edit/hf/assets videos/estudo-90-anos/estudo.jpg`
4. `montar.py` → `lint` → `render` → `finalizar.py --mix … --entrega …`.

## Cartão do estudo (o pedido principal)

- **Onde:** `janela` `topo-centro`, `largura` 0.92, `proporcao` 0.4105, `topo` 110: fica no teto do carro, **acima da cabeça**, de "No estudo" (37,6 s) até o fim do número (42,9 s). O rosto continua na tela.
- **O que tem:** o print do usuário + uma faixa escura com a tradução em Inter ("Treino de força intenso em idosos de 90 anos" / "Fiatarone et al. · JAMA, 1990" em dourado). Sem filtro TV: o texto precisa ser lido.
- **Marca-texto:** faixa dourada que desliza sobre "nonagenarians" (x 52–548, y 140–198 do print) **na palavra "90"** (1,22 s depois do cartão entrar), com `pop_suave`. Feito em ffmpeg com `blend=multiply` em `gbrp`; o `drawbox` não anima a largura, então a faixa entra deslizando sob uma máscara branca.
- **Número:** `titulo` `vivo: 2` "quase / **3× mais força** / +174% em 8 semanas" no "triplicaram" (o estudo mediu +174%), com o cartão ainda no alto.

## Linha do tempo

| Tempo | Fala | Na tela |
| --- | --- | --- |
| 0–2,8 | "melhor remédio pra você passar dos 60…" | Gancho: tela dividida, cuidadora segurando a perna de uma senhora na cadeira de rodas (Pixabay 229071, já aprovado) |
| 3,6–5,0 | "sem depender de ninguém" | Zoom seco |
| 5,0–6,4 | "nenhuma farmácia te vende" | Cartão TV: cápsulas (Pixabay 5448) |
| 6,5–10,6 | "não é suplemento, creatina, colágeno, caneta emagrecedora" | Lista "não é" com × na palavra + zoom seco |
| 10,7–15,1 | "Salva esse vídeo… corpo jovem…" | Dois zooms secos |
| 15,1–16,9 | "A partir dos 30" | Transição (trilha → tensa) + cena `numero` "30 anos / o músculo começa a ir embora" |
| 16,9–19,3 | "perder músculo todo ano" | Cartão: coxa em corte realista 30 × 70 anos |
| 22,0–24,6 | "precisar de ajuda pra levantar da cadeira" | Tela dividida: senhor levantando da poltrona com dificuldade (Mixkit 12866) |
| 24,7–27,3 | "O remédio tem nome, treino de força" | Transição (→ inspira), zoom, cartão TV de um homem treinando com kettlebell (Mixkit 4506; o peso sobe no "força") + título **treino de força** (coral). O esqueleto com halteres da 1ª versão foi recusado. |
| 28,7–33,0 | "músculo trabalha… açúcar e inflamação" | Cena `barras`: músculo ↑, açúcar ↓, inflamação ↓ |
| 33,0–35,8 | "seu corpo fabricando o próprio remédio" | Cartão TV: agachamento com elástico em casa (Mixkit 21273) |
| 37,6–42,9 | "No estudo com idosos de 90 anos, quase triplicaram…" | **Cartão do estudo** + marca-texto + título "quase 3× mais força" (lima) |
| 43,0–46,6 | "Não existe envelhecer bem sem força" | Cena `frase` sobre a câmera, "força" em coral |
| 48,3–51,2 | "chegando nos 80 com as próprias pernas" | Cartão TV: casal idoso de mãos dadas (Pixabay 365401) |
| 51,2–52,7 | — | Final "manda pra / quem você ama" + @ |

Cobertura por clipes e cenas: ~48%. Trilha calma → tensa → inspira.
