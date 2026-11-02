# Vídeo "5 hábitos que vão te dar mais 10 anos de vida" (só cortes + legenda)

Edição de 2026-10-26. O usuário pediu **só os cortes e a legenda**: sem animação, sem efeito sonoro, sem trilha, sem @. Gravado no carro (selfie, 1440×2560 HEVC, 24 fps, 43,5 s), rosto no meio do quadro.
O vídeo em si não fica no git: se precisar refazer, peça o link do Drive ao usuário.

| Arquivo | O que é |
| --- | --- |
| `edl.json` | Cortes (14 trechos, 43,5 s → 40,6 s), bordas em quadros inteiros de 24 fps. Fala numa tomada só: saíram 13 pausas com respiração. Aponta para `videos/cortes/fonte.mp4`. |
| `transcript.json` | Palavras na linha do tempo do cortado, texto corrigido (vazio = some da legenda). |
| `project.md` | Diário. |

## Refazer

```bash
python3 .claude/skills/video-use/helpers/render.py videos/cortes/edit/edl.json -o videos/cortes/edit/cortado.mp4
python3 ferramentas/legenda.py videos/cortes/edit/cortado.mp4 retomar/cortes-legenda/transcript.json \
  -o videos/cortes/edit/final.mp4 --y 1480 --entrega videos/cortes/edit/entrega/5-habitos-harvard.mp4
```

## Como os cortes foram achados

A fala já era corrida; o "silêncio" entre frases era quase todo respiração (-32 a -40 dB), que o `ajustar_cortes.py` trata como fala. Medi o áudio em quadros de 20 ms em volta de cada pausa do Whisper e cortei do fim da fala (< -42 dB) até o começo da próxima, deixando ~0,1 s de ar. Pausas de vírgula de ~0,2 s sem respiração ficaram: tirar 0,1 s só dá pulo na imagem.
