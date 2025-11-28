"""
Teste de regressão simples para o assistente LLM.

Pode ser usado em CI para garantir que mudanças em prompts/modelo
não degradem respostas em cenários críticos.
"""


def run_regression_tests() -> None:
    """
    Executa um conjunto básico de testes de regressão LLM.
    """
    # TODO: Implementar regressão local ou via chamadas ao serviço LLM.
    raise NotImplementedError("Implementar testes de regressão LLM.")


if __name__ == "__main__":
    run_regression_tests()

