"""
Registro e orquestração de ferramentas (tools) usadas pelo assistente LLM.
"""

from typing import Dict, Callable


def get_tools_registry() -> Dict[str, Callable]:
    """
    Retorna um dicionário com o mapeamento nome_da_tool -> função Python.
    """
    # TODO: Registrar tools como get_churn_risk, consultar CRM, billing, etc.
    raise NotImplementedError("Implementar registro de tools do assistente LLM.")

