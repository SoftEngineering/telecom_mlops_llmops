"""
Criação e carregamento de features no Vertex AI Feature Store.

- Cria o Feature Store e o entity type `customer`, se necessário.
- Cria as features definidas para churn.
- Carrega dados a partir de `telecom_gold.telco_churn_features`.
"""


def setup_feature_store() -> None:
    """
    Cria o Feature Store de churn e carrega features.
    """
    # TODO: Implementar criação de featurestore, entity types e ingestão de features.
    raise NotImplementedError("Implementar configuração do Feature Store de churn.")


if __name__ == "__main__":
    setup_feature_store()

