---
layout: default
title: Introduction and Feasibility
---

# Introduction and Feasibility

[Back to Home](index.md)

## Why does Peace Corps need this? What problem does it solve?

- Employees are using other LLM providers, with the risk of sending sensitive data
- Peace Corps GPT will be fully hosted and controlled by the company itself, mitigating the risk of sensitive data exposure
- In addition, we have control over the employee queries, which can be used for analysis
- The solution is flexible and scalable, so we can add tools if needed

## Product Discovery Process

Four Phases:

### Framing
Define the problem from multiple perspectives, identify risks (value, usability, feasibility, business viability)

### Planning
Use story mapping and find reference customers (6-8 loyal early adopters)

 - Value Risk: **Will employees actually use this?** There's a risk that employees won't find the chatbot valuable enough to change their existing workflows. Without clear use cases and demonstrated value, adoption will be low.

 - Usability Risk: **Is it intuitive enough?** If the interface is clunky, file uploads are confusing, or response times are slow, employees will abandon it for familiar tools like Google or existing solutions. The UX must match or exceed consumer chatbots (ChatGPT/Claude) that employees already know.

 - Feasibility Risk: **Can we build and maintain this?** Technical challenges include managing and fulfilling functional and non-functional requirements and maintaining system reliability. The team needs adequate skills in LLMOps, cloud infrastructure, and AI systems.

 - Business Viability Risk: **Is this financially sustainable?** LLM API costs can skyrocket with heavy usage, making the per-employee cost unpredictable. Without usage controls, cost monitoring, and clear ROI metrics, the project could become financially unsustainable or require constant budget justification.

### Ideation
Customer interviews, concierge testing, observation, hack days

### Prototyping
Build low-fidelity versions (feasibility, user, live-data, or hybrid prototypes)
- **Feasibility Prototype:** Build minimal proof-of-concept to test LLM API integration and file processing
- **Live-Data Prototype:** Deploy to small pilot group (6-8 reference users) to gather real usage data

### Testing
Validate all four risks through fake door tests, qualitative interviews, A/B tests, and stakeholder reviews

<div align="center">
  <img src="assets/inspired_book.jpg" alt="Inspired Book" style="max-width: 400px; width: 100%;">
  <p><em>The information has been inspired by this book</em></p>
</div>

---

# Agile Hierarchy for LLM Chatbot Project

## THEME (Level 1)
**Build Enterprise AI Assistant Platform**

---

## EPICS (Level 2)

### Epic 1: Requirements, Architecture & Scope
**User Stories:**
- Define functional requirements
- Create system architecture diagrams
- Document non-functional requirements

**Tasks:**
- Stakeholder interviews
- Architecture diagram creation
- Requirements documentation
- NFR definition (latency, availability, etc.)

---

### Epic 2: Core Infrastructure
**User Stories:**
- Set up cloud infrastructure
- Create CI/CD pipeline
- Implement monitoring and logging

**Tasks:**
- Configure networking, API Gateway
- Configure monitoring tools
- Create IaC templates with Terraform

---

### Epic 3: Backend Development
**User Stories:**
- Send messages to LLM and receive responses
- Save and retrieve conversation history
- Upload and process file attachments
- Manage user sessions

**Tasks:**
- Create API endpoints
- Implement real-time chat
- Build conversation storage service
- Develop file upload service
- Design database schema
- Implement caching layer

---

### Epic 4: Frontend Development
**User Stories:**
- Chat interface for user interaction
- Display message history
- File attachment functionality
- Responsive UI/UX

**Tasks:**
- Create React chat component
- Build message rendering UI
- Implement file upload widget
- Add conversation sidebar
- Implement responsive design
- Add error handling

---

### Epic 5: LLMOps
**User Stories:**
- Integrate with LLM API (GPT-4/Claude)
- Optimize prompt templates
- Monitor LLM usage and costs

**Tasks:**
- API integration (OpenAI/Anthropic)
- Create prompt templates
- Build token usage tracking
- Set up cost monitoring

---

### Epic 6: Security
**User Stories:**
- Implement authentication/authorization
- Encrypt user data
- Create audit logging
- Validate and sanitize inputs

**Tasks:**
- Set up SSO (OAuth2/SAML)
- Implement RBAC
- Enable encryption (at rest/in transit)
- PII detection/redaction
- Audit logging system
- Security testing