"""Coleta das fontes oficiais e divisão em trechos (um trecho = um artigo).

Uso:
    python -m src.base_conhecimento --coletar   # baixa o HTML oficial para base/raw/
    python -m src.base_conhecimento --montar    # gera base/trechos.jsonl a partir de base/raw/

O arquivo base/fontes.csv lista cada fonte com URL oficial, licença e quais
artigos entram na base (coluna `artigos`, ex.: "1-3;53-62"; vazio = todos).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from dataclasses import dataclass, asdict

from .config import ARQ_FONTES, ARQ_TRECHOS, DIR_RAW

MAX_CHARS_TRECHO = 1500   # artigos maiores são divididos em partes
# "(?![.\d]\d)" evita casar "Art. 1.783-A" (artigo de OUTRA lei citado no texto)
RE_ARTIGO = re.compile(r"^Art\.?\s*(\d+)(?![.\d]\d)\s*(?:[ºo°]\.?)?\s*(-\s*[A-Z])?\s*[\.\-–]?\s*", re.IGNORECASE)
RE_LIXO = re.compile(r"^(Vigência( encerrada)?|Regulamento|[IVXL]{1,4}|Mensagem de veto)$", re.IGNORECASE)
RE_INCISO = re.compile(r"^[IVXLC]+\s*[-–]")
RE_ALINEA = re.compile(r"^[a-z]\)")
RE_PENA = re.compile(r"^(Infração|Penalidade|Medida administrativa)\b")
RE_TITULO = re.compile(r"^(CAPÍTULO|CAPITULO|TÍTULO|TITULO|SEÇÃO|SECAO|Seção|Capítulo|Título)\b")
RE_NOTA = re.compile(r"\((?:Redação dada|Incluíd[oa]|Revogad[oa]|Vide|Vigência|Regulamento|Acrescid[oa]|Renumerad[oa])[^)]*\)", re.IGNORECASE)


@dataclass
class Trecho:
    id: str
    fonte_id: str
    fonte: str
    artigo: str
    secao: str
    texto: str
    url: str


# ---------------------------------------------------------------------------
# Leitura do catálogo de fontes
# ---------------------------------------------------------------------------
def ler_fontes() -> list[dict]:
    with open(ARQ_FONTES, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def artigos_permitidos(spec: str) -> set[int] | None:
    """"1-3;53-62" -> {1,2,3,53,...,62}. Vazio -> None (todos)."""
    spec = (spec or "").strip()
    if not spec:
        return None
    nums: set[int] = set()
    for parte in spec.split(";"):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-")
            nums.update(range(int(a), int(b) + 1))
        elif parte:
            nums.add(int(parte))
    return nums


# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------
def coletar(timeout: int = 60) -> None:
    import requests

    DIR_RAW.mkdir(parents=True, exist_ok=True)
    for fonte in ler_fontes():
        destino = DIR_RAW / f"{fonte['id']}.html"
        if destino.exists():
            print(f"[ok] {fonte['id']} já existe")
            continue
        r = requests.get(fonte["url"], timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        if not r.encoding or r.encoding.lower() == "iso-8859-1":
            r.encoding = r.apparent_encoding
        destino.write_text(r.text, encoding="utf-8")
        print(f"[baixado] {fonte['id']} ({len(r.text):,} caracteres)")


# ---------------------------------------------------------------------------
# HTML -> linhas de texto limpas
# ---------------------------------------------------------------------------
def html_para_linhas(html: str) -> list[str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    # Texto riscado no Planalto = redação revogada/substituída: não entra na base.
    for tag in soup.find_all(["strike", "s", "del", "script", "style"]):
        tag.decompose()
    for tag in soup.find_all(style=re.compile(r"line-through", re.IGNORECASE)):
        tag.decompose()
    linhas = []
    for bloco in soup.find_all(["p", "div", "li", "h1", "h2", "h3", "h4", "td"]):
        if bloco.find(["p", "div", "li", "td"]):   # evita duplicar blocos aninhados
            continue
        txt = bloco.get_text(" ", strip=True)
        txt = unicodedata.normalize("NFC", txt)
        txt = RE_NOTA.sub("", txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        # "Art. 1 o" / "§ 2 o" / "n o" (ordinais em <sup> no Planalto) -> "Art. 1º", "§ 2º", "nº"
        txt = re.sub(r"(\d) o\b", r"\1º", txt)
        txt = re.sub(r"\bn o s\b", "nºs", txt)
        txt = re.sub(r"\bn o\b", "nº", txt)
        txt = re.sub(r"\s+([,;.])", r"\1", txt)
        txt = re.sub(r"\s+(Vigência|Regulamento)$", "", txt)
        if txt and re.search(r"\w", txt) and not RE_LIXO.match(txt):
            linhas.append(txt)
    return linhas


def _dividir(texto: str, limite: int = MAX_CHARS_TRECHO) -> list[str]:
    """Divide artigos longos em partes, respeitando parágrafos/incisos.

    - linhas "Infração/Penalidade/Medida" ficam junto do inciso a que pertencem (CTB);
    - a partir da 2ª parte, o caput do artigo é repetido no início, para o trecho
      continuar compreensível sozinho (ex.: "Art. 181. Estacionar o veículo: [...]").
    """
    if len(texto) <= limite:
        return [texto]
    linhas = texto.split("\n")
    blocos: list[str] = []
    for linha in linhas:
        if blocos and RE_PENA.match(linha):
            blocos[-1] += "\n" + linha
        else:
            blocos.append(linha)
    corta = lambda x, n: x if len(x) <= n else x[:n] + "…"
    caput = corta(linhas[0], 300)
    partes, atual, inciso = [], "", None
    for b in blocos:
        if atual and len(atual) + len(b) + 1 > limite:
            partes.append(atual.strip())
            atual = caput + " [...]\n"
            # parte começando no meio das alíneas: repete o inciso-pai (ex.: "I - faixa livre ...")
            if inciso and RE_ALINEA.match(b):
                atual += corta(inciso, 200) + " [...]\n"
        if RE_INCISO.match(b):
            inciso = b.split("\n")[0]
        elif re.match(r"^(§|Parágrafo)", b):
            inciso = None
        atual += b + "\n"
    if atual.strip():
        partes.append(atual.strip())
    return partes


def linhas_para_trechos(linhas: list[str], fonte: dict) -> list[Trecho]:
    permitidos = artigos_permitidos(fonte.get("artigos", ""))
    trechos: list[Trecho] = []
    secao, art_atual, buffer = "", None, []

    def fechar():
        if art_atual is None or not buffer:
            return
        num = int(re.match(r"\d+", art_atual).group())
        if permitidos is not None and num not in permitidos:
            return
        texto = "\n".join(buffer).strip()
        if re.search(r"^Art\.?\s*\d+\S*\s*\(?\s*(VETADO|Revogado)", texto, re.IGNORECASE):
            return
        partes = _dividir(texto)
        for i, parte in enumerate(partes, 1):
            sufixo = f"-p{i}" if len(partes) > 1 else ""
            trechos.append(Trecho(
                id=f"{fonte['id']}-art{art_atual.lower()}{sufixo}",
                fonte_id=fonte["id"],
                fonte=fonte["titulo"],
                artigo=f"Art. {art_atual}" + (f" (parte {i})" if len(partes) > 1 else ""),
                secao=secao,
                texto=parte,
                url=fonte["url"],
            ))

    for linha in linhas:
        m = RE_ARTIGO.match(linha)
        if m:
            fechar()
            art_atual = m.group(1) + (m.group(2).replace(" ", "") if m.group(2) else "")
            buffer = [linha]
        elif RE_TITULO.match(linha):
            fechar()
            art_atual, buffer = None, []
            secao = linha
        elif art_atual is not None:
            # Fim do corpo normativo (assinaturas, data) encerra o último artigo.
            if re.match(r"^(Brasília|PREFEITURA DO MUNICÍPIO|São Paulo, aos)", linha):
                fechar()
                art_atual, buffer = None, []
                continue
            buffer.append(linha)
        elif secao and not art_atual and len(linha) < 120 and linha.isupper():
            secao = f"{secao} – {linha}"
    fechar()
    return trechos


def montar() -> list[Trecho]:
    todos: list[Trecho] = []
    for fonte in ler_fontes():
        html = (DIR_RAW / f"{fonte['id']}.html").read_text(encoding="utf-8")
        trechos = linhas_para_trechos(html_para_linhas(html), fonte)
        # ids únicos (algumas leis repetem número de artigo em anexos)
        vistos: dict[str, int] = {}
        for t in trechos:
            if t.id in vistos:
                vistos[t.id] += 1
                t.id = f"{t.id}-{vistos[t.id]}"
            else:
                vistos[t.id] = 1
        print(f"{fonte['id']:>10}: {len(trechos):4d} trechos")
        todos.extend(trechos)
    with open(ARQ_TRECHOS, "w", encoding="utf-8") as f:
        for t in todos:
            f.write(json.dumps(asdict(t), ensure_ascii=False) + "\n")
    print(f"Total: {len(todos)} trechos -> {ARQ_TRECHOS}")
    return todos


def carregar_trechos() -> list[dict]:
    with open(ARQ_TRECHOS, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--coletar", action="store_true")
    ap.add_argument("--montar", action="store_true")
    a = ap.parse_args()
    if a.coletar:
        coletar()
    if a.montar:
        montar()
