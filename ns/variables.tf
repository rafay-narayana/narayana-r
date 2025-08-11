variable "namespace_name" {
  description = "The name of the Kubernetes namespace"
  type        = string
  default     = "demo-namespace"
}

variable "host_cluster_name" {
  description = "The name of the cluster"
  type        = string
  validation {
    condition     = length(var.cluster_name) > 0
    error_message = "The cluster name must not be empty."
  }
}
