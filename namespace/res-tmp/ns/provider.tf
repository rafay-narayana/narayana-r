terraform {
  required_providers {
    rafay = {
     source  = "RafaySystems/rafay"
      version = "1.1.49"
    }
    kubernetes = {
      source  = "registry.terraform.io/hashicorp/kubernetes"
      version = "~> 2.29" # Use a stable, widely supported version
    }
    null = {
      source  = "hashicorp/null"
      version = "3.2.3"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.5.2"
    }
  }
}

provider "rafay" {
  provider_config_file = "/Users/narayana/Downloads/rnr.json"
}
provider "kubernetes" {
  config_path = var.kubeconfig_path
}
