#!/usr/bin/env bash
# Rebaixa do Pixabay e prepara os 9 clipes do vídeo "treino de força depois dos 45"
# exatamente como foram usados (trecho, recorte no tamanho do formato e filtro).
# Também serve de exemplo de como preparar clipes para os formatos do modelo:
#   tela dividida 1080×980 · cartão 840×800 (ou 960×620) · tela cheia 1080×1920
#
# Uso: bash retomar/treino-forca/preparar_clipes.sh videos/novo/edit/hf/assets
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
A="${1:?pasta de destino (hf/assets)}"; mkdir -p "$A"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
X=(-an -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30)
baixa() { python3 "$RAIZ/ferramentas/buscar_clipes.py" --id "$1" -o "$T/$2.mp4" >/dev/null; }
filtro() { python3 "$RAIZ/ferramentas/filtro_clipe.py" "$@" >/dev/null; }

# gancho (0–2,4 s, tela dividida): mulher no espelho preocupada com rugas
baixa 293081 gancho
ffmpeg -v error -y -ss 5.5 -t 2.6 -i "$T/gancho.mp4" -vf "scale=-2:980,crop=1080:980:(iw-1080)*0.29:0" "${X[@]}" "$A/gancho.mp4"
# retrato de senhora (cartão)
baixa 319064 senhora
ffmpeg -v error -y -ss 1.0 -t 1.9 -i "$T/senhora.mp4" -vf "scale=-2:800,crop=840:800:min(iw-840\,iw*0.6-420):0" "${X[@]}" "$A/senhora.mp4"
# academia com barra (tela dividida)
baixa 169590 academia
ffmpeg -v error -y -ss 2.0 -t 2.5 -i "$T/academia.mp4" -vf "scale=-2:980,crop=1080:980:(iw-1080)*0.2:0" "${X[@]}" "$A/academia.mp4"
# esqueleto caminhando: câmera lenta 0,7× e pan acompanhando (tela dividida)
baixa 84708 esqueleto
ffmpeg -v error -y -ss 0.15 -t 1.9 -i "$T/esqueleto.mp4" -vf "setpts=PTS/0.7,scale=-2:980,crop=1080:980:'min(662,662*t/2.6)':0" "${X[@]}" -t 2.65 "$A/esqueleto.mp4"
# mão pegando a mala na esteira (cartão), clareado
baixa 5628 mala
ffmpeg -v error -y -ss 4.4 -t 3.4 -i "$T/mala.mp4" -vf "scale=-2:800,crop=840:800,eq=brightness=0.06:gamma=1.15" "${X[@]}" "$A/mala_cartao.mp4"
# pés no gelo, "escorrega" (tela dividida)
baixa 381755 gelo
ffmpeg -v error -y -ss 3.0 -t 3.0 -i "$T/gelo.mp4" -vf "scale=-2:980,crop=1080:980:(iw-1080):0" "${X[@]}" "$A/gelo.mp4"
# ilustração do joelho (tela cheia), base escurecida para a legenda
baixa 4364 joelho
ffmpeg -v error -y -ss 2.0 -t 2.0 -i "$T/joelho.mp4" -vf "scale=-2:1920,crop=1080:1920:(iw-1080)*0.42:0,format=gbrp,geq=r='r(X\,Y)*(1-0.5*clip((Y-1150)/450\,0\,1))':g='g(X\,Y)*(1-0.5*clip((Y-1150)/450\,0\,1))':b='b(X\,Y)*(1-0.5*clip((Y-1150)/450\,0\,1))',format=yuv420p" "${X[@]}" "$A/joelho.mp4"
# agachamento com barra (tela cheia)
baixa 148204 treino
ffmpeg -v error -y -ss 0 -t 3.4 -i "$T/treino.mp4" -vf "scale=-2:1920,crop=1080:1920" "${X[@]}" "$A/treino.mp4"
# avó e neta, ilustração (cartão largo 960×620)
baixa 265617 avo
ffmpeg -v error -y -ss 2.0 -t 1.8 -i "$T/avo.mp4" -vf "scale=-2:620,crop=960:620" "${X[@]}" "$A/avo_cartao.mp4"

# filtros no estilo @elias.maman: desfoque na dividida, tv no cartão, lente na tela cheia
for c in gancho academia esqueleto gelo; do filtro desfoque "$A/$c.mp4" -o "$A/${c}_fx.mp4" --forca 1.2; done
filtro tv "$A/senhora.mp4" -o "$A/senhora_fx.mp4"
filtro tv "$A/mala_cartao.mp4" -o "$A/mala_cartao_fx.mp4" --brilho 1.7
filtro tv "$A/avo_cartao.mp4" -o "$A/avo_cartao_fx.mp4"
for c in joelho treino; do filtro lente "$A/$c.mp4" -o "$A/${c}_fx.mp4"; done
echo "clipes prontos em $A"
