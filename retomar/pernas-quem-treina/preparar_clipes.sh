#!/usr/bin/env bash
# Prepara os clipes do vídeo "perna de quem treina × quem não treina" (videos/v4).
#   cartão 840×800 (tv) · tela cheia 1080×1920 (lente)
# Compras e levantar: Mixkit 720p (licença gratuita). Halteres: Pixabay 302441 (mesmo do forca-pernas).
# foto70: recorte da PRÓPRIA imagem do usuário (a coxa de 70 anos que não treina, aos 4,5 s do fonte).
# Uso: bash retomar/pernas-quem-treina/preparar_clipes.sh videos/v4/edit/hf/assets videos/v4/fonte.mp4
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
A="${1:?pasta de destino (hf/assets)}"; FONTE="${2:?vídeo fonte do usuário}"; mkdir -p "$A"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
X=(-an -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30)
mixkit() { curl -sSL -A "Mozilla/5.0" -o "$T/$2.mp4" "https://assets.mixkit.co/videos/$1/$1-720.mp4"; }
filtro() { python3 "$RAIZ/ferramentas/filtro_clipe.py" "$@" >/dev/null; }

# casal carregando sacolas de compras (cartão) — "carrega a própria compra"
mixkit 25379 compras
ffmpeg -v error -y -ss 0.2 -t 2.3 -i "$T/compras.mp4" -vf "scale=-2:800:flags=lanczos,crop=840:800:(iw-840)*0.5:0" "${X[@]}" "$A/compras.mp4"
# senhor levantando da poltrona com dificuldade (cartão) — "quem não treina… perde isso aos poucos"
mixkit 12866 levantar
ffmpeg -v error -y -ss 0.6 -t 2.8 -i "$T/levantar.mp4" -vf "scale=-2:800:flags=lanczos,crop=840:800:(iw-840)*0.45:0" "${X[@]}" "$A/levantar.mp4"
# esqueleto levantando halteres (tela cheia) — "acha que treino de força é coisa de gente nova"
python3 "$RAIZ/ferramentas/buscar_clipes.py" --id 302441 -o "$T/halteres.mp4" >/dev/null
ffmpeg -v error -y -ss 2 -t 3.4 -i "$T/halteres.mp4" -vf "crop=1300:2160:(iw-1300)/2:0,scale=1080:-2,pad=1080:1920:0:(oh-ih)/2:black" "${X[@]}" "$A/halteres.mp4"
# a foto do usuário (coxa de 70 anos sem treino) num cartão com zoom lento — "essa foto não é o seu destino"
ffmpeg -v error -y -ss 4.5 -i "$FONTE" -frames:v 1 -vf "crop=640:760:1146-320:1779-380,pad=840:800:100:20:black" "$T/foto70.png"
ffmpeg -v error -y -loop 1 -t 1.3 -i "$T/foto70.png" -vf "zoompan=z='1+0.05*on/39':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=840x800:fps=30" -t 1.3 "${X[@]}" "$A/foto70.mp4"

for c in compras levantar foto70; do filtro tv "$A/$c.mp4" -o "$A/${c}_fx.mp4"; done
filtro lente "$A/halteres.mp4" -o "$A/halteres_fx.mp4"
echo "clipes prontos em $A"
