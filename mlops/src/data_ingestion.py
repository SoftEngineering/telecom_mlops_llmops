"""
Ingestão inicial dos dados de churn para o data lake e BigQuery.

Este script deve:
- Ler o dataset original de churn.
- Escrever uma cópia na camada bronze (GCS).
- Criar/atualizar a tabela `telecom_bronze.telco_churn_raw` em BigQuery.

A implementação detalhada será feita em etapas futuras.
"""

from typing import Optional


def run_data_ingestion(source_path: Optional[str] = None) -> None:
    """
    Executa a ingestão de dados de churn.

    :param source_path: Caminho opcional para o arquivo CSV de churn.
    """
    # TODO: Implementar leitura do CSV local/GCS e gravação em GCS + BigQuery.
    raise NotImplementedError("Implementar lógica de ingestão de dados de churn.")


if __name__ == "__main__":
    run_data_ingestion()

