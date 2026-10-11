# Projeto: treino de força depois dos 45 (vídeo novo)

## Sessão 1 — 2026-10-11

**Estratégia:** cortar só as pausas (fala já limpa, sem repetições) e aplicar o modelo Sálvia com legenda em destaque, ~1/3 do vídeo coberto por cenas e vídeos de banco (Pixabay), voz de rádio (P&B + voz abafada) em 2 trechos e trilha em 3 climas (calma → tensa → inspira).

**Decisões:**
- Cortes: 23 trechos a partir do silêncio real (silencedetect -35 dB), bordas ajustadas com `ajustar_cortes.py`, intervalos < 0,1 s unidos (evita pulo de imagem sem ganho). 57,0 s → 52,3 s + 1,8 s de quadro congelado = 54,1 s.
- Conferência: transcrição do cortado igual à da fonte; "O motivo é" virou "Motiva" só por leitura do Whisper (medido: fala começa em 16,80, corte em 16,75).
- Transcrição corrigida: hidroginástica, alongamento, "O motivo é", "densidade óssea" (sem o "de"), "uma escada", "por que".
- Voz de rádio = mesmo efeito do vídeo anterior (`pb` com voz abafada): 10,72–12,98 (objeção: medo / "não é pra minha idade", com legenda em areia) e 38,68–40,98 ("não é estética, não é aparência"); a cor volta em "autonomia" (vivo 2).
- Vivos: "treino de força" (coral) sobre o vídeo de treino; "autonomia" (verde-lima).
- Cena nova `queda` (cenas.py): músculo e densidade óssea retos até os 40 e caindo no tempo da fala.
- B-roll (Pixabay, licença livre): academia 169590 (dividida), esqueleto 84708 (dividida, câmera lenta 0,7× com pan), mala 5628 (cheia), gelo 381755 (dividida), joelho 4364 (cheia, base escurecida p/ legenda), treino 148204 (cheia), avó e neta 265617 (cheia, quadro inteiro sobre fundo desfocado).
- Trilha: transições com `"humor"` abrem seção nova (15,86 tensa; 35,26 inspira).

**Medidas:** -14,1 LUFS, pico -1,4 dBTP; fala ≈ -14 dB RMS; voz de rádio com agudos 3–5 dB abaixo; tela final (só trilha) ≈ -30 dB RMS, ~16 dB abaixo da fala (fim em fade). Entrega 27,1 MB, 1080×1920, 54,1 s.

**Raciocínio:**
- Tentei pôr o acorde final no fim da fala (escurecer_em): abriu um buraco de silêncio em 52,75 s; voltei ao acorde no início do CTA.
- Ícones da lista: Fraunces não tem ✓/setas → Inter como fonte reserva no `.ico`.

**Pendente:** retorno do usuário sobre volume da trilha e dos efeitos (`"trilha": {"volume_db"}`, `"efeitos_volume_db"`).

## Sessão 1, rodada 2 — 2026-10-11

**Retorno do usuário:** (1) começar com tela dividida e um vídeo de gatilho forte; (2) "voz de rádio ou celular" é o efeito do vídeo sério (primeira-hora-serio-v10), bem perceptível — o abafado suave não se notou; (3) não gostou do título Sálvia (caixa alta espaçada + Fraunces itálico) — já tinha recusado no vídeo sério (registro estava num branch não mesclado); (4) gosta do estilo de @elias.maman: tela dividida + "formato menor" (cartão no meio, fundo preto).
**Decisões:**
- Identidade `salvia-forte` (trazida do branch claude/salvia-forte-rede), legenda dourada `#F2C94C`.
- Gancho 0–2,4 s: tela dividida com mulher no espelho preocupada com rugas (Pixabay 293081); 2,44–4,18 cartão com retrato de senhora (319064).
- Mala e avó viraram cartão (formato menor); títulos só nos 2 momentos vivos, em Inter Black.
- Voz de rádio medida no v10: P&B ≈ graves/médios -28 dB, agudos/médios -20 dB (normal -8/-12). Filtro novo `radio` no mixar.py: 400–3000 Hz, tanh 0,8, aplicado a voz+trilha; resultado -27/-24 dB, mesmo RMS.
- `hf/assets/cortado.mp4` recodificado com quadro-chave a cada 1 s (aviso de "sparse keyframes").
**Medidas v2:** -14,1 LUFS, pico -1,1 dBTP, 54,1 s, 27,1 MB.
**Pendente:** usuário escolher se quer a legenda pequena com serifa do @elias.maman; volume da trilha/efeitos.

## Sessão 1, rodada 3 — 2026-10-11

**Retorno do usuário:** "ele distorce as imagens, deve ser algum filtro" (prints do @elias.maman).
**Análise (quadros em tamanho real da referência):** cartões = TV de tubo (abaulado, grade de pontos de ~3 px em 720p, vinheta, grão); dividida/cheia = borrão de zoom radial nas bordas com centro nítido; emenda da dividida esfumada.
**Feito:** `ferramentas/filtro_clipe.py` (`tv`: lenscorrection k1 0,16 + grade de pontos 5 px multiplicada em RGB + vinheta + grão; `lente`: média de 4 cópias ampliadas 1,00–1,12 mesclada por máscara radial + vinheta + grão; `--brilho`). Aplicado aos 9 clipes (`*_fx.mp4`); mala com `--brilho 1.7`. Emenda da `dividida` com mask-image de 190 px.
**Erros evitados:** blend multiply em YUV deixava tudo verde (forçar gbrp); `-loop 1` sem `-t` gerava arquivo infinito.
**Medidas v3:** -14,1 LUFS, pico -1,1 dBTP, 54,1 s, 27,1 MB.

## Sessão 1, rodada 4 — 2026-10-11

**Retorno do usuário:** print de outro vídeo do @elias.maman (Beckham no topo da tela dividida): "veja que filtro é esse e faça pra mim".
**Medido no print:** clipe de cima ~6× menos nítido que o rosto do apresentador, luminância média 43/255, RGB médio (60, 37, 32) → suave, escuro e avermelhado. Só há o quadro parado: pode ser também o instante de uma transição.
**Feito:** estilo `desfoque` no filtro_clipe.py (reduz para ~1/7 da largura + desfoque + amplia, gamma 0,66, colorbalance para o vermelho, vinheta, grão). Aplicado com `--forca 1.2` aos 4 clipes da tela dividida (lum 49, RGB 65/46/36). Cartões seguem `tv`, tela cheia segue `lente`.
**Observação:** o vídeo do usuário é de dia e claro; no print os dois lados são escuros. Se ele quiser, escurecer/aquecer a câmera durante a tela dividida.
**Medidas v4:** -14,1 LUFS, pico -1,1 dBTP, 54,1 s, 27,1 MB.

## Sessão 1, rodada 5 — 2026-10-11

**Pedidos:** efeitos sonoros nas transições como @elias.maman (2 trechos .mov enviados) e o @ mudando de lugar com animação (ícone branco → @ → ícone colorido).
**Análise do som:** os tons de ~3,8 e ~5,9 kHz aparecem no vídeo todo (música de fundo, 72 vezes), não são do corte. Nas entradas de cartão: tic metálico curto (parciais ~3/5/8,5/11 kHz, ~50 ms) logo antes do corte + linha fraca subindo (~4,5→6 kHz, ~0,6 s) depois. Média nos 27 cortes: +6–8 dB em médios/agudos de 0 a +0,3 s, sem grave.
**Feito:** `corte_ref`/`corte_ref_saida` em efeitos.py (sintetizados), ligados a dividida, broll, cena, inserto e janela na salvia-forte; saída da dividida com som. Efeito isolado ≈ -21 dB vs mixagem.
**Descoberto:** o @ só aparecia 1 vez no vídeo (as zonas de clipe escondiam tudo). Agora clipes não bloqueiam; intervalo 4 s; não repete posição; animação em 3 tempos.
**Incidente:** o comando de desfoque nos cartões, interrompido pelo usuário, chegou a sobrescrever senhora_fx e corromper mala_cartao_fx; refeitos com `tv` (v4 entregue não foi afetada).
**Medidas v5:** -14,1 LUFS, pico -1,2 dBTP, 54,1 s, 27,1 MB.
