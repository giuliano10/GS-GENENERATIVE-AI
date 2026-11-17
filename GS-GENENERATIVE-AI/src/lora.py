"""Especialização com LoRA.

O LoRA NÃO é usado para decorar as leis (isso é papel da base + busca). Ele ensina
o comportamento: responder curto, citar o id certo, devolver JSON válido e recusar
quando o trecho com a resposta não está no contexto.

Exemplos de treino (gerados de avaliacao/lora_treino.jsonl, disjunto do teste):
  1. pergunta que consta + contexto com o trecho certo  -> resposta + fonte
  2. a MESMA pergunta + contexto SEM o trecho certo     -> recusa   (aumento de dados)
  3. pergunta que não consta + contexto recuperado      -> recusa
"""
from __future__ import annotations

import math
import random

from .config import DIR_LORA, LLM_ID, SEMENTE, TOP_K
from .gerador import MSG_NAO_CONSTA, alvo_json, mensagens_rag


def montar_exemplos(casos: list[dict], buscador, trechos_por_id: dict) -> list[dict]:
    rnd = random.Random(SEMENTE)
    exemplos = []
    for c in casos:
        recup = buscador.buscar(c["pergunta"], TOP_K + 2)
        if c["tipo"] == "consta":
            gold = [trechos_por_id[g] for g in c["trechos_gabarito"]]
            gold_ids = {g["id"] for g in gold}
            outros = [r for r in recup if r["id"] not in gold_ids]
            # (1) contexto com o trecho certo, em posição aleatória
            ctx = gold[:1] + outros[:TOP_K - 1]
            rnd.shuffle(ctx)
            exemplos.append({"mensagens": mensagens_rag(c["pergunta"], ctx),
                             "alvo": alvo_json(c["resposta_gabarito"], [gold[0]["id"]], False)})
            # (2) contexto sem o trecho certo -> recusa
            ctx_neg = outros[:TOP_K]
            exemplos.append({"mensagens": mensagens_rag(c["pergunta"], ctx_neg),
                             "alvo": alvo_json(MSG_NAO_CONSTA, [], True)})
        else:
            exemplos.append({"mensagens": mensagens_rag(c["pergunta"], recup[:TOP_K]),
                             "alvo": alvo_json(MSG_NAO_CONSTA, [], True)})
    rnd.shuffle(exemplos)
    return exemplos


def treinar(exemplos: list[dict], epocas: int = 3, lr: float = 2e-4, r: int = 16,
            saida=DIR_LORA) -> None:
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                              TrainingArguments)

    torch.manual_seed(SEMENTE)
    tok = AutoTokenizer.from_pretrained(LLM_ID)
    tok.pad_token = tok.pad_token or tok.eos_token
    modelo = AutoModelForCausalLM.from_pretrained(LLM_ID, torch_dtype=torch.float32,
                                                  device_map="auto")
    modelo.gradient_checkpointing_enable()
    modelo.enable_input_require_grads()
    modelo = get_peft_model(modelo, LoraConfig(
        r=r, lora_alpha=2 * r, lora_dropout=0.05, task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]))
    modelo.print_trainable_parameters()

    def tokenizar(ex):
        prompt = tok.apply_chat_template(ex["mensagens"], tokenize=False, add_generation_prompt=True)
        p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
        a_ids = tok(ex["alvo"] + tok.eos_token, add_special_tokens=False)["input_ids"]
        # a perda só é calculada sobre a resposta (o prompt fica com -100)
        return {"input_ids": p_ids + a_ids, "labels": [-100] * len(p_ids) + a_ids}

    dados = [tokenizar(e) for e in exemplos]

    def colar(lote):
        n = max(len(x["input_ids"]) for x in lote)
        ids = [x["input_ids"] + [tok.pad_token_id] * (n - len(x["input_ids"])) for x in lote]
        lab = [x["labels"] + [-100] * (n - len(x["labels"])) for x in lote]
        att = [[1] * len(x["input_ids"]) + [0] * (n - len(x["input_ids"])) for x in lote]
        return {"input_ids": torch.tensor(ids), "labels": torch.tensor(lab),
                "attention_mask": torch.tensor(att)}

    # aquecimento de 5% dos passos, em número inteiro (o transformers 5 removeu `warmup_ratio`)
    passos = math.ceil(len(dados) / (2 * 4)) * epocas
    args = TrainingArguments(
        output_dir=str(saida) + "_ckpt", num_train_epochs=epocas, learning_rate=lr,
        per_device_train_batch_size=2, gradient_accumulation_steps=4,
        lr_scheduler_type="cosine", warmup_steps=max(1, round(0.05 * passos)), logging_steps=5,
        save_strategy="no", report_to=[], fp16=torch.cuda.is_available(), seed=SEMENTE)
    Trainer(model=modelo, args=args, train_dataset=dados, data_collator=colar).train()
    modelo.save_pretrained(str(saida))
    tok.save_pretrained(str(saida))
    print(f"Adaptador salvo em {saida}")
