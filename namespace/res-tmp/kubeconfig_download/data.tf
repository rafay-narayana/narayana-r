data "rafay_download_kubeconfig" "kubeconfig_cluster" {
  cluster = var.cluster_name
}
