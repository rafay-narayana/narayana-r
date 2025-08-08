terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.33"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig_path
}
