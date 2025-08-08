output "cluster_kubeconfig" {
  value = "https://${data.external.env.result.value}/v2/sentry/kubeconfig/user?opts.selector=rafay.dev/clusterName=${var.cluster_name}"
}