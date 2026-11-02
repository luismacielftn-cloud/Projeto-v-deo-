# Vídeo "Bolsonaro mandou matar Lula" (pesquise antes de opinar)

Edição de 2026-10-20, quinto vídeo e o primeiro fora do tema saúde. Pedido do usuário: "extremamente viral", com efeitos sonoros, ênfase forte na frase "Bolsonaro mandou matar Lula", uma aba do Google mostrando a pessoa pesquisando, e melhora de cor/luz.
Vídeo de 30,7 s, 1440×2560 HEVC, parede branca e camiseta azul-marinho, rosto no meio do quadro (usa o `layout` do primeiro vídeo).
O vídeo em si não fica no git: se precisar refazer, peça o link do Drive ao usuário.

| Arquivo | O que é |
| --- | --- |
| `edl.json` | Cortes (10 trechos, 30,7 s → 27,1 s + 0,7 s congelados = 28,0 s) **com o `grade` de cor** (ver abaixo). Aponta para `videos/bolsonaro-lula/fonte.mp4`. |
| `transcript.json` | Transcrição do vídeo cortado ("nula" → "Lula", "ex -presidente" → "ex- presidente"). |
| `roteiro.json` | Roteiro entregue (usa as peças novas: `trio`, `impacto`, `trilha`, cenas `busca`, `versus` e `troca`, `sons_extra`). |
| `preparar_clipes.sh` | Baixa os 4 clipes do Pixabay e faz o gancho: **abre na foto do usuário** (3º argumento) e corta com clarão para a bandeira que **racha ao meio** (ffmpeg) e as 3 faixas do `trio` (filtro `tv`). |
| `project.md` | Diário. |

## Refazer

1. `helpers/render.py retomar/bolsonaro-lula/edl.json -o videos/bolsonaro-lula/edit/cortado_base.mp4` → congelar 0,7 s (`tpad`/`apad`) → `cortado.mp4`.
2. `transcript.json` e `roteiro.json` em `videos/bolsonaro-lula/edit/hf/`; `cortado.mp4` em `hf/assets/` com `-g 30`.
3. `bash retomar/bolsonaro-lula/preparar_clipes.sh videos/bolsonaro-lula/edit/clipes_brutos videos/bolsonaro-lula/edit/hf/assets videos/bolsonaro-lula/foto_usuario.jpg` (a foto não fica no git: peça de novo ao usuário; 1600×728, duas pessoas lado a lado).
4. `montar.py` → `lint` → `render` → `finalizar.py --mix … --entrega …`.

## Cor e luz (pedido "qualidade, filtro, iluminação")

A parede branca estourava e a imagem era chapada. O `grade` do `edl.json` (aplicado por trecho no `render.py`):
mais contraste, realces comprimidos (a parede vira cinza-azulado), meios-tons quentes (pele), vinheta e nitidez leve.
`eq=contrast=1.12:brightness=-0.02:saturation=1.06,curves=…,colorbalance=…,vignette=angle=PI/4.4,unsharp=5:5:0.5`.
Bom ponto de partida para outros vídeos com parede clara.

## Linha do tempo

| Tempo | Fala | Na tela | Som |
| --- | --- | --- | --- |
| 0,0–0,94 | "Existe uma frase que…" | **Gancho**: tela dividida que **abre na foto que o usuário mandou** (zoom rápido); ele embaixo | `corte_ref` + `riser` começando a subir |
| 0,94–2,3 | "divide o Brasil ao meio" | Clarão e corte para a bandeira, que **racha ao meio** no "meio" (borda irregular, luz vermelha, tremida) | `corte_ref` + `riser` até a rachadura + `rachadura` |
| 2,3–5,1 | "e eu duvido que você tenha coragem de pesquisar" | Dois zooms secos (1,18× e 1,34× no "coragem") | `hit_tenso` no "coragem" |
| 5,1–8,8 | "envolve um ex-presidente, a Polícia Federal e o Supremo" | `trio`: 3 faixas empilhadas (bandeira no mastro, sirene azul, martelo), cada uma entra na sua palavra; o martelo dá um tranco | swoosh em cada + `impacto` no martelo |
| 8,8–10,7 | "Esse vídeo não é para defender ninguém" | P&B + voz de rádio + zoom seco | rádio |
| 10,9–13,9 | "uns juram que é verdade, outros que é mentira" | cena `versus`: VERDADE ✓ (lima) × MENTIRA ✗ (vermelho), o segundo empurra o primeiro | `hit_tenso` em cada |
| 15,4–21,6 | "Abre o Google e digita… Bolsonaro mandou matar Lula. Lê a acusação, lê a defesa e tira sua conclusão" | cena `busca`: celular com a página do Google, a frase **digitada letra a letra no tempo da fala**, teclas acendendo, borda vermelha no "matar", tecla "ir", resultados ACUSAÇÃO / DEFESA / SUA CONCLUSÃO (só barras cinzas, sem manchete inventada) | teclas, `riser` até o "Lula", `enter` |
| 17,9–18,6 | "…Lula" | `impacto`: **BOLSONARO MANDOU MATAR LULA?** gigante, "MATAR" em vermelho, clarão, fundo vermelho-escuro, falha de cor, a tela treme | `boom` + `glitch`; trilha cai para a `batida` |
| 21,6–23,0 | "Manda para quem precisa ver" | zoom seco | |
| 23,0–26,3 | "sua opinião sem pesquisa não é opinião, é torcida" | cena `troca` **sobre a câmera escurecida**: "Opinião / sem pesquisa" → risco coral no "não é opinião" → **torcida** (coral) bate | `glitch` no risco, `impacto` no "torcida" |
| 26,3–28,0 | — | Final "manda para / quem precisa ver" (lima), **sem @** | — |

Trilha: `tensa` → `tensa_pulso` (a busca) → `batida` (depois da frase). Cobertura por clipes e cenas: ~55%.

**Sem @:** depois da 1ª entrega o usuário pediu "não precisa colocar o meu @luismacciel no vídeo". A versão final não tem a marca d'água nem o ícone com o @ na tela final (`"marca": {"ativa": false}`, `"ig": false`).
