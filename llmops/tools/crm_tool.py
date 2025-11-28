"""
Tool para consultar informações de CRM do cliente.
"""

from typing import Dict


def get_customer_profile(customer_id: str) -> Dict[str, str]:
    """
    Retorna informações básicas de CRM do cliente.

    :param customer_id: Identificador único do cliente.
    """
    # TODO: Implementar consulta a fonte de dados de CRM (mock ou real).
    raise NotImplementedError("Implementar tool de consulta ao CRM.")

