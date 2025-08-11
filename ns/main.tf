
resource "rafay_download_kubeconfig" "kubeconfig_cluster" {
  cluster            = var.cluster_name
  output_folder_path = "/tmp"
  filename           = "kubeconfig"
}

data "rafay_download_kubeconfig" "kubeconfig_cluster" {
  cluster = var.cluster_name
}

resource "kubernetes_namespace" "ns" {
  metadata {
    name = var.namespace_name
  }
}
