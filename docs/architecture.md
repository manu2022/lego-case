---
layout: default
title: Architecture
---

[Back to Home](index.md)

# Architecture

## Multi-Agent System Overview

The Peace Corps LLM Chatbot is built on a microservices architecture with an intelligent router orchestrating specialized agents. This design provides flexibility, security, and control over user queries.

### Why Microservices Architecture?

In the book **"Fundamentals of Software Architecture"** by Mark Richards and Neal Ford (O'Reilly Media, Inc.), various architecture designs are described. After careful analysis, we selected the microservices architecture.

#### Architecture Selection Summary

**✅ Microservices - Best Fit**

**Why:**
- Natural service boundaries (Chat, File Processing, LLM Gateway, Sessions, Auth)
- Container-native with independent scaling
- Langfuse monitoring integration
- Technology flexibility per service


| Architecture | Reason |
|--------------|--------|
| Layered | Monolithic, can't scale independently |
| Pipeline | One-way flow, not interactive |
| Event-Driven | Overkill for synchronous chat |



<div align="center">
  <img src="assets/architecture.png" alt="System Architecture Overview" style="max-width: 1200px; width: 100%; border: 1px solid #ddd; margin: 20px 0;">
  <p><em>High-level system architecture showing the intelligent router and specialized agents</em></p>
</div>

---

## Core Components

### 1. Intelligent Router (SML)

The router uses a Small Language Model to:
- Classify incoming queries
- Detect and redact PII (Personal Identifiable Information)
- Route requests to the appropriate specialized agent
- Filter malicious or harmful queries

**Key Benefits:**
- Better understanding of query intent compared to rule-based systems
- Structured JSON output for reliable execution plans
- Low latency (<500ms routing decisions)
- Adaptable through fine-tuning on organizational query patterns

<div align="center">
  <img src="assets/router_1.png" alt="Router Architecture" style="max-width: 1200px; width: 100%; border: 1px solid #ddd; margin: 20px 0;">
  <p><em>Intelligent Router: Query classification and PII detection flow</em></p>
</div>

---

### 2. Chat Agent (Text-Only Queries)

Handles standard text-based conversational queries using Azure OpenAI's GPT models.

**Features:**
- Conversation history management
- Context-aware responses
- Token usage tracking via Langfuse
- Session management

**Model**: GPT-4o-mini (cost-optimized for standard queries)

<div align="center">
  <img src="assets/router_2.png" alt="Chat Agent Flow" style="max-width: 1200px; width: 100%; border: 1px solid #ddd; margin: 20px 0;">
  <p><em>Chat Agent: Text-based query processing pipeline</em></p>
</div>

---

### 3. Multimodal Agent (Vision + Text)

Processes queries involving images, documents, or other visual content using Azure's multimodal models.

**Features:**
- Image analysis and understanding
- Document processing (PDF, images)
- Base64 encoding for secure transmission
- Vision-language model integration (Phi-4-multimodal)

**Use Cases:**
- "What's in this image?"
- "Analyze this chart/diagram"
- "Extract text from this document"

<div align="center">
  <img src="assets/router_3.png" alt="Multimodal Agent Flow" style="max-width: 1200px; width: 100%; border: 1px solid #ddd; margin: 20px 0;">
  <p><em>Multimodal Agent: File upload and vision processing pipeline</em></p>
</div>

---

### 4. Security & Observability Layer

**PII Protection:**
- Router-level PII detection before reaching LLM APIs
- Secure storage in Azure Key Vault
- Re-injection for user-facing responses

**Observability (Langfuse):**
- Comprehensive trace logging
- Cost tracking per user/model/query
- Performance monitoring across the request chain
- Token usage analytics

**Rate Limiting & DDoS Protection:**
- Azure API Gateway as entry point
- Per-user and per-IP rate limits
- Global throttling to prevent abuse

<div align="center">
  <img src="assets/router_4.png" alt="Security and Observability" style="max-width: 1200px; width: 100%; border: 1px solid #ddd; margin: 20px 0;">
  <p><em>Security layer: PII redaction, monitoring, and rate limiting</em></p>
</div>

---

## Technology Stack

### Frontend
- **Framework**: React + TypeScript
- **UI**: Modern chat interface with file upload support
- **Deployment**: Azure Container Apps

### Backend
- **Framework**: FastAPI (Python)
- **API Gateway**: Azure API Management
- **Authentication**: Azure Entra ID (formerly Azure AD)

### AI/ML
- **LLM Provider**: Azure OpenAI Service
- **Models**: GPT-4o-mini, Phi-4-multimodal
- **Observability**: Langfuse (self-hosted on Azure)

### Infrastructure
- **Cloud**: Microsoft Azure
- **IaC**: Terraform
- **Caching**: Redis
- **Storage**: Azure Key Vault (secrets), Azure Blob Storage (files)
- **Monitoring**: Azure Application Insights

---

## Data Flow

1. **User Request** → Frontend (React)
2. **API Gateway** → Rate limiting, authentication, DDoS protection
3. **Intelligent Router** → PII detection, query classification
4. **Specialized Agent** → GPT model processing
5. **Response Processing** → PII re-injection, formatting
6. **User Response** → Frontend display

**Observability**: Every step traced through Langfuse with correlation IDs

---

## Deployment Architecture

- **CI/CD**: GitHub Actions
- **Containers**: Docker images deployed to Azure Container Apps
- **Scaling**: Auto-scaling based on CPU/memory metrics
- **Regions**: Currently West Europe (expandable to multi-region)

---

[Back to Home](index.md)
