variable "cluster_name" {
  description = "Name of the cluster to download the kubeconfig"
  type        = string
  validation {
    condition     = length(var.cluster_name) > 0
    error_message = "The cluster name must not be empty."
  }
}

variable "project" {
  description = "The project to where the cluster is deployed"
  type        = string
  validation {
    condition     = length(var.project) > 0
    error_message = "The project must not be empty."
  }
}

variable "rctl_config_path" {
  description = "The path to the Rafay CLI config file"
  type        = string
  default     = "opt/rafay"
}

variable "username" {
  description = "User to access cluster using provided kubeconfig file"
  type        = string
}

variable "enable_kubeconfig" {
   description = "Allow user to control the kubeconfig download"
   type = bool
   default = false
}