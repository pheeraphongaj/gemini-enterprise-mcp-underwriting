# 💬 Sample Prompts & Customer Demo Scenarios

This reference document contains ready-to-use demo prompts and expected multi-agent tool execution chains for customer presentations and peer CE testing.

---

## 🟢 Scenario 1: Clean Fast-Track SME Loan Pre-Approval

### 1. User Prompt (Thai)
```text
ช่วยตรวจสอบและวิเคราะห์การขอสินเชื่อธุรกิจ SME ให้กับ:
- ชื่อบริษัท: บริษัท สยาม ซอฟต์แวร์ โซลูชั่น จำกัด
- เลขทะเบียนนิติบุคคล (DBD): 0105558000001
- วงเงินที่ขอกู้: 10,000,000 บาท
- ผู้มีอำนาจลงนาม: นายสมชาย ใจดี (บัตรประชาชน: 1100500123456)
- เอกสารที่แนบมา: สำเนาบัตรประชาชน, หนังสือรับรองบริษัท DBD, สเตทเมนต์ย้อนหลัง 6 เดือน

กรุณาเรียกใช้เครื่องมือ MCP เพื่อตรวจสอบสถานะ DBD, คัดกรองรายชื่อ AML, วิเคราะห์ความผิดปกติของสเตทเมนต์, คำนวณ DSCR, ประเมินคะแนนเครดิต และออกหนังสือแจ้งผลการอนุมัติสินเชื่อเบื้องต้น (Pre-Approval Letter) เป็นภาษาไทย
```

### 2. Multi-Agent Tool Call Chain
1. `validate_document_checklist` ➔ Checklist Status: `COMPLETE`
2. `verify_dbd_registry` ➔ Status: `ACTIVE` (Capital: 5,000,000 THB, 5 years operation)
3. `verify_dopa_identity` ➔ Status: `VALID`
4. `screen_aml_sanctions` ➔ Risk: `CLEAR` (0 hits)
5. `analyze_revenue_anomaly` & `evaluate_statement_tampering` ➔ Status: `NORMAL` (0 anomalies)
6. `calculate_dscr` ➔ DSCR: `1.73` (Benchmark ≥ 1.25)
7. `score_credit_risk` ➔ Rating: `Grade A`
8. `evaluate_underwriting_decision` ➔ Decision: `PRE_APPROVED`
9. `generate_preapproval_letter` ➔ Produces Pre-Approval Letter in Thai.

---

## 🟡 Scenario 2: Missing Financial Statements (Pending Documents)

### 1. User Prompt (Thai)
```text
มีลูกค้ายื่นขอสินเชื่อธุรกิจเข้ามาดังนี้:
- ชื่อบริษัท: บริษัท บางกอก โลจิสติกส์ เซอร์วิสเซส จำกัด
- เลขนิติบุคคล: 0105558000002
- วงเงินที่ขอ: 5,000,000 บาท
- เอกสารที่ส่งมาในเบื้องต้น: หนังสือรับรองบริษัท, บัตรประชาชนกรรมการ, สเตทเมนต์ 3 เดือน

กรุณาตรวจสอบความครบถ้วนของเอกสารตามนโยบายสินเชื่อ และหากขาดเอกสารใด ให้สร้างหนังสือแจ้งขอเอกสารเพิ่มเติม (Missing Document Notice) พร้อมลิงก์อัปโหลดสำหรับลูกค้า
```

### 2. Multi-Agent Tool Call Chain
1. `validate_document_checklist` ➔ Identified missing items: `[งบการเงินผู้สอบบัญชีปีล่าสุด, สเตทเมนต์เดือนที่ 4-6]`
2. `generate_missing_doc_notice` ➔ Formats official request letter with secure upload link and OTP instructions in Thai.

---

## 🔴 Scenario 3: Bank Statement Tampering Detection (Fraud Alert)

### 1. User Prompt (Thai)
```text
กรุณาทำ Forensic Audit สเตทเมนต์และข้อมูลรายได้ของ:
- ชื่อบริษัท: บริษัท ไทย เทรดดิ้ง พาร์ทเนอร์ จำกัด (0105558000003)
- วงเงินที่ขอกู้: 15,000,000 บาท

ช่วยตรวจสอบว่าพบความผิดปกติของกระแสเงินสดหรือการแก้ไขตัวเลขในเอกสารหรือไม่ พร้อมออกบันทึกข้อความปฏิเสธสินเชื่อหากพบความเสี่ยงทุจริต
```

### 2. Multi-Agent Tool Call Chain
1. `analyze_revenue_anomaly` ➔ Statistical anomaly detected in Month 3-5 inflows.
2. `evaluate_statement_tampering` ➔ Arithmetic mismatch between running daily balance and debit/credit sums.
3. `evaluate_underwriting_decision` ➔ Decision: `REJECTED_FRAUD`
4. `generate_underwriter_memo` ➔ Issues Fraud Alert & Risk Decline Memorandum.

---

## ⛔ Scenario 4: AML / Sanction Hard Block

### 1. User Prompt (Thai)
```text
ตรวจสอบสิทธิ์การขอสินเชื่อของ:
- ชื่อบริษัท: บริษัท โกลบอล อินเวสท์เมนท์ กรุ๊ป จำกัด (0105558000004)
- วงเงินที่ขอ: 25,000,000 บาท
- กรรมการผู้มีอำนาจ: นายวิชัย มั่งคั่ง

กรุณาคัดกรองรายชื่อตามกฎหมาย ปปง. (AML/CFT) และรายงานผลทันที
```

### 2. Multi-Agent Tool Call Chain
1. `screen_aml_sanctions` ➔ `aml_hit: true` (Matches Designated Persons List).
2. `evaluate_underwriting_decision` ➔ Decision: `HARD_BLOCK_AML`
3. `generate_underwriter_memo` ➔ Generates Compliance Block Memorandum.

---

## 📧 Scenario 5: Omnichannel Inbox Scan & Auto-Intake

### 1. User Prompt (Thai)
```text
ช่วยสแกนกล่องข้อความ Gmail ที่มีหัวข้อ [underwriting] เพื่อดึงใบสมัครขอสินเชื่อล่าสุด และเริ่มกระบวนการคัดกรองเบื้องต้นให้กับทุกเคสที่เข้ามา
```

### 2. Multi-Agent Tool Call Chain
1. `scan_gmail_inbox` ➔ Discovers 4 pending loan application emails.
2. `fetch_email_attachment` ➔ Extracts attached PDF files and metadata.
3. Iterates over applicant IDs and triggers validation pipeline.
