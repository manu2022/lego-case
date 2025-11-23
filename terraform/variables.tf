variable "resource_group_name" {
  type        = string
  description = "Name of the existing resource group."
}

variable "openai_api_key" {
  type        = string
  description = "OpenAI API Key"
  sensitive   = true
}

variable "langfuse_secret_key" {
  type        = string
  description = "Langfuse Secret Key"
  sensitive   = true
}

variable "langfuse_public_key" {
  type        = string
  description = "Langfuse Public Key"
  sensitive   = true
}

variable "langfuse_base_url" {
  type        = string
  description = "Langfuse Base URL"
  default     = "http://langfuse.legocase.com"
}