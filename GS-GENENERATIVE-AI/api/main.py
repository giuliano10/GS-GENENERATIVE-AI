"""API do assistente (FastAPI). Roda 100% local: busca + LLM + LoRA na mesma máquina.

Iniciar:
    uvicorn api.main:app --port 8000
Variáveis de ambiente:
    USAR_LORA=1        usa o adaptador LoRA (padrão 1 se a pasta do adaptador existir)
    MODO_BUSCA=hibrido tfidf | denso | hibrido
"""
from __future__ import annotations

import logging
import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.base_conhecimento import carregar_trechos
from src.busca import Buscador, carregar_limiar
from src.config import DIR_LORA, MAX_CARACTERES_PERGUNTA
from src.gerador import MSG_NAO_CONSTA, carregar_modelo, responder
from src.lgpd import mascarar

# Log só com métricas anônimas: nunca a pergunta nem a resposta (LGPD).
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("assistente")

app = FastAPI(
    title="Assistente de Acessibilidade em Calçadas – SP",
    description="Responde dúvidas sobre regras de calçada e acessibilidade com base em leis "
                "federais e de São Paulo, citando a fonte, ou recusa quando não consta.",
    version="1.0.0",
)

_estado: dict = {}


def _carregar():
    if _estado:
        return _estado
    trechos = carregar_trechos()
    usar_lora = os.getenv("USAR_LORA", "1" if DIR_LORA.exists() else "0") == "1"
    _estado.update(
        trechos={t["id"]: t for t in trechos},
        buscador=Buscador(trechos, modo=os.getenv("MODO_BUSCA", "hibrido")),
        limiar=carregar_limiar(),
        modelo=carregar_modelo(com_lora=usar_lora),
        config="rag_lora" if usar_lora else "rag",
    )
    return _estado


class Pergunta(BaseModel):
    pergunta: str = Field(..., min_length=3, max_length=MAX_CARACTERES_PERGUNTA,
                          examples=["Qual a largura mínima da faixa livre da calçada em São Paulo?"])


class Fonte(BaseModel):
    id: str
    fonte: str
    artigo: str
    url: str
    trecho: str


class Resposta(BaseModel):
    resposta: str
    recusa: bool
    fontes: list[Fonte]
    explicacao: dict
    aviso_privacidade: str | None = None


@app.get("/saude")
def saude():
    return {"status": "ok"}


@app.get("/privacidade")
def privacidade():
    return {
        "base_legal": "LGPD (Lei 13.709/2018), art. 6º: finalidade, necessidade e segurança.",
        "o_que_coletamos": "Nada é armazenado. A pergunta existe só na memória durante a requisição.",
        "dados_pessoais": "CPF, CNPJ, e-mail, telefone, CEP e placa são mascarados antes do processamento.",
        "processamento": "Modelo de linguagem e busca rodam localmente; nada é enviado a terceiros.",
        "logs": "Apenas métricas anônimas: tamanho da pergunta, latência e se houve recusa.",
    }


@app.post("/perguntar", response_model=Resposta)
def perguntar(p: Pergunta):
    st = _carregar()
    texto, pii = mascarar(p.pergunta.strip())
    if not texto:
        raise HTTPException(422, "Pergunta vazia.")

    t0 = time.time()
    saida = responder(texto, st["modelo"], st["buscador"], st["limiar"], usar_contexto=True)

    # Guarda de citação: só aceita resposta afirmativa se citar um trecho recuperado.
    validas = [f for f in saida["fontes"] if f in saida["recuperados"]]
    guarda = False
    if not saida["recusa"] and (not saida["json_valido"] or not validas):
        guarda = True
        saida.update(resposta=MSG_NAO_CONSTA, recusa=True)
        validas = []

    if saida["barrado_pelo_limiar"]:
        motivo = "Nenhum trecho da base é parecido o suficiente com a pergunta (score abaixo do limiar)."
    elif guarda:
        motivo = "O modelo respondeu sem citar um trecho válido; a resposta foi bloqueada."
    elif saida["recusa"]:
        motivo = "Os trechos recuperados não contêm a resposta."
    else:
        motivo = "Resposta baseada nos trechos citados."

    log.info("config=%s tam=%d recusa=%s pii=%d latencia=%.2fs", st["config"], len(texto),
             saida["recusa"], len(pii), time.time() - t0)

    return Resposta(
        resposta=saida["resposta"],
        recusa=saida["recusa"],
        fontes=[Fonte(id=i, fonte=st["trechos"][i]["fonte"], artigo=st["trechos"][i]["artigo"],
                      url=st["trechos"][i]["url"], trecho=st["trechos"][i]["texto"]) for i in validas],
        explicacao={
            "motivo": motivo,
            "configuracao": st["config"],
            "trechos_recuperados": saida["recuperados"],
            "score_top1": round(saida["score_top1"] or 0, 4),
            "limiar": st["limiar"],
            "guarda_de_citacao_acionada": guarda,
        },
        aviso_privacidade=(f"Removemos dados pessoais da sua pergunta ({', '.join(pii)}). "
                           "Eles não são necessários para responder.") if pii else None,
    )
