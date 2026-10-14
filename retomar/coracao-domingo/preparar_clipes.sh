#!/usr/bin/env bash
# Rebaixa do Mixkit e prepara os clipes do vídeo "exercício mais perigoso para o coração (atleta de domingo)":
# trecho, recorte no tamanho do formato e filtro no estilo @elias.maman.
#   tela dividida 1080×980 (desfoque) · cartão 840×800 ou largo 960×620 (tv)
# Todos do Mixkit (licença gratuita, sem crédito), em 720p (o 1080 dá 403).
# Uso: bash retomar/coracao-domingo/preparar_clipes.sh videos/v3/edit/hf/assets
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
A="${1:?pasta de destino (hf/assets)}"; mkdir -p "$A"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
X=(-an -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30)
baixa() { curl -sSL -A "Mozilla/5.0" -o "$T/$2.mp4" "https://assets.mixkit.co/videos/$1/$1-720.mp4"; }
filtro() { python3 "$RAIZ/ferramentas/filtro_clipe.py" "$@" >/dev/null; }

# gancho (dividida): homem ofegante, boca aberta, depois de esforço — "o exercício mais perigoso para o seu coração"
baixa 21955 gancho
ffmpeg -v error -y -ss 7.0 -t 2.3 -i "$T/gancho.mp4" -vf "scale=-2:980:flags=lanczos,crop=1080:980:(iw-1080)*0.1:0" "${X[@]}" "$A/gancho.mp4"
# homem no sofá com pipoca e controle (cartão) — "passa a maior parte da semana sem atividade física"
baixa 9252 sofa
ffmpeg -v error -y -ss 0 -t 2.5 -i "$T/sofa.mp4" -vf "scale=-2:800:flags=lanczos,crop=840:800:(iw-840)*0.13:0" "${X[@]}" "$A/sofa.mp4"
# homem entediado no escritório (dividida) — "passa a semana inteira parada"
baixa 33259 escritorio
ffmpeg -v error -y -ss 0.5 -t 2.8 -i "$T/escritorio.mp4" -vf "scale=-2:980:flags=lanczos,crop=1080:980:0:0" "${X[@]}" "$A/escritorio.mp4"
# amigos chegando para jogar futebol (cartão largo 960×620) — "no domingo resolve jogar uma partida de futebol"
baixa 4567 futebol
ffmpeg -v error -y -ss 1 -t 2.5 -i "$T/futebol.mp4" -vf "scale=-2:620:flags=lanczos,crop=960:620:(iw-960)*0.5:0" "${X[@]}" "$A/futebol.mp4"
# corredor para e se curva sem fôlego (dividida) — "correr ou fazer um exercício intenso de uma hora"
baixa 723 corrida
ffmpeg -v error -y -ss 3.6 -t 2.4 -i "$T/corrida.mp4" -vf "scale=-2:980:flags=lanczos,crop=1080:980:(iw-1080)*0.95:0" "${X[@]}" "$A/corrida.mp4"

filtro desfoque "$A/gancho.mp4" -o "$A/gancho_fx.mp4" --forca 1.2 --brilho 1.3
filtro desfoque "$A/escritorio.mp4" -o "$A/escritorio_fx.mp4" --forca 1.2
filtro desfoque "$A/corrida.mp4" -o "$A/corrida_fx.mp4" --forca 1.2 --brilho 1.5
for c in sofa futebol; do filtro tv "$A/$c.mp4" -o "$A/${c}_fx.mp4"; done
echo "clipes prontos em $A"
