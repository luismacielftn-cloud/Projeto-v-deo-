# Vídeo "essa pergunta vai dizer como seu corpo vai estar daqui a 10 anos" (só cortes + legenda)

Edição de 2026-10-30, terceiro pedido de só cortes + legenda e o primeiro com os cortes feitos pelo `ferramentas/pausas.py`. 1440×2560 HEVC, 24 fps, 46,9 s → 44,5 s.
O vídeo não fica no git: se precisar refazer, peça o link do Drive ao usuário.

```bash
python3 ferramentas/pausas.py videos/cortes3/fonte.mp4          # gera edit/edl.json
python3 .claude/skills/video-use/helpers/render.py videos/cortes3/edit/edl.json -o videos/cortes3/edit/cortado.mp4
python3 ferramentas/legenda.py videos/cortes3/edit/cortado.mp4 retomar/pergunta-sexta/transcript.json \
  -o videos/cortes3/edit/final.mp4 --y 1480 --entrega videos/cortes3/edit/entrega/pergunta-sexta.mp4
```
