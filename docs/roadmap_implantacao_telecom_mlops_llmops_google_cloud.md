# Roadmap de Implantação – Plataforma Telecom MLOps + LLMOps no Google Cloud

Este documento é um **guia operacional** para os times de **MLOps** e **LLMOps** implementarem, no Google Cloud, a plataforma de churn + assistente LLM descrita neste repositório.

Ele se baseia no documento:

- `docs/arquitetura_mlops_llmops_google_cloud_de_para_databricks.md`

e expande em forma de **roadmap passo a passo**, incluindo:

- Arquitetura completa (MLOps e LLMOps) com componentes Google Cloud.
- Como usar cada serviço Google Cloud no contexto do projeto.
- Quais **arquivos Python**, **notebooks**, **scripts de pipeline** e **arquivos Terraform** devem ser criados.
- Ordem recomendada de implantação (por fases/sprints).

> Linguagem: o documento assume conhecimento prévio em Python, Git, Google Cloud e conceitos de MLOps/LLMOps.

---

## 1. Visão Geral da Arquitetura

### 1.1 Componentes Principais (Google Cloud)

**Dados & Governança**
- **Cloud Storage (GCS)**: data lake com camadas `bronze/`, `silver/`, `gold/` e documentos para RAG.
- **BigQuery**: data warehouse e fonte principal para treino, inferência batch e monitoramento.
- **Dataplex**: organização de dados em lakes e zonas, integrando GCS e BigQuery.
- **Data Catalog**: catálogo de metadados, documentação de tabelas e classificação de dados.

**MLOps – Modelo de Churn**
- **Vertex AI Workbench**: notebooks gerenciados para desenvolvimento (exploração, protótipos).
- **Vertex AI Feature Store**: armazenamento de features de clientes (offline + online).
- **Vertex AI Pipelines**: orquestração do ciclo de vida (data prep, treino, avaliação, deploy).
- **Vertex AI Custom Jobs**: execução de scripts de treino, inferência ou jobs auxiliares.
- **Vertex AI Experiments**: rastreamento de experimentos (métricas, parâmetros, artefatos).
- **Vertex AI Model Registry**: versionamento e gestão de modelos de churn.
- **Vertex AI Batch Prediction**: inferência batch e gravação em BigQuery (camada “diamond”).
- **Vertex AI Online Prediction (opcional)**: endpoint online para uso pelo assistente LLM.
- **Vertex Explainable AI (opcional)**: explicabilidade (importância de features, SHAP-like).
- **Vertex AI Model Monitoring**: monitoramento de drift para endpoints online.

**LLMOps – Assistente Telecom**
- **Vertex AI Search (RAG)**: índice de documentos (GCS/BigQuery) para base de conhecimento.
- **Vertex AI Generative AI (Gemini / Model Garden)**: modelos LLM usados pelo assistente.
- **Vertex AI Agents (opcional)**: orquestração de ferramentas e fluxos LLM.
- **Vertex AI Evaluation**: avaliação de prompts e respostas (regressão semântica).
- **Vertex AI Observability**: métricas, logs e traces do uso dos modelos generativos.

**Execução, CI/CD e Observabilidade**
- **Cloud Run**: APIs do modelo de churn, assistente LLM e tasks batch leves.
- **GKE (opcional)**: execução em pods Kubernetes para cenários mais customizados.
- **Cloud Build**: build de containers, testes e pipelines de CI/CD.
- **Artifact Registry**: repositório de imagens Docker.
- **Cloud Deploy (opcional)**: orquestração de deploys para GKE/Cloud Run.
- **Cloud Scheduler**: agendamento de jobs (batch, pipelines, retreino, avaliações).
- **Cloud Functions (ou Cloud Run)**: funções leves para reagir a eventos (Pub/Sub, agendamentos).
- **Pub/Sub**: mensageria e disparo de pipelines (retreino, alertas, workflows).
- **Cloud Logging**: centralização de logs de serviços GCP e aplicações.
- **Cloud Monitoring + Alerting**: métricas e alertas (drift, falhas, SLOs).
- **Error Reporting**: consolidação de exceptions das aplicações (Cloud Run, GKE).
- **Secret Manager**: armazenamento de segredos (chaves de APIs externas, etc.).

**Ferramentas externas/internas**
- **GitHub + GitHub Actions**: versionamento de código e CI/CD no repositório.
- **Terraform**: IaC para provisionamento de recursos GCP.

---

## 2. Roadmap por Fases

### 2.1 Visão Macro das Fases

Mantendo a ideia de 6 grupos (do README/PDF), expandimos em fases:

1. **Fase 0 – Preparação e Fundamentos**
   - Projeto GCP, IAM, redes, APIs, repositório, ambientes (dev/stg/prod).
2. **Fase 1 – Infraestrutura de Dados**
   - Buckets, BigQuery, Dataplex/Data Catalog, ingestão inicial de churn.
3. **Fase 2 – MLOps Churn: Data Prep, Treino, Deploy Batch**
   - Estrutura de código, Feature Store, pipelines de treino, batch prediction.
4. **Fase 3 – Monitoramento, Drift e Retreino**
   - Métricas de drift, alertas, pipelines de retreino.
5. **Fase 4 – LLMOps: RAG e Base de Conhecimento**
   - Vertex AI Search, ingestão de documentos, prompts, avaliação.
6. **Fase 5 – Assistente LLM Telecom + Integrações**
   - Cloud Run/Agents, tools (churn, CRM, billing), observabilidade e testes LLM.
7. **Fase 6 – CI/CD, Qualidade e Operação**
   - Workflows GitHub, Cloud Build, deploy automatizado, dashboards e SLOs.

Nas seções seguintes, detalhamos o **passo a passo** por fase, incluindo **arquivos a criar**.

---

## 3. Fase 0 – Preparação e Fundamentos

### 3.1 Organização e Projetos GCP

1. **Criar projeto(s) GCP** (um por ambiente ou um único com separação lógica):
   - Sugestão: `telecom-mlops-llmops-dev`, `telecom-mlops-llmops-prod`.
2. **Habilitar APIs necessárias**:
   - `Vertex AI API`
   - `BigQuery API`
   - `Cloud Storage`
   - `Cloud Run`
   - `Cloud Build`
   - `Artifact Registry`
   - `Cloud Logging`
   - `Cloud Monitoring`
   - `Secret Manager`
   - `Cloud Scheduler`
   - `Cloud Functions`
   - `Pub/Sub`
   - `Dataplex API`
   - `Data Catalog API`
   - `Vertex AI Search` / `Discovery Engine API`

3. **Criar contas de serviço chave**:
   - `sa-mlops@<project>.iam.gserviceaccount.com`
   - `sa-llmops@<project>.iam.gserviceaccount.com`
   - `sa-ci-cd@<project>.iam.gserviceaccount.com`

4. **Configurar IAM**:
   - `sa-mlops`: papéis como `roles/aiplatform.admin`, `roles/bigquery.admin`, `roles/storage.admin` (ou mais restritivos).
   - `sa-llmops`: `roles/aiplatform.user`, `roles/discoveryengine.admin` (para Vertex AI Search), `roles/run.admin` (se for criar serviços).
   - `sa-ci-cd`: `roles/cloudbuild.builds.editor`, `roles/run.developer`, `roles/artifactregistry.writer`, etc.

5. **Conectar GitHub → GCP (OIDC ou chave de serviço)**:
   - Recomendado: **Workload Identity Federation** (sem chave estática).

### 3.2 Infraestrutura como Código (Terraform)

Criar estrutura inicial em `infra/terraform/`:

```text
infra/
  terraform/
    envs/
      dev/
        main.tf
        variables.tf
        outputs.tf
      prod/
        main.tf
        variables.tf
        outputs.tf
    modules/
      project/
      networking/
      gcs/
      bigquery/
      vertex_ai/
      cloud_run/
      artifact_registry/
      monitoring/
      dataplex/
      data_catalog/
      scheduler_pubsub/
```

Em alto nível:

- `modules/project`: criação de projeto (se aplicável) e APIs.
- `modules/networking`: VPC, sub-redes, firewall (se necessário).
- `modules/gcs`: buckets `bronze/silver/gold/docs`.
- `modules/bigquery`: datasets `telecom_bronze/silver/gold/monitoring`.
- `modules/vertex_ai`: configurações base (locais, feature store, etc.).
- `modules/cloud_run`: serviços de churn e assistente LLM.
- `modules/artifact_registry`: repositório Docker.
- `modules/monitoring`: dashboards e alert policies.
- `modules/dataplex`: lakes e zones.
- `modules/data_catalog`: tags e templates de metadados.
- `modules/scheduler_pubsub`: jobs scheduler + pub/sub + functions/run de orquestração.

### 3.3 Repositório GitHub e Convenções

No repositório atual:

- Manter a estrutura base indicada no README:

```text
mlops/
llmops/
infra/
docs/
.github/workflows/
```

Configurações adicionais:

- `pyproject.toml` ou `requirements.txt` na raiz ou por pasta:
  - Dependências Python (google-cloud-aiplatform, google-cloud-bigquery, xgboost, pandas, etc.).
- `ruff.toml` / configs do `flake8`, `black`, `isort`.

---

## 4. Fase 1 – Infraestrutura de Dados (Bronze/Silver/Gold)

### 4.1 Cloud Storage (Data Lake)

**Objetivo**: replicar o padrão bronze/silver/gold que você usava no Databricks.

Com Terraform (`modules/gcs`), criar:

- Bucket principal:
  - `telecom-mlops-llmops-data-<env>`

Estrutura de diretórios:

```text
gs://telecom-mlops-llmops-data-<env>/
  bronze/
    churn/
  silver/
    churn/
  gold/
    churn/
  docs/
    telecom/
      pdfs/
      faq/
```

**Uso no projeto**:

- Ingestão inicial do dataset de churn (`WA_Fn-UseC_-Telco-Customer-Churn.csv`) em `bronze/churn/`.
- Outputs intermediários de data prep em `silver/`.
- Exports de datasets de treino/inferência em `gold/` (quando não estiverem em BQ).
- Documentos para RAG em `docs/telecom/`.

### 4.2 BigQuery (Data Warehouse)

Criar datasets via Terraform (`modules/bigquery`):

- `telecom_bronze`
- `telecom_silver`
- `telecom_gold`
- `telecom_monitoring`

**Uso no projeto**:

- `telecom_bronze`: tabelas espelho da camada bronze (se necessário).
- `telecom_silver`: tabelas limpas, tipadas, com joins.
- `telecom_gold`: tabelas finais de features + label para treino/inferência (e outputs de batch).
- `telecom_monitoring`: métricas de drift, estatísticas de produção, logs analíticos.

### 4.3 Dataplex e Data Catalog

**Dataplex**:

- Criar um **lake** `telecom-lake` e zonas:
  - Zona `telecom-raw` mapeando o path GCS `bronze/`.
  - Zona `telecom-curated` mapeando `silver/` + datasets BQ `telecom_silver`.
  - Zona `telecom-analytics` mapeando `gold/` + dataset BQ `telecom_gold`.

**Data Catalog**:

- Criar templates de tag para:
  - Sensibilidade do dado (PII, confidencial, público).
  - Domínio (churn, CRM, billing).
  - Qualidade (SLAs, donos).
- Aplicar tags às tabelas de BQ relevantes.

---

## 5. Fase 2 – MLOps Churn: Data Prep, Treino, Deploy Batch

### 5.1 Estrutura de Código MLOps

Em `mlops/`:

```text
mlops/
  src/
    config.py
    data_ingestion.py
    data_prep_churn.py
    feature_store_loader.py
    train_churn.py
    evaluate_churn.py
    batch_inference.py
    drift_monitoring.py
    utils_vertex.py
    utils_bigquery.py
  notebooks/
    eda_churn.ipynb
    data_prep_churn.ipynb
    train_churn_xgboost.ipynb
    drift_monitoring_churn.ipynb
    batch_inference_churn.ipynb
  tests/
    test_data_prep_churn.py
    test_train_churn.py
    test_batch_inference.py
    test_feature_store_loader.py
```

#### 5.1.1 `config.py`

- Centraliza configurações:
  - IDs de projeto.
  - Regiões (ex.: `us-central1`).
  - Nomes de buckets e datasets.
  - Namespaces de Feature Store.
  - IDs de modelos e endpoints.

#### 5.1.2 `utils_vertex.py`

- Funções helper para:
  - Inicializar o cliente `aiplatform` com projeto/região.
  - Criar/atualizar modelos no Model Registry.
  - Criar Custom Jobs e Batch Prediction Jobs.
  - Interagir com Feature Store (lista de entity types, features).

#### 5.1.3 `utils_bigquery.py`

- Funções para:
  - Executar queries parametrizadas.
  - Gravar DataFrames em tabelas.
  - Ler tabelas em DataFrames.

### 5.2 Data Prep e Ingestão

#### 5.2.1 `data_ingestion.py`

Responsável por:

- Ler o CSV de churn localmente (no repositório) ou recebê-lo via GCS.
- Gravar a versão bruta em:
  - `gs://.../bronze/churn/...`
  - Tabela `telecom_bronze.telco_churn_raw` em BigQuery.

Este script pode ser executado:

- Localmente (durante desenvolvimento).
- Como Custom Job no Vertex AI (para cargas periódicas).

#### 5.2.2 `data_prep_churn.py`

Responsável por:

- Ler de `telecom_bronze.telco_churn_raw`.
- Aplicar:
  - Limpeza de nulos.
  - Conversão de tipos.
  - Criação de colunas derivadas (tempo de contrato, tipos de plano etc.).
- Persistir:
  - Tabela `telecom_silver.telco_churn_clean`.
  - Tabela `telecom_gold.telco_churn_features` (features finais + label).

**Notebook associado**: `mlops/notebooks/data_prep_churn.ipynb` para desenvolvimento, referenciando as funções do módulo.

### 5.3 Vertex AI Feature Store

#### 5.3.1 Design de Entity Types e Features

- `entity_type`: `customer`
  - `entity_id`: `customer_id`
  - Features:
    - `tenure_months`
    - `monthly_charges`
    - `total_charges`
    - `contract_type`
    - `internet_service`
    - `payment_method`
    - etc.

#### 5.3.2 `feature_store_loader.py`

Responsável por:

- Criar o **Feature Store** (se ainda não existir) via SDK:
  - `aiplatform.Featurestore.create()`.
- Criar o `entity_type customer`.
- Criar features com seus tipos (string, float, int).
- Carregar dados a partir da tabela `telecom_gold.telco_churn_features` para o offline store.
- (Opcional) Configurar online store para features mais usadas na inferência online.

Execução:

- Inicialmente via notebook ou script local.
- Depois como componente de pipeline (Vertex AI Pipelines).

### 5.4 Treino do Modelo de Churn

#### 5.4.1 `train_churn.py`

Responsável por:

- Ler dataset de treino:
  - Direto de BigQuery `telecom_gold.telco_churn_features`.
  - Ou via Feature Store (com referência temporal se necessário).
- Fazer split treino/validação/teste.
- Treinar modelo XGBoost (ou outro).
- Calcular métricas (AUC, f1, recall churn, etc.).
- Salvar:
  - Modelo serializado (ex.: `model.bst` ou `model.joblib`) em GCS.
  - Metrics em um JSON para registro.
- Registrar modelo no **Vertex AI Model Registry**.
- Registrar experimento em **Vertex AI Experiments**:
  - `aiplatform.start_run()`, log de métricas e parâmetros.

#### 5.4.2 `evaluate_churn.py`

Responsável por:

- Comparar o modelo treinado com:
  - Modelos anteriores (via Model Registry/Experiments).
  - Critérios de promoção (ex.: AUC >= baseline + delta).
- Retornar decisão:
  - `promote = True/False`.

### 5.5 Pipelines de Treino e Deploy (Vertex AI Pipelines)

Criar módulo de pipeline em `mlops/src/pipelines/churn_pipeline.py`:

- Usando o DSL de pipelines do `google-cloud-aiplatform` (Kubeflow Pipelines v2).
- Componentes do pipeline:
  1. `data_prep_op`: chama `data_prep_churn.py`.
  2. `feature_store_op`: chama `feature_store_loader.py`.
  3. `train_op`: chama `train_churn.py`.
  4. `evaluate_op`: chama `evaluate_churn.py`.
  5. `deploy_op` (condicional): se `promote == True`:
     - Cria/atualiza um **Vertex AI Endpoint** (se online).
     - Ou registra modelo para uso em Batch Prediction (batch-only).

O pipeline é empacotado em um container e submetido via:

- `aiplatform.PipelineJob(...)`.

### 5.6 Inferência Batch – Vertex AI Batch Prediction

#### 5.6.1 `batch_inference.py`

Responsável por (2 modos):

1. **Modo Vertex Batch Prediction (recomendado)**:
   - Dado um modelo do Model Registry, criar um `BatchPredictionJob` via SDK indicando:
     - Input: tabela BQ `telecom_gold.telco_churn_features_score_input`.
     - Output: tabela BQ `telecom_gold.telco_churn_scored` (camada “diamond”).
2. **Modo script customizado** (se preferir):
   - Ler a tabela de input de BQ.
   - Carregar modelo de GCS.
   - Aplicar scoring e escrever a tabela de saída.

#### 5.6.2 Agendamento

Configurar, via Terraform (`modules/scheduler_pubsub`):

- Um `Cloud Scheduler Job` diário ou semanal:
  - Envia mensagem em `Pub/Sub`.
- Uma `Cloud Function` ou serviço `Cloud Run`:
  - Recebe Pub/Sub.
  - Chama `batch_inference.py` ou dispara um `BatchPredictionJob`.

---

## 6. Fase 3 – Monitoramento, Drift e Retreino

### 6.1 Drift Offline (Batch)

#### 6.1.1 `drift_monitoring.py`

Responsável por:

- Ler amostras de:
  - Dados de treino `telecom_gold.telco_churn_features` (baseline).
  - Dados de produção `telecom_gold.telco_churn_scored`.
- Calcular métricas de drift:
  - PSI, KS, diferenças de média/variância.
  - Frequência de categorias.
- Gravar métricas em:
  - Tabelas BQ `telecom_monitoring.feature_drift_metrics`.
  - Métricas customizadas no Cloud Monitoring (via API).

### 6.2 Model Monitoring (Online) – Vertex AI

Se houver um endpoint online do modelo:

- Configurar **Vertex AI Model Monitoring**:
  - Especificar schema de features.
  - Habilitar detecção de drift.
  - Definir thresholds.
  - Integrar com Cloud Monitoring para alertas.

### 6.3 Alertas e Retreino Automático

#### 6.3.1 Alertas

Configurar, via Terraform (`modules/monitoring`):

- **Alert policies**:
  - Condições: `churn_feature_drift_score > X`.
  - Notificações: email, Slack, webhook, etc.

#### 6.3.2 Pipeline de Retreino

Criar pipeline `mlops/src/pipelines/churn_retraining_pipeline.py`:

- Passos:
  1. Ler métricas de drift.
  2. Se drift > threshold, executar:
     - `data_prep_churn.py`.
     - `train_churn.py`.
     - `evaluate_churn.py`.
     - `deploy` (se modelo for melhor).

Agendamento:

- `Cloud Scheduler` → `Pub/Sub` → `Cloud Run/Function`:
  - Dispara `PipelineJob` do pipeline de retreino.

---

## 7. Fase 4 – LLMOps: RAG e Base de Conhecimento

### 7.1 Estrutura de Código LLMOps

Em `llmops/`:

```text
llmops/
  rag/
    ingest_documents.py
    build_vertex_search_datastore.py
    sync_bigquery_knowledge.py
  prompts/
    system/
      suporte_tecnico.md
      retencao_churn.md
    rules/
      politicas_atendimento.md
      limites_ofertas.md
    templates/
      troubleshooting_template.md
      fatura_template.md
  agent/
    assistant_service.py
    tools_registry.py
  tools/
    churn_tool.py
    crm_tool.py
    billing_tool.py
    network_diagnostics_tool.py
  evaluations/
    eval_scenarios.json
    run_vertex_evaluation.py
    regression_tests_llm.py
```

### 7.2 Base RAG – Vertex AI Search

#### 7.2.1 Ingestão de Documentos

`rag/ingest_documents.py`:

- Copiar documentos de `docs/` do repositório para GCS:
  - `gs://.../docs/telecom/`.
- Normalizar formatos (PDF, DOCX, HTML).

#### 7.2.2 Criação do DataStore do Vertex AI Search

`rag/build_vertex_search_datastore.py`:

- Criar um **DataStore** no Vertex AI Search (Discovery Engine):
  - Tipo: `unstructured` (para PDFs, HTML etc.).
- Associar o DataStore ao bucket GCS de documentos.
- Iniciar job de indexação.

#### 7.2.3 Integração com BigQuery

`rag/sync_bigquery_knowledge.py`:

- Criar views ou tabelas de conhecimento em BQ (ex.: FAQs estruturadas).
- Configurar DataStore adicional com origem BigQuery (se necessário).

### 7.3 Prompts e Templates

- `prompts/system/*.md`:
  - Prompts de sistema para:
    - Suporte técnico.
    - Retenção de churn.
- `prompts/rules/*.md`:
  - Políticas de atendimento, compliance, limites de desconto.
- `prompts/templates/*.md`:
  - Estrutura de respostas (ex.: diagnóstico passo a passo, resumo de fatura).

Versão de prompts:

- Controlada via Git neste diretório.
- Utilizar tags ou convenção de versão nos arquivos (`v1`, `v2`).

### 7.4 Vertex AI Generative AI (Gemini / Llama)

Configurar, no código do agente (`agent/assistant_service.py`):

- Uso do SDK `google-cloud-aiplatform` para:
  - Chamar **Gemini 1.5 Pro** ou equivalente.
  - Passar:
    - Prompt de sistema (da pasta `prompts/system/`).
    - Prompt de regras.
    - Contexto RAG (conteúdo retornado pelo Vertex AI Search).
  - Definir parâmetros:
    - `temperature`, `top_p`, `top_k`, limites de tokens, etc.

### 7.5 Vertex AI Evaluation

`evaluations/run_vertex_evaluation.py`:

- Define conjuntos de testes (`eval_scenarios.json`):
  - Inputs (perguntas).
  - Respostas esperadas ou critérios.
- Usa **Vertex AI Evaluation** para:
  - Rodar regressão semântica em prompts.
  - Medir métricas como qualidade, segurança, consistência.

`evaluations/regression_tests_llm.py`:

- Roda consultas de teste localmente, comparando respostas atuais com baseline.

---

## 8. Fase 5 – Assistente LLM Telecom + Integrações

### 8.1 Ferramentas (Tools) do Agente

Em `llmops/tools/`:

#### 8.1.1 `churn_tool.py`

- Fornece função `get_churn_risk(customer_id)`:
  - Consulta:
    - Tabela BQ `telecom_gold.telco_churn_scored` (batch).
    - Ou endpoint online (Vertex AI Endpoint ou Cloud Run).
  - Retorna:
    - Probabilidade de churn.
    - Segmento de risco.

#### 8.1.2 `crm_tool.py`

- Simula chamadas a um CRM (via API mock ou tabela BQ).

#### 8.1.3 `billing_tool.py`

- Consulta faturas, planos, status de pagamento.

#### 8.1.4 `network_diagnostics_tool.py`

- Simula testes de conexão, reset de modem etc. (mockado para o MVP).

### 8.2 Serviço do Assistente – Cloud Run

`agent/assistant_service.py`:

- API HTTP (ex.: FastAPI ou Flask) rodando em **Cloud Run**:
  - Endpoint `/chat`:
    - Entrada: mensagens do usuário, contexto, identificadores (customer_id, canal).
    - Fluxo:
      1. Chamar Vertex AI Search para obter contexto RAG.
      2. Carregar prompts de sistema/regras.
      3. Chamar Gemini/LLM com contexto+prompts.
      4. Quando necessário, acionar tools (churn, CRM, billing).
      5. Retornar resposta estruturada (mensagem + ações propostas).

**Deploy**:

- Dockerfile na raiz ou em `llmops/`.
- Pipeline de build com Cloud Build:
  - Build da imagem.
  - Push para Artifact Registry.
  - Deploy para Cloud Run (dev/prod).

### 8.3 Vertex AI Agents (Opcional)

Alternativa ao serviço manual:

- Configurar um **Vertex AI Agent**:
  - Ferramentas definidas (chamadas HTTP do agent para Cloud Run/CRM/churn).
  - DataStore de Vertex AI Search como fonte de contexto.
  - LLM (Gemini) configurado pelo console ou via SDK.

O código `assistant_service.py` pode então ser apenas um proxy para o Agent.

### 8.4 Observabilidade LLM

Usar:

- **Vertex AI Observability**:
  - Logs de prompts/respostas (com cuidado a PII).
  - Métricas de uso e latência.
- **Cloud Logging**:
  - Logs da aplicação Cloud Run.
- **Cloud Monitoring**:
  - Dashboards para:
    - Latência do assistente.
    - Taxa de erros.
    - Distribuição de tipos de chamadas (suporte, retenção, fatura).

---

## 9. Fase 6 – CI/CD, Qualidade e Operação

### 9.1 Workflows GitHub Actions

Em `.github/workflows/`:

#### 9.1.1 `ci.yml`

- Objetivo: qualidade de código.
- Passos:
  - `checkout` do repositório.
  - Setup Python.
  - Instalar dependências.
  - Rodar:
    - `black --check`.
    - `isort --check-only`.
    - `ruff`/`flake8`.
    - `pytest --cov`.
  - Publicar:
    - Relatório de testes (JUnit XML).
    - Cobertura (coverage.xml).

#### 9.1.2 `cd-ml.yml`

- Objetivo: deploy de componentes MLOps.
- Gatilhos:
  - Push/merge em `main` ou tags específicas.
- Passos:
  - Build de imagens Docker (se necessário) para pipelines ou jobs.
  - Deploy de arquivos Terraform (`infra/terraform/envs/dev`).
  - Submissão de pipelines Vertex AI (churn, retreino).

#### 9.1.3 `cd-llm.yml`

- Objetivo: deploy do assistente LLM.
- Passos:
  - Build da imagem do serviço Cloud Run.
  - Push para Artifact Registry.
  - Deploy para Cloud Run (usando gcloud ou Cloud Deploy).
  - Atualização de configurações de Vertex AI Search/Agents (se scriptadas).

#### 9.1.4 Relatórios de testes e dashboards (analogia ao Azure DevOps)

No Azure DevOps você usa um `azure-pipelines.yaml` com stages de testes e visualiza os relatórios nos dashboards. O equivalente neste projeto, usando **GitHub + Google Cloud**, será:

- **Arquivo de pipeline**:
  - Em vez de `azure-pipelines.yaml`, usaremos arquivos YAML em `.github/workflows/` (por exemplo, `ci.yml`).
  - Esses workflows são disparados em push/PR e executam os testes da mesma forma.

- **Execução de testes no GitHub Actions**:
  - No `ci.yml`, rodar:
    - `pytest --junitxml=reports/junit.xml --cov=.` para gerar:
      - Arquivo JUnit XML (`reports/junit.xml`) com detalhes de testes (passou/falhou).
      - Arquivo de cobertura (`coverage.xml`) via `coverage xml`.
  - Publicar esses arquivos como artifacts do workflow:
    - Usar `actions/upload-artifact` para anexar `reports/junit.xml` e `coverage.xml`.
  - Opcionalmente, usar ações especializadas (ex.: publicadores de resultados de teste) para:
    - Exibir testes e falhas diretamente no summary do job.
    - Comentar em PRs com resumo de cobertura e testes.

- **Dashboards de testes**:
  - Dentro do próprio GitHub:
    - Usar a aba **Actions** e o summary do workflow para acompanhar:
      - Histórico de sucesso/falha dos pipelines.
      - Resumo de testes (por job).
    - Integrar com serviços externos de cobertura (ex.: Codecov) se desejado.
  - No Google Cloud:
    - Opcionalmente, enviar métricas agregadas de testes (ex.: quantidade total de testes, número de falhas) para:
      - **Cloud Monitoring** como métricas customizadas.
      - **BigQuery** via job adicional no workflow (gravando estatísticas de testes).
    - Construir dashboards em:
      - **Cloud Monitoring** (painéis com métricas de execução de CI).
      - **Looker Studio** (relatórios mais ricos usando tabelas de BigQuery).

Em resumo, o papel do `azure-pipelines.yaml` será cumprido por um ou mais arquivos `.github/workflows/*.yml`, e a visualização de testes será feita principalmente nos **dashboards do GitHub Actions**, com a opção de espelhar métricas em **Cloud Monitoring/BigQuery** para dashboards corporativos, se necessário.

### 9.2 Cloud Build e Artifact Registry

Em `infra/`:

- `cloudbuild-mlops.yaml`:
  - Pipeline de build/teste de imagens MLOps (treino/inferência/pipelines).
- `cloudbuild-llmops.yaml`:
  - Build da imagem do assistente LLM.

`Artifact Registry`:

- Repositório: `telecom-mlops-llmops-docker`.

### 9.3 Dashboards e SLOs

Usar Terraform (`modules/monitoring`) para:

- Criar dashboards:
  - MLOps:
    - Latência de pipelines.
    - Taxa de falha de jobs.
    - Métricas de churn (AUC, f1 por versão).
  - LLMOps:
    - Latência de resposta do assistente.
    - QPS.
    - Erros por tipo.
- Criar SLOs (opcional) para:
  - Disponibilidade do assistente (Cloud Run).
  - Taxa de sucesso de batch jobs.

---

## 10. Resumo e Próximos Passos

Este roadmap define:

- Os serviços Google Cloud a serem usados e seus papéis específicos.
- A estrutura de código esperada (módulos Python, notebooks, pipelines).
- A estrutura de IaC (Terraform) para provisionamento consistente.
- Os mecanismos de CI/CD, monitoramento, drift e retreino.
- A integração entre MLOps (churn) e LLMOps (assistente Telecom).

### Próximas ações recomendadas

1. Implementar a **Fase 0 e 1** com Terraform (projeto, GCS, BQ, Dataplex, Data Catalog).
2. Criar os módulos Python e notebooks básicos em `mlops/` seguindo a Fase 2.
3. Subir o primeiro pipeline de treino + batch prediction no Vertex AI.
4. Implantar a base RAG com Vertex AI Search e preparar prompts (Fase 4).
5. Construir o serviço do assistente em Cloud Run e integrá-lo ao modelo de churn.
6. Configurar CI/CD e dashboards para fechar o ciclo operacional.

Com isso, o time terá um caminho claro para sair do repositório atual até uma plataforma completa de **Telecom MLOps + LLMOps** em produção no Google Cloud.
