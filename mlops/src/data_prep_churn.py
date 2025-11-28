"""
Preparação de dados de churn (bronze → silver → gold).

Responsável por:
- Ler `telecom_bronze.telco_churn_raw`.
- Aplicar limpeza, ajustes de tipos e feature engineering.
- Escrever tabelas `telecom_silver.telco_churn_clean` e
  `telecom_gold.telco_churn_features` em BigQuery.
"""


def run_data_prep() -> None:
    """
    Executa a preparação de dados de churn.
    """
    # TODO: Implementar lógica de transformação em BigQuery / pandas.
    raise NotImplementedError("Implementar preparação de dados de churn.")


if __name__ == "__main__":
    run_data_prep()

