
resource "rafay_download_kubeconfig" "kubeconfig_cluster" {
  cluster            = var.cluster_name
  output_folder_path = "/tmp"
  filename           = "kubeconfig"
}
data "local_file" "kubeconfig_content" {
  depends_on = [rafay_download_kubeconfig.kubeconfig_cluster]
  filename   = "/tmp/kubeconfig"
}

provider "kubernetes" {
  config_path = "/tmp/kubeconfig"
}

# Create namespace
resource "kubernetes_namespace" "ns" {
  metadata {
    name = var.namespace_name
  }
}

