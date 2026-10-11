# Projeto-v-deo-

Edição de vídeo pelo chat com o Claude Code, usando o
[Video Use](https://github.com/browser-use/video-use) e o
[HyperFrames](https://github.com/heygen-com/hyperframes).

## Como usar

1. Abra uma sessão do Claude Code com este repositório. Pelo celular é a aba **Code** do app do Claude.
2. Mande o vídeo pelo **+** da caixa de mensagem, ou cole um link do Google Drive com acesso "qualquer pessoa com o link".
3. Diga o que quer. O padrão é:
   - **Video Use** corta todos os silêncios, repetições e hesitações;
   - **HyperFrames** adiciona animações, gráficos e textos ligados ao que é falado;
   - legenda opcional, colocada por último.
4. O Claude mostra um plano curto. Depois do seu OK, edita, confere o resultado e manda o vídeo final no chat.

## Requisitos do ambiente

- Acesso à rede **Completo** (ou Custom com `huggingface.co`) nas configurações do ambiente de nuvem.
- Opcional: `ELEVENLABS_API_KEY` nas variáveis de ambiente, para transcrição mais precisa. Sem ela, usa o Whisper local, que é gratuito.

As instruções detalhadas do fluxo estão em [`CLAUDE.md`](CLAUDE.md).
