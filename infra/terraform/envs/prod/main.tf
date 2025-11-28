// Terraform main para ambiente de produção.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

// TODO: Instanciar módulos (gcs, bigquery, vertex_ai, etc.) com configurações de produção.

