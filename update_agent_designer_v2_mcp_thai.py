"""Updates the Underwriting Multi-Agent Orchestrator in ge-demo1 with MCP tool bindings and 100% Thai language instructions."""

import json
import subprocess
import urllib.request
import urllib.error

with open("agent_prompt_th.md", "r", encoding="utf-8") as f:
    thai_system_instruction = f.read()

token = (
    subprocess.check_output(
        ["gcloud", "auth", "print-access-token"]
    )
    .decode("utf-8")
    .strip()
)

parent = "projects/hong-ai-demo/locations/global/collections/default_collection/engines/ge-demo1/assistants/default_assistant"
agent_id = "underwriting-orchestrator"

# 7 Specialized Sub-Agent Nodes with Thai prompts & direct MCP tool configurations
sub_nodes = [
    {
        "id": "root_agent",
        "displayName": "Underwriting Multi-Agent Orchestrator",
        "llmAgentNode": {
            "description": "ระบบควบคุมหลัก (Main Orchestrator) สำหรับบริหารจัดการกระบวนการพิจารณาสินเชื่อธุรกิจและ SME อัตโนมัติ 7 ขั้นตอน ทุกคำตอบเป็นภาษาไทย",
            "model": "gemini-1.5-pro",
            "instruction": thai_system_instruction,
            "subAgentIds": [
                "doc_intake_agent",
                "doc_parser_agent",
                "verification_agent",
                "fraud_risk_agent",
                "scoring_engine_agent",
                "decision_agent",
                "notification_agent"
            ],
            "selectedTools": {
                "tool": [
                    {"name": "scan_gmail_inbox"},
                    {"name": "fetch_email_attachment"},
                    {"name": "googleSearch"}
                ]
            }
        }
    },
    {
        "id": "doc_intake_agent",
        "displayName": "DocIntakeAgent (ตรวจสอบเอกสาร)",
        "llmAgentNode": {
            "description": "ตรวจสอบความครบถ้วน ถูกต้อง และความชัดเจนของเอกสารบังคับในการขอสินเชื่อ (หนังสือรับรอง DBD, บอจ.5, สเตทเมนท์ 6 เดือน, งบการเงิน, บัตรประชาชนกรรมการ)",
            "model": "gemini-1.5-pro",
            "instruction": """คุณคือ DocIntakeAgent (เจ้าหน้าที่ปัญญาประดิษฐ์ตรวจสอบเอกสารสินเชื่อ)
หน้าที่:
1. ตรวจสอบรายการเอกสารบังคับสำหรับการสมัครสินเชื่อธุรกิจตามกฎหมายและนโยบายธนาคาร
2. เรียกใช้เครื่องมือ MCP `validate_document_checklist` (application_id, entity_type)
3. ตรวจสอบความถูกต้องและวันหมดอายุ (หนังสือรับรอง DBD ต้องอายุไม่เกิน 3 เดือน)
4. สรุปผลเป็นภาษาไทย: หากครบถ้วนให้ระบุ 'DOCS_VALIDATED (เอกสารครบถ้วน)' หากขาดให้ระบุ 'DOCS_MISSING (เอกสารไม่ครบถ้วน)' พร้อมแจกแจงรายการที่ขาดอย่างชัดเจน""",
            "selectedTools": {
                "tool": [
                    {"name": "validate_document_checklist"},
                    {"name": "googleSearch"}
                ]
            }
        }
    },
    {
        "id": "doc_parser_agent",
        "displayName": "DocParserAgent (สกัดข้อมูลการเงิน)",
        "llmAgentNode": {
            "description": "สกัดและแปลงข้อมูลตัวเลขทางการเงินจากงบการเงิน รายการเดินบัญชีธนาคาร และแบบแสดงรายการภาษี ป.พ.30 เข้าสู่โครงสร้างมาตรฐาน",
            "model": "gemini-1.5-pro",
            "instruction": """คุณคือ DocParserAgent (เจ้าหน้าที่ปัญญาประดิษฐ์สกัดข้อมูลทางการเงิน)
หน้าที่:
1. สกัดตัวเลขทางการเงินที่สำคัญจากเอกสารผ่านเครื่องมือ MCP `parse_financial_documents` (application_id)
2. รวบรวมข้อมูล: ยอดเงินหมุนเวียนรายเดือน, รายได้จากการดำเนินงานสุทธิ (NOI), ภาระผ่อนชำระหนี้รายเดือน, ยอดขายรายงานภาษี ป.พ.30, สัดส่วนการใช้วงเงินเบิกเกินบัญชี (O/D) และจำนวนเช็คคืน
3. รายงานสรุปผลตัวเลขทางการเงินเป็นภาษาไทยและตารางที่อ่านง่าย""",
            "selectedTools": {
                "tool": [
                    {"name": "parse_financial_documents"},
                    {"name": "googleSearch"}
                ]
            }
        }
    },
    {
        "id": "verification_agent",
        "displayName": "VerificationAgent (ตรวจสอบภาครัฐ & ปปง.)",
        "llmAgentNode": {
            "description": "ตรวจสอบสถานะนิติบุคคลจากกรมพัฒนาธุรกิจการค้า (DBD), ตรวจสอบความถูกต้องของบัตรประชาชนกรรมการจากกรมการปกครอง (DOPA) และคัดกรองบุคคลต้องห้ามตามกฎหมายฟอกเงิน (AMLO/PEP)",
            "model": "gemini-1.5-pro",
            "instruction": """คุณคือ VerificationAgent (เจ้าหน้าที่ปัญญาประดิษฐ์ตรวจสอบคุณสมบัติและกฎหมาย)
หน้าที่:
1. ตรวจสอบสถานะนิติบุคคลผ่านเครื่องมือ MCP `verify_dbd_registry` (registration_id)
   - สถานะต้องเป็น ACTIVE (ยังดำเนินกิจการ) และส่วนของผู้ถือหุ้น (Net Equity) ต้องเป็นบวก
2. ตรวจสอบบัตรประชาชนกรรมการผ่านเครื่องมือ MCP `verify_dopa_identity` (national_id)
   - บัตรประชาชนต้องมีสถานะ VALID และไม่หมดอายุ
3. คัดกรองรายชื่อบุคคลต้องห้ามผ่านเครื่องมือ MCP `screen_aml_sanctions` (national_id, registration_id)
   - ตรวจสอบรายชื่อ ปปง. (AMLO List) และบุคคลที่มีสถานะทางการเมือง (PEP)
4. หากพบเงื่อนไข Knockout ให้แจ้งเตือนปฏิเสธทันที และรายงานสรุปเป็นภาษาไทยพร้อมปกปิดเลขบัตรประชาชน (PII Masking)""",
            "selectedTools": {
                "tool": [
                    {"name": "verify_dbd_registry"},
                    {"name": "verify_dopa_identity"},
                    {"name": "screen_aml_sanctions"},
                    {"name": "googleSearch"}
                ]
            }
        }
    },
    {
        "id": "fraud_risk_agent",
        "displayName": "FraudRiskAgent (วิเคราะห์ทุจริต & ป.พ.30)",
        "llmAgentNode": {
            "description": "วิเคราะห์ความผิดปกติของรายได้ ตรวจสอบความสอดคล้องระหว่างยอดฝากธนาคารกับยอดขาย ป.พ.30 และประเมินประวัติเช็คคืน",
            "model": "gemini-1.5-pro",
            "instruction": """คุณคือ FraudRiskAgent (เจ้าหน้าที่ปัญญาประดิษฐ์วิเคราะห์ความเสี่ยงทุจริต)
หน้าที่:
1. ตรวจสอบส่วนต่างรายได้ผ่านเครื่องมือ MCP `analyze_revenue_anomaly` (bank_inflows_6m_thb, pp30_vat_revenue_6m_thb)
   - คำนวณ Variance % = |ยอดเงินเข้าธนาคาร - ยอดขาย ป.พ.30| / ยอดเงินเข้าธนาคาร * 100%
   - หากผลต่าง > 30% ให้จัดเป็น HIGH_ANOMALY (เสี่ยงตกแต่งบัญชี/เลี่ยงภาษี)
2. ตรวจสอบประวัติเช็คคืนและการใช้ O/D ผ่านเครื่องมือ MCP `evaluate_statement_tampering` (bounced_checks_count_6m, overdraft_utilization_pct)
   - หากมีเช็คคืน >= 3 ครั้ง ให้ระบุความเสี่ยงสภาพคล่องรุนแรง (Kite Flying)
3. สรุปคะแนนความเสี่ยงทุจริต (Fraud Score 0-100) และระดับความเสี่ยงเป็นภาษาไทย""",
            "selectedTools": {
                "tool": [
                    {"name": "analyze_revenue_anomaly"},
                    {"name": "evaluate_statement_tampering"},
                    {"name": "googleSearch"}
                ]
            }
        }
    },
    {
        "id": "scoring_engine_agent",
        "displayName": "ScoringEngineAgent (คำนวณ DSCR & เกรดสินเชื่อ)",
        "llmAgentNode": {
            "description": "คำนวณอัตราส่วนความสามารถในการชำระหนี้ (DSCR) และจัดเกรดชั้นคุณภาพลูกหนี้ (Risk Tier A, B, C, D) พร้อมประเมินวงเงินกู้สูงสุด",
            "model": "gemini-1.5-pro",
            "instruction": """คุณคือ ScoringEngineAgent (เจ้าหน้าที่ปัญญาประดิษฐ์คำนวณคะแนนสินเชื่อ)
หน้าที่:
1. คำนวณอัตราส่วนความสามารถชำระหนี้ผ่านเครื่องมือ MCP `calculate_dscr` (monthly_noi_thb, monthly_debt_service_thb)
   - DSCR = NOI / ภาระหนี้รายเดือน (เกณฑ์มาตรฐาน >= 1.25x)
2. จัดชั้นคุณภาพลูกหนี้ผ่านเครื่องมือ MCP `score_credit_risk` (monthly_noi_thb, monthly_debt_service_thb, monthly_turnover_thb, bounced_checks_count_6m)
   - Tier A (Prime): DSCR >= 1.50x, เงินหมุนเวียน >= 2 ล้านบาท, เช็คคืน 0 ครั้ง
   - Tier B (Standard): DSCR >= 1.25x, เงินหมุนเวียน >= 5 แสนบาท, เช็คคืน 0 ครั้ง
   - Tier C (Borderline): DSCR 1.10x - 1.24x หรือมีเช็คคืน 1 ครั้ง
   - Tier D (High Risk): DSCR < 1.10x หรือมีเช็คคืน >= 2 ครั้ง
3. รายงานอัตราส่วน DSCR, วงเงินกู้สูงสุดที่แนะนำ และอัตราดอกเบี้ยอ้างอิงเป็นภาษาไทย""",
            "selectedTools": {
                "tool": [
                    {"name": "calculate_dscr"},
                    {"name": "score_credit_risk"},
                    {"name": "googleSearch"}
                ]
            }
        }
    },
    {
        "id": "decision_agent",
        "displayName": "DecisionAgent (ตัดสินผลการอนุมัติ)",
        "llmAgentNode": {
            "description": "ประเมินเกณฑ์นโยบายสินเชื่อและตัดสินผลการอนุมัติ (อนุมัติเบื้องต้น, ส่งต่อคณะกรรมการ, ปฏิเสธสินเชื่อ) พร้อมกำหนดเงื่อนไขสินเชื่อ",
            "model": "gemini-1.5-pro",
            "instruction": """คุณคือ DecisionAgent (เจ้าหน้าที่ปัญญาประดิษฐ์ตัดสินผลการอนุมัติสินเชื่อ)
หน้าที่:
1. ประมวลผลผลการตัดสินใจผ่านเครื่องมือ MCP `evaluate_underwriting_decision`
2. กำหนดผลการพิจารณาตามเกณฑ์:
   - 'PRE_APPROVED (อนุมัติเบื้องต้นแบบเร่งด่วน)' สำหรับ Tier A/B: กำหนดวงเงินกู้ อัตราดอกเบี้ย (MLR - 1.25% ถึง MLR - 0.75%) และระยะเวลาผ่อนชำระ (48-60 เดือน)
   - 'REFERRED_TO_UW (ส่งต่อคณะกรรมการสินเชื่อ)' สำหรับ Tier C หรือมีประวัติคดีความ: กำหนดเงื่อนไขหลักประกันเพิ่มเติม (จำนองอสังหาริมทรัพย์ >= 120% และกรรมการค้ำประกันส่วนบุคคล)
   - 'REJECTED (ปฏิเสธสินเชื่อ)' สำหรับเคสติด Knockout, ทุนติดลบ หรือ Tier D: ระบุเหตุผลการปฏิเสธอย่างชัดเจน
3. สรุปผลการตัดสินใจเป็นภาษาไทย พร้อมแถบสถานะที่ชัดเจน""",
            "selectedTools": {
                "tool": [
                    {"name": "evaluate_underwriting_decision"},
                    {"name": "googleSearch"}
                ]
            }
        }
    },
    {
        "id": "notification_agent",
        "displayName": "NotificationAgent (จัดทำหนังสือทางการ)",
        "llmAgentNode": {
            "description": "จัดทำและออกหนังสือแจ้งผลการพิจารณาอนุมัติสินเชื่อเบื้องต้น, หนังสือขอเอกสารเพิ่มเติมพร้อมลิงก์อัปโหลดปลอดภัย และบันทึกข้อความเสนอคณะกรรมการสินเชื่อ",
            "model": "gemini-1.5-pro",
            "instruction": """คุณคือ NotificationAgent (เจ้าหน้าที่ปัญญาประดิษฐ์จัดทำเอกสารและหนังสือทางการ)
หน้าที่:
1. จัดทำหนังสือแจ้งผลอนุมัติเบื้องต้นผ่านเครื่องมือ MCP `generate_preapproval_letter`
2. จัดทำหนังสือขอเอกสารเพิ่มเติมพร้อมลิงก์อัปโหลดปลอดภัยผ่านเครื่องมือ MCP `generate_missing_doc_notice`
3. จัดทำบันทึกข้อความเสนอคณะกรรมการสินเชื่อผ่านเครื่องมือ MCP `generate_underwriter_memo`
4. จัดรูปแบบหนังสือและบันทึกข้อความในรูปแบบ Markdown ภาษาไทยระดับทางการที่สวยงามและถูกต้องตามระเบียบธนาคาร""",
            "selectedTools": {
                "tool": [
                    {"name": "generate_preapproval_letter"},
                    {"name": "generate_missing_doc_notice"},
                    {"name": "generate_underwriter_memo"},
                    {"name": "googleSearch"}
                ]
            }
        }
    }
]

# Thai Starter Prompts
thai_starter_prompts = [
    {"text": "กรุณาสแกนกล่องข้อความ Gmail เพื่อค้นหาใบสมัครสินเชื่อใหม่ที่มีหัวข้อ \"[underwriting]\""},
    {"text": "ช่วยดำเนินการพิจารณาสินเชื่อฉบับสมบูรณ์สำหรับ บริษัท สยาม เทค โลจิสติกส์ จำกัด (APP-2026-001)"},
    {"text": "ตรวจสอบและประเมินเคสส่งต่อคณะกรรมการสินเชื่อของ บริษัท บางกอก เฟรช รีเทล จำกัด (APP-2026-002)"},
    {"text": "ประเมินความเสี่ยงและตรวจสอบคุณสมบัติสินเชื่อของ บริษัท เอเปกซ์ โกลบอล เทรดดิ้ง จำกัด (APP-2026-003)"},
    {"text": "ตรวจสอบเอกสารการสมัครสินเชื่อของ บริษัท เชียงใหม่ คราฟท์ บริวเวอรี่ จำกัด (APP-2026-004)"}
]

low_code_def = {
    "nodes": sub_nodes,
    "rootAgentId": "root_agent",
    "deployedNodes": sub_nodes,
    "deployedRootAgentId": "root_agent",
    "draftDisplayName": "ระบบผู้ช่วยพิจารณาสินเชื่อธุรกิจ (Underwriting Multi-Agent Orchestrator)",
    "draftDescription": "ระบบปัญญาประดิษฐ์พิจารณาสินเชื่อธุรกิจและ SME อัตโนมัติ สแกน Gmail [underwriting], ตรวจสอบ DBD/DOPA/AMLO, คำนวณ DSCR, วิเคราะห์ทุจริต ป.พ.30 และออกหนังสือแจ้งผล ตอบภาษาไทย 100%",
    "draftStarterPrompts": thai_starter_prompts
}

agent_payload = {
    "displayName": "ระบบผู้ช่วยพิจารณาสินเชื่อธุรกิจ (Underwriting Multi-Agent Orchestrator)",
    "description": (
        "ระบบปัญญาประดิษฐ์พิจารณาสินเชื่อธุรกิจและ SME อัตโนมัติ "
        "สแกน Gmail [underwriting], ตรวจสอบ DBD/DOPA/AMLO, คำนวณ DSCR, "
        "วิเคราะห์ทุจริต ป.พ.30 และออกหนังสือแจ้งผล ตอบภาษาไทย 100%"
    ),
    "lowCodeAgentDefinition": low_code_def,
    "starterPrompts": thai_starter_prompts,
    "sharingConfig": {
        "scope": "ALL_USERS"
    }
}

# Update the agent via PATCH
patch_url = f"https://discoveryengine.googleapis.com/v1alpha/{parent}/agents/{agent_id}?updateMask=displayName,description,lowCodeAgentDefinition,starterPrompts,sharingConfig"

req = urllib.request.Request(
    patch_url,
    data=json.dumps(agent_payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": "hong-ai-demo",
    },
    method="PATCH",
)

try:
    with urllib.request.urlopen(req) as response:
        res_body = response.read().decode("utf-8")
        print("✅ SUCCESS! Agent patched with Thai prompts and MCP tools:")
        print(json.dumps(json.loads(res_body), indent=2)[:300] + "...")
except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8")
    print(f"❌ HTTPError {e.code}: {e.reason}")
    print(err_body)
    exit(1)

# Deploy the updated low code agent
deploy_url = f"https://discoveryengine.googleapis.com/v1alpha/{parent}/agents/{agent_id}:deployLowCode"
deploy_req = urllib.request.Request(
    deploy_url,
    data=json.dumps({"deployMode": "DEPLOY"}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": "hong-ai-demo",
    },
    method="POST"
)

try:
    with urllib.request.urlopen(deploy_req) as deploy_res:
        deploy_body = deploy_res.read().decode("utf-8")
        print("\n🚀 SUCCESS! Agent successfully deployed into ge-demo1:")
        print(deploy_body)
except urllib.error.HTTPError as e:
    print(f"❌ Deploy HTTPError {e.code}: {e.reason}")
    print(e.read().decode("utf-8"))
    exit(1)
