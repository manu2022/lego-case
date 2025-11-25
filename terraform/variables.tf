variable "resource_group_name" {
  type        = string
  description = "Name of existing resource group"
}

variable "openai_api_key" {
  type      = string
  sensitive = true
}

variable "langfuse_secret_key" {
  type      = string
  sensitive = true
}

variable "langfuse_public_key" {
  type      = string
  sensitive = true
}

variable "langfuse_base_url" {
  type    = string
  default = "http://langfuse.legocase.com"
}

variable "claude_api_key" {
  type      = string
  sensitive = true
}