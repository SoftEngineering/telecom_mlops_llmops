"""
Ingestão de documentos de telecom para a base RAG.

- Copia documentos locais (pasta docs/) para GCS.
- Pode realizar normalização de formatos se necessário.
"""


def run_ingestion() -> None:
    """
    Executa a ingestão de documentos para o bucket GCS configurado.
    """
    # TODO: Implementar cópia de documentos para GCS.
    raise NotImplementedError("Implementar ingestão de documentos para RAG.")


if __name__ == "__main__":
    run_ingestion()

