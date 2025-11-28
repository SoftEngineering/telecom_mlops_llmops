"""
Testes básicos para o módulo de preparação de dados de churn.
"""

from mlops.src import data_prep_churn


def test_run_data_prep_exists() -> None:
    """
    Garante que a função principal de preparação de dados existe.
    """
    assert hasattr(data_prep_churn, "run_data_prep")

