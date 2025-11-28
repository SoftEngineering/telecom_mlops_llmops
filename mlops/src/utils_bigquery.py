"""
Funções utilitárias para interação com BigQuery.
"""

from typing import Any


def run_query(sql: str) -> Any:
    """
    Executa uma query SQL no BigQuery.

    :param sql: Comando SQL a ser executado.
    :return: Resultado da query (por exemplo, DataFrame).
    """
    # TODO: Implementar execução de queries usando o cliente BigQuery.
    raise NotImplementedError("Implementar execução de query no BigQuery.")


def write_dataframe(dataset_table: str, df: Any) -> None:
    """
    Escreve um DataFrame em uma tabela BigQuery.

    :param dataset_table: Nome no formato 'dataset.tabela'.
    :param df: DataFrame com os dados a serem gravados.
    """
    # TODO: Implementar gravação de DataFrame no BigQuery.
    raise NotImplementedError("Implementar gravação de DataFrame no BigQuery.")

