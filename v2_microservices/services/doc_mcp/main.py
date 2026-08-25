"""Document Validation & Financial Extraction MCP Microservice (underwriting-doc-mcp).

Provides:
- validate_document_checklist: Validates document checklists for corporate/individual underwriting.
- parse_financial_documents: Extracts financial metrics, P.P.30 VAT, and bank statement turnover.
Supports REST (/tools/...) and MCP JSON-RPC (/mcp).
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import datetime

app = FastAPI(
    title="Underwriting Document MCP Service",
    description="MCP Microservice for Document Intake Validation & Structured Financial Parsing",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_APPLICATIONS = {
    "APP-2026-001": {
        "entity_name": "Siam Tech Logistics Co., Ltd.",
        "entity_type": "CORPORATE",
        "registration_id": "0105561023456",
        "requested_facility_thb": 10000000.0,
        "provided_docs": ["DBD_CERTIFICATE", "BOR_OR_JOR_5", "BANK_STATEMENT_6M", "FINANCIAL_STATEMENTS", "DIRECTOR_NATIONAL_ID"],
        "extracted_financials": {
            "monthly_turnover_thb": 3500000.0,
            "monthly_net_operating_income_thb": 850000.0,
            "monthly_debt_service_thb": 420000.0,
            "annual_revenue_thb": 42000000.0,
            "bank_inflows_6m_thb": 21000000.0,
            "pp30_vat_revenue_6m_thb": 20800000.0,
            "overdraft_utilization_pct": 35.0,
            "bounced_checks_count_6m": 0
        }
    },
    "APP-2026-002": {
        "entity_name": "Bangkok Fresh Retail Co., Ltd.",
        "entity_type": "CORPORATE",
        "registration_id": "0105562098765",
        "requested_facility_thb": 3000000.0,
        "provided_docs": ["DBD_CERTIFICATE", "BOR_OR_JOR_5", "BANK_STATEMENT_6M", "FINANCIAL_STATEMENTS", "DIRECTOR_NATIONAL_ID"],
        "extracted_financials": {
            "monthly_turnover_thb": 1200000.0,
            "monthly_net_operating_income_thb": 210000.0,
            "monthly_debt_service_thb": 180000.0,
            "annual_revenue_thb": 14400000.0,
            "bank_inflows_6m_thb": 7200000.0,
            "pp30_vat_revenue_6m_thb": 7100000.0,
            "overdraft_utilization_pct": 78.0,
            "bounced_checks_count_6m": 1
        }
    },
    "APP-2026-003": {
        "entity_name": "Apex Global Trading Co., Ltd.",
        "entity_type": "CORPORATE",
        "registration_id": "0105558012345",
        "requested_facility_thb": 15000000.0,
        "provided_docs": ["DBD_CERTIFICATE", "BOR_OR_JOR_5", "BANK_STATEMENT_6M", "FINANCIAL_STATEMENTS", "DIRECTOR_NATIONAL_ID"],
        "extracted_financials": {
            "monthly_turnover_thb": 6000000.0,
            "monthly_net_operating_income_thb": -300000.0,
            "monthly_debt_service_thb": 800000.0,
            "annual_revenue_thb": 72000000.0,
            "bank_inflows_6m_thb": 36000000.0,
            "pp30_vat_revenue_6m_thb": 12000000.0,
            "overdraft_utilization_pct": 98.0,
            "bounced_checks_count_6m": 4
        }
    },
    "APP-2026-004": {
        "entity_name": "Chiang Mai Craft Brewery Co., Ltd.",
        "entity_type": "CORPORATE",
        "registration_id": "0505563045678",
        "requested_facility_thb": 5000000.0,
        "provided_docs": ["DBD_CERTIFICATE", "FINANCIAL_STATEMENTS", "DIRECTOR_NATIONAL_ID"],
        "extracted_financials": None
    }
}

MANDATORY_DOCS = {
    "CORPORATE": ["DBD_CERTIFICATE", "BOR_OR_JOR_5", "BANK_STATEMENT_6M", "FINANCIAL_STATEMENTS", "DIRECTOR_NATIONAL_ID"],
    "INDIVIDUAL": ["NATIONAL_ID", "PROOF_OF_INCOME", "BANK_STATEMENT_6M"]
}

class ValidateDocRequest(BaseModel):
    application_id: str = Field(..., description="Application ID")
    entity_type: str = Field(default="CORPORATE", description="CORPORATE or INDIVIDUAL")

class ParseDocRequest(BaseModel):
    application_id: str = Field(..., description="Application ID")

def validate_docs_logic(application_id: str, entity_type: str) -> Dict[str, Any]:
    app_data = MOCK_APPLICATIONS.get(application_id)
    if not app_data:
        return {"status": "ERROR", "message": f"Application {application_id} not found"}
    
    required = MANDATORY_DOCS.get(entity_type.upper(), MANDATORY_DOCS["CORPORATE"])
    provided = app_data.get("provided_docs", [])
    missing = [d for d in required if d not in provided]

    status = "DOCS_VALIDATED" if not missing else "DOCS_MISSING"
    return {
        "application_id": application_id,
        "entity_name": app_data["entity_name"],
        "entity_type": entity_type.upper(),
        "status": status,
        "checklist_passed": len(missing) == 0,
        "required_documents": required,
        "provided_documents": provided,
        "missing_documents": missing,
        "validated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

def parse_docs_logic(application_id: str) -> Dict[str, Any]:
    app_data = MOCK_APPLICATIONS.get(application_id)
    if not app_data:
        return {"status": "ERROR", "message": f"Application {application_id} not found"}
    if not app_data.get("extracted_financials"):
        return {
            "application_id": application_id,
            "status": "PARSE_BLOCKED",
            "message": "Cannot parse incomplete document submission. Missing required statements."
        }
    return {
        "application_id": application_id,
        "entity_name": app_data["entity_name"],
        "status": "PARSE_SUCCESS",
        "financial_metrics": app_data["extracted_financials"],
        "extracted_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "underwriting-doc-mcp", "version": "2.0.0"}

@app.post("/tools/validate-documents")
def validate_documents_rest(req: ValidateDocRequest):
    return validate_docs_logic(req.application_id, req.entity_type)

@app.post("/tools/parse-documents")
def parse_documents_rest(req: ParseDocRequest):
    return parse_docs_logic(req.application_id)

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()
    req_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "underwriting-doc-mcp", "version": "2.0.0"},
                "capabilities": {"tools": {}}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
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
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "validate_document_checklist":
            res = validate_docs_logic(args.get("application_id", ""), args.get("entity_type", "CORPORATE"))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        elif tool_name == "parse_financial_documents":
            res = parse_docs_logic(args.get("application_id", ""))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
