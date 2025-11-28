"""
Funções utilitárias para interação com Vertex AI.

Inclui helpers para:
- Inicializar o cliente `aiplatform`.
- Criar e monitorar Custom Jobs e Batch Jobs.
- Interagir com Feature Store e Model Registry.
"""

from typing import Any


def init_vertex_ai(project_id: str, region: str) -> None:
    """
    Inicializa o SDK do Vertex AI para um projeto/região.

    :param project_id: ID do projeto GCP.
    :param region: Região do Vertex AI (por exemplo, 'us-central1').
    """
    # TODO: Implementar inicialização do aiplatform.init(...)
    raise NotImplementedError("Implementar inicialização do Vertex AI SDK.")


def create_custom_job(job_spec: Any) -> str:
    """
    Cria um Custom Job no Vertex AI a partir de uma especificação.

    :param job_spec: Especificação do job (dicionário ou objeto específico).
    :return: ID do job criado.
    """
    # TODO: Implementar criação de Custom Job via aiplatform.CustomJob.
    raise NotImplementedError("Implementar criação de Custom Job no Vertex AI.")

