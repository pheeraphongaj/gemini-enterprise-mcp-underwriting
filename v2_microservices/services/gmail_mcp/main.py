"""Gmail Scanner & Ingestion MCP Microservice (underwriting-gmail-mcp).

Provides:
- scan_gmail_inbox: Scans mailbox for '[underwriting]' subject triggers and extracts application packages.
- fetch_email_attachment: Fetches raw/structured attachment metadata and payloads.
Supports REST (/tools/...) and MCP JSON-RPC (/mcp).
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import datetime

app = FastAPI(
    title="Underwriting Gmail MCP Service",
    description="MCP Microservice for Gmail Ingestion & Application Triggering",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_GMAIL_INBOX = [
    {
        "email_id": "MSG-GMAIL-98201",
        "sender": "somchai@siamtechlogistics.co.th",
        "recipient": "underwriting-intake@enterprise.gemini",
        "subject": "[underwriting] Credit Facility Application - Siam Tech Logistics Co., Ltd.",
        "received_at": "2026-08-24T09:30:00Z",
        "body_text": (
            "Dear Underwriting Team,\n\n"
            "Please find attached our complete loan application package for Siam Tech Logistics Co., Ltd. (Registration: 0105561023456).\n"
            "We are requesting a THB 10,000,000 credit facility for commercial fleet expansion.\n"
            "All 5 required documents including DBD certificate, BorOrJor.5, 6-month SCB bank statements, audited financials, and Director ID are attached.\n\n"
            "Best regards,\nSomchai Siriwattanakul\nManaging Director"
        ),
        "attachments": [
            {"attachment_id": "ATT-001", "filename": "dbd_affidavit_2026.pdf", "type": "DBD_CERTIFICATE", "size_kb": 1450, "legible": True, "issue_date": "2026-07-15"},
            {"attachment_id": "ATT-002", "filename": "shareholder_list_boj5.pdf", "type": "BOR_OR_JOR_5", "size_kb": 820, "legible": True, "issue_date": "2026-07-15"},
            {"attachment_id": "ATT-003", "filename": "scb_statement_6m.pdf", "type": "BANK_STATEMENT_6M", "size_kb": 4300, "legible": True, "months_count": 6},
            {"attachment_id": "ATT-004", "filename": "audited_financials_2025.pdf", "type": "FINANCIAL_STATEMENTS", "size_kb": 6200, "legible": True, "audited": True},
            {"attachment_id": "ATT-005", "filename": "director_somchai_id.pdf", "type": "DIRECTOR_NATIONAL_ID", "size_kb": 950, "legible": True, "holder_id": "1100400123456"},
        ],
        "application_id": "APP-2026-001",
    },
    {
        "email_id": "MSG-GMAIL-98202",
        "sender": "wichai@bangkokfresh.com",
        "recipient": "underwriting-intake@enterprise.gemini",
        "subject": "[underwriting] SME Loan Application - Bangkok Fresh Retail Co., Ltd.",
        "received_at": "2026-08-24T09:45:00Z",
        "body_text": (
            "Dear Credit Committee,\n\n"
            "Submitting application for Bangkok Fresh Retail Co., Ltd. (Registration: 0105562098765) for THB 3,000,000 working capital.\n"
            "Attached are our DBD certificate, BorOrJor.5, KBank statements, financials, and director ID.\n\n"
            "Thank you,\nWichai Ratanarungreang"
        ),
        "attachments": [
            {"attachment_id": "ATT-006", "filename": "dbd_affidavit_bfresh.pdf", "type": "DBD_CERTIFICATE", "size_kb": 1200, "legible": True, "issue_date": "2026-06-01"},
            {"attachment_id": "ATT-007", "filename": "boj5_bangkok_fresh.pdf", "type": "BOR_OR_JOR_5", "size_kb": 780, "legible": True, "issue_date": "2026-06-01"},
            {"attachment_id": "ATT-008", "filename": "kbank_statement_6m.pdf", "type": "BANK_STATEMENT_6M", "size_kb": 3900, "legible": True, "months_count": 6},
            {"attachment_id": "ATT-009", "filename": "financial_stmt_2025.pdf", "type": "FINANCIAL_STATEMENTS", "size_kb": 5100, "legible": True, "audited": True},
            {"attachment_id": "ATT-010", "filename": "id_wichai.pdf", "type": "DIRECTOR_NATIONAL_ID", "size_kb": 890, "legible": True, "holder_id": "3100800345678"},
        ],
        "application_id": "APP-2026-002",
    },
    {
        "email_id": "MSG-GMAIL-98203",
        "sender": "thanakrit@apexglobal.biz",
        "recipient": "underwriting-intake@enterprise.gemini",
        "subject": "[underwriting] Trade Credit Line Request - Apex Global Trading",
        "received_at": "2026-08-24T10:00:00Z",
        "body_text": (
            "Attn: Underwriting,\n\n"
            "Requesting THB 15,000,000 export facility for Apex Global Trading Co., Ltd. (Registration: 0105558012345).\n"
            "Attached documents enclosed."
        ),
        "attachments": [
            {"attachment_id": "ATT-011", "filename": "apex_dbd_2023.pdf", "type": "DBD_CERTIFICATE", "size_kb": 980, "legible": True, "issue_date": "2023-01-10"},
            {"attachment_id": "ATT-012", "filename": "apex_shareholders.pdf", "type": "BOR_OR_JOR_5", "size_kb": 650, "legible": True, "issue_date": "2023-01-10"},
            {"attachment_id": "ATT-013", "filename": "apex_bank_stmts.pdf", "type": "BANK_STATEMENT_6M", "size_kb": 2800, "legible": True, "months_count": 6},
            {"attachment_id": "ATT-014", "filename": "apex_financials.pdf", "type": "FINANCIAL_STATEMENTS", "size_kb": 3200, "legible": True, "audited": False},
            {"attachment_id": "ATT-015", "filename": "thanakrit_id.pdf", "type": "DIRECTOR_NATIONAL_ID", "size_kb": 750, "legible": True, "holder_id": "1100900456789"},
        ],
        "application_id": "APP-2026-003",
    },
    {
        "email_id": "MSG-GMAIL-98204",
        "sender": "karn@cmbrewery.th",
        "recipient": "underwriting-intake@enterprise.gemini",
        "subject": "[underwriting] Equipment Financing Application - Chiang Mai Craft Brewery",
        "received_at": "2026-08-24T10:15:00Z",
        "body_text": (
            "Hello,\n\n"
            "We are applying for THB 5,000,000 equipment financing for Chiang Mai Craft Brewery Co., Ltd. (Registration: 0505563045678).\n"
            "Attached are our DBD certificate, financial statements, and director ID. Note that our accountant is preparing the BorOrJor.5 and bank statements.\n\n"
            "Karn Suwannasit"
        ),
        "attachments": [
            {"attachment_id": "ATT-016", "filename": "cm_dbd_cert.pdf", "type": "DBD_CERTIFICATE", "size_kb": 1100, "legible": True, "issue_date": "2026-08-01"},
            {"attachment_id": "ATT-017", "filename": "financial_stmt_2025.pdf", "type": "FINANCIAL_STATEMENTS", "size_kb": 4800, "legible": True, "audited": True},
            {"attachment_id": "ATT-018", "filename": "karn_id.pdf", "type": "DIRECTOR_NATIONAL_ID", "size_kb": 920, "legible": True, "holder_id": "5500100567890"},
        ],
        "application_id": "APP-2026-004",
    }
]

class ScanGmailRequest(BaseModel):
    subject_filter: str = Field(default="[underwriting]", description="Subject line filter prefix")
    max_results: int = Field(default=10, description="Max emails to return")

class FetchAttachmentRequest(BaseModel):
    email_id: str = Field(..., description="Email ID")
    attachment_id: str = Field(..., description="Attachment ID")

def scan_inbox_logic(subject_filter: str, max_results: int) -> Dict[str, Any]:
    matched = [
        email for email in MOCK_GMAIL_INBOX
        if subject_filter.lower() in email["subject"].lower()
    ][:max_results]
    return {
        "total_matching_emails": len(matched),
        "subject_filter_applied": subject_filter,
        "scanned_at": datetime.datetime.utcnow().isoformat() + "Z",
        "emails": matched,
    }

def fetch_attachment_logic(email_id: str, attachment_id: str) -> Dict[str, Any]:
    for email in MOCK_GMAIL_INBOX:
        if email["email_id"] == email_id:
            for att in email["attachments"]:
                if att.get("attachment_id") == attachment_id:
                    return {"status": "SUCCESS", "email_id": email_id, "attachment": att}
    return {"status": "NOT_FOUND", "message": f"Attachment {attachment_id} not found in email {email_id}"}

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "underwriting-gmail-mcp", "version": "2.0.0"}

@app.post("/tools/scan-gmail-inbox")
def scan_gmail_inbox_rest(req: ScanGmailRequest):
    return scan_inbox_logic(req.subject_filter, req.max_results)

@app.post("/tools/fetch-attachment")
def fetch_attachment_rest(req: FetchAttachmentRequest):
    return fetch_attachment_logic(req.email_id, req.attachment_id)

# MCP JSON-RPC 2.0 endpoint
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
                "serverInfo": {"name": "underwriting-gmail-mcp", "version": "2.0.0"},
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
                        "name": "scan_gmail_inbox",
                        "description": "Scans inbox for loan application packages matching subject filter (e.g. '[underwriting]').",
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
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "scan_gmail_inbox":
            res = scan_inbox_logic(args.get("subject_filter", "[underwriting]"), args.get("max_results", 10))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        elif tool_name == "fetch_email_attachment":
            res = fetch_attachment_logic(args.get("email_id", ""), args.get("attachment_id", ""))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
