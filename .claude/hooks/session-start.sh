#!/bin/bash
# Prepara a sessão na nuvem para editar vídeo: Video Use + Whisper + HyperFrames.
# Idempotente: quando tudo já está instalado, só confere e sai rápido.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
HYPERFRAMES_VERSION="0.8.145"
WHISPER_MODEL="small"

export HYPERFRAMES_NO_TELEMETRY=1
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  grep -qs HYPERFRAMES_NO_TELEMETRY "$CLAUDE_ENV_FILE" || echo 'export HYPERFRAMES_NO_TELEMETRY=1' >> "$CLAUDE_ENV_FILE"
fi

# 1. Dependências Python (Video Use + transcrição local)
pip install --break-system-packages -q --disable-pip-version-check \
  -r ferramentas/requirements.txt 2>&1 | grep -v -E "^WARNING: Running pip as the 'root' user" || true
python3 -c "import faster_whisper, librosa, matplotlib, PIL, requests" \
  || { echo "session-start: falha ao instalar dependências Python" >&2; exit 1; }

# 2. Modelo do Whisper (precisa de huggingface.co liberado na rede do ambiente)
if [ ! -d "$HOME/.cache/huggingface/hub/models--Systran--faster-whisper-$WHISPER_MODEL" ]; then
  python3 -c "from faster_whisper import WhisperModel; WhisperModel('$WHISPER_MODEL', device='cpu', compute_type='int8')" >/dev/null 2>&1 \
    || echo "session-start: aviso: não consegui baixar o modelo Whisper '$WHISPER_MODEL' (rede?)" >&2
fi

# 3. HyperFrames CLI + Chrome Headless Shell usado na renderização
npx --yes "hyperframes@$HYPERFRAMES_VERSION" --version >/dev/null 2>&1 \
  || echo "session-start: aviso: não consegui instalar hyperframes@$HYPERFRAMES_VERSION" >&2
if ! ls "$HOME"/.cache/hyperframes/chrome/chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell >/dev/null 2>&1; then
  npx --yes "hyperframes@$HYPERFRAMES_VERSION" browser ensure >/dev/null 2>&1 \
    || echo "session-start: aviso: não consegui baixar o Chrome do HyperFrames" >&2
fi

echo "session-start: ambiente de edição pronto (ffmpeg, Video Use, Whisper $WHISPER_MODEL, HyperFrames $HYPERFRAMES_VERSION)"
