# Diário — "Bolsonaro mandou matar Lula" (videos/bolsonaro-lula)

**Pedido:** "Edite esse vídeo de uma forma extremamente viral. Coloque efeitos sonoros." Na frase "Bolsonaro mandou matar Lula", efeito sonoro e ênfase (texto); no "pesquisa/digita", uma aba do Google mostrando a pessoa pesquisando; editar os cortes; melhorar qualidade, filtro e iluminação.
**Plano aprovado** ("Sim") sem prints ou vídeos próprios.
**Cuidado combinado no plano:** a busca mostra só a barra e a frase; os resultados são barras cinzas com etiquetas ACUSAÇÃO / DEFESA / SUA CONCLUSÃO. Nada de manchetes ou jornais reais inventados, e nada de fotos/vídeos do Bolsonaro e do Lula baixados por conta própria (só se o usuário mandar). O vídeo é neutro ("não vou dizer quem está certo") e a edição também: a frase leva "?".
**Cortes:** fala limpa numa tomada; saíram 1,6 s do começo e 9 pausas de 0,2–0,5 s. A vírgula de 0,26 s depois de "ex-presidente" ficou (corte < 0,1 s dá pulo). "Existe" começa em 1,65 s no áudio (o Whisper dizia 1,30). Transcrição do cortado: 89 palavras, nenhuma comida.
**Cor:** comparei 2 versões lado a lado num quadro; ficou a com parede cinza-azulada e pele quente (teal/laranja leve) + vinheta.
**Clipes (Pixabay):** 149843 bandeira (gancho, `desfoque --forca 0.6` e rachadura em ffmpeg), 112718 bandeira no mastro, 7315 sirene azul, 254922 martelo (as 3 em faixas 1000×340 com `tv`). Ex-presidente sem imagem boa no banco ("podium", "press conference", "brasilia" fracos): a bandeira no mastro representa o governo.
**Peças novas no modelo:** `trio`, `impacto`, `trilha` (troca de humor sem véu), `sons_extra`, cenas `busca`, `versus`, `troca` (com `sobre_camera`), sons `tecla`, `enter`, `glitch`, `rachadura`.
**Bug achado nas fotos:** `tl.fromTo` com estado inicial visível (borda vermelha, tecla apertada) aparecia antes da hora (o GSAP aplica o "from" na criação). Troquei por `tl.set` + `tl.to`.
**Entrega:** -14,0 LUFS, pico -1,5 dBTP, 28,07 s, 26,7 MB. O boom fica ~4 dB acima da fala por 0,4 s.
**Pendente:** retorno do usuário sobre o volume dos efeitos (teclado, boom) e da trilha.
