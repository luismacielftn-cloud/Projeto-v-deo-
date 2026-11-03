"""Gancho escrito: caixa branca de cantos arredondados com texto preto (Inter Black), centralizado."""
import sys
from PIL import Image, ImageDraw, ImageFont

fonte, saida, *linhas = sys.argv[1:]
f = ImageFont.truetype(fonte, 50)
d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
larg = max(d0.textlength(l, font=f) for l in linhas)
asc, desc = f.getmetrics()
alt_linha = asc + desc + 6
px, py = 34, 22
w, h = int(larg + 2 * px), int(alt_linha * len(linhas) + 2 * py - 6)
img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle((0, 0, w - 1, h - 1), radius=26, fill=(255, 255, 255, 255))
for i, l in enumerate(linhas):
    tw = d.textlength(l, font=f)
    d.text(((w - tw) / 2, py + i * alt_linha), l, font=f, fill=(17, 17, 17, 255))
img.save(saida)
print(img.size)
