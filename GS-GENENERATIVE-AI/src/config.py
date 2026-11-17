"""Configuração central do projeto.

Todos os caminhos são relativos à raiz do repositório, então o mesmo código
roda no Colab, no VS Code ou num servidor.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# --- Base de conhecimento -------------------------------------------------
DIR_BASE = RAIZ / "base"
DIR_RAW = DIR_BASE / "raw"
ARQ_FONTES = DIR_BASE / "fontes.csv"
ARQ_TRECHOS = DIR_BASE / "trechos.jsonl"

# --- Avaliação ------------------------------------------------------------
DIR_AVAL = RAIZ / "avaliacao"
ARQ_TESTE = DIR_AVAL / "casos_teste.jsonl"      # conjunto de teste (nunca usado no treino)
ARQ_TREINO = DIR_AVAL / "lora_treino.jsonl"     # perguntas de treino/validação (LoRA e limiar)
ARQ_LIMIAR = DIR_AVAL / "limiar.json"           # limiar escolhido no notebook 01

# --- Modelos (todos rodam localmente, sem API externa) --------------------
LLM_ID = "Qwen/Qwen2.5-1.5B-Instruct"
EMB_ID = "intfloat/multilingual-e5-small"
DIR_LORA = RAIZ / "modelos" / "lora-acessibilidade"

# --- Busca ----------------------------------------------------------------
TOP_K = 3
LIMIAR_PADRAO = 0.80   # substituído pelo valor medido em avaliacao/limiar.json

# --- Geração --------------------------------------------------------------
MAX_NOVOS_TOKENS = 320
SEMENTE = 42

# --- API / LGPD -----------------------------------------------------------
MAX_CARACTERES_PERGUNTA = 500
