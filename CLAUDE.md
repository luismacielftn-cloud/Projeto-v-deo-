# Projeto de edição de vídeo

O usuário manda vídeos pelo chat (geralmente do celular) e quer de volta o vídeo editado.
Responda sempre em português. Explique em linguagem simples: o usuário não é programador.

O fluxo tem duas etapas fixas:

1. **Video Use** corta todos os silêncios, repetições, falsos começos e hesitações.
2. **HyperFrames** adiciona animações, visualizações e gráficos ligados ao que está sendo dito.

Depois, `ferramentas/finalizar.py` junta tudo e coloca a legenda por último.

## O que já está no repositório

| Caminho | O que é |
| --- | --- |
| `.claude/skills/video-use/` | Skill do Video Use (browser-use/video-use @ 43cfc56, MIT). Leia o `SKILL.md` dela antes de editar. Os helpers ficam em `helpers/`. |
| `.claude/skills/hyperframes*`, `talking-head-recut`, `motion-graphics` | Skills do HyperFrames (heygen-com/hyperframes @ 64c47cf, Apache-2.0). Comece por `hyperframes/SKILL.md`. Para animar em cima de vídeo de pessoa falando, use `talking-head-recut`. |
| `ferramentas/transcrever.py` | Transcrição local e gratuita (faster-whisper), no mesmo formato JSON do ElevenLabs Scribe. |
| `ferramentas/ajustar_cortes.py` | Encosta as bordas do `edl.json` no silêncio real do áudio. |
| `ferramentas/finalizar.py` | Junta a imagem do HyperFrames com o áudio do Video Use e queima a legenda (opcional). |
| `.claude/hooks/session-start.sh` | Instala dependências, modelo Whisper, HyperFrames 0.8.145 e o Chrome dele em toda sessão nova. |
| `ferramentas/licencas/` | Licenças das ferramentas copiadas. |

O ambiente na nuvem precisa ter acesso à rede **Completo** (ou Custom com `huggingface.co`, `*.hf.co`, npm e jsdelivr). Sem isso, o modelo do Whisper e o HyperFrames não baixam.

## Recebendo o vídeo

- Anexos do chat chegam em `/root/.claude/uploads/<sessão>/`. Liste a pasta para achar o arquivo.
- Link do Google Drive: use `pip install --break-system-packages gdown` e `gdown --fuzzy <link>`. Link direto: `curl -L -o`.
- Copie para `videos/<nome-curto>/` e trabalhe lá. Todas as saídas vão em `videos/<nome-curto>/edit/` (regra 12 do Video Use).
- Vídeos e áudios estão no `.gitignore`. Nunca faça commit de mídia, porque o GitHub recusa arquivos acima de 100 MB.

## Etapa 1: cortes (Video Use)

Siga `.claude/skills/video-use/SKILL.md` (Hard Rules inclusas). Para este projeto, o padrão é:

1. **Transcrever.**
   - Se `ELEVENLABS_API_KEY` existir, use `helpers/transcribe.py` (Scribe). É o mais preciso para hesitações.
   - Senão, rode `python3 ferramentas/transcrever.py videos/x/fonte.mp4`. O resultado vai para `edit/transcripts/` e o resto do Video Use funciona igual.
   - Depois rode `helpers/pack_transcripts.py --edit-dir videos/x/edit` e leia o `takes_packed.md`.
2. **Montar o `edl.json`** com o objetivo padrão do usuário:
   - Tirar todo silêncio entre frases. Sobra só a folga de 30 a 200 ms da regra 7.
   - Em frases repetidas ou refeitas, manter a última versão completa e boa.
   - Remover falsos começos e hesitações ("é...", "hum", "tipo", "né" soltos).
3. **Ajustar os cortes:** rode `python3 ferramentas/ajustar_cortes.py videos/x/edit/edl.json`.
   - Com Whisper, é obrigatório: ele marca o fim da palavra antes de uma pausa até 0,7 s cedo demais e o corte come a palavra.
   - Bordas marcadas com `!` estão em fala: confira com `helpers/timeline_view.py`.
4. **Renderizar sem legenda e sem overlays:** `helpers/render.py videos/x/edit/edl.json -o videos/x/edit/cortado.mp4`.
5. **Conferir:** transcreva o `cortado.mp4` e confirme que nenhuma palavra foi comida. Se a transcrição mudar um número ou uma palavra no ponto de corte, é sinal de corte cedo demais.

Antes de executar, mostre ao usuário um plano curto e espere o OK (regra 11 do Video Use). O plano diz:
- o que será cortado e a duração estimada;
- quais animações entram, em que momentos;
- o formato de saída;
- se vai ter legenda.

Um único OK vale para as duas etapas.

## Etapa 2: animações (HyperFrames)

1. Transcreva o vídeo cortado para sincronizar as animações:
   `python3 ferramentas/transcrever.py videos/x/edit/cortado.mp4 --edit-dir videos/x/edit/hf --flat videos/x/edit/hf/transcript.json`
2. Monte a composição em `videos/x/edit/hf/index.html`, seguindo `talking-head-recut` e `hyperframes-core`:
   - `<video id="a-roll" class="clip" src="assets/cortado.mp4" data-has-audio="true">` cobrindo **toda** a duração.
   - Os cards (títulos, números, gráficos, citações, listas, ícones) são elementos `.clip` com `data-start`/`data-duration`, animados com GSAP.
   - Fontes e GSAP ficam em `.claude/skills/talking-head-recut/assets/` (copie para `hf/assets/`, sem depender de CDN).
   - Faça o "payoff" de cada animação aterrissar na palavra falada (veja os tempos no `transcript.json`).
   - Antes de posicionar os cards, extraia alguns quadros do vídeo para não cobrir o rosto de quem fala.
3. `npx hyperframes init` foi bloqueado pelo filtro de segurança desta sessão. Crie os arquivos à mão a partir de `.claude/skills/talking-head-recut/references/`.
4. Na pasta `hf/`, rode `npx --yes hyperframes@0.8.145 lint` (zero erros) e depois `npx --yes hyperframes@0.8.145 render --quality looks --output com_animacoes.mp4`.
5. Use `HYPERFRAMES_NO_TELEMETRY=1`. Nunca rode `hyperframes feedback`: ele publica num canal público.
6. Para vídeos de apoio (B-roll), não há banco de vídeos configurado. Use o que o usuário mandar ou visualizações geradas. Se o usuário quiser stock, peça uma chave gratuita do Pexels.

## Finalizar e entregar

```bash
python3 ferramentas/finalizar.py --video videos/x/edit/hf/com_animacoes.mp4 \
  --audio videos/x/edit/cortado.mp4 -o videos/x/edit/final.mp4 [--legenda-edl videos/x/edit/edl.json]
```

- O HyperFrames remasteriza o áudio (+3 dB, comprimido). O `finalizar.py` devolve o áudio do Video Use (-14 LUFS), que é o correto.
- **Autoavaliação antes de mostrar** (passo 7 do Video Use):
  - quadros em cada borda de corte;
  - uma folha de contato com os momentos das animações;
  - `ffmpeg -af ebur128=peak=true` (alvo: -14 LUFS, pico ≤ -1 dBTP);
  - durações com `ffprobe`.
- Entregue com `SendUserFile` (`display: "render"`) e um resumo de uma linha: quanto foi cortado e o que foi animado.
- Registre a sessão em `videos/x/edit/project.md` (memória do Video Use).

## Atualizar as ferramentas

As skills foram copiadas, não estão ligadas ao repositório original. Para atualizar:
1. Clone de novo `browser-use/video-use` e `heygen-com/hyperframes`.
2. Copie as pastas por cima.
3. Rode os testes do Video Use (`pytest tests`).
4. Atualize os commits na tabela acima e a versão em `.claude/hooks/session-start.sh`.
