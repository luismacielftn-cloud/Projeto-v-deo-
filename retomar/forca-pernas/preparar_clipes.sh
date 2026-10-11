#!/usr/bin/env bash
# Rebaixa do Pixabay e prepara os clipes do vídeo "força das pernas (60 segundos)":
# trecho, recorte no tamanho do formato e filtro no estilo @elias.maman.
#   tela dividida 1080×980 (desfoque) · cartão 840×800 (tv) · tela cheia 1080×1920 (lente)
# Uso: bash retomar/forca-pernas/preparar_clipes.sh videos/v2/edit/hf/assets
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
A="${1:?pasta de destino (hf/assets)}"; mkdir -p "$A"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
X=(-an -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30)
baixa() { python3 "$RAIZ/ferramentas/buscar_clipes.py" --id "$1" -o "$T/$2.mp4" >/dev/null; }
filtro() { python3 "$RAIZ/ferramentas/filtro_clipe.py" "$@" >/dev/null; }

# gancho (dividida): fisioterapeuta segurando a perna de uma senhora na cadeira de rodas
baixa 229071 gancho
ffmpeg -v error -y -ss 4 -t 3.1 -i "$T/gancho.mp4" -vf "scale=-2:980,crop=1080:980:(iw-1080)*0.12:0" "${X[@]}" "$A/gancho.mp4"
# pernas caminhando (cartão)
baixa 3171 pernas
ffmpeg -v error -y -ss 3.5 -t 3.2 -i "$T/pernas.mp4" -vf "scale=-2:800,crop=840:800:(iw-840)*0.5:0" "${X[@]}" "$A/pernas.mp4"
# idoso de bengala levantando da cadeira (dividida): trecho ao contrário e 2× mais rápido
baixa 215081 cadeira
ffmpeg -v error -y -ss 14 -t 6.4 -i "$T/cadeira.mp4" -vf "scale=1080:-2,crop=1080:980:0:(ih-980)*0.62,reverse,setpts=PTS/2" "${X[@]}" -t 3.1 "$A/cadeira.mp4"
# escadaria (cartão)
baixa 152203 escada
ffmpeg -v error -y -ss 1 -t 3.4 -i "$T/escada.mp4" -vf "scale=-2:800,crop=840:800:(iw-840)*0.5:0" "${X[@]}" "$A/escada.mp4"
# "sarcopenia" (cartão): coxa em corte realista (fotos em modelos/estilo-referencia/assets/sarcopenia/),
# a de 70 anos vira músculo tomado de gordura.
# (O clipe de banco de músculos fortes foi recusado: precisa mostrar PERDA de músculo.)
python3 "$RAIZ/ferramentas/secao_musculo.py" -o "$A/sarcopenia_ilustra.mp4" --dur 2.2 --muda 0.5 >/dev/null
# músculos das pernas em raio-X (dividida)
baixa 57691 pernas_raiox
ffmpeg -v error -y -ss 9.5 -t 3.3 -i "$T/pernas_raiox.mp4" -vf "scale=-2:980,crop=1080:980:(iw-1080)*0.5:0" "${X[@]}" "$A/pernas_raiox.mp4"
# aula de idosos com as cadeiras atrás (tela cheia)
baixa 32937 aula
ffmpeg -v error -y -ss 2 -t 4.2 -i "$T/aula.mp4" -vf "scale=-2:1920,crop=1080:1920:(iw-1080)*0.55:0" "${X[@]}" "$A/aula.mp4"
# senhora no sofá (cartão) — "o que você faz várias vezes por dia"
baixa 298667 sofa
ffmpeg -v error -y -ss 2 -t 3.8 -i "$T/sofa.mp4" -vf "scale=-2:800,crop=840:800:(iw-840)*0.32:0" "${X[@]}" "$A/sofa.mp4"
# casal idoso caminhando (dividida) — "independência"
baixa 365401 casal
ffmpeg -v error -y -ss 0 -t 4.6 -i "$T/casal.mp4" -vf "scale=-2:980,crop=1080:980:(iw-1080)*0.5:0" "${X[@]}" "$A/casal.mp4"
# ilustração do joelho (cartão) — "dor no joelho"
baixa 4364 joelho
ffmpeg -v error -y -ss 2 -t 1.9 -i "$T/joelho.mp4" -vf "scale=-2:800,crop=840:800:(iw-840)*0.45:0" "${X[@]}" "$A/joelho.mp4"
# esqueleto levantando halteres (tela cheia, quadro inteiro sobre preto)
baixa 302441 halteres
ffmpeg -v error -y -ss 2 -t 3.4 -i "$T/halteres.mp4" -vf "crop=1300:2160:(iw-1300)/2:0,scale=1080:-2,pad=1080:1920:0:(oh-ih)/2:black" "${X[@]}" "$A/halteres.mp4"

filtro desfoque "$A/gancho.mp4" -o "$A/gancho_fx.mp4" --forca 1.2 --brilho 1.5
for c in cadeira pernas_raiox casal; do filtro desfoque "$A/$c.mp4" -o "$A/${c}_fx.mp4" --forca 1.2; done
for c in pernas escada sofa joelho; do filtro tv "$A/$c.mp4" -o "$A/${c}_fx.mp4"; done
filtro tv "$A/sarcopenia_ilustra.mp4" -o "$A/sarcopenia_ilustra_fx.mp4" --brilho 1.2
for c in aula halteres; do filtro lente "$A/$c.mp4" -o "$A/${c}_fx.mp4"; done
echo "clipes prontos em $A"
