"""Busca de trechos: TF-IDF (lexical), denso (embeddings e5) ou híbrido.

O score do 1º resultado é comparado com um limiar: abaixo dele o sistema
responde "não consta" sem nem chamar a LLM (primeira barreira contra alucinação).
"""
from __future__ import annotations

import json
import re
import unicodedata

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import ARQ_LIMIAR, EMB_ID, LIMIAR_PADRAO, TOP_K

STOPWORDS = set("""a o as os um uma uns umas de do da dos das em no na nos nas por pelo pela pelos pelas
para pra com sem sob sobre entre ate e ou que se ao aos à às é ser sao são foi como qual quais quando onde
mais menos muito pouco ja já nao não sim lhe isso isto essa esse esta este meu minha seu sua""".split())


def normalizar(txt: str) -> str:
    txt = unicodedata.normalize("NFD", txt.lower())
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9,\.\s]", " ", txt)


def texto_indexavel(t: dict) -> str:
    return f"{t['fonte']} {t['artigo']} {t.get('secao', '')}\n{t['texto']}"


class Buscador:
    def __init__(self, trechos: list[dict], modo: str = "hibrido", peso_denso: float = 0.7,
                 modelo_emb=None):
        assert modo in {"tfidf", "denso", "hibrido"}
        self.trechos = trechos
        self.modo = modo
        self.peso_denso = peso_denso
        docs = [texto_indexavel(t) for t in trechos]

        self.tfidf = TfidfVectorizer(preprocessor=normalizar, stop_words=list(STOPWORDS),
                                     ngram_range=(1, 2), sublinear_tf=True, min_df=1)
        self.m_tfidf = self.tfidf.fit_transform(docs)

        self.emb = None
        if modo in {"denso", "hibrido"}:
            if modelo_emb is None:
                from sentence_transformers import SentenceTransformer
                modelo_emb = SentenceTransformer(EMB_ID)
            self.emb = modelo_emb
            # e5 exige os prefixos "passage: " / "query: "
            self.m_denso = self.emb.encode([f"passage: {d}" for d in docs],
                                           normalize_embeddings=True, batch_size=32,
                                           show_progress_bar=False)

    # ------------------------------------------------------------------
    def _scores(self, pergunta: str) -> np.ndarray:
        s_lex = (self.m_tfidf @ self.tfidf.transform([pergunta]).T).toarray().ravel()
        if self.modo == "tfidf":
            return s_lex
        q = self.emb.encode([f"query: {pergunta}"], normalize_embeddings=True,
                            show_progress_bar=False)[0]
        s_den = self.m_denso @ q
        if self.modo == "denso":
            return s_den
        return self.peso_denso * s_den + (1 - self.peso_denso) * s_lex

    def buscar(self, pergunta: str, k: int = TOP_K) -> list[dict]:
        s = self._scores(pergunta)
        idx = np.argsort(-s)[:k]
        return [{**self.trechos[i], "score": float(s[i]), "rank": r + 1}
                for r, i in enumerate(idx)]


# ----------------------------------------------------------------------
# Métricas de busca e escolha do limiar
# ----------------------------------------------------------------------
def recall_at_k(buscador: Buscador, casos: list[dict], k: int) -> float:
    """Fração das perguntas respondíveis em que algum trecho-gabarito aparece no top-k."""
    respondiveis = [c for c in casos if c["tipo"] == "consta"]
    acertos = 0
    for c in respondiveis:
        ids = {r["id"] for r in buscador.buscar(c["pergunta"], k)}
        acertos += bool(ids & set(c["trechos_gabarito"]))
    return acertos / max(len(respondiveis), 1)


def varrer_limiar(buscador: Buscador, casos: list[dict], grade=None) -> list[dict]:
    """Para cada limiar: % de 'não consta' barrados e % de perguntas válidas que passam.

    Retorna linhas com f1 (média harmônica entre barrar não-consta e deixar passar
    as respondíveis) para justificar o limiar escolhido.
    """
    top1 = [(c["tipo"], buscador.buscar(c["pergunta"], 1)[0]["score"]) for c in casos]
    if grade is None:
        sc = [s for _, s in top1]
        grade = np.round(np.linspace(min(sc), max(sc), 60), 4)
    linhas = []
    for lim in grade:
        nc = [s for t, s in top1 if t == "nao_consta"]
        ok = [s for t, s in top1 if t == "consta"]
        barra_nc = sum(s < lim for s in nc) / max(len(nc), 1)
        passa_ok = sum(s >= lim for s in ok) / max(len(ok), 1)
        f1 = 0 if barra_nc + passa_ok == 0 else 2 * barra_nc * passa_ok / (barra_nc + passa_ok)
        linhas.append({"limiar": float(lim), "barra_nao_consta": float(barra_nc),
                       "passa_respondiveis": float(passa_ok), "f1": float(f1)})
    return linhas


def escolher_limiar(linhas: list[dict], min_passa: float = 0.95) -> dict:
    """Maior f1 entre os limiares que ainda deixam passar >= min_passa das respondíveis.

    Preferimos errar deixando passar (a LLM ainda pode recusar) a bloquear pergunta
    válida, que nunca mais teria chance de ser respondida. Se vários limiares empatam
    no melhor f1, pegamos o do meio da faixa (maior margem dos dois lados).
    """
    candidatos = [l for l in linhas if l["passa_respondiveis"] >= min_passa] or linhas
    melhor = max(l["f1"] for l in candidatos)
    empatados = sorted((l for l in candidatos if l["f1"] == melhor), key=lambda l: l["limiar"])
    return empatados[len(empatados) // 2]


def carregar_limiar() -> float:
    try:
        return float(json.loads(ARQ_LIMIAR.read_text(encoding="utf-8"))["limiar"])
    except (FileNotFoundError, KeyError, ValueError):
        return LIMIAR_PADRAO
