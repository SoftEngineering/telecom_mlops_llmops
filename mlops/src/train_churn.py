"""
Treino do modelo de churn (ex.: XGBoost) usando dados em BigQuery ou Feature Store.

- Lê `telecom_gold.telco_churn_features`.
- Realiza split treino/validação/teste.
- Treina o modelo.
- Registra modelo no Vertex AI Model Registry e em Experiments.
"""


def run_training() -> None:
    """
    Executa o pipeline de treino do modelo de churn.
    """
    # TODO: Implementar treino e registro do modelo em Vertex AI.
    raise NotImplementedError("Implementar treino do modelo de churn.")


if __name__ == "__main__":
    run_training()

