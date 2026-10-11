# Retomar o vídeo "sério" (primeira hora do dia, versão suspense)

Arquivos de edição da sessão de 2026-10-11, para uma sessão nova não refazer tudo.
O vídeo em si não fica no git: peça o link do Drive ao usuário de novo.

1. Baixe para `videos/serio/fonte.mp4` (1080×1920, 95,47 s; o `edl.json` aponta para esse caminho).
2. `render.py videos/serio/edit/edl.json -o videos/serio/edit/cortado_base.mp4 --no-subtitles` (cópia do `edl.json` em `videos/serio/edit/`)
   e congele 2,0 s no fim (`tpad`/`apad`, ver GUIA) → `cortado.mp4` com 91,57 s.
3. `transcript.json` já está corrigido (tempos do vídeo cortado) e `roteiro.json` é o roteiro entregue.
   Copie ambos para `videos/serio/edit/hf/` e o `cortado.mp4` (com `-g 30`) para `hf/assets/`.
4. Pendente: o usuário corrigiu a `PIXABAY_API_KEY`. Acrescente B-roll do Pixabay:
   - 2,62–4,30 "depois de estudar neurociência" → `dividida` (cérebro/neurônios)
   - 15,90–18,95 hoje é a cena `rede`; pode virar `dividida` com clipe de cérebro
   - 34,86–37,55 "se você acorda e pega o celular" → `broll` (pessoa no celular na cama)
   - 43,94–46,88 "cabeça a mil" → `dividida` (pessoa estressada com café)
   - 65,00–67,28 "atrasa o relógio biológico" → `broll` (tela de celular no escuro / relógio)
   Tire o `zoom` que estiver no mesmo trecho e mantenha a cobertura total perto de 35–40%.
