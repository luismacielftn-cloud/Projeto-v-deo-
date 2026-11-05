## Sessão 1 — 2026-10-26

**Pedido:** "edite só os cortes e coloque a legenda" — sem animação, efeito sonoro, trilha nem @. Vídeo "5 hábitos de Harvard" (link do Drive), 1440×2560 HEVC 24 fps, 43,5 s, no carro.
**Estratégia:** pedido já veio fechado (cortes + legenda), então fui direto sem plano. Fala limpa numa tomada, sem repetição nem hesitação: só saíram pausas.
**Cortes:** o ajustar_cortes.py estimou limiar -33 dB e queria devolver respirações (fim em 26,44) e cortar o "s" do "se mexer" (28,68); medi o áudio em quadros de 20 ms e marquei à mão as 13 pausas com respiração (fala termina < -42 dB, respiração entre -32 e -40 dB). Bordas em quadros inteiros de 24 fps, fim ≥ fala + 40 ms, início ≤ fala − 40 ms. Pausas de vírgula de ~0,2 s sem respiração ficaram. 43,5 → 40,6 s.
**Sincronia:** o render.py atrasava o áudio a cada trecho (+21 ms no 1º, +170 ms no 14º): vídeo arredondado em quadros, áudio não, e o AAC de cada trecho somava ~21 ms de "priming". Corrigido no render.py (duração em quadros inteiros + PCM nos trechos, AAC uma vez na emenda): 0 ms em todos os trechos.
**Legenda:** ferramentas/legenda.py (nova): estilo destaque do modelo (Inter Black 66 px, dourado #F2C94C, palavra ativa 12 % maior numa camada de cima), centro em y 1480 (queixo em ~1365). Tempos das palavras: transcrição da fonte levada pelo EDL (a do cortado errava até 0,3 s logo depois dos cortes). Correções: 5 / 10 em número, "pra" (médio ouviu "pra"; small escreveu "para a"), "treinamento de força" (small: "e força"), "segunda-feira", pontuação.
**Entrega:** -14,1 LUFS, pico -1,2 dBTP (limitador 4x no legenda.py; o AAC dava -0,8), 27,0 MB, 1080×1920.
**Pendente:** retorno do usuário.
