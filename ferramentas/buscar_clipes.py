"""Busca e baixa clipes gratuitos do Pixabay (licença livre, inclusive comercial).

Precisa de PIXABAY_API_KEY (variável de ambiente do ambiente de nuvem).
Busque em inglês: o acervo responde muito melhor ("woman waking up" em vez de
"mulher acordando").

Uso:
    python3 ferramentas/buscar_clipes.py "sunrise window" -o videos/x/edit/hf/assets/sol.mp4
    python3 ferramentas/buscar_clipes.py "phone in bed" --listar        # só mostra as opções
    python3 ferramentas/buscar_clipes.py "phone in bed" --escolha 2 -o …  # baixa a 3ª opção

Prefere clipes verticais e com resolução >= 1080 px no lado menor quando há.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://pixabay.com/api/videos/"
# O Pixabay recusa (403) o User-Agent padrão do Python.
UA = {"User-Agent": "Mozilla/5.0"}


def buscar(termo: str, por_pagina: int = 20) -> list[dict]:
    chave = os.environ.get("PIXABAY_API_KEY")
    if not chave:
        sys.exit(
            "PIXABAY_API_KEY não está definida nesta sessão. Ela é configurada nas variáveis "
            "de ambiente do ambiente de nuvem e só vale em sessões novas."
        )
    q = urllib.parse.urlencode(
        {"key": chave, "q": termo, "per_page": por_pagina, "safesearch": "true"}
    )
    with urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers=UA), timeout=30) as r:
        dados = json.load(r)
    opcoes = []
    for h in dados.get("hits", []):
        for tam in ("large", "medium"):
            v = h["videos"].get(tam) or {}
            if v.get("url"):
                opcoes.append(
                    {
                        "id": h["id"],
                        "url": v["url"],
                        "largura": v["width"],
                        "altura": v["height"],
                        "duracao": h["duration"],
                        "tags": h.get("tags", ""),
                        "pagina": h.get("pageURL", ""),
                    }
                )
                break

    def nota(o: dict) -> tuple:
        vertical = o["altura"] > o["largura"]
        nitido = min(o["largura"], o["altura"]) >= 1080
        return (vertical, nitido, -abs(o["duracao"] - 8))

    return sorted(opcoes, key=nota, reverse=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Busca e baixa clipes do Pixabay")
    ap.add_argument("termo")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--escolha", type=int, default=0)
    args = ap.parse_args()

    opcoes = buscar(args.termo)
    if not opcoes:
        sys.exit(f"nada encontrado para: {args.termo}")
    for i, o in enumerate(opcoes[:8]):
        forma = "vertical" if o["altura"] > o["largura"] else "horizontal"
        print(
            f"[{i}] {o['largura']}x{o['altura']} {forma} {o['duracao']}s  {o['tags']}"
        )
    if args.listar or not args.output:
        return
    o = opcoes[args.escolha]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(o["url"], headers=UA), timeout=120) as r, open(args.output, "wb") as f:
        f.write(r.read())
    print(f"baixado: {args.output}  (Pixabay {o['id']}, {o['pagina']})")


if __name__ == "__main__":
    main()
