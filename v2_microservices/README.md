# 🏛️ Underwriting Multi-Agent v2: Microservices & Agent Platform MCP Utilities

This directory contains the **v2 Microservices Architecture** for the Underwriting Multi-Agent System on Google Cloud, decomposing the monolithic backend into 7 dedicated Cloud Run microservices serving as reusable **Model Context Protocol (MCP)** utilities.

---

## 1. Architectural Map

```
Underwriting Multi-Agent System (v2)
├── 📧 underwriting-gmail-mcp (Email Ingestion & Trigger Scanner)
├── 📑 underwriting-doc-mcp (Intake Checklist Validator & OCR Extraction)
├── 🏢 underwriting-registry-mcp (Thai DBD Corporate, DOPA Civil ID & AMLO/PEP Screening)
├── 🛡️ underwriting-fraud-mcp (Bank vs PP30 VAT Variance & Statement Tampering)
├── 📊 underwriting-scoring-mcp (DSCR Ratio Math & Credit Rating Tiers)
├── ⚖️ underwriting-decision-mcp (Deterministic Policy Matrix & Escalation Engine)
└── 📨 underwriting-notification-mcp (Pre-Approval Letters, Missing Doc Portal Links & Referral Memos)
```

---

## 2. Microservice Registry & Endpoints

| Microservice | Cloud Run Service | MCP Interface URL | Primary MCP Tools |
| :--- | :--- | :--- | :--- |
| **Gmail Ingestion** | `underwriting-gmail-mcp` | `https://underwriting-gmail-mcp-<REGION_HASH>.a.run.app/mcp` | `scan_gmail_inbox`, `fetch_email_attachment` |
| **Doc Validation** | `underwriting-doc-mcp` | `https://underwriting-doc-mcp-<REGION_HASH>.a.run.app/mcp` | `validate_document_checklist`, `parse_financial_documents` |
| **National Registries** | `underwriting-registry-mcp` | `https://underwriting-registry-mcp-<REGION_HASH>.a.run.app/mcp` | `verify_dbd_registry`, `verify_dopa_identity`, `screen_aml_sanctions` |
| **Fraud & Risk** | `underwriting-fraud-mcp` | `https://underwriting-fraud-mcp-<REGION_HASH>.a.run.app/mcp` | `analyze_revenue_anomaly`, `evaluate_statement_tampering` |
| **Credit Scoring** | `underwriting-scoring-mcp` | `https://underwriting-scoring-mcp-<REGION_HASH>.a.run.app/mcp` | `calculate_dscr`, `score_credit_risk` |
| **Decision Engine** | `underwriting-decision-mcp` | `https://underwriting-decision-mcp-<REGION_HASH>.a.run.app/mcp` | `evaluate_underwriting_decision` |
| **Notification** | `underwriting-notification-mcp` | `https://underwriting-notification-mcp-<REGION_HASH>.a.run.app/mcp` | `generate_preapproval_letter`, `generate_missing_doc_notice`, `generate_underwriter_memo` |

---

## 3. Dual Protocol Support

Every microservice simultaneously supports:
1. **JSON-RPC 2.0 MCP Protocol (`/mcp`)**:
   - `initialize`: Protocol negotiation & capabilities handshake.
   - `tools/list`: Dynamic discovery of tool definitions and JSON schemas.
   - `tools/call`: Tool execution with argument validation.
   - `ping`: Liveness check.
2. **Standard REST Endpoints (`/tools/...` & `/openapi.json`)**:
   - For direct webhooks, OpenAPI imports, and Swagger UI inspection.

---

## 4. Verification & Testing

To verify all 7 live Cloud Run microservices:
```bash
python3 test_deployed_microservices.py
```
