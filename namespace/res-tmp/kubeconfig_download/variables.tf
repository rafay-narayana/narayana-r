variable "rafay_config_file" {
  description = "rafay provider config file for authentication"
  type        = string
  default     = "/Users/config.json"
}

variable "cluster_name" {
  description = "The name of the cluster"
  type        = string
  validation {
    condition     = length(var.cluster_name) > 0
    error_message = "The cluster name must not be empty."
  }
}