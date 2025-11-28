"""
Serviço do assistente LLM Telecom exposto via API (para Cloud Run).

Responsável por:
- Receber requisições de chat.
- Consultar a base RAG (Vertex AI Search).
- Invocar o modelo LLM (Gemini/Llama).
- Acionar tools (churn, CRM, billing) quando necessário.
"""


def create_app():
    """
    Cria e retorna a aplicação web (ex.: FastAPI ou Flask).

    A implementação concreta será adicionada posteriormente.
    """
    # TODO: Implementar aplicação FastAPI/Flask para Cloud Run.
    raise NotImplementedError("Implementar serviço HTTP do assistente LLM.")


if __name__ == "__main__":
    create_app()

