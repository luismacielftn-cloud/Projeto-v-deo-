# Projeto: força das pernas ("Me dê 60 segundos")

## Sessão 1 — 2026-10-11

**Pedido:** "Edite esse vídeo no mesmo formato que esse que editamos agora" (o treino de força).
**Fonte:** 1440×2560 HEVC, 103,4 s, estúdio com luz azul, rosto no alto do quadro (y ≈ 210–900 em 1080×1920). O usuário já tinha juntado as gravações: cortes dele em 19,7 / 23,7 / 49,1 / 51,7 / 59,8 / 80,0 / 85,7 / 92,3 s, todos limpos.
**Cortes:** só pausas (37 pausas, 7,5 s). 20 trechos depois de juntar os intervalos < 0,1 s → 100,8 s + 1,8 s congelado = 102,6 s.
**Frase confirmada pelo usuário (1min23s):** "ou nunca associou isso à falta de exercício de força" (o Whisper ouviu "nunca só se ouíso"). O "força. força," do Whisper small era uma palavra só (medido: um único pico de som).
**Transcrição corrigida:** sarcopenia, dor no joelho, 15%/40%, da força, que vem, estar, reduz, pontuação.
**Clipes (Pixabay):** gancho 229071 (perna na cadeira de rodas; desfoque com --brilho 1.5 e recorte mais à esquerda, senão fica só calça escura), pernas 3171, cadeira 215081 (silhueta com bengala, trecho ao contrário e 2× mais rápido = "levantando"), escada 152203, sarcopenia 118021, pernas em raio-X 57691, aula 32937, sofá 298667, casal 365401, joelho 4364, esqueleto com halteres 302441.
**Layout:** rosto alto → tela dividida com `"descer": 820` (com 445 a legenda da emenda cai no cabelo).
**Código novo:** cena `numero` aceita `tam` ("10–15%" não cabia em 300 px); cena `queda` aceita `marco` por linha (força cai aos 40, massa muscular aos 60).
**Vivos:** "25–40%" (coral, título), "reversíveis" (verde-lima, título), "exercício de força" (coral, na frase).

## Rodada 2 — 2026-10-11

**Retorno do usuário:** a imagem em "é o que os estudos sobre sarcopenia mostram" (raio-X de corpo musculoso) não condiz; precisa mostrar perda de músculo.
**Feito:** `ferramentas/secao_musculo.py`: ilustração animada da coxa em corte, 30 × 70 anos; o corte de 70 anos envelhece em 0,5–1,4 s (músculo encolhe, gordura engrossa e entra no músculo), caindo no "sarcopenia" (35,6 s). Cartão com `tv --brilho 1.2`, 34,62–36,7 s. Script de clipes atualizado.
**Medidas v2:** -14,0 LUFS, pico -1,2 dBTP, 102,6 s, 27,1 MB.

**Retorno do usuário (2):** mandou um post de @rafaelladellasanta (coxa crua em corte, "sem/com treinamento de força") e pediu a imagem "mais próxima do real".
**Feito:** duas fotos realistas geradas no Canva do usuário (coxa saudável e coxa com sarcopenia), guardadas em `modelos/estilo-referencia/assets/sarcopenia/`. O Canva só deixa baixar a prévia de 200 px; o `secao_musculo.py` amplia com lanczos + realce, recorta em círculo e mistura a de 70 anos de saudável → sarcopenia em 0,5–1,4 s. O filtro `tv` esconde a ampliação. Entregue como `forca-das-pernas-v3.mp4`.

**Retorno do usuário (3):** no "esse movimento simples… para treinar a força da perna" (65,25 s) estava a aula de idosos com os braços para cima: "sem sentido"; o ideal seria alguém sentando e levantando, fazendo exercício.
**Feito:** busca funda no Pixabay (1.682 clipes) e no Mixkit: não há pessoa madura sentando/levantando da cadeira como exercício (o senhor do Mixkit 12866 levanta com dor nas costas, de pijama: contradiz). O Pexels tem, mas bloqueia o acesso daqui. O usuário escolheu "o mais parecido": homem agachando em casa (Mixkit 21273, 720p), trecho que desce, segura e sobe, 1,4× mais rápido, na tela dividida com `desfoque` (o cartão seguinte é o sofá). Entregue como `forca-das-pernas-v4.mp4`.

**Retorno do usuário (4):** gostou do som de entrada das imagens, mas não do de saída ("muita entrada e saída no vídeo todo"); pediu também para tirar a batida aguda antes da entrada ("o sino") e deixar só o swoosh.
**Feito:** `corte_ref` sem o tic metálico, só o swoosh (ganho -32 dB = mesmo nível de antes); `cena_saida`, `dividida_saida` e `broll_saida` vazios na Sálvia forte. Só o som mudou (mesmo `com_animacoes.mp4`). A cópia de entrega passou a copiar o áudio: recomprimir criava um pico de +2,6 dB. Entregue como `forca-das-pernas-v5.mp4` (-14 LUFS, pico -1,4 dB).
