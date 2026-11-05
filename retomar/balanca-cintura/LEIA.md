# Vídeo "se a balança desceu, não comemora ainda" (só cortes + legenda)

Edição de 2026-10-29, segundo pedido de **só cortes + legenda** (o primeiro é `retomar/cortes-legenda/`). Gravado no carro (selfie, 1080×1920 HEVC, 30 fps, 41,3 s), rosto no meio do quadro.
O vídeo em si não fica no git: se precisar refazer, peça o link do Drive ao usuário.

| Arquivo | O que é |
| --- | --- |
| `edl.json` | Cortes (14 trechos, 41,3 s → 37,5 s), bordas em quadros inteiros de 30 fps. Aponta para `videos/cortes2/fonte.mp4`. |
| `transcript.json` | Palavras no tempo do cortado (`legenda.py mapear`), texto corrigido. |
| `project.md` | Diário. |

## Refazer

```bash
python3 .claude/skills/video-use/helpers/render.py videos/cortes2/edit/edl.json -o videos/cortes2/edit/cortado.mp4
python3 ferramentas/legenda.py videos/cortes2/edit/cortado.mp4 retomar/balanca-cintura/transcript.json \
  -o videos/cortes2/edit/final.mp4 --y 1480 --entrega videos/cortes2/edit/entrega/balanca-cintura.mp4
```
