resource "rafay_download_kubeconfig" "kubeconfig_cluster" {
  cluster            = var.cluster_name
  output_folder_path = "/tmp"
  filename           = "kubeconfig"
}
