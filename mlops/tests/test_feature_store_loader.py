"""
Testes básicos para o módulo de Feature Store.
"""

from mlops.src import feature_store_loader


def test_setup_feature_store_exists() -> None:
    """
    Garante que a função principal de configuração do Feature Store existe.
    """
    assert hasattr(feature_store_loader, "setup_feature_store")

