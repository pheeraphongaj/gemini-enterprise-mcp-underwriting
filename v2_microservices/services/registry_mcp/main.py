"""National Registries & Compliance MCP Microservice (underwriting-registry-mcp).

Provides:
- verify_dbd_registry: Queries DBD Corporate Registry for operational status, capital, equity, and litigation.
- verify_dopa_identity: Checks DOPA Civil Identity database for director ID validity.
- screen_aml_sanctions: Screens against AMLO and PEP watchlists.
Supports REST (/tools/...) and MCP JSON-RPC (/mcp).
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import datetime

app = FastAPI(
    title="Underwriting Registry MCP Service",
    description="MCP Microservice for Thai DBD, DOPA, and AML/PEP Compliance Verification",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_DBD_REGISTRY = {
    "0105561023456": {
        "registration_id": "0105561023456",
        "company_name_th": "บริษัท สยาม เทค โลจิสติกส์ จำกัด",
        "company_name_en": "Siam Tech Logistics Co., Ltd.",
        "status": "ACTIVE",
        "registered_capital_thb": 20000000.0,
        "paid_up_capital_thb": 20000000.0,
        "registration_date": "2018-03-12",
        "latest_equity_thb": 18450000.0,
        "litigation_records": [],
        "directors": ["1100400123456"]
    },
    "0105562098765": {
        "registration_id": "0105562098765",
        "company_name_th": "บริษัท บางกอก เฟรช รีเทล จำกัด",
        "company_name_en": "Bangkok Fresh Retail Co., Ltd.",
        "status": "ACTIVE",
        "registered_capital_thb": 5000000.0,
        "paid_up_capital_thb": 5000000.0,
        "registration_date": "2019-11-04",
        "latest_equity_thb": 3200000.0,
        "litigation_records": [
            {"case_no": "Black Case No. MorPor 128/2567", "type": "COMMERCIAL_SUPPLIER_DISPUTE", "amount_thb": 250000.0, "status": "SETTLED"}
        ],
        "directors": ["3100800345678"]
    },
    "0105558012345": {
        "registration_id": "0105558012345",
        "company_name_th": "บริษัท เอเปกซ์ โกลบอล เทรดดิ้ง จำกัด",
        "company_name_en": "Apex Global Trading Co., Ltd.",
        "status": "INACTIVE_SUSPENDED",
        "registered_capital_thb": 50000000.0,
        "paid_up_capital_thb": 50000000.0,
        "registration_date": "2015-06-20",
        "latest_equity_thb": -12500000.0,
        "litigation_records": [
            {"case_no": "Red Case No. Phor 892/2566", "type": "DEFAULT_JUDGMENT_LOAN", "amount_thb": 14200000.0, "status": "PENDING_EXECUTION"}
        ],
        "directors": ["1100900456789"]
    },
    "0505563045678": {
        "registration_id": "0505563045678",
        "company_name_th": "บริษัท เชียงใหม่ คราฟท์ บริวเวอรี่ จำกัด",
        "company_name_en": "Chiang Mai Craft Brewery Co., Ltd.",
        "status": "ACTIVE",
        "registered_capital_thb": 8000000.0,
        "paid_up_capital_thb": 8000000.0,
        "registration_date": "2020-08-15",
        "latest_equity_thb": 6100000.0,
        "litigation_records": [],
        "directors": ["5500100567890"]
    }
}

MOCK_DOPA_CIVIL_ID = {
    "1100400123456": {"name": "นายสมชาย ศิริวัฒนากุล", "status": "VALID", "expiry_date": "2029-05-14", "laser_code_verified": True},
    "3100800345678": {"name": "นายวิชัย รัตนรุ่งเรือง", "status": "VALID", "expiry_date": "2028-10-22", "laser_code_verified": True},
    "1100900456789": {"name": "นายธนกฤต ทรัพย์ไพศาล", "status": "EXPIRED", "expiry_date": "2023-01-15", "laser_code_verified": False},
    "5500100567890": {"name": "นายกานต์ สุวรรณสิทธิ์", "status": "VALID", "expiry_date": "2030-03-08", "laser_code_verified": True}
}

MOCK_AML_PEP_WATCHLIST = {
    "1100900456789": {
        "hit": True,
        "category": "AMLO_SANCTIONS_LIST_1",
        "reason": "Suspected illicit trade financing & customs violations",
        "risk_level": "SANCTIONS_BLOCKED"
    }
}

class DBDVerifyRequest(BaseModel):
    registration_id: str = Field(..., description="13-digit Thai Tax/DBD Registration ID")
    company_name: Optional[str] = Field(None, description="Optional company name")

class DOPAVerifyRequest(BaseModel):
    national_id: str = Field(..., description="13-digit Thai National ID")

class AMLScreenRequest(BaseModel):
    national_id: Optional[str] = Field(None, description="13-digit National ID")
    registration_id: Optional[str] = Field(None, description="13-digit Corporate Registration ID")
    name: Optional[str] = Field(None, description="Individual or Entity Name")

def verify_dbd_logic(registration_id: str) -> Dict[str, Any]:
    dbd_rec = MOCK_DBD_REGISTRY.get(registration_id)
    if not dbd_rec:
        return {"status": "NOT_FOUND", "message": f"Company {registration_id} not found in DBD database"}
    
    is_active = dbd_rec["status"] == "ACTIVE"
    has_positive_equity = dbd_rec["latest_equity_thb"] > 0
    knockout = (not is_active) or (not has_positive_equity)

    return {
        "registration_id": registration_id,
        "company_name_th": dbd_rec["company_name_th"],
        "company_name_en": dbd_rec["company_name_en"],
        "status": dbd_rec["status"],
        "is_active_operating": is_active,
        "registered_capital_thb": dbd_rec["registered_capital_thb"],
        "latest_equity_thb": dbd_rec["latest_equity_thb"],
        "positive_equity": has_positive_equity,
        "litigation_records": dbd_rec["litigation_records"],
        "knockout_triggered": knockout,
        "knockout_reason": "Company inactive or negative equity" if knockout else None,
        "verified_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

def verify_dopa_logic(national_id: str) -> Dict[str, Any]:
    dopa_rec = MOCK_DOPA_CIVIL_ID.get(national_id)
    if not dopa_rec:
        return {"national_id": national_id, "status": "NOT_FOUND", "is_valid": False}
    is_valid = dopa_rec["status"] == "VALID"
    return {
        "national_id": f"***-***-{national_id[-4:]}",
        "name": dopa_rec["name"],
        "status": dopa_rec["status"],
        "is_valid": is_valid,
        "expiry_date": dopa_rec["expiry_date"],
        "laser_code_verified": dopa_rec["laser_code_verified"],
        "verified_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

def screen_aml_logic(national_id: Optional[str], registration_id: Optional[str], name: Optional[str]) -> Dict[str, Any]:
    hit_rec = None
    if national_id and national_id in MOCK_AML_PEP_WATCHLIST:
        hit_rec = MOCK_AML_PEP_WATCHLIST[national_id]
    if registration_id and registration_id in MOCK_AML_PEP_WATCHLIST:
        hit_rec = MOCK_AML_PEP_WATCHLIST[registration_id]

    if hit_rec:
        return {
            "aml_hit": True,
            "category": hit_rec["category"],
            "reason": hit_rec["reason"],
            "risk_level": hit_rec["risk_level"],
            "hard_block": True,
            "screened_at": datetime.datetime.utcnow().isoformat() + "Z"
        }
    return {
        "aml_hit": False,
        "category": None,
        "risk_level": "CLEAR",
        "hard_block": False,
        "screened_at": datetime.datetime.utcnow().isoformat() + "Z"
    }

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "underwriting-registry-mcp", "version": "2.0.0"}

@app.post("/tools/verify-dbd")
def verify_dbd_rest(req: DBDVerifyRequest):
    return verify_dbd_logic(req.registration_id)

@app.post("/tools/verify-dopa")
def verify_dopa_rest(req: DOPAVerifyRequest):
    return verify_dopa_logic(req.national_id)

@app.post("/tools/screen-aml")
def screen_aml_rest(req: AMLScreenRequest):
    return screen_aml_logic(req.national_id, req.registration_id, req.name)

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
                "serverInfo": {"name": "underwriting-registry-mcp", "version": "2.0.0"},
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
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "verify_dbd_registry":
            res = verify_dbd_logic(args.get("registration_id", ""))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        elif tool_name == "verify_dopa_identity":
            res = verify_dopa_logic(args.get("national_id", ""))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        elif tool_name == "screen_aml_sanctions":
            res = screen_aml_logic(args.get("national_id"), args.get("registration_id"), args.get("name"))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": str(res)}]}}
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
