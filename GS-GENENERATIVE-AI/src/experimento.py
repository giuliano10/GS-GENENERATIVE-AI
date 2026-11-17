"""Roda uma configuração sobre o conjunto de teste e salva as respostas."""
from __future__ import annotations

from .avaliacao import salvar_jsonl
from .config import DIR_AVAL
from .gerador import responder

CONFIGS = {
    "sem_contexto": "LLM base, sem busca (só o conhecimento do modelo)",
    "rag": "LLM base + busca híbrida + limiar (RAG simples)",
    "rag_lora": "LLM com adaptador LoRA + mesma busca + mesmo limiar",
}


def arq_respostas(nome: str):
    return DIR_AVAL / f"respostas_{nome}.jsonl"


def rodar(nome: str, casos: list[dict], modelo, buscador=None, limiar=None) -> list[dict]:
    usar_ctx = nome != "sem_contexto"
    saidas = []
    for i, c in enumerate(casos, 1):
        s = responder(c["pergunta"], modelo, buscador, limiar if usar_ctx else None, usar_contexto=usar_ctx)
        s["id"] = c["id"]
        saidas.append(s)
        if i % 10 == 0 or i == len(casos):
            print(f"[{nome}] {i}/{len(casos)}")
    salvar_jsonl(saidas, arq_respostas(nome))
    return saidas
