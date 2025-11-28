"""
Inferência batch do modelo de churn.

Pode utilizar:
- Vertex AI Batch Prediction, apontando para tabelas BigQuery ou arquivos GCS.
- Ou um job customizado que lê de BigQuery, aplica o modelo e grava a saída.
"""


def run_batch_inference() -> None:
    """
    Executa job de inferência batch e grava resultados na camada 'diamond'.
    """
    # TODO: Implementar chamada ao BatchPredictionJob ou lógica customizada.
    raise NotImplementedError("Implementar inferência batch de churn.")


if __name__ == "__main__":
    run_batch_inference()

