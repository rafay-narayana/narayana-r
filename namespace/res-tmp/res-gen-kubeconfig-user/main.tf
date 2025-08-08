terraform {
  required_providers {
    rafay = {
      version = "1.1.47"
      source  = "RafaySystems/rafay"
    }
  }
}

/***************************************
  Get kubeconfig for cluster
 ***************************************/
data "rafay_download_kubeconfig" "kubeconfig_cluster" {
  cluster = var.cluster_name
}