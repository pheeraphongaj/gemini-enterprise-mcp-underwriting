"""Underwriting Decision Engine MCP Microservice (underwriting-decision-mcp).

Provides:
- evaluate_underwriting_decision: Evaluates policy rules, fast-track eligibility, rate spreads, and facility structuring.
Supports REST (/tools/...) and MCP JSON-RPC (/mcp).
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import datetime

app = FastAPI(
    title="Underwriting Decision MCP Service",
    description="MCP Microservice for Policy Matrix Decisioning, Facility Terms, and Underwriter Escalation",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DecisionRequest(BaseModel):
    application_id: str = Field(..., description="Application ID")
    requested_facility_thb: float = Field(..., description="Requested loan/credit amount in THB")
    credit_risk_tier: str = Field(..., description="TIER_A_PRIME, TIER_B_STANDARD, TIER_C_BORDERLINE, TIER_D_HIGH_RISK")
    fraud_risk_level: str = Field(default="LOW", description="LOW, MEDIUM_ANOMALY, HIGH_ANOMALY")
    registry_knockout: bool = Field(default=False, description="Whether any DBD, DOPA, or AML knockout triggered")
    knockout_reason: Optional[str] = Field(None, description="Reason if knockout triggered")
    litigation_flag: bool = Field(default=False, description="Whether there are active or settled litigation cases")

def evaluate_decision_logic(
    application_id: str,
    requested_facility: float,
    tier: str,
    fraud_level: str,
    knockout: bool,
    knockout_reason: Optional[str],
    litigation: bool
) -> Dict[str, Any]:
    # 1. Hard Knockout Gate
    if knockout or tier == "TIER_D_HIGH_RISK" or fraud_level == "HIGH_ANOMALY":
        reasons = []
        if knockout:
            reasons.append(knockout_reason or "Regulatory registry knockout triggered")
        if tier == "TIER_D_HIGH_RISK":
            reasons.append("Fails minimum DSCR and credit policy ratio thresholds (Tier D)")
        if fraud_level == "HIGH_ANOMALY":
            reasons.append("Severe revenue variance between bank statements and P.P.30 VAT filings")

        return {
            "application_id": application_id,
            "decision": "REJECTED",
            "decision_badge": "❌ DECLINED / REJECTED",
            "approved_facility_limit_thb": 0.0,
            "interest_rate": None,
            "tenor_months": 0,
            "rejection_reasons": reasons,
            "adverse_action_notice_required": True,
            "decided_at": datetime.datetime.utcnow().isoformat() + "Z"
        }

    # 2. Referral Gate (Tier C, Moderate Fraud Anomaly, or Litigation History)
    if tier == "TIER_C_BORDERLINE" or fraud_level == "MEDIUM_ANOMALY" or litigation:
        referral_reasons = []
        if tier == "TIER_C_BORDERLINE":
            referral_reasons.append("Borderline DSCR (1.10x - 1.24x) requiring senior credit officer review")
        if fraud_level == "MEDIUM_ANOMALY":
            referral_reasons.append("Moderate turnover variance between VAT and bank inflows")
        if litigation:
            referral_reasons.append("Commercial dispute / litigation record on file requiring legal sign-off")

        mitigating_structure = [
            "Mandatory Director Personal Guarantee with Joint & Several Liability",
            "Pledge of Commercial Property / Fixed Asset Mortgage covering >= 120% of facility",
            "Negative Pledge on Core Operating Machinery"
        ]

        return {
            "application_id": application_id,
            "decision": "REFERRED_TO_UW",
            "decision_badge": "⚠️ REFERRED TO CREDIT COMMITTEE",
            "approved_facility_limit_thb": requested_facility,
            "indicative_pricing": "MLR + 0.50% (7.625% p.a.)",
            "tenor_months": 36,
            "referral_reasons": referral_reasons,
            "mitigating_collateral_conditions": mitigating_structure,
            "committee_escalation_memo_generated": True,
            "decided_at": datetime.datetime.utcnow().isoformat() + "Z"
        }

    # 3. Fast-Track Pre-Approval (Tier A or Tier B)
    if tier == "TIER_A_PRIME":
        spread = "MLR - 1.25% (5.875% p.a.)"
        tenor = 60
    else: # TIER_B_STANDARD
        spread = "MLR - 0.75% (6.375% p.a.)"
        tenor = 48

    covenants = [
        "Maintain minimum DSCR of >= 1.25x audited annually",
        "Maintain debt-to-equity (D/E) ratio below 3.0x",
        "Continuous personal guarantee of principal directors"
    ]

    return {
        "application_id": application_id,
        "decision": "PRE_APPROVED",
        "decision_badge": "✅ FAST-TRACK PRE-APPROVED",
        "approved_facility_limit_thb": requested_facility,
        "indicative_pricing": spread,
        "tenor_months": tenor,
        "standard_covenants": covenants,
        "pre_approval_letter_generated": True,
        "decided_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "underwriting-decision-mcp", "version": "2.0.0"}

@app.post("/tools/evaluate-decision")
def evaluate_decision_rest(req: DecisionRequest):
    return evaluate_decision_logic(
        req.application_id,
        req.requested_facility_thb,
        req.credit_risk_tier,
        req.fraud_risk_level,
        req.registry_knockout,
        req.knockout_reason,
        req.litigation_flag
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
                "serverInfo": {"name": "underwriting-decision-mcp", "version": "2.0.0"},
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
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "evaluate_underwriting_decision":
            res = evaluate_decision_logic(
                args.get("application_id", ""),
                args.get("requested_facility_thb", 0.0),
                args.get("credit_risk_tier", "TIER_B_STANDARD"),
                args.get("fraud_risk_level", "LOW"),
                args.get("registry_knockout", False),
                args.get("knockout_reason"),
                args.get("litigation_flag", False)
            )
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
