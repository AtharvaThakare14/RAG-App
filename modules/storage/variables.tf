variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "stage" {
  description = "Deployment stage (dev, staging, prod)"
  type        = string
}

variable "enable_lifecycle_rules" {
  type    = bool
  default = false
}

variable "standard_ia_transition_days" {
  type    = number
  default = 90
}

variable "glacier_transition_days" {
  type    = number
  default = 365
}