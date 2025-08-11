data "rafay_download_kubeconfig" "kubeconfig_cluster" {
  cluster = var.cluster_name
}

resource "rafay_download_kubeconfig" "kubeconfig_cluster" {
  cluster            = var.cluster_name
  output_folder_path = "/tmp"
  filename           = "kubeconfig"
}

resource "kubernetes_namespace" "ns" {
  metadata {
    name = var.namespace_name
  }
}
