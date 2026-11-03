# Vídeo "será que você se identifica com essa cena?" (só cortes + legenda simples + cena de filme)

Edição de 2026-11-02. Pedido: **só cortes e legenda**, com a legenda **toda branca e sem sombra** (sem a palavra ficando amarela) e a **cena do filme** que o usuário mandou no espaço que a gravação deixou para ela. Sem animação, sem trilha, sem efeito sonoro.
Gravação: 1080×1920 HEVC, 60 fps, 100,3 s, pessoa falando para a câmera em casa. Ela fala 4 s ("Será que você se identifica com essa cena do filme Minha Melhor Amiga?"), fica 45,8 s em silêncio total olhando um tablet (o espaço da cena) e volta a falar.
Cena: gravação de tela do filme, 1180×584, 60 fps, 44,8 s, **com diálogo** (é a cena; o som dela fica).
Os vídeos não ficam no git: se precisar refazer, peça os dois links do Drive ao usuário.

| Arquivo | O que é |
| --- | --- |
| `edl.json` | 13 trechos: abertura, **a cena inteira** (fonte `cena`), e a fala com 10 pausas cortadas pelo `pausas.py`. 100,3 s → 95,6 s. |
| `transcript.json` | Palavras no tempo do cortado (`legenda.py mapear`), texto conferido com o modelo `medium`. A cena não tem legenda. |
| `gancho_texto.py` | Gancho escrito da abertura: caixa branca de cantos arredondados com texto preto em Inter Black 50 px. |
| `project.md` | Diário. |

## Refazer

```bash
python3 ferramentas/pausas.py videos/v8/fonte.mp4            # tira também o espaço da cena
# cena na vertical: largura toda, faixas pretas, 60 fps, som +2,6 dB (mesmo volume da fala)
ffmpeg -i videos/v8/cena.mov -vf "scale=1080:-2:flags=lanczos,pad=1080:1920:0:(oh-ih)/2:black,fps=60,setsar=1" \
  -af "volume=2.6dB,aresample=192000,alimiter=limit=0.89:level=false,aresample=48000" \
  -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac -b:a 256k videos/v8/cena_vertical.mp4
# no edl.json: fonte "cena" e o trecho {"source": "cena", "start": 0, "end": 44.8} logo depois da abertura
echo '{"words": []}' > videos/v8/edit/transcripts/cena.json   # a cena fica sem legenda
python3 .claude/skills/video-use/helpers/render.py videos/v8/edit/edl.json -o videos/v8/edit/cortado.mp4
# abertura em tela dividida (até a cena começar, 3,6 s): o trecho mais animado da cena rolando SEM SOM
# em cima (1,6–5,2 s do filme: a atriz em close, rindo e gesticulando; o plano aberto acaba em 1,37 s),
# na largura toda (1080×534, sem cortar ninguém), a câmera descida 250 px embaixo e o gancho escrito
# na emenda (y 450–624: sobre o pé da cena, acima da cabeça, que fica em y≈630)
python3 retomar/cena-filme-incontinencia/gancho_texto.py modelos/estilo-referencia/assets/Inter-Black.otf \
  videos/v8/edit/capa/gancho.png "Muitas mulheres escondem isso" "por anos achando que é normal."
ffmpeg -i videos/v8/edit/cortado.mp4 -ss 1.6 -t 3.62 -i videos/v8/cena.mov -i videos/v8/edit/capa/gancho.png -filter_complex \
  "[1:v]scale=1080:-2:flags=lanczos,fps=60,setpts=PTS-STARTPTS[f];[0:v]split[o][c];[c]crop=1080:1670:0:0,pad=1080:1920:0:250:black[s];[s][f]overlay=0:0:eof_action=repeat[d1];[d1][2:v]overlay=101:450[d];[o][d]overlay=0:0:enable='lt(t,3.6)'" \
  -map 0:a -c:v libx264 -crf 16 -c:a copy videos/v8/edit/cortado_capa.mp4
python3 ferramentas/legenda.py videos/v8/edit/cortado_capa.mp4 retomar/cena-filme-incontinencia/transcript.json \
  -o videos/v8/edit/final.mp4 --y 1480 --simples --entrega videos/v8/edit/entrega/incontinencia_cena_filme.mp4
```
