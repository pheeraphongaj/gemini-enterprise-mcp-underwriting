"""Registers all 7 Cloud Run MCP Microservices into Agent Platform / Agent Registry (agentregistry.googleapis.com)."""

import json
import subprocess
import urllib.request
import urllib.error

PROJECT_ID = "hong-ai-demo"
REGION = "asia-southeast1"

GCLOUD = "gcloud"

def get_service_url(svc_name: str) -> str:
    res = subprocess.check_output([
        GCLOUD, "run", "services", "describe", svc_name,
        "--region", REGION,
        "--project", PROJECT_ID,
        "--format=value(status.url)"
    ]).decode("utf-8").strip()
    return res

token = subprocess.check_output([GCLOUD, "auth", "print-access-token"]).decode("utf-8").strip()

mcp_definitions = [
    {
        "server_id": "underwriting-gmail-mcp",
        "display_name": "Underwriting Gmail Ingestion MCP",
        "description": "MCP server for automated email ingestion and attachment retrieval for credit applications.",
        "tools": [
            {
                "name": "scan_gmail_inbox",
                "description": "Scans mailbox for '[underwriting]' subject triggers and extracts application packages.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "subject_filter": {"type": "string", "default": "[underwriting]"},
                        "max_results": {"type": "integer", "default": 10}
                    }
                }
            },
            {
                "name": "fetch_email_attachment",
                "description": "Fetches attachment payload and metadata from an email submission.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email_id": {"type": "string"},
                        "attachment_id": {"type": "string"}
                    },
                    "required": ["email_id", "attachment_id"]
                }
            }
        ]
    },
    {
        "server_id": "underwriting-doc-mcp",
        "display_name": "Underwriting Document Validation MCP",
        "description": "MCP server for validating mandatory Thai corporate/individual document checklists and OCR parsing.",
        "tools": [
            {
                "name": "validate_document_checklist",
                "description": "Verifies presence and completeness of mandatory Thai corporate / individual underwriting documents.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "application_id": {"type": "string"},
                        "entity_type": {"type": "string", "default": "CORPORATE"}
                    },
                    "required": ["application_id"]
                }
            },
            {
                "name": "parse_financial_documents",
                "description": "Extracts structured financial metrics (Turnover, NOI, Debt Service, VAT) from submitted documents.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "application_id": {"type": "string"}
                    },
                    "required": ["application_id"]
                }
            }
        ]
    },
    {
        "server_id": "underwriting-registry-mcp",
        "display_name": "Underwriting National Registries MCP",
        "description": "MCP server for Thai Department of Business Development (DBD), DOPA Civil Identity, and AMLO sanctions verification.",
        "tools": [
            {
                "name": "verify_dbd_registry",
                "description": "Queries Thai Department of Business Development registry for corporate status, registered capital, net equity, and litigation.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "registration_id": {"type": "string"}
                    },
                    "required": ["registration_id"]
                }
            },
            {
                "name": "verify_dopa_identity",
                "description": "Checks Thai DOPA Civil Identity Registry for director national ID validity and expiry.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "national_id": {"type": "string"}
                    },
                    "required": ["national_id"]
                }
            },
            {
                "name": "screen_aml_sanctions",
                "description": "Screens applicants and directors against Thai AMLO sanctions watchlists and PEP records.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "national_id": {"type": "string"},
                        "registration_id": {"type": "string"},
                        "name": {"type": "string"}
                    }
                }
            }
        ]
    },
    {
        "server_id": "underwriting-fraud-mcp",
        "display_name": "Underwriting Fraud Risk MCP",
        "description": "MCP server for Revenue Anomaly, Statement Tampering, and Check Bounce evaluation.",
        "tools": [
            {
                "name": "analyze_revenue_anomaly",
                "description": "Calculates revenue variance between 6M bank statement deposits and P.P.30 VAT gross reported sales.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "bank_inflows_6m_thb": {"type": "number"},
                        "pp30_vat_revenue_6m_thb": {"type": "number"}
                    },
                    "required": ["bank_inflows_6m_thb", "pp30_vat_revenue_6m_thb"]
                }
            },
            {
                "name": "evaluate_statement_tampering",
                "description": "Evaluates check bounce frequency and overdraft utilization for liquidity distress / check kiting.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "bounced_checks_count_6m": {"type": "integer", "default": 0},
                        "overdraft_utilization_pct": {"type": "number", "default": 0.0}
                    }
                }
            }
        ]
    },
    {
        "server_id": "underwriting-scoring-mcp",
        "display_name": "Underwriting Credit Scoring MCP",
        "description": "MCP server for DSCR ratio calculation, Credit Tier classification, and pricing spread recommendation.",
        "tools": [
            {
                "name": "calculate_dscr",
                "description": "Calculates Debt Service Coverage Ratio (DSCR = Monthly NOI / Debt Service).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "monthly_noi_thb": {"type": "number"},
                        "monthly_debt_service_thb": {"type": "number"}
                    },
                    "required": ["monthly_noi_thb", "monthly_debt_service_thb"]
                }
            },
            {
                "name": "score_credit_risk",
                "description": "Computes credit rating tiers (Tier A Prime, Tier B Standard, Tier C Borderline, Tier D High Risk) and indicative pricing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "monthly_noi_thb": {"type": "number"},
                        "monthly_debt_service_thb": {"type": "number"},
                        "monthly_turnover_thb": {"type": "number"},
                        "bounced_checks_count_6m": {"type": "integer", "default": 0}
                    },
                    "required": ["monthly_noi_thb", "monthly_debt_service_thb", "monthly_turnover_thb"]
                }
            }
        ]
    },
    {
        "server_id": "underwriting-decision-mcp",
        "display_name": "Underwriting Decision Engine MCP",
        "description": "MCP server for deterministic policy matrix decisioning, facility terms structuring, and credit committee escalation.",
        "tools": [
            {
                "name": "evaluate_underwriting_decision",
                "description": "Evaluates policy rules to make PRE_APPROVED, REFERRED_TO_UW, or REJECTED determinations with interest spreads and terms.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "application_id": {"type": "string"},
                        "requested_facility_thb": {"type": "number"},
                        "credit_risk_tier": {"type": "string"},
                        "fraud_risk_level": {"type": "string", "default": "LOW"},
                        "registry_knockout": {"type": "boolean", "default": False},
                        "knockout_reason": {"type": "string"},
                        "litigation_flag": {"type": "boolean", "default": False}
                    },
                    "required": ["application_id", "requested_facility_thb", "credit_risk_tier"]
                }
            }
        ]
    },
    {
        "server_id": "underwriting-notification-mcp",
        "display_name": "Underwriting Notification & Dispatch MCP",
        "description": "MCP server for generating customer pre-approval letters, missing doc links, and credit committee memos.",
        "tools": [
            {
                "name": "generate_preapproval_letter",
                "description": "Generates formatted customer pre-approval letter with loan limit, spread, and covenants.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "application_id": {"type": "string"},
                        "borrower_name": {"type": "string"},
                        "recipient_email": {"type": "string"},
                        "approved_limit_thb": {"type": "number"},
                        "interest_rate": {"type": "string"},
                        "tenor_months": {"type": "integer"}
                    },
                    "required": ["application_id", "borrower_name", "recipient_email", "approved_limit_thb", "interest_rate", "tenor_months"]
                }
            },
            {
                "name": "generate_missing_doc_notice",
                "description": "Generates missing document request letter with secure upload portal token.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "application_id": {"type": "string"},
                        "borrower_name": {"type": "string"},
                        "recipient_email": {"type": "string"},
                        "missing_documents": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["application_id", "borrower_name", "recipient_email", "missing_documents"]
                }
            },
            {
                "name": "generate_underwriter_memo",
                "description": "Generates internal Credit Committee briefing memo for referred applications.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "application_id": {"type": "string"},
                        "borrower_name": {"type": "string"},
                        "requested_facility_thb": {"type": "number"},
                        "observed_dscr": {"type": "number"},
                        "referral_reasons": {"type": "array", "items": {"type": "string"}},
                        "mitigating_conditions": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["application_id", "borrower_name", "requested_facility_thb", "observed_dscr", "referral_reasons", "mitigating_conditions"]
                }
            }
        ]
    }
]

def main():
    manifest_records = []
    print("=" * 60)
    print("📋 GENERATING MCP SERVER CATALOG & MANIFESTS FOR AGENT PLATFORM")
    print("=" * 60)

    for item in mcp_definitions:
        svc_name = item["server_id"]
        url = get_service_url(svc_name)
        
        manifest = {
            "displayName": item["display_name"],
            "description": item["description"],
            "mcpServerId": f"urn:mcp:projects-YOUR_PROJECT_NUMBER:projects:YOUR_PROJECT_NUMBER:locations:global:run:services:{svc_name}",
            "interfaces": [
                {
                    "url": f"{url}/mcp",
                    "protocolBinding": "JSONRPC"
                }
            ],
            "tools": item["tools"]
        }
        manifest_records.append(manifest)
        print(f"\n📦 Server: {item['display_name']}")
        print(f"   URL: {url}/mcp")
        print(f"   Tools: {[t['name'] for t in item['tools']]}")

    # Save to catalog file
    output_path = "./v2_microservices/mcp_catalog.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest_records, f, indent=2)
    print(f"\n💾 Saved MCP Manifest Catalog to: {output_path}")

if __name__ == "__main__":
    main()
