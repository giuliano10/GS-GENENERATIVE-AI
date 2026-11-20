# Assistente de Acessibilidade em Calçadas – São Paulo

LLM local (Qwen2.5-1.5B-Instruct) que responde dúvidas sobre **regras de calçada, acessibilidade e
mobilidade a pé** com base em leis federais e do Município de São Paulo, **citando o artigo** usado
e **recusando** ("não consta") quando a base não cobre a pergunta.

Trabalho da disciplina *Generative AI for Engineering* — tema **mobilidade**.
Relatório completo: [`RELATORIO.md`](RELATORIO.md).

## Ficha Técnica do MVP

| Campo | Resposta |
|---|---|
| **Nome do produto** | Caminho Livre: tecnologia para uma cidade acessível |
| **Cidadão e território** | Pessoas com deficiência, idosos e pessoas com mobilidade reduzida, na cidade de São Paulo |
| **Problema, em uma frase** | Calçadas com buracos, desníveis, obstáculos e obras dificultam a circulação de quem tem mobilidade reduzida, e os relatos chegam dispersos, sem um processo ágil para conferir, priorizar e encaminhar |
| **Proposta de valor** | O cidadão registra o obstáculo com foto, rua e ponto de referência. A plataforma identifica a barreira, prioriza e encaminha as ocorrências aos órgãos públicos, alimenta um painel de dados e um assistente responde dúvidas sobre as normas citando o artigo |
| **Arquitetura: componentes** | Coleta e dados: Airflow + Databricks (Bronze, Prata, Ouro). RPA: robô Python a cada 1 min + servidor com formulário, painel e API REST + SQLite. Triagem visual: Python, OpenCV, Tkinter. Assistente de normas: FastAPI, busca híbrida e LLM com LoRA |
| **Fontes de dados** | SP156 (Portal de Dados Abertos da Prefeitura de SP), Open-Meteo, relatos do app e CSVs da prefeitura e de ONGs (fictícios nos testes), 7 normas federais e municipais, imagens anotadas no Roboflow |
| **Modelos de IA utilizados** | RF-DETR (Roboflow), YOLOv8n, Qwen2.5-1.5B-Instruct + LoRA, multilingual-e5-small |
| **URL do MVP e repositório** | MVP executável localmente (formulário em localhost:8000, painel em /painel). Repositórios: [Generative AI](https://github.com/giuliano10/GS-GENERATIVE-AI) · [Applied Vision](https://github.com/giuliano10/GS-AMPPLIED-VISION) · RPA: [https://github.com/giuliano10/GS-RPA] · Big Data: [https://github.com/giuliano10/GS-BIG-DATA] |
| **Indicadores de impacto** | Assistente: 75% de acurácia, 13,3% de alucinação e 86,7% de recusa correta (60 perguntas de teste). RPA: 30 testes unitários e 48 verificações ponta a ponta. Dados pessoais apagados após 90 dias |
| **ODS conectados** | ODS 11 (cidades e comunidades sustentáveis) e ODS 10 (redução das desigualdades) |


| Integrante | RM |
|---|---|
| Arthur Abreu | 98283 |
| Arthur Petrin | 98735 |
| Giuliano Marques | 99694 |

## Resultados (60 perguntas de teste)

| Configuração | Acurácia | Alucinação | Recusa correta (não consta) | Citação correta |
|---|---|---|---|---|
| Modelo sem contexto | 11,7% | 88,3% | 13,3% | 0% |
| RAG simples | 68,3% | 25,0% | 53,3% | 68,3% |
| **RAG + LoRA** | **75,0%** | **13,3%** | **86,7%** | **78,9%** |

Busca híbrida: recall@1 = 0,622 e recall@3 = 0,978. Detalhes, gráficos e os 5 erros analisados estão no
[`RELATORIO.md`](RELATORIO.md).

## Estrutura

```
base/          fontes.csv (fonte, URL, licença), raw/ (HTML oficial), trechos.jsonl (238 trechos, 1 por artigo)
avaliacao/     casos_teste.jsonl (60 perguntas, 15 "não consta"), lora_treino.jsonl (62), placar e erros
notebooks/     01 base e busca · 02 sem contexto × RAG · 03 LoRA · 04 placar e erros · 05 API
src/           busca, geração, avaliação, LoRA, LGPD
api/           API FastAPI (main.py)
scripts/       montar_casos.py (gabarito ancorado no texto da lei), gerar_notebooks.py
modelos/       adaptador LoRA treinado (17 MB, gerado pelo notebook 03)
```

## Como reproduzir (Google Colab, GPU T4 gratuita)

1. Abra cada notebook de `notebooks/` no Colab (*Arquivo › Abrir notebook › GitHub* e cole a URL do repositório).
2. *Ambiente de execução › Alterar tipo de ambiente › T4 GPU*.
3. A primeira célula já aponta para este repositório (`REPO_URL` e `SUBPASTA`); ajuste só se fizer um fork.
4. Rode **na ordem**, cada um com *Ambiente de execução › Executar tudo*. Cada notebook pede acesso ao
   Google Drive: é por lá (pasta `assistente-calcadas-resultados`) que os resultados passam de um notebook
   para o outro, porque no Colab cada notebook roda numa máquina separada.
 
| Notebook | O que faz | GPU | Tempo aprox. |
|---|---|---|---|
| `01_base_e_busca` | tabela da base, recall@1/@3, escolha do limiar | opcional | 2 min |
| `02_sem_contexto_e_rag` | configurações 1 e 2 no teste | sim | 10–15 min |
| `03_lora` | treina o LoRA e roda a configuração 3 | sim | 15–25 min |
| `04_placar_e_erros` | placar, gráfico, alucinações, erros e download de `resultados.zip` | não | 1 min |
| `05_api` | demonstração da API | sim | 3 min |

5. Para guardar no repositório: *Arquivo › Salvar uma cópia no GitHub* em cada notebook (salva com as saídas)
   e suba o conteúdo de `resultados.zip` (pastas `avaliacao/` e `modelos/`).

Resultados são determinísticos (decodificação gulosa, semente 42).

### Rodar local (VS Code)

```bash
python -m venv .venv && .venv\Scripts\activate      # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python -m src.base_conhecimento --montar             # opcional: refaz base/trechos.jsonl a partir de base/raw/
python scripts/montar_casos.py                        # opcional: refaz os conjuntos de teste e treino
uvicorn api.main:app --port 8000                     # abre http://localhost:8000/docs
```

Sem GPU o modelo de 1,5B roda em CPU, mas leva alguns segundos por resposta.

## API

`POST /perguntar` — `{"pergunta": "Qual a largura mínima da faixa livre da calçada?"}`

```json
{
  "resposta": "...",
  "recusa": false,
  "fontes": [{"id": "...", "fonte": "...", "artigo": "Art. ...", "url": "...", "trecho": "..."}],
  "explicacao": {"motivo": "...", "trechos_recuperados": ["..."], "score_top1": 0.0, "limiar": 0.0,
                 "guarda_de_citacao_acionada": false},
  "aviso_privacidade": null
}
```

Também: `GET /saude`, `GET /privacidade`, documentação interativa em `/docs`.

**Segurança e LGPD:** modelo e busca rodam localmente (nada vai para terceiros); CPF, CNPJ, e-mail,
telefone, CEP e placa são mascarados antes do processamento; nenhuma pergunta é gravada (o log tem só
métricas anônimas); pergunta limitada a 500 caracteres; o prompt manda ignorar instruções embutidas;
uma guarda bloqueia qualquer resposta que não cite um trecho recuperado.

