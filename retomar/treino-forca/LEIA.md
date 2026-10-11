# Vídeo "treino de força depois dos 45" — o exemplo mais completo do modelo

Edição de 2026-10-11, aprovada pelo usuário na versão 5. Use como **receita de referência** para os próximos vídeos e para retomar este, se ele pedir ajustes.
O vídeo em si não fica no git: se precisar refazer, peça o link do Drive ao usuário de novo (57,0 s, 1080×1920, ele falando ao ar livre, de dia).

## O que tem aqui

| Arquivo | O que é |
| --- | --- |
| `edl.json` | Cortes do Video Use (23 trechos, 57,0 s → 52,3 s). Aponta para `videos/novo/fonte.mp4`. |
| `transcript.json` | Transcrição do vídeo cortado, já corrigida (só o texto). |
| `roteiro.json` | Roteiro da versão 5 (todos os eventos, layout, @, voz de rádio). |
| `preparar_clipes.sh` | Rebaixa os 9 clipes do Pixabay pelo número e aplica recorte e filtro. |
| `project.md` | Diário da sessão: cada pedido do usuário, o que foi medido e decidido. |

## Como refazer

1. Baixe o vídeo para `videos/novo/fonte.mp4`, copie `edl.json` para `videos/novo/edit/` e rode
   `helpers/render.py videos/novo/edit/edl.json -o videos/novo/edit/cortado_base.mp4`.
2. Congele 1,8 s no fim (`tpad`/`apad`, ver GUIA) → `cortado.mp4` (54,1 s).
3. Copie `transcript.json` e `roteiro.json` para `videos/novo/edit/hf/` e `cortado.mp4` para `hf/assets/` com
   `-g 30` (um quadro-chave por segundo).
4. `bash retomar/treino-forca/preparar_clipes.sh videos/novo/edit/hf/assets`
5. `montar.py` → `lint` → `render` → `finalizar.py --mix … --entrega …` (comandos no CLAUDE.md).

## Como o vídeo foi montado (linha do tempo)

| Tempo | Fala | Na tela | Som |
| --- | --- | --- | --- |
| 0,0–2,4 | "Tem um exercício que se você parar… depois dos 45" | **Gancho**: tela dividida com mulher no espelho preocupada com rugas (desfoque) | `corte_ref` |
| 2,4–4,2 | "seu corpo começa a envelhecer mais rápido" | Cartão (TV) com retrato de senhora | `corte_ref` |
| 4,2–8,6 | "não é caminhada, hidroginástica, alongamento" | Lista com × entrando na palavra + zoom seco | tick |
| 8,7–10,7 | "a maioria das mulheres foge" | Tela dividida: mulher na academia | `corte_ref` |
| 10,7–13,0 | "porque tem medo, ou acha que não é mais pra idade dela" | **P&B + voz de rádio**, legenda em areia | rádio |
| 15,9–21,8 | "O motivo é simples. Depois dos 40… músculo… densidade óssea" | Transição + cena `queda` (linhas caindo depois dos 40) | trilha muda para **tensa** |
| 23,6–26,1 | "seu corpo vai ficando mais frágil" | Tela dividida: esqueleto caminhando em câmera lenta | `corte_ref` |
| 27,3–35,2 | mala / escorrega / joelho | Cartão (mala), dividida (gelo), tela cheia (joelho) | `corte_ref` em cada |
| 35,3–38,6 | "Esse exercício é o treino de força" | Transição + tela cheia de treino + título **treino de força** (coral, vivo 1) | trilha muda para **inspira**, impacto |
| 38,7–41,0 | "não é sobre estética, não é aparência" | **P&B + voz de rádio** | rádio |
| 41,2–42,6 | "é sobre autonomia" | Título **autonomia** (verde-lima, vivo 2), a cor volta | impacto |
| 42,6–48,5 | "daqui a 20 anos… levantar do chão, subir a escada, brincar com seu neto" | Cena número "20 anos" → lista ✓ → cartão com avó e neta | `corte_ref` |
| 49,9–54,1 | "me segue…" | Final "me segue para / mais conteúdo / toda semana" + @ grande | sino |

Cobertura por clipes e cenas: ~40% do vídeo. O @ fica o tempo todo na tela e muda de lugar a cada 4 s.
