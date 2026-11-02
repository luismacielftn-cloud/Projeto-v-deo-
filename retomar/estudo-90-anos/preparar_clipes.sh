#!/usr/bin/env bash
# Prepara os clipes do vídeo "o melhor remédio para passar dos 60, 70 anos" (estudo dos idosos de 90 anos).
#   tela dividida 1080×980 (desfoque) · cartão 840×800 (tv)
# Pixabay (licença livre) e Mixkit 12866 (licença gratuita do Mixkit), quase todos já aprovados em vídeos anteriores.
# Uso: bash retomar/estudo-90-anos/preparar_clipes.sh videos/x/edit/clipes_brutos videos/x/edit/hf/assets videos/x/estudo.jpg
set -euo pipefail
B=${1:?brutos}; A=${2:?assets}; ESTUDO=${3:?print do estudo}
RAIZ=$(cd "$(dirname "$0")" && git rev-parse --show-toplevel 2>/dev/null || echo /home/user/Projeto-v-deo-)
X=(-an -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30)
pixabay() { [ -f "$B/$2.mp4" ] || python3 "$RAIZ/ferramentas/buscar_clipes.py" --id "$1" -o "$B/$2.mp4" >/dev/null; }
mixkit() { [ -f "$B/$2.mp4" ] || curl -sSL -A "Mozilla/5.0" -o "$B/$2.mp4" "https://assets.mixkit.co/videos/$1/$1-720.mp4"; }
filtro() { python3 "$RAIZ/ferramentas/filtro_clipe.py" "$@" >/dev/null; }
mkdir -p "$B" "$A"

# gancho (dividida): cuidadora segurando a perna de uma senhora na cadeira de rodas — "sem depender de ninguém"
pixabay 229071 gancho
ffmpeg -v error -y -ss 4 -t 3.0 -i "$B/gancho.mp4" -vf "scale=-2:980,crop=1080:980:(iw-1080)*0.12:0" "${X[@]}" "$A/gancho.mp4"
# cápsulas de remédio (cartão) — "nenhuma farmácia te vende"
pixabay 5448 remedios
ffmpeg -v error -y -ss 0 -t 1.6 -i "$B/remedios.mp4" -vf "scale=-2:800,crop=840:800:(iw-840)*0.25:0" "${X[@]}" "$A/remedios.mp4"
# coxa em corte realista (cartão): 30 × 70 anos, a de 70 vira músculo tomado de gordura — "perder músculo"
python3 "$RAIZ/ferramentas/secao_musculo.py" -o "$A/coxa.mp4" --dur 2.4 --muda 0.5 >/dev/null
# senhor levantando da poltrona com dificuldade (dividida) — "precisar de ajuda pra levantar da cadeira"
mixkit 12866 levantar
ffmpeg -v error -y -ss 0.4 -t 2.6 -i "$B/levantar.mp4" -vf "scale=-2:980:flags=lanczos,crop=1080:980:(iw-1080)*0.45:0" "${X[@]}" "$A/levantar.mp4"
# homem adulto treinando com kettlebell (cartão) — "treino de força": a subida do peso cai no "força".
# O usuário recusou o esqueleto com halteres ("coloca uma pessoa fazendo exercício"). O agachamento com
# barra do Pixabay 148204 ficou um close das costas de uma moça jovem. Os bancos não têm idoso treinando força.
mixkit 4506 kettlebell
ffmpeg -v error -y -ss 6.9 -t 1.6 -i "$B/kettlebell.mp4" -vf "scale=-2:800:flags=lanczos,crop=840:800:(iw-840)*0.32:0" "${X[@]}" "$A/treino.mp4"
# agachamento em casa com elástico (cartão) — "o seu corpo fabricando o próprio remédio" (Mixkit 21273)
mixkit 21273 agachamento
ffmpeg -v error -y -ss 8.3 -t 3.9 -i "$B/agachamento.mp4" -vf "setpts=PTS/1.4,scale=-2:800:flags=lanczos,crop=840:800:(iw-840)*0.55:0" "${X[@]}" -t 2.8 "$A/agachamento.mp4"
# casal idoso caminhando de mãos dadas (cartão) — "chegando nos 80 com as próprias pernas"
pixabay 365401 casal
ffmpeg -v error -y -ss 0 -t 3.0 -i "$B/casal.mp4" -vf "scale=-2:800,crop=840:800:(iw-840)*0.5:0" "${X[@]}" "$A/casal.mp4"

filtro desfoque "$A/gancho.mp4" -o "$A/gancho_fx.mp4" --forca 1.2
filtro desfoque "$A/levantar.mp4" -o "$A/levantar_fx.mp4" --forca 1.2
for c in remedios agachamento casal; do filtro tv "$A/$c.mp4" -o "$A/${c}_fx.mp4"; done
filtro tv "$A/coxa.mp4" -o "$A/coxa_fx.mp4" --brilho 1.2
filtro tv "$A/treino.mp4" -o "$A/treino_fx.mp4" --brilho 1.45   # academia escura e camiseta preta

# Cartão do estudo (janela no alto, 994×408): o print do usuário + faixa escura com a tradução.
# O marca-texto dourado passa em "nonagenarians" (x 52–548, y 140–198 do print) em MARCA s.
FONTES="$RAIZ/modelos/estilo-referencia/assets"
MARCA=1.22; D=5.4
# (o drawbox não anima a largura: a faixa amarela entra deslizando por baixo de uma máscara branca)
ffmpeg -v error -y -i "$ESTUDO" -f lavfi -t $D -i "color=c=white:s=1290x390:r=30" -f lavfi -t $D -i "color=c=0xF2C94C:s=496x58:r=30" -filter_complex "
  [0:v]scale=1290:390,format=gbrp,loop=loop=-1:size=1,trim=duration=$D,fps=30[print];
  [1:v][2:v]overlay=x='52-496+min(496,max(0,(t-$MARCA)*1500))':y=140,drawbox=x=0:y=0:w=52:h=390:color=white:t=fill,format=gbrp[luz];
  [print][luz]blend=all_mode=multiply,format=yuv420p,
  pad=1290:530:0:0:color=0x111111,
  drawtext=fontfile=$FONTES/Inter-Bold.otf:text='Treino de força intenso em idosos de 90 anos':fontsize=50:fontcolor=white:x=40:y=412,
  drawtext=fontfile=$FONTES/Inter-Medium.otf:text='Fiatarone et al. · JAMA, 1990':fontsize=38:fontcolor=0xF2C94C:x=40:y=474,
  scale=994:408:flags=lanczos" -t $D "${X[@]}" "$A/estudo.mp4"
rm -f "$A/gancho.mp4" "$A/levantar.mp4" "$A/remedios.mp4" "$A/agachamento.mp4" "$A/casal.mp4" "$A/coxa.mp4" "$A/treino.mp4"
echo "clipes prontos em $A"
