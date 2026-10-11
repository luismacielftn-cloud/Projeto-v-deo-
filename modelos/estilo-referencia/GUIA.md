# Estilo referência

Este é o estilo **padrão** dos vídeos do usuário. Ele foi tirado da análise de um vídeo de referência que o usuário mandou como modelo: 2min13s, vertical 9:16, uma pessoa falando para a câmera e explicando "3 princípios" de outra criadora.

Use este guia para planejar a edição e o `montar.py` para gerar a composição do HyperFrames.

## Estrutura do roteiro (para mapear os eventos)

| Trecho | Na referência | O que entra na edição |
| --- | --- | --- |
| Gancho (0–10 s) | Trecho do vídeo citado + frase engraçada e provocativa | `janela` ou `inserto` com o material citado e legenda amarela (`vozes`) quando é a voz de outra pessoa |
| Credibilidade e promessa (10–20 s) | Números ("4 milhões de seguidores") e "3 princípios que…" | `titulo` com a palavra-chave em laranja; `janela` com print do perfil |
| Lista numerada | "1. conflitos universais", "2. efeito jornal", "3. autenticidade" | `clarao` + `capitulo` no início de cada ponto; `janela` com exemplos |
| Objeção | Imita o espectador: "ai, mas pra mim é difícil…" | `pb` + legenda amarela (`vozes`) |
| CTA final (últimos 3–5 s) | "toca no link da minha bio" | `final` |

## Ritmo

- **Zero silêncio:** depois do Video Use não sobra pausa maior que ~0,15 s. A referência tem 205 palavras/min e só 2 pausas acima de 0,3 s em 2 minutos.
- **Novidade constante:** algo novo na tela a cada **4–6 s**. Alterne zoom, janela, título, P&B e inserto, sem repetir o mesmo recurso duas vezes seguidas.
- **Zoom de ênfase** (`zoom`, escala 1,25–1,4) nas frases de impacto. Ele entra e sai seco, como um corte.
- **Payoff no tempo da fala:** o elemento aterrissa na palavra falada (tempos no `transcript.json`).

## Elementos

| Tipo | Quando usar | Visual |
| --- | --- | --- |
| legenda | Sempre (automática) | Branca, Inter Medium Itálico 44 px, 2–3 palavras, caixa normal, na altura do peito (y ≈ 1090). Some durante título, capítulo e tela final. |
| `vozes` | Outra pessoa falando: imitação, objeção, trecho citado | Legenda amarela `#F1F454` |
| `titulo` | Promessa, número forte, palavra-chave | Palavras pequenas brancas (Inter Bold) + palavra gigante laranja `#E9870A` (Inter Black, caixa alta) |
| `capitulo` | Início de cada ponto da lista | "1." gigante + palavra pequena + palavra grande, brancos, no alto à esquerda |
| `janela` | Citar post, perfil, print, foto | Cartão com cantos arredondados e sombra, no alto, sem cobrir o rosto |
| `inserto` | Mostrar o vídeo citado com destaque | Cartão grande no centro; o fundo fica preto e branco, escuro e desfocado |
| `pb` | Apartes, brincadeiras, objeção imitada | Câmera em preto e branco |
| `zoom` | Ênfase | Aproximação seca (punch-in) |
| `clarao` | Transição entre seções (antes do capítulo) | Vazamento de luz laranja, 0,7 s |
| marca d'água | Sempre (automática) | Ícone do Instagram + @, pequeno, muda de lugar a cada ~5–6 s e desvia dos outros elementos |
| `final` | Últimos 3–5 s | "tocar / **NO LINK** / da minha bio"; depois escurece e mostra o ícone com o @ |

Cores: branco, laranja `#E9870A` e amarelo `#F1F454`. Fonte: Inter (OFL), com os arquivos em `assets/`.

Cor da imagem: o visual quente (laranja e azul-petróleo) da referência vem mais da luz do cenário do que de correção de cor. Na etapa do Video Use, olhe os quadros e só aplique `grade.py --preset warm_cinematic` (ou uma correção sob medida) se a imagem estiver sem graça.

## Como gerar

1. Video Use → `edit/cortado.mp4` (sem legenda).
2. `python3 ferramentas/transcrever.py edit/cortado.mp4 --edit-dir edit/hf --flat edit/hf/transcript.json`
3. Copie `cortado.mp4` e as mídias citadas para `edit/hf/assets/` e escreva `edit/hf/roteiro.json` (modelo em `exemplo-roteiro.json`):
   - `video`, `transcricao`, `arroba`, `vozes` e `eventos`;
   - os tempos estão em segundos do vídeo cortado;
   - `fim` é opcional no `final`.
4. `python3 modelos/estilo-referencia/montar.py edit/hf/roteiro.json` gera o `index.html` e copia fontes e GSAP.
5. Na pasta `edit/hf/`, rode `npx --yes hyperframes@0.8.145 lint` e depois `render --quality looks --output com_animacoes.mp4`.
6. Rode `ferramentas/finalizar.py --video edit/hf/com_animacoes.mp4 --audio edit/cortado.mp4 -o edit/final.mp4`, **sem** `--legenda-edl`: a legenda já está na composição.

O canvas é 1080×1920. Vídeo horizontal é recortado no centro (`object-fit: cover`), então confira o enquadramento.

## Limitações atuais

- Janelas e insertos entram **sem som**: o áudio final é o do Video Use. Um trecho citado que precisa tocar com o próprio som deve entrar no `edl.json` como mais uma fonte, na etapa do Video Use.
- A trilha sonora ainda não é mixada automaticamente. Se o usuário mandar uma música, ela precisa ser mixada com ducking por baixo da voz, em -14 LUFS no total.
- Prints e vídeos citados vêm do usuário. Não baixe conteúdo de terceiros por conta própria.
