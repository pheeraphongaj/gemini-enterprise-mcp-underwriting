"""Notification & Dispatch MCP Microservice (underwriting-notification-mcp).

Provides:
- generate_preapproval_letter: Generates official customer pre-approval letter with terms and covenants.
- generate_missing_doc_notice: Generates missing documents request with secure upload portal token.
- generate_underwriter_memo: Generates internal Credit Committee referral briefing memo.
Supports REST (/tools/...) and MCP JSON-RPC (/mcp).
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import datetime

app = FastAPI(
    title="Underwriting Notification MCP Service",
    description="MCP Microservice for Customer Pre-Approval Letters, Missing Document Requests, and Credit Committee Memos",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PreApprovalLetterRequest(BaseModel):
    application_id: str = Field(..., description="Application ID")
    borrower_name: str = Field(..., description="Borrower Company or Individual Name")
    recipient_email: str = Field(..., description="Recipient email address")
    approved_limit_thb: float = Field(..., description="Approved facility limit in THB")
    interest_rate: str = Field(..., description="Interest rate spread (e.g. MLR - 1.25%)")
    tenor_months: int = Field(..., description="Loan tenor in months")

class MissingDocNoticeRequest(BaseModel):
    application_id: str = Field(..., description="Application ID")
    borrower_name: str = Field(..., description="Borrower Name")
    recipient_email: str = Field(..., description="Recipient email address")
    missing_documents: List[str] = Field(..., description="List of missing document types")

class UnderwriterMemoRequest(BaseModel):
    application_id: str = Field(..., description="Application ID")
    borrower_name: str = Field(..., description="Borrower Company Name")
    requested_facility_thb: float = Field(..., description="Requested facility limit")
    observed_dscr: float = Field(..., description="Observed DSCR")
    referral_reasons: List[str] = Field(..., description="List of policy exception / referral reasons")
    mitigating_conditions: List[str] = Field(..., description="List of proposed collateral / guarantee conditions")

def generate_preapproval_logic(
    app_id: str, borrower: str, email: str, limit: float, rate: str, tenor: int
) -> Dict[str, Any]:
    formatted_limit = f"THB {limit:,.2f}"
    markdown_content = f"""# 🏦 COMMERCIAL CREDIT PRE-APPROVAL NOTICE

**Date:** {datetime.date.today().strftime('%B %d, %Y')}  
**Application Reference:** `{app_id}`  
**To:** {borrower}  
**Attention:** {email}  

---

### Dear Valued Client,

We are pleased to inform you that following comprehensive automated underwriting and risk evaluation, **{borrower}** has been **PRE-APPROVED** for commercial credit facilities under the following indicative terms:

| Facility Parameter | Pre-Approved Term |
| :--- | :--- |
| **Facility Type** | Commercial Working Capital & Fleet Expansion Term Loan |
| **Approved Facility Limit** | **{formatted_limit}** |
| **Indicative Interest Rate** | **{rate}** |
| **Loan Tenor** | **{tenor} Months** |
| **Repayment Structure** | Monthly principal and interest amortization |

### Conditions Precedent to Final Disbursement:
1. Execution of Standard Commercial Facility Agreement.
2. Direct Debit Mandate setup for monthly debt service.
3. Annual submission of certified financial statements maintaining a minimum DSCR >= 1.25x.

---
*Authorized by Gemini Enterprise Underwriting Multi-Agent Orchestrator*
"""
    return {
        "application_id": app_id,
        "recipient_email": email,
        "document_type": "CUSTOMER_PRE_APPROVAL_LETTER",
        "markdown_body": markdown_content,
        "dispatched": True,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

def generate_missing_doc_logic(app_id: str, borrower: str, email: str, missing: List[str]) -> Dict[str, Any]:
    missing_bullets = "\n".join([f"- ❌ **{doc.replace('_', ' ').title()}**" for doc in missing])
    upload_url = f"https://portal.enterprise.gemini/underwriting/upload?token=SECURE-TOKEN-{app_id}"

    markdown_content = f"""# 📑 ACTION REQUIRED: MISSING UNDERWRITING DOCUMENTS

**Application Reference:** `{app_id}`  
**Applicant:** {borrower}  
**Recipient:** {email}  

---

### Dear {borrower},

Thank you for your credit facility application. During our automated intake verification, our document validation engine identified that the following required regulatory or financial documents are currently missing:

{missing_bullets}

### Next Steps:
Please upload the missing files directly through our secure document verification portal:
🔗 **[Upload Documents to Secure Customer Portal]({upload_url})**

*Please complete this upload within 7 business days to proceed with credit scoring and final facility decisioning.*
"""
    return {
        "application_id": app_id,
        "recipient_email": email,
        "document_type": "MISSING_DOCUMENTS_REQUEST",
        "missing_items": missing,
        "secure_upload_url": upload_url,
        "markdown_body": markdown_content,
        "dispatched": True,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

def generate_memo_logic(
    app_id: str, borrower: str, requested: float, dscr: float, reasons: List[str], mitigations: List[str]
) -> Dict[str, Any]:
    reasons_md = "\n".join([f"- ⚠️ {r}" for r in reasons])
    mitigations_md = "\n".join([f"- 🛡️ {m}" for m in mitigations])

    markdown_content = f"""# 📑 INTERNAL MEMORANDUM: CREDIT COMMITTEE ESCALATION

**Date:** {datetime.date.today().strftime('%B %d, %Y')}  
**To:** Commercial Credit Committee (Level 2)  
**From:** Underwriting Multi-Agent Orchestrator  
**Subject:** Credit Referral & Policy Exception Briefing — `{app_id}` ({borrower})  

---

### 1. Case Overview
* **Borrower:** {borrower}
* **Requested Facility:** THB {requested:,.2f}
* **Observed DSCR:** **{dscr:.2f}x** (Standard Policy Target: >= 1.25x)

### 2. Referral & Policy Exception Triggers
{reasons_md}

### 3. Proposed Mitigating Collateral & Covenant Structure
{mitigations_md}

---
*Recommendation: Proceed with conditional approval subject to committee sign-off on collateral terms.*
"""
    return {
        "application_id": app_id,
        "document_type": "CREDIT_COMMITTEE_REFERRAL_MEMO",
        "markdown_body": markdown_content,
        "dispatched_to_committee": True,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "underwriting-notification-mcp", "version": "2.0.0"}

@app.post("/tools/generate-preapproval-letter")
def generate_preapproval_rest(req: PreApprovalLetterRequest):
    return generate_preapproval_logic(
        req.application_id, req.borrower_name, req.recipient_email, req.approved_limit_thb, req.interest_rate, req.tenor_months
    )

@app.post("/tools/generate-missing-doc-notice")
def generate_missing_doc_rest(req: MissingDocNoticeRequest):
    return generate_missing_doc_logic(req.application_id, req.borrower_name, req.recipient_email, req.missing_documents)

@app.post("/tools/generate-underwriter-memo")
def generate_memo_rest(req: UnderwriterMemoRequest):
    return generate_memo_logic(
        req.application_id, req.borrower_name, req.requested_facility_thb, req.observed_dscr, req.referral_reasons, req.mitigating_conditions
    )

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
                "serverInfo": {"name": "underwriting-notification-mcp", "version": "2.0.0"},
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
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "generate_preapproval_letter":
            res = generate_preapproval_logic(
                args.get("application_id", ""),
                args.get("borrower_name", ""),
                args.get("recipient_email", ""),
                args.get("approved_limit_thb", 0.0),
                args.get("interest_rate", "MLR - 1.25%"),
                args.get("tenor_months", 60)
            )
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        elif tool_name == "generate_missing_doc_notice":
            res = generate_missing_doc_logic(
                args.get("application_id", ""),
                args.get("borrower_name", ""),
                args.get("recipient_email", ""),
                args.get("missing_documents", [])
            )
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        elif tool_name == "generate_underwriter_memo":
            res = generate_memo_logic(
                args.get("application_id", ""),
                args.get("borrower_name", ""),
                args.get("requested_facility_thb", 0.0),
                args.get("observed_dscr", 1.25),
                args.get("referral_reasons", []),
                args.get("mitigating_conditions", [])
            )
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
