# Vídeo "levantar do chão sem as mãos" (só cortes + legenda simples)

Edição de 2026-11-05. Pedido: **só tirar os silêncios, fazer os cortes, deixar a fala mais harmônica e pôr a legenda**. Sem animação, trilha, efeito nem @.
Gravação: 1080×1920 HEVC, 30 fps, 52,2 s, ao ar livre (palmeiras atrás), camiseta cinza-clara, rosto no meio do quadro.
O vídeo não fica no git: se precisar refazer, peça o link do Drive ao usuário.

| Arquivo | O que é |
| --- | --- |
| `edl.json` | 16 trechos do `pausas.py`, 52,2 s → 48,0 s. Aponta para `videos/v9/fonte.mp4`. |
| `transcript.json` | Palavras no tempo do cortado (`legenda.py mapear`), texto conferido. |
| `project.md` | Diário. |

## Refazer

```bash
python3 ferramentas/pausas.py videos/v9/fonte.mp4            # gera videos/v9/edit/edl.json
python3 .claude/skills/video-use/helpers/render.py videos/v9/edit/edl.json -o videos/v9/edit/cortado.mp4
python3 ferramentas/legenda.py videos/v9/edit/cortado.mp4 retomar/levantar-do-chao/transcript.json \
  -o videos/v9/edit/final.mp4 --y 1560 --simples --base-escura 1380 \
  --entrega videos/v9/edit/entrega/levantar-do-chao.mp4
```
