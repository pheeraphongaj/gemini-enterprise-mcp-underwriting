"""Credit Policy Math & Financial Ratio Scoring MCP Microservice (underwriting-scoring-mcp).

Provides:
- calculate_dscr: Computes Debt Service Coverage Ratio (DSCR).
- score_credit_risk: Computes credit scoring tiers (Tier A, B, C, D) and recommended debt capacity.
Supports REST (/tools/...) and MCP JSON-RPC (/mcp).
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import datetime

app = FastAPI(
    title="Underwriting Credit Scoring MCP Service",
    description="MCP Microservice for DSCR Math, Turnover Ratios, and Credit Rating Tier Classification",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DSCRRequest(BaseModel):
    monthly_noi_thb: float = Field(..., description="Monthly Net Operating Income in THB")
    monthly_debt_service_thb: float = Field(..., description="Total Monthly Debt Service in THB")

class CreditRiskRequest(BaseModel):
    monthly_noi_thb: float = Field(..., description="Monthly Net Operating Income in THB")
    monthly_debt_service_thb: float = Field(..., description="Total Monthly Debt Service in THB")
    monthly_turnover_thb: float = Field(..., description="Average Monthly Bank Turnover in THB")
    bounced_checks_count_6m: int = Field(default=0, description="Number of bounced checks in last 6 months")

def calculate_dscr_logic(monthly_noi: float, monthly_debt_service: float) -> Dict[str, Any]:
    if monthly_debt_service <= 0:
        return {"status": "ERROR", "message": "Monthly debt service must be positive"}
    
    dscr = round(monthly_noi / monthly_debt_service, 2)
    benchmark_status = "MEETS_BENCHMARK" if dscr >= 1.25 else "BELOW_BENCHMARK"
    
    return {
        "monthly_noi_thb": monthly_noi,
        "monthly_debt_service_thb": monthly_debt_service,
        "dscr": dscr,
        "policy_benchmark_target": 1.25,
        "benchmark_status": benchmark_status,
        "calculated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

def score_credit_risk_logic(monthly_noi: float, monthly_debt_service: float, monthly_turnover: float, bounces: int) -> Dict[str, Any]:
    if monthly_debt_service <= 0:
        return {"status": "ERROR", "message": "Debt service must be positive"}

    dscr = round(monthly_noi / monthly_debt_service, 2)
    inflow_to_installment = round(monthly_turnover / monthly_debt_service, 2)

    if dscr >= 1.50 and monthly_turnover >= 2000000.0 and bounces == 0:
        risk_tier = "TIER_A_PRIME"
        fast_track_eligible = True
        recommended_interest_spread = "MLR - 1.25%"
        max_multiplier = 3.5
    elif dscr >= 1.25 and monthly_turnover >= 500000.0 and bounces == 0:
        risk_tier = "TIER_B_STANDARD"
        fast_track_eligible = True
        recommended_interest_spread = "MLR - 0.75%"
        max_multiplier = 2.5
    elif (1.10 <= dscr < 1.25) or (bounces == 1):
        risk_tier = "TIER_C_BORDERLINE"
        fast_track_eligible = False
        recommended_interest_spread = "MLR + 0.50%"
        max_multiplier = 1.5
    else:
        risk_tier = "TIER_D_HIGH_RISK"
        fast_track_eligible = False
        recommended_interest_spread = "N/A - DECLINE"
        max_multiplier = 0.0

    max_credit_limit_thb = round(monthly_turnover * max_multiplier, 2)

    return {
        "dscr": dscr,
        "monthly_turnover_thb": monthly_turnover,
        "inflow_to_installment_ratio": inflow_to_installment,
        "bounced_checks_count_6m": bounces,
        "credit_risk_tier": risk_tier,
        "fast_track_eligible": fast_track_eligible,
        "indicative_pricing_spread": recommended_interest_spread,
        "max_recommended_limit_thb": max_credit_limit_thb,
        "scored_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "underwriting-scoring-mcp", "version": "2.0.0"}

@app.post("/tools/calculate-dscr")
def calculate_dscr_rest(req: DSCRRequest):
    return calculate_dscr_logic(req.monthly_noi_thb, req.monthly_debt_service_thb)

@app.post("/tools/score-credit-risk")
def score_credit_risk_rest(req: CreditRiskRequest):
    return score_credit_risk_logic(req.monthly_noi_thb, req.monthly_debt_service_thb, req.monthly_turnover_thb, req.bounced_checks_count_6m)

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
                "serverInfo": {"name": "underwriting-scoring-mcp", "version": "2.0.0"},
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
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "calculate_dscr":
            res = calculate_dscr_logic(args.get("monthly_noi_thb", 0.0), args.get("monthly_debt_service_thb", 1.0))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        elif tool_name == "score_credit_risk":
            res = score_credit_risk_logic(
                args.get("monthly_noi_thb", 0.0),
                args.get("monthly_debt_service_thb", 1.0),
                args.get("monthly_turnover_thb", 0.0),
                args.get("bounced_checks_count_6m", 0)
            )
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
