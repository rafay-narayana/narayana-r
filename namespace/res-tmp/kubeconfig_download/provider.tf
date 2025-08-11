terraform {
    required_providers {
    rafay = {
     source  = "RafaySystems/rafay"
      version = "1.1.49"
    }
  }
}

provider "rafay" {
  provider_config_file = var.rctl_config_path
}
