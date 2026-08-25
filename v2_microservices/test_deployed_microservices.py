"""Comprehensive Live Test Suite for All 7 Deployed Cloud Run MCP Microservices."""

import requests
import json

services = [
    {
        "name": "underwriting-gmail-mcp",
        "url": "https://underwriting-gmail-mcp-<REGION_HASH>.a.run.app",
        "expected_tools": ["scan_gmail_inbox", "fetch_email_attachment"],
        "sample_call": {"name": "scan_gmail_inbox", "arguments": {"subject_filter": "[underwriting]", "max_results": 2}}
    },
    {
        "name": "underwriting-doc-mcp",
        "url": "https://underwriting-doc-mcp-<REGION_HASH>.a.run.app",
        "expected_tools": ["validate_document_checklist", "parse_financial_documents"],
        "sample_call": {"name": "validate_document_checklist", "arguments": {"application_id": "APP-2026-001", "entity_type": "CORPORATE"}}
    },
    {
        "name": "underwriting-registry-mcp",
        "url": "https://underwriting-registry-mcp-<REGION_HASH>.a.run.app",
        "expected_tools": ["verify_dbd_registry", "verify_dopa_identity", "screen_aml_sanctions"],
        "sample_call": {"name": "verify_dbd_registry", "arguments": {"registration_id": "0105561023456"}}
    },
    {
        "name": "underwriting-fraud-mcp",
        "url": "https://underwriting-fraud-mcp-<REGION_HASH>.a.run.app",
        "expected_tools": ["analyze_revenue_anomaly", "evaluate_statement_tampering"],
        "sample_call": {"name": "analyze_revenue_anomaly", "arguments": {"bank_inflows_6m_thb": 21000000.0, "pp30_vat_revenue_6m_thb": 20800000.0}}
    },
    {
        "name": "underwriting-scoring-mcp",
        "url": "https://underwriting-scoring-mcp-<REGION_HASH>.a.run.app",
        "expected_tools": ["calculate_dscr", "score_credit_risk"],
        "sample_call": {"name": "score_credit_risk", "arguments": {"monthly_noi_thb": 850000.0, "monthly_debt_service_thb": 420000.0, "monthly_turnover_thb": 3500000.0, "bounced_checks_count_6m": 0}}
    },
    {
        "name": "underwriting-decision-mcp",
        "url": "https://underwriting-decision-mcp-<REGION_HASH>.a.run.app",
        "expected_tools": ["evaluate_underwriting_decision"],
        "sample_call": {"name": "evaluate_underwriting_decision", "arguments": {"application_id": "APP-2026-001", "requested_facility_thb": 10000000.0, "credit_risk_tier": "TIER_A_PRIME"}}
    },
    {
        "name": "underwriting-notification-mcp",
        "url": "https://underwriting-notification-mcp-<REGION_HASH>.a.run.app",
        "expected_tools": ["generate_preapproval_letter", "generate_missing_doc_notice", "generate_underwriter_memo"],
        "sample_call": {"name": "generate_preapproval_letter", "arguments": {"application_id": "APP-2026-001", "borrower_name": "Siam Tech Logistics", "recipient_email": "somchai@siamtechlogistics.co.th", "approved_limit_thb": 10000000.0, "interest_rate": "MLR - 1.25%", "tenor_months": 60}}
    }
]

def main():
    print("=" * 70)
    print("🚀 LIVE CLOUD RUN MCP PROTOCOL TEST (7 MICROSERVICES)")
    print("=" * 70)

    for svc in services:
        print(f"\n📡 Testing Service: {svc['name']}")
        print(f"   URL: {svc['url']}/mcp")

        # 1. MCP Initialize Handshake
        init_payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        r_init = requests.post(f"{svc['url']}/mcp", json=init_payload, timeout=10)
        assert r_init.status_code == 200, f"Initialize failed: {r_init.text}"
        server_info = r_init.json().get("result", {}).get("serverInfo", {})
        print(f"   ✅ MCP Handshake OK: {server_info.get('name')} v{server_info.get('version')}")

        # 2. MCP Tools Discovery (tools/list)
        list_payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        r_list = requests.post(f"{svc['url']}/mcp", json=list_payload, timeout=10)
        tools = r_list.json().get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]
        for exp in svc["expected_tools"]:
            assert exp in tool_names, f"Missing expected tool {exp} in {tool_names}"
        print(f"   ✅ MCP Tools Discovered ({len(tools)}): {tool_names}")

        # 3. MCP Tool Execution (tools/call)
        call_payload = {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": svc["sample_call"]}
        r_call = requests.post(f"{svc['url']}/mcp", json=call_payload, timeout=10)
        assert r_call.status_code == 200, f"Tool call failed: {r_call.text}"
        call_res = r_call.json().get("result", {}).get("content", [{}])[0].get("text", "")
        preview = (call_res[:80] + "...") if len(call_res) > 80 else call_res
        print(f"   ✅ MCP Tool Execution ({svc['sample_call']['name']}): {preview}")

    print("\n" + "=" * 70)
    print("🎉 ALL 7 CLOUD RUN MCP MICROSERVICES ARE FULLY OPERATIONAL AND VERIFIED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
