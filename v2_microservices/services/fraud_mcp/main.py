"""Fraud Risk & Anomaly Detection MCP Microservice (underwriting-fraud-mcp).

Provides:
- analyze_revenue_anomaly: Cross-validates bank statement inflows against P.P.30 VAT filings.
- evaluate_statement_tampering: Evaluates bounced check patterns and cash-flow tampering.
Supports REST (/tools/...) and MCP JSON-RPC (/mcp).
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import datetime

app = FastAPI(
    title="Underwriting Fraud Risk MCP Service",
    description="MCP Microservice for Revenue Anomaly, Statement Tampering & Check Bounce Analysis",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RevenueAnomalyRequest(BaseModel):
    bank_inflows_6m_thb: float = Field(..., description="Total 6-month bank statement deposits in THB")
    pp30_vat_revenue_6m_thb: float = Field(..., description="Total 6-month P.P.30 VAT gross reported sales in THB")

class StatementTamperingRequest(BaseModel):
    bounced_checks_count_6m: int = Field(default=0, description="Total number of bounced checks in last 6 months")
    overdraft_utilization_pct: float = Field(default=0.0, description="Average Overdraft (O/D) line utilization %")

def analyze_revenue_anomaly_logic(bank_inflows: float, pp30_vat: float) -> Dict[str, Any]:
    if bank_inflows <= 0:
        return {"status": "ERROR", "message": "Bank inflows must be positive"}
    
    variance_thb = abs(bank_inflows - pp30_vat)
    variance_pct = round((variance_thb / bank_inflows) * 100.0, 2)

    # Fraud scoring based on variance
    if variance_pct <= 5.0:
        risk_level = "LOW"
        fraud_score = 5
    elif variance_pct <= 15.0:
        risk_level = "LOW"
        fraud_score = 15
    elif variance_pct <= 30.0:
        risk_level = "MEDIUM_ANOMALY"
        fraud_score = 45
    else:
        risk_level = "HIGH_ANOMALY"
        fraud_score = 85

    return {
        "bank_inflows_6m_thb": bank_inflows,
        "pp30_vat_revenue_6m_thb": pp30_vat,
        "variance_thb": variance_thb,
        "variance_pct": variance_pct,
        "fraud_score": fraud_score,
        "risk_level": risk_level,
        "tax_audit_risk": "HIGH" if variance_pct > 25.0 else "NORMAL",
        "evaluated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

def evaluate_tampering_logic(bounces: int, od_util: float) -> Dict[str, Any]:
    distress_flags = []
    if bounces >= 3:
        distress_flags.append("FREQUENT_CHECK_BOUNCE_KITE_FLYING")
    elif bounces >= 1:
        distress_flags.append("OCCASIONAL_CHECK_BOUNCE")
    
    if od_util >= 90.0:
        distress_flags.append("CHRONIC_OVERDRAFT_SATURATION")

    status = "HIGH_DISTRESS" if bounces >= 3 or od_util >= 95.0 else "NORMAL"
    return {
        "bounced_checks_count_6m": bounces,
        "overdraft_utilization_pct": od_util,
        "distress_status": status,
        "distress_flags": distress_flags,
        "evaluated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "underwriting-fraud-mcp", "version": "2.0.0"}

@app.post("/tools/analyze-revenue-anomaly")
def analyze_revenue_anomaly_rest(req: RevenueAnomalyRequest):
    return analyze_revenue_anomaly_logic(req.bank_inflows_6m_thb, req.pp30_vat_revenue_6m_thb)

@app.post("/tools/evaluate-tampering")
def evaluate_tampering_rest(req: StatementTamperingRequest):
    return evaluate_tampering_logic(req.bounced_checks_count_6m, req.overdraft_utilization_pct)

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
                "serverInfo": {"name": "underwriting-fraud-mcp", "version": "2.0.0"},
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
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "analyze_revenue_anomaly":
            res = analyze_revenue_anomaly_logic(args.get("bank_inflows_6m_thb", 0.0), args.get("pp30_vat_revenue_6m_thb", 0.0))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        elif tool_name == "evaluate_statement_tampering":
            res = evaluate_tampering_logic(args.get("bounced_checks_count_6m", 0), args.get("overdraft_utilization_pct", 0.0))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
