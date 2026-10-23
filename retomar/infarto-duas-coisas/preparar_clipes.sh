#!/usr/bin/env bash
# Prepara os clipes do vídeo "o infarto odeia quem para de fazer essas duas coisas".
#   tela dividida 1080×980 (desfoque) · cartão 840×800 (tv) · faixas do trio 1000×340 (tv)
# Mixkit 33767 (licença gratuita do Mixkit) e Pixabay (licença livre).
# Uso: bash retomar/infarto-duas-coisas/preparar_clipes.sh videos/x/edit/clipes_brutos videos/x/edit/hf/assets
set -euo pipefail
B=${1:?brutos}; A=${2:?assets}
RAIZ=$(cd "$(dirname "$0")" && git rev-parse --show-toplevel 2>/dev/null || echo /home/user/Projeto-v-deo-)
X=(-an -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30)
pixabay() { [ -f "$B/$2.mp4" ] || python3 "$RAIZ/ferramentas/buscar_clipes.py" --id "$1" -o "$B/$2.mp4" >/dev/null; }
mixkit() { [ -f "$B/$2.mp4" ] || curl -sSL -A "Mozilla/5.0" -o "$B/$2.mp4" "https://assets.mixkit.co/videos/$1/$1-720.mp4"; }
filtro() { python3 "$RAIZ/ferramentas/filtro_clipe.py" "$@" >/dev/null; }
mkdir -p "$B" "$A"

# gancho (dividida): senhora com a mão no peito, sentindo dor de infarto — "o infarto odeia…" (Mixkit 33767)
mixkit 33767 infarto
ffmpeg -v error -y -ss 0 -t 3.2 -i "$B/infarto.mp4" -vf "scale=-2:980:flags=lanczos,crop=1080:980:(iw-1080)*0.16:0" "${X[@]}" "$A/infarto.mp4"
# trio "caminhar mais, subir escadas, se movimentar durante o dia": pernas caminhando, homem
# subindo a escadaria, aula de idosos se mexendo (os dois primeiros já aprovados no forca-pernas)
pixabay 3171 pernas
pixabay 152203 escada
pixabay 32937 aula
ffmpeg -v error -y -ss 1.6 -t 4.6 -i "$B/pernas.mp4" -vf "scale=1000:-2,crop=1000:340:0:(ih-340)*0.62" "${X[@]}" "$A/pernas.mp4"
ffmpeg -v error -y -ss 1.0 -t 3.6 -i "$B/escada.mp4" -vf "scale=1000:-2,crop=1000:340:0:(ih-340)*0.62" "${X[@]}" "$A/escada.mp4"
ffmpeg -v error -y -ss 5.0 -t 2.6 -i "$B/aula.mp4" -vf "scale=1000:-2,crop=1000:340:0:(ih-340)*0.45" "${X[@]}" "$A/aula.mp4"
# homem fumando (dividida) — "o cigarro agrede…"
pixabay 139472 fumando
ffmpeg -v error -y -ss 2.8 -t 2.0 -i "$B/fumando.mp4" -vf "scale=-2:980:flags=lanczos,crop=1080:980:(iw-1080)*0.5:0" "${X[@]}" "$A/fumando.mp4"
# vasos sanguíneos acesos no corpo (cartão) — "os vasos sanguíneos"
pixabay 57691 vasos
ffmpeg -v error -y -ss 0.3 -t 2.0 -i "$B/vasos.mp4" -vf "scale=-2:800:flags=lanczos,crop=840:800:(iw-840)*0.5:0" "${X[@]}" "$A/vasos.mp4"

filtro desfoque "$A/infarto.mp4" -o "$A/infarto_fx.mp4" --forca 1.2
filtro desfoque "$A/fumando.mp4" -o "$A/fumando_fx.mp4" --forca 0.35 --brilho 1.3   # com 1.2 o cigarro some
filtro tv "$A/pernas.mp4" -o "$A/pernas_fx.mp4" --brilho 1.4
for c in escada aula vasos; do filtro tv "$A/$c.mp4" -o "$A/${c}_fx.mp4"; done
rm -f "$A/infarto.mp4" "$A/fumando.mp4" "$A/pernas.mp4" "$A/escada.mp4" "$A/aula.mp4" "$A/vasos.mp4"
echo "clipes prontos em $A"
