"""
Monitoramento de data drift e model drift para churn.

- Compara distribuições de features entre treino e produção.
- Calcula métricas como PSI, KS, mudanças de média/variância.
- Opcionalmente escreve métricas em BigQuery e Cloud Monitoring.
"""


def run_drift_monitoring() -> None:
    """
    Executa o cálculo de métricas de drift para churn.
    """
    # TODO: Implementar cálculo de métricas de drift e persistência.
    raise NotImplementedError("Implementar monitoramento de drift para churn.")


if __name__ == "__main__":
    run_drift_monitoring()

