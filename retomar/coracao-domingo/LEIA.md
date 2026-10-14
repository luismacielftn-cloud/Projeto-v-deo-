# Vídeo "o exercício mais perigoso para o coração" (atleta de domingo)

Edição de 2026-10-14, terceiro vídeo feito com a receita de `retomar/treino-forca/`. Gravado no carro (selfie, 1080×1920, 46,2 s), rosto no meio do quadro: usa o `layout` do primeiro vídeo, sem `descer`.
O vídeo em si não fica no git: se precisar refazer, peça o link do Drive ao usuário.

| Arquivo | O que é |
| --- | --- |
| `edl.json` | Cortes (8 trechos, 46,2 s → 44,5 s). Fala numa tomada só, sem repetições: só saíram 7 pausas. Aponta para `videos/v3/fonte.mp4`. |
| `transcript.json` | Transcrição do vídeo cortado ("Salva" → "Salve"). |
| `roteiro.json` | Roteiro entregue. |
| `preparar_clipes.sh` | Rebaixa os 5 clipes (todos do Mixkit: o Pixabay não tinha nada bom para sofá, escritório, futebol amador e corrida) e aplica recorte e filtro. |
| `project.md` | Diário. |

## Refazer

1. `render.py edl.json -o videos/v3/edit/cortado_base.mp4` → congelar 1,8 s (`tpad`/`apad`) → `cortado.mp4` (46,5 s).
2. `transcript.json` e `roteiro.json` em `videos/v3/edit/hf/`; `cortado.mp4` em `hf/assets/` com `-g 30`.
3. `bash retomar/coracao-domingo/preparar_clipes.sh videos/v3/edit/hf/assets`
4. `montar.py` → `lint` → `render` → `finalizar.py --mix … --entrega …`.

## Linha do tempo

| Tempo | Fala | Na tela |
| --- | --- | --- |
| 0–2,2 | "O exercício mais perigoso para o seu coração" | Gancho: dividida, homem ofegante de boca aberta |
| 2,2–6,4 | "não é o agachamento, o supino… esteira" | Lista × |
| 6,4–10,4 | "existe um tipo… muito mais preocupante" | Zoom + zoom seco |
| 10,5–13 | "maior parte da semana sem atividade física" | Cartão: homem no sofá com pipoca e controle |
| 13,5–16,1 | "achando que está cuidando da saúde" | P&B + voz de rádio |
| 16,7–19,5 | "a semana inteira parada" | Dividida: homem entediado no escritório |
| 19,5–24,3 | "no domingo… futebol, correr ou exercício intenso" | Trilha tensa · cartão largo: amigos chegando para o futebol · dividida: corredor parando sem fôlego |
| 25,9–28,3 | "é o esforço intenso sem estar preparado" | Título **sem estar preparado** (coral) |
| 28,4–34,1 | "sedentário… não tem o mesmo condicionamento" | Cena `barras` "condicionamento": parado ↓ × ativo ↑ (lima) |
| 34,2–38,6 | "em vez de compensar no domingo… um pouco todos os dias" | Trilha inspira · lista × compensar no domingo / ✓ um pouco todo dia |
| 38,7–41,4 | "Seu coração precisa de constância" | Título **constância** (verde-lima) |
| 41,5–46,5 | "Salve esse vídeo e manda para aquele amigo…" | Final "salve e manda pro / **amigo do domingo**" + @ |

Cobertura por clipes e cenas: ~38%.
