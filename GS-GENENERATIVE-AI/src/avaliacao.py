"""Correção automática das respostas contra o gabarito e montagem do placar.

Definições (iguais para as três configurações):
- acerto           : pergunta que consta -> respondeu (sem recusar) e contém todos os
                     grupos de palavras-chave do gabarito; pergunta "não consta" -> recusou.
- alucinação       : afirmou algo e estava errado, OU respondeu uma pergunta que não consta.
- recusa indevida  : recusou uma pergunta cuja resposta estava na base.
- citação correta  : entre as respostas a perguntas que constam, a fonte citada aponta para
                     o artigo do gabarito (por id do trecho ou por "Lei nº + Art. nº" em texto).
- citação fora do contexto: citou id que não estava entre os trechos recuperados (só RAG).
"""
from __future__ import annotations

import json
import re

from .busca import normalizar


def carregar_jsonl(caminho) -> list[dict]:
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def salvar_jsonl(linhas: list[dict], caminho) -> None:
    with open(caminho, "w", encoding="utf-8") as f:
        for l in linhas:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")


# ----------------------------------------------------------------------
def _casa(alt: str, r: str) -> bool:
    """Busca `alt` em `r` sem casar pedaço de número ("2 m" não casa em "42 metros",
    "50" não casa em "50.000"). Palavras podem ser radicais ("proibid" casa "proibido")."""
    a = re.sub(r"\s+", " ", normalizar(alt).strip())
    esq = r"(?<![\w,.])" if a[:1].isalnum() else ""
    dir_ = r"(?!\d|\.\d|,(?!00\b)\d)" if a[-1:].isdigit() else ""   # ",00" (centavos) pode
    return re.search(esq + re.escape(a) + dir_, r) is not None


def contem_palavras_chave(resposta: str, grupos: list[list[str]]) -> bool:
    r = re.sub(r"\s+", " ", " " + normalizar(resposta) + " ")
    return all(any(_casa(alt, r) for alt in grupo) for grupo in grupos)


def _chave_trecho(trecho_id: str) -> tuple[str, str] | None:
    """'SP-D59671-art7-p2' -> ('SP-D59671', '7')."""
    m = re.match(r"(.+)-art(\d+[a-z]?)", trecho_id, re.IGNORECASE)
    return (m.group(1), re.match(r"\d+", m.group(2)).group()) if m else None


def _num_fonte(fonte_id: str) -> str:
    return re.sub(r"\D", "", fonte_id)


def resolver_citacoes(fontes: list[str], ids_validos: set[str], fontes_ids: set[str]) -> set[tuple[str, str]]:
    """Converte citações (ids ou texto livre) em pares (fonte_id, artigo)."""
    chaves = set()
    num2fonte = {_num_fonte(f): f for f in fontes_ids}
    for item in fontes:
        if item in ids_validos:
            k = _chave_trecho(item)
            if k:
                chaves.add(k)
            continue
        txt = item.lower()
        leis = [re.sub(r"\D", "", n) for n in re.findall(r"\b\d{1,2}\.?\d{3}\b", txt)]
        arts = re.findall(r"art(?:igo|\.)?\s*(\d+)", txt)
        for lei in leis:
            if lei in num2fonte:
                for a in arts:
                    chaves.add((num2fonte[lei], a))
    return chaves


def corrigir(caso: dict, saida: dict, ids_validos: set[str], fontes_ids: set[str]) -> dict:
    consta = caso["tipo"] == "consta"
    respondeu = not saida["recusa"]
    conteudo_ok = consta and respondeu and contem_palavras_chave(saida["resposta"], caso["palavras_chave"])
    acerto = conteudo_ok if consta else saida["recusa"]
    alucinacao = respondeu and (not consta or not conteudo_ok)

    cit_ok = None
    if consta and respondeu:
        gold = {_chave_trecho(t) for t in caso["trechos_gabarito"]}
        cit_ok = bool(resolver_citacoes(saida["fontes"], ids_validos, fontes_ids) & gold)

    fora = None
    if saida.get("recuperados"):
        fora = any(f not in saida["recuperados"] for f in saida["fontes"])

    return {
        "id": caso["id"], "tipo": caso["tipo"], "categoria": caso.get("categoria", ""),
        "acerto": acerto, "alucinacao": alucinacao,
        "recusa_indevida": consta and saida["recusa"],
        "json_valido": saida["json_valido"], "citacao_correta": cit_ok,
        "citacao_fora_contexto": fora, "latencia_s": saida.get("latencia_s"),
    }


def placar(correcoes: list[dict], nome: str) -> dict:
    n = len(correcoes)
    consta = [c for c in correcoes if c["tipo"] == "consta"]
    nconsta = [c for c in correcoes if c["tipo"] == "nao_consta"]
    cit = [c["citacao_correta"] for c in correcoes if c["citacao_correta"] is not None]
    fora = [c["citacao_fora_contexto"] for c in correcoes if c["citacao_fora_contexto"] is not None]
    lat = [c["latencia_s"] for c in correcoes if c["latencia_s"] is not None]
    pct = lambda xs: round(100 * sum(xs) / len(xs), 1) if xs else None
    return {
        "configuracao": nome,
        "n": n,
        "acuracia_%": pct([c["acerto"] for c in correcoes]),
        "acerto_consta_%": pct([c["acerto"] for c in consta]),
        "recusa_correta_nao_consta_%": pct([c["acerto"] for c in nconsta]),
        "alucinacao_%": pct([c["alucinacao"] for c in correcoes]),
        "recusa_indevida_%": pct([c["recusa_indevida"] for c in consta]),
        "json_valido_%": pct([c["json_valido"] for c in correcoes]),
        "citacao_correta_%": pct(cit),
        "citacao_fora_contexto_%": pct(fora),
        "latencia_media_s": round(sum(lat) / len(lat), 2) if lat else None,
    }
