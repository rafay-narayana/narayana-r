terraform {
  required_providers {
    kubernetes = {
      source  = "registry.terraform.io/hashicorp/kubernetes"
      version = "~> 2.29" # Use a stable, widely supported version
    }
  }
}

provider "kubernetes" {
  config_raw = var.kubeconfig_content
}

