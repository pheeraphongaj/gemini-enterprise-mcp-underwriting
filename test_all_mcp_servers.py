"""Comprehensive test script for all 7 Cloud Run MCP microservices.
Tests tools/list and tools/call for every single tool across all microservices."""

import json
import urllib.request
import urllib.error
import time

mcp_servers = [
    {
        "name": "Underwriting Gmail Scanner MCP",
        "url": "https://underwriting-gmail-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "tests": [
            {
                "tool": "scan_gmail_inbox",
                "args": {"query": "label:loan-applications", "max_results": 5}
            },
            {
                "tool": "fetch_email_attachment",
                "args": {"message_id": "msg_001", "attachment_id": "att_001"}
            }
        ]
    },
    {
        "name": "Underwriting Document Parser MCP",
        "url": "https://underwriting-doc-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "tests": [
            {
                "tool": "validate_document_checklist",
                "args": {"applicant_id": "APP-2026-001", "submitted_documents": ["id_card", "bank_statement_6m", "company_registration"]}
            },
            {
                "tool": "parse_financial_documents",
                "args": {"document_type": "bank_statement", "document_data": "sample_statement_payload"}
            }
        ]
    },
    {
        "name": "Underwriting Registry & AML MCP",
        "url": "https://underwriting-registry-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "tests": [
            {
                "tool": "verify_dbd_registry",
                "args": {"juristic_id": "0105558000001", "company_name": "บริษัท สยาม ซอฟต์แวร์ โซลูชั่น จำกัด"}
            },
            {
                "tool": "verify_dopa_identity",
                "args": {"national_id": "1100500123456", "first_name": "สมชาย", "last_name": "ใจดี"}
            },
            {
                "tool": "screen_aml_sanctions",
                "args": {"entity_name": "บริษัท สยาม ซอฟต์แวร์ โซลูชั่น จำกัด", "entity_type": "JURISTIC"}
            }
        ]
    },
    {
        "name": "Underwriting Fraud Risk MCP",
        "url": "https://underwriting-fraud-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "tests": [
            {
                "tool": "analyze_revenue_anomaly",
                "args": {"monthly_revenues": [1200000, 1250000, 1180000, 1300000, 1220000, 1280000], "industry_type": "IT_SERVICES"}
            },
            {
                "tool": "evaluate_statement_tampering",
                "args": {"statement_id": "STMT-9921", "reported_balance": 4500000}
            }
        ]
    },
    {
        "name": "Underwriting Credit Scoring MCP",
        "url": "https://underwriting-scoring-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "tests": [
            {
                "tool": "calculate_dscr",
                "args": {"net_operating_income": 3600000, "total_debt_service": 2400000}
            },
            {
                "tool": "score_credit_risk",
                "args": {"applicant_type": "SME", "dscr": 1.5, "years_in_business": 5, "ncb_grade": "A", "revenue_anomaly_score": 0.05}
            }
        ]
    },
    {
        "name": "Underwriting Decision Engine MCP",
        "url": "https://underwriting-decision-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "tests": [
            {
                "tool": "evaluate_underwriting_decision",
                "args": {
                    "applicant_id": "APP-2026-001",
                    "requested_amount": 10000000,
                    "credit_score": 820,
                    "dscr": 1.5,
                    "fraud_risk": "LOW",
                    "dbd_verified": True,
                    "aml_cleared": True
                }
            }
        ]
    },
    {
        "name": "Underwriting Notification & Memo MCP",
        "url": "https://underwriting-notification-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "tests": [
            {
                "tool": "generate_preapproval_letter",
                "args": {
                    "applicant_id": "APP-2026-001",
                    "company_name": "บริษัท สยาม ซอฟต์แวร์ โซลูชั่น จำกัด",
                    "approved_amount": 10000000,
                    "interest_rate": "5.75%",
                    "tenor_months": 60
                }
            },
            {
                "tool": "generate_missing_doc_notice",
                "args": {"applicant_id": "APP-2026-001", "missing_docs": ["financial_statement_audited_2025"]}
            },
            {
                "tool": "generate_underwriter_memo",
                "args": {"applicant_id": "APP-2026-001", "decision": "APPROVE", "rationale": "Strong DSCR 1.5, low fraud risk, 5 years profitable operation"}
            }
        ]
    }
]

def send_rpc(url, method, params=None, req_id=1):
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
    }
    if params is not None:
        payload["params"] = params
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read().decode("utf-8"))

print("===================================================================")
print("🧪 DIRECT MCP MICROSERVICE TESTING (All 7 Cloud Run Services)")
print("===================================================================")

total_tools = 0
passed_tools = 0

for s in mcp_servers:
    print(f"\n📦 Service: {s['name']}")
    print(f"   URL: {s['url']}")
    
    # 1. Test tools/list
    try:
        list_res = send_rpc(s["url"], "tools/list")
        tools = list_res.get("result", {}).get("tools", [])
        tool_names = [t.get("name") for t in tools]
        print(f"   ✓ tools/list: {len(tools)} tools discovered -> {tool_names}")
    except Exception as e:
        print(f"   ❌ tools/list failed: {e}")
        continue
    
    # 2. Test each tool call
    for t in s["tests"]:
        total_tools += 1
        tool_name = t["tool"]
        tool_args = t["args"]
        try:
            call_res = send_rpc(
                s["url"],
                "tools/call",
                params={"name": tool_name, "arguments": tool_args}
            )
            result = call_res.get("result", {})
            content = result.get("content", [])
            output_snippet = content[0].get("text", "")[:120] if content else str(result)[:120]
            print(f"   ✅ tools/call [{tool_name}]: Success")
            print(f"      Result: {output_snippet}...")
            passed_tools += 1
        except Exception as e:
            print(f"   ❌ tools/call [{tool_name}] failed: {e}")

print("\n===================================================================")
print(f"📊 SUMMARY: {passed_tools}/{total_tools} MCP Tools Successfully Tested")
print("===================================================================")
