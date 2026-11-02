## Sessão 1 — 2026-10-29

**Pedido:** "só os cortes, tirar o silêncio… e colocar a legenda" — sem imagem nem efeito. Vídeo "balança x cintura" (link do Drive), 1080×1920 HEVC 30 fps, 41,3 s, no carro.
**Cortes:** fala numa tomada, sem repetição. Mapa do áudio em quadros de 20 ms; 13 pausas com respiração cortadas (fala < -42 dB, respiração -32 a -40 dB), bordas em quadros de 30 fps com 40 ms de folga. A de "cintura. | Ela" ficou (tiraria só 0,1 s); o estalo de boca antes de "a balança" (35,24) ficou de fora. Começo: 0,13 s de silêncio cortados. O ajustar_cortes.py (limiar -44,5 dB) queria devolver as respirações: ignorado. 41,3 → 37,5 s.
**Sincronia:** 0 ms em todos os 14 trechos (render.py corrigido na sessão anterior).
**Legenda:** `legenda.py mapear` (novo) levou as palavras da transcrição da fonte para o tempo do cortado. Modelo médio usado para conferir o texto: "Perdeu **o** que deixa" (o small pulou o "o"), "emagrecendo/emagreceu" (small: "emagricendo"), "salve". Espaço entre palavras agora proporcional à maior palavra do bloco: em "emagrecendo" a palavra ativa encostava na vizinha.
**Entrega:** -14,2 LUFS, pico -1,2 dBTP, 27,1 MB, 1080×1920.
**Pendente:** retorno do usuário.
