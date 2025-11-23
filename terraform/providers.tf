terraform {
  required_version = ">=1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
  }

  # Remote backend for state storage
  # Run setup-backend.sh first to create the storage account
  backend "azurerm" {
    # Configuration loaded from backend-config.tfbackend
    # Or set via environment variables or CLI flags
  }
}

provider "azurerm" {
  features {}
}