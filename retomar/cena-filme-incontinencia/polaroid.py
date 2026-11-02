"""Foto da cena em moldura de polaroid inclinada, para pôr acima da cabeça na abertura."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

quadro, fonte, saida = sys.argv[1], sys.argv[2], sys.argv[3]
foto = Image.open(quadro).convert("RGB").crop((0, 20, 836, 490)).resize((480, 270), Image.LANCZOS)
borda, base = 12, 58
w, h = 480 + 2 * borda, 270 + borda + base
card = Image.new("RGBA", (w, h), (255, 255, 255, 255))
card.paste(foto, (borda, borda))
d = ImageDraw.Draw(card)
f = ImageFont.truetype(fonte, 30)
titulo = "Minha Melhor Amiga"
tw = d.textlength(titulo, font=f)
d.text(((w - tw) / 2, 270 + borda + 12), titulo, font=f, fill=(34, 34, 34, 255))
# sombra suave embaixo do cartão, para destacar da parede clara
m = 30
tela = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
sombra = Image.new("RGBA", (w, h), (0, 0, 0, 120))
tela.paste(sombra, (m + 4, m + 8))
tela = tela.filter(ImageFilter.GaussianBlur(12))
tela.alpha_composite(card, (m, m))
tela.rotate(4, resample=Image.BICUBIC, expand=True).save(saida)
print(Image.open(saida).size)
