"""
Configurações centrais do projeto de churn.

Este módulo centraliza IDs de projeto, regiões e nomes padrão de
recursos GCP utilizados pelos scripts de MLOps.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GCPConfig:
    project_id: str = "telecom-mlops-llmops-dev"
    region: str = "us-central1"
    gcs_bucket_data: str = "telecom-mlops-llmops-data-dev"
    bq_dataset_bronze: str = "telecom_bronze"
    bq_dataset_silver: str = "telecom_silver"
    bq_dataset_gold: str = "telecom_gold"
    bq_dataset_monitoring: str = "telecom_monitoring"
    featurestore_id: str = "telecom_churn_featurestore"
    featurestore_entity_type_customer: str = "customer"
    model_display_name: str = "telecom_churn_xgboost"
    model_endpoint_name: Optional[str] = None


gcp_config = GCPConfig()

