# Projeto de edição de vídeo

O usuário manda vídeos pelo chat (geralmente do celular) e quer de volta o vídeo editado.
Responda sempre em português. Explique em linguagem simples: o usuário não é programador.

O fluxo tem duas etapas fixas:

1. **Video Use** corta todos os silêncios, repetições, falsos começos e hesitações.
2. **HyperFrames** adiciona animações, visualizações e gráficos ligados ao que está sendo dito.

Depois, `ferramentas/finalizar.py` junta tudo.

**Modelo padrão: `modelos/estilo-referencia/`.** Todo vídeo sai nesse modelo, a não ser que o usuário peça outro. Leia o `GUIA.md` antes de planejar a edição.

- **Estrutura e ritmo:** vêm de um vídeo de referência que o usuário mandou. A arquitetura é gancho → promessa → lista numerada → objeção → chamada final, com zero silêncio e algo novo na tela a cada 4–6 s.
- **Aparência:** é a identidade própria do usuário, **Sálvia**: verde-sálvia, off-white e Fraunces itálico, com animações suaves. Em 1 a 3 momentos fortes por vídeo entram cores vivas (`"vivo": 1` coral, `"vivo": 2` verde-lima).
- **Som:** trilha gerada sem direitos autorais, que troca a cada capítulo e abaixa sob a fala; efeitos sonoros sintetizados; voz abafada nos apartes em P&B; vídeos de gatilho com o próprio som.

**Usuário:** @luismacciel. Tema: emagrecimento, saúde e longevidade. Estilo: elegante e minimalista.

**Gancho visual nos primeiros 3 segundos:** todo vídeo abre com algo forte na tela já no 0 s (clipe de banco, inserto ou animação ligada à primeira frase). Não comece só com o rosto.

## O que já está no repositório

| Caminho | O que é |
| --- | --- |
| `.claude/skills/video-use/` | Skill do Video Use (browser-use/video-use @ 43cfc56, MIT). Leia o `SKILL.md` dela antes de editar. Os helpers ficam em `helpers/`. |
| `.claude/skills/hyperframes*`, `talking-head-recut`, `motion-graphics` | Skills do HyperFrames (heygen-com/hyperframes @ 64c47cf, Apache-2.0). Comece por `hyperframes/SKILL.md`. Para animar em cima de vídeo de pessoa falando, use `talking-head-recut`. |
| `ferramentas/transcrever.py` | Transcrição local e gratuita (faster-whisper), no mesmo formato JSON do ElevenLabs Scribe. |
| `ferramentas/ajustar_cortes.py` | Encosta as bordas do `edl.json` no silêncio real do áudio. |
| `modelos/estilo-referencia/` | Modelo padrão: `GUIA.md` (receita), `montar.py` (gera `index.html` + `mix.json` a partir de um `roteiro.json`), `identidades/` (Sálvia é a padrão), `exemplo-roteiro.json`, fontes e GSAP. |
| `ferramentas/finalizar.py` | Junta a imagem do HyperFrames com o áudio. Com `--mix`, usa a mixagem completa do `mixar.py`. Queima legenda só fora do modelo. |
| `ferramentas/mixar.py`, `efeitos.py`, `trilha.py` | Mixagem (voz + efeitos + insertos com som + trilha com ducking, -14 LUFS), efeitos sonoros sintetizados e trilhas geradas. Tudo sem direitos autorais. |
| `.claude/hooks/session-start.sh` | Instala dependências, modelo Whisper, HyperFrames 0.8.145 e o Chrome dele em toda sessão nova. |
| `ferramentas/licencas/` | Licenças das ferramentas copiadas. |

O ambiente na nuvem precisa ter acesso à rede **Completo** (ou Custom com `huggingface.co`, `*.hf.co`, npm e jsdelivr). Sem isso, o modelo do Whisper e o HyperFrames não baixam.

## Recebendo o vídeo

- Anexos do chat chegam em `/root/.claude/uploads/<sessão>/`. Liste a pasta para achar o arquivo.
- O app do Claude limita anexos a 30 MB. Vídeos maiores chegam por link do Google Drive: baixe com `gdown "<link>" -O videos/<nome>/` (o gdown 6 não tem mais `--fuzzy`; ele entende o link sozinho) (já instalado pelo hook). Link direto: `curl -L -o`.
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

Silêncios **intencionais** levam `"manter": true` no `edl.json`, para o `ajustar_cortes.py` não apertá-los. São eles:
- ~1,5–2,5 s depois da última fala, para a tela final respirar;
- o espaço para um vídeo de gatilho tocar com o próprio som.

Antes de executar, mostre ao usuário um plano curto e espere o OK (regra 11 do Video Use). O plano diz:
- o que será cortado e a duração estimada;
- quais animações entram, em que momentos;
- o formato de saída (o padrão é vertical 1080×1920);
- se vai ter legenda.

Pergunte também se há prints, fotos ou vídeos de gatilho para as janelas e insertos. O @ já é conhecido (@luismacciel). A trilha é gerada automaticamente, a não ser que o usuário mande músicas.

Um único OK vale para as duas etapas.

## Etapa 2: animações (HyperFrames)

1. Transcreva o vídeo cortado para sincronizar as animações:
   `python3 ferramentas/transcrever.py videos/x/edit/cortado.mp4 --edit-dir videos/x/edit/hf --flat videos/x/edit/hf/transcript.json`
2. **Com o modelo padrão:**
   - Corrija os erros do Whisper no `transcript.json`: só o `text`, sem mexer nos tempos.
   - Copie `cortado.mp4` e as mídias citadas para `hf/assets/`.
   - Escreva `hf/roteiro.json` com os eventos (veja `modelos/estilo-referencia/GUIA.md` e `exemplo-roteiro.json`).
   - Rode `python3 modelos/estilo-referencia/montar.py videos/x/edit/hf/roteiro.json`. Ele gera `index.html` e `mix.json`. A legenda e a marca d'água já saem na composição.
   - Pule para o passo 4.
3. **Fora do estilo padrão** (o usuário pediu algo diferente), monte `videos/x/edit/hf/index.html` à mão, seguindo `talking-head-recut` e `hyperframes-core`:
   - `<video id="a-roll" class="clip" src="assets/cortado.mp4" data-has-audio="true">` cobrindo **toda** a duração.
   - Os cards (títulos, números, gráficos, citações, listas, ícones) são elementos `.clip` com `data-start`/`data-duration`, animados com GSAP.
   - Fontes e GSAP ficam em `.claude/skills/talking-head-recut/assets/` (copie para `hf/assets/`, sem depender de CDN).
   - Faça o "payoff" de cada animação aterrissar na palavra falada (veja os tempos no `transcript.json`).
   - Antes de posicionar os cards, extraia alguns quadros do vídeo para não cobrir o rosto de quem fala.
   - `npx hyperframes init` foi bloqueado pelo filtro de segurança desta sessão. Crie os arquivos à mão a partir de `.claude/skills/talking-head-recut/references/`.
4. Antes de renderizar, extraia quadros do vídeo cortado para conferir que nada cobre o rosto. Depois, na pasta `hf/`, rode `npx --yes hyperframes@0.8.145 lint` (zero erros) e depois `npx --yes hyperframes@0.8.145 render --quality looks --output com_animacoes.mp4`.
5. Use `HYPERFRAMES_NO_TELEMETRY=1`. Nunca rode `hyperframes feedback`: ele publica num canal público.
6. **Vídeos de apoio (B-roll):** use `python3 ferramentas/buscar_clipes.py "<termo em inglês>" --listar` e depois `-o hf/assets/x.mp4 --escolha N`. O banco é o Pixabay, com licença livre; precisa de `PIXABAY_API_KEY`, configurada pelo usuário nas variáveis de ambiente. O Pexels pausou a emissão de chaves. Encaixe os clipes com os eventos `broll` ou `dividida`.
   - Clipes de terceiros (notícias, famosos) só entram se o usuário mandar o arquivo ou o link. Não busque esse tipo de material por conta própria.

## Finalizar e entregar

```bash
python3 ferramentas/finalizar.py --video videos/x/edit/hf/com_animacoes.mp4 \
  --audio videos/x/edit/cortado.mp4 --mix videos/x/edit/hf/mix.json -o videos/x/edit/final.mp4
```

- No modelo padrão, a legenda já está na composição. **Não** use `--legenda-edl` (ficaria duplicada). Use-o só fora do modelo.
- O `--mix` faz a mixagem completa (efeitos, trilha com ducking, voz abafada, insertos com som) em -14 LUFS.
- Você não consegue ouvir. Meça os níveis e peça o retorno do usuário sobre o volume da trilha e dos efeitos: `"trilha": {"volume_db": ...}` e `"efeitos_volume_db"` no roteiro.

- O HyperFrames remasteriza o áudio (+3 dB, comprimido). O `finalizar.py` devolve o áudio do Video Use (-14 LUFS), que é o correto.
- **Autoavaliação antes de mostrar** (passo 7 do Video Use):
  - quadros em cada borda de corte;
  - uma folha de contato com os momentos das animações;
  - `ffmpeg -af ebur128=peak=true` (alvo: -14 LUFS, pico ≤ -1 dBTP);
  - durações com `ffprobe`.
- Entregue com `SendUserFile` (`display: "render"`) e um resumo de uma linha: quanto foi cortado e o que foi animado.
  - O envio pelo chat aceita **no máximo 30 MB**. Use `--entrega` no `finalizar.py`, que grava uma cópia em duas passadas abaixo desse limite, mantendo 1080×1920.
- Registre a sessão em `videos/x/edit/project.md` (memória do Video Use).

## Atualizar as ferramentas

As skills foram copiadas, não estão ligadas ao repositório original. Para atualizar:
1. Clone de novo `browser-use/video-use` e `heygen-com/hyperframes`.
2. Copie as pastas por cima.
3. Rode os testes do Video Use (`pytest tests`).
4. Atualize os commits na tabela acima e a versão em `.claude/hooks/session-start.sh`.
