"""
Testes básicos para o módulo de inferência batch de churn.
"""

from mlops.src import batch_inference


def test_run_batch_inference_exists() -> None:
    """
    Garante que a função principal de inferência batch existe.
    """
    assert hasattr(batch_inference, "run_batch_inference")

