# Modelo de edição (estrutura da referência + identidade Sálvia)

Este é o modelo **padrão** dos vídeos do usuário.

- **Estrutura e ritmo** vêm de um vídeo de referência que o usuário mandou como modelo: 2min13s, vertical 9:16, uma pessoa falando para a câmera e explicando "3 princípios" de outra criadora.
- **Aparência** é a identidade própria do usuário, **Sálvia**.
- **Usuário:** @luismacciel. Tema: emagrecimento, saúde e longevidade. Estilo: elegante e minimalista, com cores mais vivas em alguns momentos.

Use este guia para planejar a edição, o `montar.py` para gerar a composição do HyperFrames e o `ferramentas/finalizar.py --mix` para a mixagem final.

## Identidade visual

Cada identidade fica em `identidades/<nome>.json` e define:
- cores;
- fontes (Inter, Fraunces e Cormorant Garamond, todas OFL, em `assets/`);
- jeito de animar: com quique (`pop`) ou suave (desfoque e subida);
- zoom seco ou suave;
- transição: clarão ou véu de luz;
- quais efeitos sonoros cada elemento dispara.

No `roteiro.json`, use `"identidade": "<nome>"`. **O padrão é `salvia-forte`** (o usuário recusou o título fino da `salvia`).

| Identidade | Visual |
| --- | --- |
| `salvia` (só cenas; o título dela foi recusado) | Verde-sálvia `#B5CBA8`, off-white `#F5F2EA` e Fraunces itálico; voz secundária em areia `#E3D3AE`; animação suave, véu de luz |
| `oceano` | Azul-gelo, branco e Inter minimalista; suave |
| `champanhe` | Preto e branco com dourado e Cormorant Garamond itálico; suave |
| `referencia` | Cópia da referência: laranja, Inter Black, quique |
| `salvia-forte` | Sálvia com letra forte: todo texto em Inter Black, palavra-chave em dourado `#F2C94C` (o mesmo da legenda em destaque) e cenas mais escuras. Usada no vídeo sério. |

**Cores vivas** (pedido do usuário: "em alguns momentos"): `"vivo": 1` usa **coral** `#FF8A5B` e `"vivo": 2` usa **verde-lima** `#D4F25E`. Elas valem para `titulo`, `capitulo` (no número) e `final`. Use em 1 a 3 momentos fortes por vídeo, como um número que choca, a resposta principal ou o hábito mais importante. Nunca use em todos.

## Estrutura do roteiro (para mapear os eventos)

| Trecho | Na referência | O que entra na edição |
| --- | --- | --- |
| Gancho (0–10 s) | Trecho do vídeo citado + frase provocativa | `janela` ou `inserto` com o vídeo de gatilho; `vozes` quando é a voz de outra pessoa |
| Credibilidade e promessa (10–20 s) | Números e "3 princípios que…" | `titulo` com a palavra-chave; `janela` com print |
| Lista numerada | "1.", "2.", "3." | `transicao` + `capitulo` no início de cada ponto; `janela` com exemplos |
| Objeção | Imita o espectador: "ai, mas pra mim é difícil…" | `pb` (com voz abafada) + `vozes` |
| CTA final (últimos 3–5 s) | "toca no link da minha bio" | `final` |

## Ritmo

- **Zero silêncio:** depois do Video Use não sobra pausa maior que ~0,15 s. A referência tem 205 palavras/min e só 2 pausas acima de 0,3 s em 2 minutos.
- **Novidade constante:** algo novo na tela a cada **4–6 s**. Alterne zoom, janela, título, P&B e inserto, sem repetir o mesmo recurso duas vezes seguidas.
- **Gatilhos visuais:** a referência tem ~20 imagens e vídeos de gatilho em 2 min. Prints, fotos e trechos emocionais ilustram cada afirmação.
- **Payoff no tempo da fala:** o elemento aterrissa na palavra falada (tempos no `transcript.json`).

## Elementos

| Tipo | Quando usar | Na Sálvia |
| --- | --- | --- |
| legenda | Sempre (automática) | Inter Medium 42 px off-white, 2–3 palavras, na altura do peito (y ≈ 1090). Some durante título, capítulo e tela final. Corrija os erros do Whisper no `transcript.json` antes de montar. |
| `vozes` | Outra pessoa falando: imitação, objeção, trecho citado | Legenda em areia `#E3D3AE` |
| `titulo` | Promessa, número forte, palavra-chave | Palavras pequenas em caixa alta espaçada + palavra-chave em Fraunces itálico sálvia (ou `vivo`) |
| `capitulo` | Início de cada ponto da lista | "01" em Fraunces + rótulo pequeno + palavra grande, no alto à esquerda |
| `janela` | Citar post, perfil, print, foto, vídeo de gatilho | Cartão com borda fina, no alto, sem cobrir o rosto. `"som": true` toca o som do vídeo. |
| `inserto` | Mostrar o vídeo citado com destaque | Cartão grande no centro; o fundo fica P&B, escuro e desfocado. `"som": true` toca o som do vídeo. |
| `lista` | Dados, mecanismos, passo a passo ("cortisol ↑, dopamina ↓, foco ↑"; "no lugar disso: …") | Título pequeno + itens com ícone (`↑ ↓ →`) que entram um a um no tempo da palavra (`"t"` de cada item). A legenda some enquanto a lista está na tela. `"vivo"` também vale por item. |
| `pb` | Apartes, brincadeiras, objeção imitada | Câmera em P&B e **voz de rádio/celular** (`"voz": "radio"`, padrão; `"abafada"` = corte suave de agudos; `"normal"` desliga). `"voz_pb"` no roteiro muda o padrão do vídeo. |
| `zoom` | Ênfase | Aproximação suave (1,12×); `"estilo": "seco"` faz punch-in |
| `transicao` | Antes de cada capítulo | Véu de luz que atravessa a tela |
| marca d'água | Sempre (automática) | Ícone + @LUISMACCIEL, muda de lugar a cada ~4 s (`"marca": {"intervalo": 4, "posicoes": [...]}`), não repete a posição anterior e só desvia de textos (títulos, listas, miolo das cenas, cartão); fica por cima de tela cheia e dividida. Animação (`"animada": true`): ícone branco → @ → ícone colorido do Instagram |
| `final` | Últimos 3–5 s | CTA (por exemplo "me segue para / *mais dicas*"); depois escurece e mostra o ícone com o @ |

Cor da imagem: na etapa do Video Use, olhe os quadros e só aplique `grade.py` se a imagem estiver sem graça.

## Preferências do usuário (pedidas depois do 1º vídeo)

- **Legenda em destaque:** grande (Inter Black 66 px), e a palavra falada acende em **amarelo** `#FFD43B` e cresce. No roteiro: `"legenda": {"estilo": "destaque", "cor": "#FFD43B", "tam": 66}`.
- **Cenas em tela cheia cobrindo a câmera:** ele não precisa aparecer o tempo todo. Mire em ~30–35% do vídeo coberto por cenas animadas ligadas ao conteúdo.
- **Nada de texto fino e espaçado** (pedido no vídeo sério): ele não gostou do título da Sálvia (caixa alta espaçada + Fraunces itálico). O texto na tela deve seguir a legenda em destaque: Inter Black, palavra marcando em **dourado `#F2C94C`**. Use `"identidade": "salvia-forte"` e não use eventos `titulo`; a ênfase vem de zoom seco e cenas.
- **Mais gatilhos visuais com whoosh:** zooms secos (`"estilo": "seco"`) a cada poucos segundos, whoosh na entrada e saída das cenas e nos títulos, impacto nos títulos `vivo`.

## Cenas em tela cheia (`"tipo": "cena"`, código em `cenas.py`)

| `modelo` | Para quê | Campos |
| --- | --- | --- |
| `numero` | Número de impacto ("3 hábitos", "60–90 minutos") | `grande`, `unidade`, `texto`, `t`, `vivo`, `tam` (px; use ~210 para números compridos como "10–15%") |
| `barras` | Comparar níveis (cortisol ↑, dopamina ↓, foco ↑) | `itens: [{rotulo, valor 0–100, seta, t, vivo}]` |
| `notificacoes` | Celular recebendo notificações e vibrando | `itens: [{titulo, sub, t}]` |
| `pico` | Gráfico com pico e queda | `t_pico`, `rotulo_pico`, `t_queda`, `rotulo_queda` |
| `sol` | Nascer do sol + lista de hábitos bons | `itens: [{texto, t}]` |
| `frase` | Frase grande, palavra por palavra | `palavras: [{texto, t, destaque, quebra}]` (`destaque`: `true`/1 coral, 2 verde-lima; `quebra`: pula linha depois) |
| `rede` | Rede de neurônios que se desenha e acende (cérebro, neurociência) | `t` (onda de luz), `rotulo` |
| `queda` | Perda com a idade: linhas retas até um marco e caindo depois ("depois dos 40 perde músculo e osso") | `idades` ([30,40,50,60,70]), `marco` (índice, 1 = 40), `t_marco`, `linhas: [{rotulo, t, t_fim, tam, marco}]` (até 3; `marco` por linha faz cada uma cair numa idade, ex.: força aos 40 e massa muscular aos 60) |
| `busca` | "Pesquisa no Google": celular com a página de busca, a frase **digitada letra a letra no tempo da fala** (teclas acendem, som de tecla), tecla "ir" e resultados | `palavras: [{texto, t, fim}]` (tempos do `transcript.json`), `t_logo`, `t_alerta` (borda vermelha + tremida na palavra forte), `t_enter`, `resultados: [{rotulo, vivo\|cor, borda, t}]`, `logo` |
| `versus` | Dois lados opostos ("verdade × mentira", "antes × depois") | `lados: [{texto, icone: "check"\|"x", cor, t}]`, `t_vs` |
| `troca` | Palavra que é riscada e trocada por outra no tempo da fala ("opinião sem pesquisa → torcida") | `de: {texto, t}`, `sub: {texto, t}`, `t_risco`, `para: {texto, t, vivo}`, `topo` |

Qualquer cena aceita `"sobre_camera": true`: em vez do fundo escuro, a câmera fica atrás, escurecida e desfocada (bom para frase de efeito com o rosto ainda presente).

Os resultados da `busca` são **barras cinzas com etiquetas** (ACUSAÇÃO, DEFESA…): nunca invente manchete, site ou jornal real.

Todas aceitam `titulo` (rótulo pequeno no alto). O conteúdo fica entre y 200 e 1250, e a legenda continua por cima. A entrada e a saída são cortes rápidos com desfoque e whoosh. Para vídeo real de banco (B-roll), use `ferramentas/buscar_clipes.py` (Pixabay). Se a chave for recusada ("Invalid or missing API key"), troque os clipes por cenas e avise o usuário.

## Vídeos de prova e tom tenso (2ª referência do usuário)

Na segunda referência, o criador **prova o que fala com vídeos**: tira a própria imagem da tela e deixa só a voz, divide a tela, e às vezes cala para o clipe tocar com o próprio som. O som é **tenso**: *riser* antes das revelações, "boom" grave nos impactos e trilha sombria e pulsante.

| Evento | O que faz | Campos |
| --- | --- | --- |
| `dividida` | Clipe/imagem na metade de cima; a câmera desce e você fica na de baixo; a legenda vai para a emenda (se o rosto estiver no alto do quadro, use `"descer": 820` para a legenda não cair no cabelo). A borda de baixo do clipe se dissolve em 190 px (emenda esfumada, como em @elias.maman) | `midia`, `altura` (980), `descer` (445), `som`, `inicio_midia` |
| `broll` | Clipe cobrindo a câmera: `"estilo": "cheia"` (tela cheia) ou `"cartao"` (**formato menor**: cartão 840×800 de cantos suaves e borda esfumada, centralizado sobre fundo preto, como no vídeo de @elias.maman) | `midia`, `estilo`, `som`, `inicio_midia`, `ganho_db`; no cartão, `largura`, `altura`, `topo` (px). Prepare o clipe já no tamanho do cartão (ffmpeg `scale`+`crop`). |
| `rotulos` | Etiquetas em cima de imagens que o **usuário já colocou no vídeo** (ex.: as coxas em corte no começo do vídeo 4). Cada etiqueta entra na palavra e sai quando a imagem dele some; a legenda some no trecho para não cobrir as fotos. Meça onde e quando as imagens dele aparecem (quadros a cada 0,2 s) e não cubra nada. | `itens: [{texto, sub, x (centro), y (topo), t, fim, vivo}]` |
| `final` (opções) | Quando o usuário põe imagens próprias no fim (ex.: "qual das duas?" com as duas coxas), use `"escurecer": false` (não escurece a tela), `"cta_y"` para pôr o texto abaixo das imagens (~1630) e `"ig_y"` para o ícone do @ ficar no alto (~40), fora do rosto. `"ig": false` tira o ícone com o @ da tela final. | `cta_y`, `ig_y`, `escurecer`, `ig` |

- **Tom tenso, para vídeos sérios** (o usuário escolhe vídeo a vídeo): `"tom": "tenso"` no roteiro. Os sons passam a ser:
  - `riser` + `boom` nas entradas de clipe;
  - `hit_tenso` nos títulos e zooms;
  - `boom` nos capítulos e na tela final;
  - `coracao` no P&B.
  A trilha usa os humores `tensa` e `tensa_pulso`. Sem `"tom"`, fica a Sálvia suave.
- **Clipes com som próprio:** use `"som": true` e abra espaço na fala na etapa do Video Use (trecho com `"manter": true`).
- **Origem dos clipes:** o usuário manda os clipes de terceiros (notícias, entrevistas). Não baixe por conta própria. Clipes genéricos vêm do Pixabay (`buscar_clipes.py`, com a `PIXABAY_API_KEY` do usuário); quando ele não tem, do Mixkit (`mixkit.co/free-stock-video/<termo>/`, arquivo em `assets.mixkit.co/videos/<id>/<id>-720.mp4`). O clipe mostra o que a fala descreve: "sentar e levantar" pede alguém sentando e levantando, não uma aula com os braços para cima (recusado). Busque termos simples em inglês ("skeleton", "knee", "luggage"): frases longas dão resultados fracos. Prefira pessoas maduras para o público 45+ e recorte cada clipe antes (trecho, enquadramento, câmera lenta) com ffmpeg para `hf/assets/`.
- **Anatomia realista, não desenho:** quando a fala pede uma imagem do corpo por dentro (músculo, gordura), o usuário quer algo **próximo do real** (carne em corte, textura de verdade), como os posts "seu músculo sem/com treino de força". Para sarcopenia já existe `ferramentas/secao_musculo.py`: duas fotos realistas da coxa em corte (`assets/sarcopenia/`, geradas no Canva do usuário) lado a lado, 30 × 70 anos, e a de 70 anos passa de músculo vermelho para músculo tomado de gordura no meio do clipe. Cartão + `filtro_clipe.py tv --brilho 1.2`. Para outro tema, gere fotos realistas no Canva (`generate-image`); só a prévia de 200 px pode ser baixada, então amplie com lanczos e deixe o filtro `tv` disfarçar.

## Peças "virais" (5º vídeo, `retomar/bolsonaro-lula/`)

Pedido do usuário: "extremamente viral", com efeitos sonoros e ênfase forte numa frase. Peças novas do `montar.py`:

| Evento | O que faz | Campos |
| --- | --- | --- |
| `impacto` | A frase forte **carimbada** na tela: clarão, fundo vermelho-escuro, texto gigante (Inter Black) que bate, falha de cor vermelho/ciano, a câmera e as cenas tremem. A legenda some. Som: `boom` + `glitch`. Use em 1 frase por vídeo. | `linhas: [{texto, cor\|vivo}]`, `tam` (150), `topo`, `tremer` |
| `trio` | Três faixas de vídeo empilhadas (1000×340, filtro `tv`), cada uma entra na sua palavra de uma enumeração ("ex-presidente, Polícia Federal e o Supremo") com número e rótulo. `batida` dá um tranco + impacto (martelo do juiz). | `itens: [{midia, rotulo, numero, t, batida, inicio_midia}]`, `topo` |
| `trilha` | Invisível: só troca o humor da trilha nesse instante (sem véu). Ex.: `tensa` → `tensa_pulso` na busca → `batida` logo depois da frase forte (o "drop"). | `humor` |
| `sons_extra` (no roteiro, fora dos eventos) | Efeitos avulsos: `[{"t": 17.88, "som": "riser"}]`. O `riser` termina no `t` (sobe até o impacto). | `t`, `som` |

- **Rachar a imagem ao meio** (gancho "divide o Brasil ao meio"): feito em ffmpeg, com borda irregular, luz vermelha na fenda e tremida (`retomar/bolsonaro-lula/preparar_clipes.sh`). Som: `riser` terminando na rachadura + `rachadura`.
- **Foto do usuário no gancho sem perder o clipe:** a imagem racha e as metades se abrem para os lados, **revelando a foto por trás** (3º argumento do mesmo script). A tela dividida vai até ~3,6 s para a foto ficar ~1,5 s na tela, com o usuário embaixo. Som: `whoosh` na abertura + `impacto` quando a foto aparece.
- **Sons novos** em `ferramentas/efeitos.py`: `tecla`/`tecla2`/`tecla3` (digitação, -25 dB), `enter` (-19), `glitch` (-20), `rachadura` (-13).
- **Cor e luz** quando o usuário pede ("qualidade, filtro, iluminação"): use o `grade` do `retomar/bolsonaro-lula/edl.json` como ponto de partida (contraste, realces comprimidos, pele quente, parede fria, vinheta, nitidez leve). Compare antes/depois num quadro lado a lado antes de renderizar.
- **Tema político ou polêmico:** a edição segue o tom do vídeo (neutro: a frase leva "?"). Sem manchetes inventadas, sem imagens de pessoas reais baixadas por conta própria.
- **Vídeo sem @:** neste vídeo o usuário pediu "não precisa colocar o meu @". Tire os dois: `"marca": {"ativa": false}` no roteiro e `"ig": false` no `final`. Confira com `grep -ci luismacciel index.html` (tem que dar 0).
- **GSAP:** `tl.fromTo` aplica o "from" assim que o timeline é criado. Se o estado inicial é visível (borda acesa, tecla apertada), ele aparece antes da hora. Use `tl.set` no instante + `tl.to` logo depois.

## Layout: não cobrir o rosto

As posições padrão servem para um rosto no terço superior. Antes de montar, olhe 3 quadros do vídeo e, se o rosto ocupar o meio do quadro, desça os textos para a altura do peito:

```json
"layout": {"legenda_y": 1400, "titulo_y": 1340, "capitulo_y": 1380, "cta_y": 1360, "lista_y": 1330, "fim_ig_y": 560},
"marca": {"intervalo": 6, "posicoes": [[40, 420], [840, 1110], [40, 140], [820, 1230], [40, 1230]]}
```

- Janelas: `"topo": 80` (com `"largura": 0.40` e `"proporcao": 0.95`) as coloca acima da cabeça.
- Marca d'água: escolha posições sobre fundo escuro, longe de quadros claros e do rosto. Ela desvia sozinha dos títulos, capítulos, listas e janelas.
- Confira com `npx hyperframes snapshot --at t1,t2,…` antes do render completo, que leva ~3,5× a duração do vídeo.

Exemplo real (vídeo "primeira hora do dia"): rosto entre y 555 e 1260, quadro amarelo atrás da cabeça e camiseta preta. Os textos foram para y 1330–1400, sobre a camiseta, onde o contraste é ótimo.

## Som

Na referência, o som tem quatro camadas: trilha que troca a cada capítulo, efeitos sonoros quando algo entra na tela, voz abafada nos apartes em P&B e vídeos citados tocando com o próprio som. O modelo reproduz as quatro. O `montar.py` grava as deixas no `mix.json` e o `ferramentas/mixar.py` faz a mixagem.

| Camada | Como funciona | Onde ajustar |
| --- | --- | --- |
| Efeitos | Sintetizados em `ferramentas/efeitos.py`, sem direitos autorais: `whoosh_suave` (título), `tick` (capítulo), `respiro` (transição), `pop_suave` (janela), entre outros (o `sino` da tela final foi tirado da Sálvia forte a pedido do usuário). O ponto de impacto cai no instante do evento. Na Sálvia forte, toda entrada de clipe ou cena leva `corte_ref`: só o swoosh subindo, sem o tic metálico antes e sem som na saída (os `*_saida` ficam vazios), a pedido do usuário. | `sons` na identidade; volume em `GANHO_DB` ou `"efeitos_volume_db"` no roteiro |
| Trilha | Gerada em `ferramentas/trilha.py`, sem direitos autorais. Uma seção por capítulo, com os humores `calma` → `leve` → `inspira`; cai e troca na virada e termina num acorde aberto na tela final. Ducking: fica ~20 dB abaixo da voz enquanto há fala e sobe nas pausas. | `"humor"` no `capitulo` (ou numa `transicao`, em vídeos sem lista numerada), `"humor_inicial"`, `"trilha": {"volume_db": -3}` no roteiro |
| Música do usuário | Se o usuário mandar faixas: `"musica": [{"arquivo": "assets/x.mp3", "inicio": 0, "fim": 30, "volume_db": 0}]`. Isso substitui a trilha gerada, com o mesmo ducking. | roteiro |
| Voz de rádio | Nos trechos `pb`, voz **e trilha** passam por um passa-faixa 400–3000 Hz com leve saturação: ~20 dB a menos de graves e ~8 dB a menos de agudos, mesmo volume. Calibrado no vídeo sério, que o usuário aprovou ("voz de rádio ou celular"). A opção `"abafada"` (corte suave de agudos) quase não se percebe. | `"voz"` no `pb`, `"voz_pb"` no roteiro |
| Inserto com som | `janela`/`inserto` com `"som": true`. O áudio do clipe entra no nível da voz (`"ganho_db"` ajusta). Abra espaço na fala na etapa do Video Use: um trecho de silêncio com `"manter": true` no `edl.json`. | evento |

No final, tudo é normalizado em dois passes para **-14 LUFS** e pico de **-1 dBTP**. Eu não consigo ouvir: meço os níveis (voz, trilha sob a fala, efeitos) e peço o retorno do usuário.

## Como gerar

1. Video Use → `edit/cortado.mp4` (sem legenda).
   - Silêncios intencionais, como o respiro da tela final ou o espaço para um inserto com som, levam `"manter": true` no `edl.json` para o `ajustar_cortes.py` não apertá-los.
   - Deixe ~1,5–2,5 s depois da última fala para a tela final. Se não houver silêncio no fim do arquivo, congele o último quadro: `ffmpeg -i cortado_base.mp4 -vf tpad=stop_mode=clone:stop_duration=1.5 -af apad=pad_dur=1.5 … cortado.mp4`. No `final`, use `"escurecer_em"` para escurecer só depois que a fala termina.
2. `python3 ferramentas/transcrever.py edit/cortado.mp4 --edit-dir edit/hf --flat edit/hf/transcript.json`. Depois corrija os erros de transcrição no `transcript.json` (só o `text`; mantenha os tempos).
3. Copie `cortado.mp4` para `edit/hf/assets/` com um quadro-chave por segundo (`ffmpeg -i edit/cortado.mp4 -c:v libx264 -crf 18 -r 30 -g 30 -keyint_min 30 -pix_fmt yuv420p -c:a copy edit/hf/assets/cortado.mp4`; sem isso o HyperFrames avisa "sparse keyframes" e a imagem pode congelar), copie as mídias e escreva `edit/hf/roteiro.json` (modelo em `exemplo-roteiro.json`). Os tempos estão em segundos do vídeo cortado.
4. `python3 modelos/estilo-referencia/montar.py edit/hf/roteiro.json` gera `index.html` + `mix.json` e copia fontes e GSAP.
5. Na pasta `edit/hf/`, rode `npx --yes hyperframes@0.8.145 lint` (zero erros) e depois `render --quality looks --output com_animacoes.mp4`.
6. `python3 ferramentas/finalizar.py --video edit/hf/com_animacoes.mp4 --audio edit/cortado.mp4 --mix edit/hf/mix.json --crf 20 -o edit/final.mp4 --entrega edit/entrega/<nome>.mp4`. Não use `--legenda-edl`: a legenda já está na composição.
   - `--entrega` grava uma cópia abaixo de 30 MB, que é o limite de envio pelo chat, e é essa que vai pelo `SendUserFile`.

O canvas é 1080×1920. Vídeo horizontal é recortado no centro (`object-fit: cover`), então confira o enquadramento.

## Limitações

- Prints, fotos e vídeos de gatilho vêm do usuário. Não baixe conteúdo de terceiros por conta própria. Imagens e vídeos de banco vêm do Pixabay.
- A trilha gerada é simples, de fundo. Se o usuário quiser algo específico, ele manda a música.
