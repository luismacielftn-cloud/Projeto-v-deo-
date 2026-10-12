# Vídeo "força das pernas" ("Me dê 60 segundos…")

Edição de 2026-10-11, no mesmo formato do `retomar/treino-forca/` (o exemplo completo). Este é o segundo vídeo feito com a receita.
O vídeo em si não fica no git: se precisar refazer, peça o link do Drive ao usuário (103,4 s, 1440×2560, estúdio com luz azul).

| Arquivo | O que é |
| --- | --- |
| `edl.json` | Cortes (20 trechos, 103,4 s → 100,8 s). Aponta para `videos/v2/fonte.mp4`. |
| `transcript.json` | Transcrição do vídeo cortado, corrigida. |
| `roteiro.json` | Roteiro entregue. |
| `preparar_clipes.sh` | Rebaixa os clipes (10 do Pixabay, 1 do Mixkit), gera a coxa em corte e aplica recorte e filtro. |
| `project.md` | Diário: o que foi medido e decidido. |

## Refazer

1. `videos/v2/fonte.mp4` → `render.py videos/v2/edit/edl.json -o …/cortado_base.mp4` → congelar 1,8 s → `cortado.mp4` (102,6 s).
2. `transcript.json` e `roteiro.json` em `videos/v2/edit/hf/`; `cortado.mp4` em `hf/assets/` com `-g 30`.
3. `bash retomar/forca-pernas/preparar_clipes.sh videos/v2/edit/hf/assets`
4. `montar.py` → `lint` → `render` → `finalizar.py --mix … --entrega …`.

## Diferenças em relação ao primeiro vídeo

- **Rosto no alto do quadro:** a tela dividida usa `"descer": 820` (senão a legenda da emenda cai no cabelo); `fim_ig_y` 520.
- **Números compridos:** cena `numero` com `"tam": 210` para "10–15%".
- **Duas quedas diferentes:** cena `queda` com `marco` por linha (força cai aos 40, massa muscular aos 60): "a perda de força vem antes da perda de massa".
- **Silhueta ao contrário:** o clipe do idoso sentando foi invertido e acelerado para virar "levantando da cadeira com dificuldade".
- **Gancho escuro demais com o desfoque:** abra o recorte para mostrar mãos/rosto e use `--brilho 1.5`.

## Linha do tempo

| Tempo | Fala | Na tela |
| --- | --- | --- |
| 0–3 | "Me dê 60 segundos… força das pernas" | Gancho: dividida, perna na cadeira de rodas |
| 6,5–9,6 | "perdendo força na perna todos os dias" | Cartão: pernas caminhando |
| 10,8–12,6 | "E o pior, essa perda é silenciosa" | P&B + voz de rádio |
| 12,7–19 | "levantar da cadeira… sobe uma escada" | Dividida: silhueta levantando · Cartão: escadaria |
| 19,3–23 | "não precisa de academia lotada nem de 2 horas" | Lista × |
| 23–29 | "depois dos 40… 10 e 15% por década" | Trilha tensa · cena número **10–15%** |
| 32–34,5 | "depois dos 70… 25 a 40%" | Título **25–40%** (coral) |
| 34,6–36,7 | "estudos sobre sarcopenia" | Cartão: coxa em corte **realista** (carne vermelha aos 30 → tomada de gordura aos 70), feita com `ferramentas/secao_musculo.py` — o raio-X de músculos fortes foi recusado e depois o desenho chapado também ("mais próximo do real") |
| 36,8–41,4 | "perda de força vem antes da massa muscular" | Cena `queda` com duas idades |
| 45,9–49 | "suas pernas cansam mais rápido" | Dividida: pernas em raio-X |
| 50,7–52,2 | "isso não é coisa de idade que você tem que aceitar" | P&B + voz de rádio |
| 57–58,7 | "uma das coisas mais reversíveis" | Título **reversíveis** (verde-lima) |
| 58,7–65 | "faz comigo agora…" | Trilha inspira · lista ✓ dos 3 passos |
| 65–78 | "exercício mais usado… vida real… independência" | Dividida: agachamento em casa (Mixkit; a aula com braços para cima foi recusada) · cartão (sofá) · dividida (casal) |
| 79,6–81,4 | "dor no joelho" | Cartão: joelho |
| 85,6–90 | "não existe perna forte sem exercício de força… não é sorte, não é genética" | Frase grande (coral) · lista |
| 90,2–93,4 | "o músculo só mantém a força quando é desafiado" | Tela cheia: esqueleto com halteres |
| 97,4–102,6 | "Comenta aqui embaixo quantas vezes…" | Final "comenta aqui / **quantas vezes?**" + @ |
