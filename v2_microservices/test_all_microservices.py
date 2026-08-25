"""Automated Verification Suite for All 7 v2 Microservices using independent module loaders."""

import importlib.util
import os

services_dir = "/google/src/cloud/pheeraphong/hong-ai-demo/google3/underwriting_demo/v2_microservices/services"

def load_module(service_name: str):
    path = os.path.join(services_dir, service_name, "main.py")
    spec = importlib.util.spec_from_file_location(service_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Test 1: Gmail MCP
gmail_svc = load_module("gmail_mcp")
res_gmail = gmail_svc.scan_inbox_logic("[underwriting]", 10)
assert res_gmail["total_matching_emails"] == 4, f"Gmail scan failed: {res_gmail}"
print("✅ 1. underwriting-gmail-mcp logic PASSED")

# Test 2: Doc MCP
doc_svc = load_module("doc_mcp")
res_doc_valid = doc_svc.validate_docs_logic("APP-2026-001", "CORPORATE")
assert res_doc_valid["status"] == "DOCS_VALIDATED", f"Doc validation failed: {res_doc_valid}"
res_doc_miss = doc_svc.validate_docs_logic("APP-2026-004", "CORPORATE")
assert res_doc_miss["status"] == "DOCS_MISSING", f"Doc missing check failed: {res_doc_miss}"
print("✅ 2. underwriting-doc-mcp logic PASSED")

# Test 3: Registry MCP
reg_svc = load_module("registry_mcp")
res_dbd_ok = reg_svc.verify_dbd_logic("0105561023456")
assert res_dbd_ok["is_active_operating"] is True, f"DBD verify failed: {res_dbd_ok}"
res_dbd_bad = reg_svc.verify_dbd_logic("0105558012345")
assert res_dbd_bad["knockout_triggered"] is True, f"DBD knockout failed: {res_dbd_bad}"
print("✅ 3. underwriting-registry-mcp logic PASSED")

# Test 4: Fraud MCP
fraud_svc = load_module("fraud_mcp")
res_fraud_low = fraud_svc.analyze_revenue_anomaly_logic(21000000.0, 20800000.0)
assert res_fraud_low["risk_level"] == "LOW", f"Fraud low check failed: {res_fraud_low}"
res_fraud_high = fraud_svc.analyze_revenue_anomaly_logic(36000000.0, 12000000.0)
assert res_fraud_high["risk_level"] == "HIGH_ANOMALY", f"Fraud high check failed: {res_fraud_high}"
print("✅ 4. underwriting-fraud-mcp logic PASSED")

# Test 5: Scoring MCP
score_svc = load_module("scoring_mcp")
res_score_a = score_svc.score_credit_risk_logic(850000.0, 420000.0, 3500000.0, 0)
assert res_score_a["credit_risk_tier"] == "TIER_A_PRIME", f"Scoring prime failed: {res_score_a}"
res_score_c = score_svc.score_credit_risk_logic(210000.0, 180000.0, 1200000.0, 1)
assert res_score_c["credit_risk_tier"] == "TIER_C_BORDERLINE", f"Scoring borderline failed: {res_score_c}"
print("✅ 5. underwriting-scoring-mcp logic PASSED")

# Test 6: Decision MCP
dec_svc = load_module("decision_mcp")
res_dec_app = dec_svc.evaluate_decision_logic("APP-2026-001", 10000000.0, "TIER_A_PRIME", "LOW", False, None, False)
assert res_dec_app["decision"] == "PRE_APPROVED", f"Decision approve failed: {res_dec_app}"
res_dec_ref = dec_svc.evaluate_decision_logic("APP-2026-002", 3000000.0, "TIER_C_BORDERLINE", "LOW", False, None, True)
assert res_dec_ref["decision"] == "REFERRED_TO_UW", f"Decision referral failed: {res_dec_ref}"
print("✅ 6. underwriting-decision-mcp logic PASSED")

# Test 7: Notification MCP
notif_svc = load_module("notification_mcp")
res_letter = notif_svc.generate_preapproval_logic("APP-2026-001", "Siam Tech Logistics", "somchai@siamtechlogistics.co.th", 10000000.0, "MLR - 1.25%", 60)
assert res_letter["dispatched"] is True, f"Letter gen failed: {res_letter}"
print("✅ 7. underwriting-notification-mcp logic PASSED")

print("\n🎉 ALL 7 v2 MICROSERVICES VERIFIED SUCCESSFULLY 100%!")
