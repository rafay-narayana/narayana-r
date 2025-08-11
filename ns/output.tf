
output "namespace" {
  description = "The name of the created namespace"
  value       = kubernetes_namespace.ns.metadata[0].name
}
