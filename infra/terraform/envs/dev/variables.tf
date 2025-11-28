variable "project_id" {
  description = "ID do projeto GCP para ambiente de desenvolvimento."
  type        = string
}

variable "region" {
  description = "Região padrão (por exemplo, us-central1)."
  type        = string
  default     = "us-central1"
}

