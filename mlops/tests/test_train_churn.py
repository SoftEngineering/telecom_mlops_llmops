"""
Testes básicos para o módulo de treino do modelo de churn.
"""

from mlops.src import train_churn


def test_run_training_exists() -> None:
    """
    Garante que a função principal de treino existe.
    """
    assert hasattr(train_churn, "run_training")

