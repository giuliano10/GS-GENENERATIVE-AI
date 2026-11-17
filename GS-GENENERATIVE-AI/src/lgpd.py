"""Proteção de dados pessoais (LGPD, Lei 13.709/2018).

Princípios aplicados:
- Necessidade/minimização (art. 6º, III): o assistente não precisa de dado pessoal
  para responder sobre regras de calçada, então CPF, e-mail, telefone, CEP e placa
  são mascarados ANTES de a pergunta chegar à busca ou à LLM.
- Segurança (art. 6º, VII) e livre acesso: o modelo roda localmente; nenhuma
  pergunta é enviada a serviço externo nem gravada em disco. O log guarda só
  métricas anônimas (tamanho, latência, se recusou).
"""
import re

PADROES = [
    ("CNPJ", re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")),
    ("CPF", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("TELEFONE", re.compile(r"(?:\+?55\s?)?\(?\b\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b")),
    ("CEP", re.compile(r"\b\d{5}-\d{3}\b")),
    ("PLACA", re.compile(r"\b[A-Z]{3}-?\d[A-Z0-9]\d{2}\b")),
]


def mascarar(texto: str) -> tuple[str, list[str]]:
    """Retorna (texto mascarado, tipos de dado encontrados)."""
    encontrados = []
    for nome, padrao in PADROES:
        if padrao.search(texto):
            encontrados.append(nome)
            texto = padrao.sub(f"[{nome} REMOVIDO]", texto)
    return texto, encontrados
