# Arquitetura MLOps/LLMOps no Google Cloud – De-Para Databricks

Este documento descreve como implementar, no **Google Cloud**, uma solução de **MLOps** para modelo de churn batch (por exemplo, **XGBoost**), com boas práticas similares ao que você já fazia no **Databricks**, integrando com o contexto deste projeto de **Telecom MLOps + LLMOps**.

O foco é:

- Fazer um **de-para Databricks → Google Cloud**.
- Detalhar os **componentes GCP/Vertex AI** recomendados.
- Mostrar como encaixar isso na estrutura deste repositório (`mlops/`, `llmops/`, `infra/`, `.github/`).

> Observação: componentes e nomes seguem a documentação pública da Google Cloud (Vertex AI, BigQuery, Cloud Storage, etc.), considerando o estado atual até 2024.

---

## 1. De-Para Databricks → Google Cloud

### 1.1 Visão Geral

| Camada / Função                         | Databricks                                             | Google Cloud / Vertex AI                                                                                  |
|----------------------------------------|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Workspace / ambiente de desenvolvimento| Databricks Workspace + Notebooks                      | Vertex AI Workbench (managed notebooks) / Colab Enterprise / Cloud Shell Editor                          |
| Orquestração de jobs / pipelines       | Databricks Jobs                                        | Vertex AI Pipelines, Cloud Composer (Airflow), Cloud Scheduler + Cloud Run/Cloud Functions               |
| Cluster de execução                    | Clusters Databricks (Spark)                           | Vertex AI Custom Jobs (gerenciados), Dataproc (Spark gerenciado), GKE (opcional)                         |
| Data Lake                              | DBFS + Delta Lake (bronze/silver/gold)                | Cloud Storage (GCS) com camadas `bronze/`, `silver/`, `gold/`                                            |
| Catálogo / Governança de dados         | Unity Catalog                                          | Dataplex + Data Catalog + IAM                                                                            |
| Warehouse / Lakehouse                  | Tabelas Delta + SQL Analytics                          | BigQuery (DW principal)                                                                                  |
| Feature Store                          | Databricks Feature Store                               | Vertex AI Feature Store (BigQuery + online store)                                                        |
| Experimentos                           | MLflow Tracking                                        | Vertex AI Experiments (ou TensorBoard + BigQuery)                                                        |
| Registro de modelos                    | MLflow Model Registry                                  | Vertex AI Model Registry                                                                                  |
| Treinamento de modelos                 | Notebooks + MLlib/XGBoost + Jobs                       | Vertex AI Custom Training (Python/Container) ou AutoML Tabular, rodando sobre GCS/BigQuery               |
| Inferência batch                       | Jobs Databricks lendo Delta e escrevendo tabelas       | Vertex AI Batch Prediction + BigQuery/GCS (outputs)                                                      |
| Inferência online                      | Modelos servidos via endpoints REST (às vezes em pods) | Vertex AI Online Prediction (endpoints gerenciados) ou Cloud Run/GKE com containers próprios             |
| AutoML                                 | Databricks AutoML                                      | Vertex AI AutoML (tabular, forecasting, etc.)                                                            |
| Testes & Qualidade                     | pytest + MLflow + integrações externas                 | pytest dentro de containers + GitHub Actions + Cloud Build / Cloud Deploy                                |
| Observabilidade                        | Logs Databricks, dashboards externos                   | Cloud Logging, Cloud Monitoring, Error Reporting, Vertex AI Observability                                |
| Alertas                                | Integrações com email, Slack                           | Cloud Monitoring Alerting + Pub/Sub + Cloud Functions/Run (email, Slack, Webhook)                       |
| Infra como código                      | (Opcional) Terraform para Databricks                   | Terraform para GCP (IAM, redes, GCS, BQ, Vertex, Cloud Run, etc.)                                       |

---

## 2. Camada de Dados: Bronze, Silver, Gold

### 2.1 De-Para

| Conceito                             | Databricks / Unity Catalog      | Google Cloud                                                       |
|--------------------------------------|----------------------------------|--------------------------------------------------------------------|
| Data Lake bruto (bronze)             | Tabelas Delta em bronze         | GCS bucket `gcs://<project>-telecom-data/bronze/`                 |
| Dados refinados (silver)             | Silver tables                   | `gcs://.../silver/` + tabelas intermediárias em BigQuery          |
| Camada analítica (gold)              | Gold tables                     | Tabelas de consumo em BigQuery (`bq://<project>.telecom_gold.*`)  |
| Catálogo e governança                | Unity Catalog                    | Dataplex (zonas data lake) + Data Catalog (metadados, tags)       |

### 2.2 Recomendações de estrutura (neste projeto)

- Criar um bucket principal:
  - `telecom-mlops-llmops-data-<env>` (por exemplo: `-dev`, `-prod`).
- Dentro do bucket:
  - `bronze/churn/…` — ingestão crua (ex.: CSVs originais como `WA_Fn-UseC_-Telco-Customer-Churn.csv`).
  - `silver/churn/…` — dados limpos, tipados, com join de múltiplas fontes.
  - `gold/churn/…` — dataset final usado pelo modelo (features + label).
- Em **BigQuery**:
  - Dataset `telecom_bronze` (opcional) para staging.
  - Dataset `telecom_silver` com views e tabelas refinadas.
  - Dataset `telecom_gold` com tabelas de treino/inferência.

A governança (equivalente ao Unity Catalog) virá de:

- **Dataplex** para definir zonas (bronze/silver/gold), políticas de qualidade e descoberta.
- **Data Catalog** para metadados, descrições, lineage e tags (sensibilidade, PII, etc.).

---

## 3. Notebooks e Scripts: Preparação, Treino, Drift, Inferência

No Databricks, você organiza o fluxo em **notebooks**. No Google Cloud, recomendamos:

- Usar **Vertex AI Workbench** (managed notebooks) para desenvolvimento interativo.
- Extrair a lógica crítica em **módulos Python** neste repositório (`mlops/src/`).
- Orquestrar execução em produção via **Vertex AI Pipelines** ou **Custom Jobs**.

### 3.1 Notebook de preparação de dados

**Databricks (como era):**

- Notebooks Spark lendo bronze, gerando silver/gold.
- Registro de features na Databricks Feature Store.
- Jobs Databricks agendados.

**Google Cloud (proposta):**

- `mlops/notebooks/data_prep_churn.ipynb`:
  - Desenvolvido em Vertex AI Workbench.
  - Usa `pandas`/`scikit-learn` ou **Spark** em Dataproc, se necessário.
  - Lê `bronze` de GCS, faz limpeza, joins, encoding e grava em BigQuery (`telecom_silver`, `telecom_gold`).
  - (Opcional) Automatizar conversão do notebook para script usando `papermill`/`nbconvert`, para uso em pipeline.

- Registro de features em **Vertex AI Feature Store**:
  - Definir **entity types** (ex.: `customer`).
  - Criar **features** (ex.: `tenure`, `monthly_charges`, `contract_type`, etc.).
  - Carregar dados da tabela BigQuery `telecom_gold.features_churn` para o Feature Store offline.
  - Habilitar online store para features usadas em inferência online (se necessário).

### 3.2 Notebook de treino do modelo

**Databricks (como era):**

- Notebook treinando XGBoost, lendo da Feature Store.
- Registro do modelo no MLflow Model Registry.
- Geração de plots de importância/explicabilidade (SHAP etc.).

**Google Cloud (proposta):**

- `mlops/notebooks/train_churn_xgboost.ipynb`:
  - Usa **Vertex AI Feature Store** ou diretamente BQ (`telecom_gold.features_churn`).
  - Se necessário, reconstrói dataset “no tempo” para evitar leakage (usando colunas de datas e partições de BQ).
  - Treina modelo XGBoost (via `xgboost` ou `sklearn`).
  - Calcula métricas (AUC, precision-recall, etc.) e curvas de ROC, PR.
  - Gera explicabilidade usando SHAP ou **Vertex Explainable AI** (se modelo implantado em Vertex).

- Para produção:
  - Empacotar a lógica de treino em `mlops/src/train_churn.py`.
  - Criar um **Vertex AI Custom Job** ou um **componente de Vertex Pipelines** que chame esse script.
  - Registrar o modelo e os artefatos:
    - Modelo em `Vertex AI Model Registry`.
    - Métricas e parâmetros em **Vertex AI Experiments**.

### 3.3 Notebook de avaliação de data drift e model drift

**Databricks (como era):**

- Notebook com estatísticas de drift.
- Alertas via email.
- Retreino automático ao detectar drift.

**Google Cloud (proposta):**

- `mlops/notebooks/drift_monitoring_churn.ipynb` (para exploração) + scripts produtivos:
  - Coleta amostras de:
    - Dados de produção (features + scores) de BigQuery (`telecom_gold.scored_churn`).
    - Dados históricos usados no treino.
  - Calcula estatísticas de drift (ex.: PSI, KS, mudança de média/variância, frequência de categorias).
  - Para **online prediction** (se existir), pode usar **Vertex AI Model Monitoring**, que já oferece:
    - Drift de feature.
    - Drift de label (se disponível).
    - Alertas integrados a Cloud Monitoring.

- Para **alertas**:
  - Salvar métricas de drift em BigQuery.
  - Configurar **Cloud Monitoring + Alerting**:
    - Job (Cloud Run/Custom Job) escreve métricas em Cloud Monitoring.
    - Política de alerta dispara para:
      - Email.
      - Webhook (ex.: Slack).
      - Pub/Sub → Cloud Function/Run → integrações personalizadas.

- Para **retreino automático**:
  - Criar um **Vertex AI Pipeline de retreino** com passos:
    1. Leitura das métricas de drift (BigQuery).
    2. Condição: se drift > threshold configurado.
    3. Execução do componente de treino (`train_churn`).
    4. Avaliação e comparação com modelo atual.
    5. Se melhor, atualização do endpoint (batch/online) e registro da nova versão.
  - Agendar o pipeline com **Cloud Scheduler** ou **Cloud Composer**.

### 3.4 Notebook de inferência batch

**Databricks (como era):**

- Notebook lendo features atuais, aplicando modelo XGBoost, gravando resultados em tabela “diamond”.

**Google Cloud (proposta):**

- Inferência batch preferencialmente via **Vertex AI Batch Prediction**:
  - Input: tabela BigQuery `telecom_gold.features_churn_score_input` ou arquivos em GCS.
  - Output: tabela BigQuery `telecom_gold.scored_churn` (equivalente à tua “camada diamond”).
  - Configurável quanto a recursos, paralelismo e GCS/BQ como destino.

- Alternativa (se quiser replicar lógica “notebook”):
  - `mlops/notebooks/batch_inference_churn.ipynb` para prototipagem.
  - Em produção, um script `mlops/src/batch_inference.py` chamado por:
    - **Vertex AI Custom Job** agendado.
    - Ou Cloud Run job lendo da Feature Store/BigQuery e escrevendo de volta em BQ.

---

## 4. Boas Práticas: Testes, Qualidade, CI/CD

### 4.1 Testes unitários e de integração

**Databricks (como era):**

- pytest em notebooks/scripts.
- Integração com MLflow ou ferramentas externas para relatórios.

**Google Cloud (proposta):**

- Estruturar o código em módulos:
  - `mlops/src/`: lógica de EDA, data prep, feature engineering, treino, inferência.
  - `mlops/tests/`: testes unitários e, quando possível, de integração (ex.: små mocks de BigQuery/FS).

- Ferramentas de qualidade:
  - `black`, `isort`, `flake8` ou `ruff`.
  - `pytest` + `pytest-cov` para cobertura.

- Execução dos testes:
  - **GitHub Actions** (conforme já previsto no README):
    - Workflow `ci.yml` em `.github/workflows/`:
      - Instala dependências.
      - Roda `black --check`, `isort --check-only`, `ruff`/`flake8`.
      - Roda `pytest --cov`.
      - Publica relatório de cobertura (ex.: Codecov ou artifact do próprio GitHub).

  - **Cloud Build** (opcional/alternativo):
    - Ao dar push/merge em branch principal, Cloud Build:
      - Roda pipeline de testes.
      - Constrói imagens Docker (treino/inferência/pipeline components).
      - Publica imagens no **Artifact Registry**.

### 4.2 Relatórios de testes

- Nos workflows de CI, configurar geração de:
  - Relatório JUnit XML (`pytest --junitxml=...`).
  - Relatório de cobertura (`coverage.xml`).
- GitHub Actions consegue:
  - Exibir testes que falharam.
  - Mostrar cobertura por arquivo.

---

## 5. Deploy do Modelo: Batch e Kubernetes

### 5.1 Batch (principal)

Para o teu caso de uso (modelo batch de churn), o fluxo recomendado é:

1. **Treino**:
   - Vertex AI Pipelines orquestra `custom job` de treino com XGBoost.
   - Modelo registrado no **Vertex AI Model Registry**.

2. **Batch Prediction**:
   - Job de Batch Prediction referenciando o modelo registrado.
   - Input: BigQuery (features) ou GCS.
   - Output: BigQuery em tabela `telecom_gold.scored_churn` (camada “diamond”).

3. **Agendamento**:
   - **Cloud Scheduler** + **Cloud Functions/Run** chamando a API do Vertex AI para iniciar jobs de batch.
   - Ou steps no **Vertex AI Pipeline** com agendamento recorrente.

### 5.2 Kubernetes (opcional, similar ao que fazia com pods)

Se você quiser deploy opcional em pods (equivalente ao que fazia em Kubernetes/Databricks):

- Usar **GKE (Google Kubernetes Engine)**:
  - Construir uma imagem Docker com:
    - Código do modelo.
    - Dependências (XGBoost, etc.).
    - API em `FastAPI` ou `Flask`.
  - Fazer deploy em GKE Autopilot ou Standard.
  - Expor um endpoint HTTP (para consumo interno ou por APIs).

- Alternativa serverless mais simples:
  - **Cloud Run**:
    - Mesmo container do GKE.
    - Escalonamento automático.
    - Ideal para servir APIs de churn ou integrar com o Assistente LLM.

No contexto deste projeto, para batch puro, **Vertex AI Batch Prediction** costuma ser suficiente; Kubernetes/Cloud Run é mais relevante se:

- Você quiser inferência em tempo real para o agente LLM acessar o risco de churn.
- Houver necessidades específicas de latência, protocolos ou libs nativas.

---

## 6. Monitoramento, Data Drift e Model Drift

### 6.1 Monitoramento de modelo no Vertex AI

- Para modelos servidos em endpoints **Online Prediction**:
  - Habilitar **Vertex AI Model Monitoring**:
    - Configurar esquemas de features (tipos, faixas, categorias).
    - Definir thresholds de drift.
    - Vertex AI monitora o tráfego e calcula métricas.
    - Integra com **Cloud Monitoring** para alertas.

- Para **Batch Predictions**:
  - O monitoramento é mais “offline”:
    - Após cada job batch, gravar:
      - Estatísticas das features de entrada.
      - Distribuição de scores.
      - Labels observadas (quando disponíveis futuramente).
    - Usar scripts (Custom Jobs/Cloud Run) que:
      - Comparam essas distribuições com as de treino.
      - Calculam PSI, KS, etc.
      - Escrevem resultados em BigQuery + Cloud Monitoring.

### 6.2 Alertas e Retreino

- Alertas:
  - Criar métricas customizadas (ex.: `churn_feature_drift_score`) em Cloud Monitoring.
  - Configurar **Alerting Policy**:
    - Condição: `churn_feature_drift_score > threshold`.
    - Notificações: email, Slack, webhook, SMS etc.

- Retreino:
  - O alerta pode:
    - Disparar um **Pub/Sub**.
    - Pub/Sub aciona Cloud Function/Run que:
      - Inicia o **Vertex AI Pipeline** de retreino.
  - Ou, mais simples:
    - Rodar o pipeline de retreino em agenda fixa (ex.: semanal) e nele verificar drift.

---

## 7. Integração com LLMOps e Assistente Telecom

Embora o foco seja o MLOps de churn, neste projeto o modelo se conecta a um **Assistente LLM de Telecom** (RAG + agentes), conforme o README e o PDF.

### 7.1 De-Para conceitual

| Função                               | Databricks (hipotético)                         | Google Cloud / Vertex AI                                             |
|--------------------------------------|-------------------------------------------------|----------------------------------------------------------------------|
| Orquestração de pipelines LLM       | Jobs + notebooks                                | Vertex AI Pipelines + Agents + Cloud Run                            |
| Base RAG                            | Delta tables + libs externas                    | Vertex AI Search (sobre GCS + BQ)                                   |
| Modelos LLM                         | Modelos hospedados externamente                 | Gemini 1.5 Pro, Llama 3, Mistral (Vertex AI Model Garden)           |
| Ferramentas/Tools do agente         | Funções PySpark/Python internas                 | Cloud Run/Functions, APIs Vertex AI (churn, CRM, billing etc.)      |
| Observabilidade LLM                 | Logs customizados                                | Vertex AI Observability + Cloud Logging                             |
| Avaliação de prompts                | Testes ad hoc                                   | Vertex AI Evaluation (regressão semântica, métricas de qualidade)   |

### 7.2 Ponto de integração com o modelo de churn

- Endpoints possíveis:
  - **Batch**:
    - Assistente LLM consulta tabelas BigQuery com scores `churn_risk` pré-calculados.
  - **Online**:
    - Assistente chama uma API em Cloud Run (ou Vertex Endpoint) que:
      - Recebe os dados do cliente.
      - Busca features (Vertex Feature Store).
      - Executa o modelo XGBoost.
      - Retorna o risco de churn.

- No **agente LLM**:
  - Definir uma “tool” tipo `get_churn_risk(customer_id)` que chama esta API.
  - A lógica do agente (em Cloud Run ou Vertex AI Agents) usa essa tool para:
    - Ajustar tom da resposta.
    - Sugerir retenção/ofertas personalizadas.

---

## 8. Automação e AutoML

### 8.1 AutoML para novos modelos

**Databricks (como era):**

- Databricks AutoML sugerindo modelos, features, etc.

**Google Cloud (proposta):**

- **Vertex AI AutoML (Tabular)**:
  - Dataset de entrada: tabela BigQuery `telecom_gold.features_churn`.
  - Configuração:
    - Target: coluna de churn.
    - Features: colunas de entrada configuradas.
    - Split treino/validação/teste (auto ou manual).
  - Vertex AutoML:
    - Treina múltiplos modelos candidatos.
    - Sugere o “best model”.
    - Gera explicabilidade global e local.

- Integração com pipeline:
  - Ter um pipeline “paralelo” de AutoML para experimentação.
  - Comparar o modelo AutoML com o modelo “manual” XGBoost.
  - Se superar métricas definidas, registrar no Model Registry e avaliar promoção.

---

## 9. Como isso encaixa neste repositório

### 9.1 Sugestão de estrutura (evolução)

- `mlops/`
  - `src/`
    - `data_prep_churn.py` — preparação de dados (bronze → silver → gold + carregamento Feature Store).
    - `train_churn.py` — treino do modelo (XGBoost) + registro no Vertex AI.
    - `batch_inference.py` — inferência batch, se não usar apenas Batch Prediction.
    - `drift_monitoring.py` — cálculo de métricas de drift e escrita em BQ/Monitoring.
    - `utils_vertex.py` — helpers para Vertex AI (experiments, model registry, jobs etc.).
  - `notebooks/`
    - `data_prep_churn.ipynb`
    - `train_churn_xgboost.ipynb`
    - `drift_monitoring_churn.ipynb`
    - `batch_inference_churn.ipynb`
  - `tests/`
    - `test_data_prep.py`
    - `test_train_churn.py`
    - `test_batch_inference.py`

- `llmops/`
  - `prompts/`, `rag/`, `agent/`, `tools/`, `evaluations/` (como já sugerido no README).
  - Tools chamando APIs de churn (Cloud Run ou Vertex Endpoint).

- `infra/`
  - `terraform/`
    - `gcs.tf` — buckets bronze/silver/gold.
    - `bigquery.tf` — datasets e tabelas.
    - `vertex.tf` — Feature Store, Model Registry, Pipelines, endpoints.
    - `cloud_run.tf` / `gke.tf` — APIs de churn/assistente.
    - `monitoring.tf` — dashboards, alertas.

- `.github/workflows/`
  - `ci.yml` — testes, lint, build.
  - `cd-ml.yml` — deploy de pipelines e serviços ML.
  - `cd-llm.yml` — deploy de componentes LLM (prompts, agentes).

---

## 10. Resumo

Replicando o que você fazia no Databricks no contexto Google Cloud, a arquitetura recomendada para este projeto:

- Usa **Cloud Storage + BigQuery + Dataplex** como data lakehouse (bronze/silver/gold).
- Usa **Vertex AI Feature Store + Pipelines + Custom Jobs + Model Registry + Batch Prediction** para o ciclo MLOps do modelo de churn.
- Garante boas práticas via **GitHub Actions** e/ou **Cloud Build** (testes, lint, cobertura).
- Faz monitoramento de drift e retreino automático com **BigQuery + Cloud Monitoring + Vertex Pipelines**.
- Integra o modelo ao **Assistente LLM Telecom** usando **Vertex AI Search, Gemini/Llama, Agents e Cloud Run**.

Assim, você mantém o mesmo nível (ou maior) de maturidade MLOps/LLMOps que tinha no Databricks, aproveitando os serviços nativos do Google Cloud e a arquitetura desenhada neste repositório.

