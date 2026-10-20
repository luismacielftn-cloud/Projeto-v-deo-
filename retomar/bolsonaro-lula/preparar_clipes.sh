#!/usr/bin/env bash
# Prepara os clipes do vídeo "Bolsonaro mandou matar Lula" (Pixabay, licença livre).
# Uso: bash retomar/bolsonaro-lula/preparar_clipes.sh videos/x/edit/clipes_brutos videos/x/edit/hf/assets [foto do gancho]
set -euo pipefail
B=${1:?brutos}; A=${2:?assets}
RAIZ=$(cd "$(dirname "$0")" && git rev-parse --show-toplevel 2>/dev/null || echo /home/user/Projeto-v-deo-)
F="python3 $RAIZ/ferramentas/filtro_clipe.py"
baixar() { [ -f "$B/$2.mp4" ] || python3 "$RAIZ/ferramentas/buscar_clipes.py" --id "$1" -o "$B/$2.mp4"; }
mkdir -p "$B" "$A"
baixar 149843 bandeira; baixar 112718 mastro; baixar 7315 sirene; baixar 254922 martelo

# Gancho (tela dividida 1080x980, 3,7 s): bandeira em tela cheia que racha ao meio no "ao meio"
# (1,88 s); em 2,05 s as metades se abrem para os lados e revelam a foto que o usuário mandou
# (3º argumento), com um zoom lento. Sem foto, a bandeira só racha (versão de 2,4 s).
FOTO=${3:-}
TC=1.88; TA=2.05
D=$([ -n "$FOTO" ] && echo 3.7 || echo 2.4)
ffmpeg -v error -y -ss 3 -t $D -i "$B/bandeira.mp4" -an \
  -vf "scale=-2:980,crop=1080:980,fps=30,setsar=1" -c:v libx264 -crf 16 -pix_fmt yuv420p "$A/bandeira_rec.mp4"
$F desfoque "$A/bandeira_rec.mp4" -o "$A/bandeira_fx.mp4" --forca 0.6
J="16*sin(Y/31)+9*sin(Y/9.7)+5*sin(Y/3.1)"   # borda irregular da rachadura
if [ -n "$FOTO" ]; then
  # foto no quadro de cima: fundo = a própria foto ampliada, desfocada e escura; frente = as
  # duas pessoas inteiras (recorte x 270–1330 da foto de 1600x728), com as cabeças no alto
  ffmpeg -v error -y -i "$FOTO" -filter_complex "
    [0:v]split[f0][f1];
    [f0]scale=-2:980,crop=1080:980,gblur=sigma=30,eq=brightness=-0.18[bg];
    [f1]crop=1060:728:270:0,scale=1080:-2[fg];
    [bg][fg]overlay=0:40,scale=2160:1960" -frames:v 1 "$A/foto_quadro.png"
  ffmpeg -v error -y -i "$A/foto_quadro.png" -vf "zoompan=z='if(lt(on,62),1,1+0.08*(on-62)/49)':x='iw/2-(iw/zoom/2)':y='ih*0.25-(ih/zoom*0.25)':d=111:s=1080x980:fps=30,setsar=1,format=yuv420p" \
    -frames:v 111 -c:v libx264 -crf 16 "$A/foto_zoom.mp4"
  FUNDO="[1:v]format=rgba[foto];[2:v]format=rgba,geq=r=0:g=0:b=0:a='255*max(0,min(1,1-(T-$TA)*3.3))'[preto];[foto][preto]overlay[fundo]"
  ENTRADA=(-i "$A/foto_zoom.mp4")
  N=2
else
  FUNDO="[1:v]format=rgba,geq=r=0:g=0:b=0:a=255[fundo]"
  ENTRADA=()
  N=1
fi
# a luz vermelha da fenda acende na rachadura e apaga quando as metades se abrem
SAI=$([ -n "$FOTO" ] && echo "*max(0,1-max(0,T-$TA)*4)" || echo "")
XE="if(lt(t,$TA),-min(38,max(0,t-$TC)*900),-38-$([ -n "$FOTO" ] && echo 640 || echo 0)*pow(min(1,(t-$TA)/0.36),2))"
XD="if(lt(t,$TA),min(38,max(0,t-$TC)*900),38+$([ -n "$FOTO" ] && echo 640 || echo 0)*pow(min(1,(t-$TA)/0.36),2))"
ffmpeg -v error -y -i "$A/bandeira_fx.mp4" "${ENTRADA[@]}" -f lavfi -t $D -i "color=c=black:s=1080x980:r=30" -filter_complex "
  [$N:v]drawbox=x=525:y=0:w=30:h=980:color=0xC81E14@1:t=fill,gblur=sigma=34,format=rgba,
       geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*min(1,max(0,(T-$TC)*5))$SAI'[luz];
  $(echo "$FUNDO" | sed "s/\[2:v\]/[$N:v]/; s/\[1:v\]format=rgba,geq=r=0/[$N:v]format=rgba,geq=r=0/");
  [fundo][luz]overlay[bg];
  [0:v]format=rgba,split[a][b];
  [a]geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*lt(X,540+$J)'[esq];
  [b]geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*gte(X,540+$J)'[dir];
  [bg][esq]overlay=x='$XE':y='min(10,max(0,t-$TC)*240)'[m];
  [m][dir]overlay=x='$XD':y='-min(10,max(0,t-$TC)*240)',format=yuv420p,
  pad=1120:1020:20:20,crop=1080:980:x='20+if(gt(t,$TC),14*sin((t-$TC)*95)*exp(-(t-$TC)*7),0)':y='20+if(gt(t,$TC),10*cos((t-$TC)*80)*exp(-(t-$TC)*7),0)'
" -t $D -c:v libx264 -crf 16 -pix_fmt yuv420p "$A/gancho_racha.mp4"
rm -f "$A/foto_quadro.png" "$A/foto_zoom.mp4"

# Três faixas 1000x340 (filtro TV): ex-presidente, Polícia Federal, Supremo.
ffmpeg -v error -y -ss 20 -t 3.4 -i "$B/mastro.mp4" -an -vf "scale=1000:-2,crop=1000:340:0:110,fps=30,setsar=1" -c:v libx264 -crf 16 -pix_fmt yuv420p "$A/mastro_rec.mp4"
ffmpeg -v error -y -ss 2.6 -t 2.4 -i "$B/sirene.mp4" -an -vf "scale=1300:-2,crop=1000:340:150:170,fps=30,setsar=1" -c:v libx264 -crf 16 -pix_fmt yuv420p "$A/sirene_rec.mp4"
ffmpeg -v error -y -ss 0 -t 1.4 -i "$B/martelo.mp4" -an -vf "scale=1300:-2,crop=1000:340:150:200,fps=30,setsar=1" -c:v libx264 -crf 16 -pix_fmt yuv420p "$A/martelo_rec.mp4"
$F tv "$A/mastro_rec.mp4" -o "$A/mastro_fx.mp4"
$F tv "$A/sirene_rec.mp4" -o "$A/sirene_fx.mp4" --brilho 1.3
$F tv "$A/martelo_rec.mp4" -o "$A/martelo_fx.mp4" --brilho 1.2
rm -f "$A"/*_rec.mp4 "$A/bandeira_fx.mp4"
