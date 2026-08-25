# Underwriting Multi-Agent Live Demo Runbook

Use this runbook to demonstrate the **Underwriting Multi-Agent Orchestrator** in **Gemini Enterprise (`ge_demo`)**.

---

## 🎬 Demo Scenario 1: Gmail Trigger & Prime Pre-Approval (Fast Track)

### 💬 User Prompt in GE App
```text
Please scan our Gmail inbox for any incoming loan applications marked with "[underwriting]". If you find any new submissions, please run full underwriting on application for Siam Tech Logistics Co., Ltd.
```

### 🤖 Expected Agent Behavior & Tool Sequence
1. Calls `scanGmailInbox(subject_filter="[underwriting]")`
   - Finds email from `somchai@siamtechlogistics.co.th` with subject `[underwriting] Credit Facility Application - Siam Tech Logistics Co., Ltd.` (Ref: `APP-2026-001`).
   - Identifies 5 attachments: DBD Affidavit, BorOrJor.5, 6M SCB Statement, Audited Financials, Director ID.
2. Calls `validateDocuments(application_id="APP-2026-001")` -> `DOCS_VALIDATED`
3. Calls `parseDocuments(application_id="APP-2026-001")` -> Turnover 3.5M THB/mo, Revenue 42M THB.
4. Calls `verifyRegistries(application_id="APP-2026-001")` -> DBD `ACTIVE`, DOPA IDs `VALID`, AML hits `0`.
5. Calls `analyzeFraud(application_id="APP-2026-001")` -> Risk `LOW`, Variance `< 1%`.
6. Calls `scoreCredit(application_id="APP-2026-001")` -> `TIER_A`, DSCR `2.89x`.
7. Calls `makeDecision(application_id="APP-2026-001")` -> `PRE_APPROVED` (THB 10,000,000 @ 4.75% p.a., 60 Months).
8. Calls `sendNotification(application_id="APP-2026-001")` -> Pre-Approval Letter dispatched to `somchai@siamtechlogistics.co.th`.

---

## 🎬 Demo Scenario 2: Credit Policy Referral (Underwriter Escalation)

### 💬 User Prompt in GE App
```text
Please process the underwriting case for Bangkok Fresh Retail Co., Ltd. (Application ID: APP-2026-002).
```

### 🤖 Expected Agent Behavior & Tool Sequence
1. Calls `validateDocuments(application_id="APP-2026-002")` -> `DOCS_VALIDATED`
2. Calls `parseDocuments(application_id="APP-2026-002")` -> Turnover 850K THB/mo, Debt Service 80K THB/mo.
3. Calls `verifyRegistries(application_id="APP-2026-002")` -> DBD `ACTIVE`, notes pending commercial dispute (THB 150,000).
4. Calls `scoreCredit(application_id="APP-2026-002")` -> `TIER_C`, DSCR `1.15x` (Breaches standard 1.25x policy).
5. Calls `makeDecision(application_id="APP-2026-002")` -> `REFERRED_TO_UW` (Recommends THB 3,000,000 limit @ 6.25% p.a. with 120% property mortgage).
6. Calls `sendNotification(application_id="APP-2026-002")` -> Generates Internal Credit Committee Referral Memo to `CREDIT_COMMITTEE_ESCALATION_TIER_2`.

---

## 🎬 Demo Scenario 3: AML & Inactive Registry Knockout (Instant Rejection)

### 💬 User Prompt in GE App
```text
Run underwriting evaluation on Apex Global Trading Co., Ltd. (Application ID: APP-2026-003).
```

### 🤖 Expected Agent Behavior & Tool Sequence
1. Calls `validateDocuments(application_id="APP-2026-003")` -> `DOCS_VALIDATED`
2. Calls `verifyRegistries(application_id="APP-2026-003")` ->
   - ❌ DBD Status: `DISSOLVED` (Non-operational)
   - ❌ Negative Net Equity on balance sheet
   - ❌ Director National ID `EXPIRED`
   - ❌ AML Watchlist Critical Match: AMLO List 4 Trade Fraud Flag.
3. Calls `analyzeFraud(application_id="APP-2026-003")` -> `HIGH_ANOMALY` (55% variance between Bank and Tax filings, 4 bounced checks).
4. Calls `makeDecision(application_id="APP-2026-003")` -> `REJECTED`
5. Calls `sendNotification(application_id="APP-2026-003")` -> Dispatches Adverse Action Notice detailing compliance knockouts.

---

## 🎬 Demo Scenario 4: Missing Mandatory Documents

### 💬 User Prompt in GE App
```text
Evaluate the loan application for Chiang Mai Craft Brewery Co., Ltd. (Application ID: APP-2026-004).
```

### 🤖 Expected Agent Behavior & Tool Sequence
1. Calls `validateDocuments(application_id="APP-2026-004")` -> `DOCS_MISSING`
   - Missing: `BOR_OR_JOR_5` (Shareholder List)
   - Missing: `BANK_STATEMENT_6M` (6-Month Bank Statements)
2. Halts pipeline and calls `sendNotification(application_id="APP-2026-004")` -> Generates Missing Documents Notice with direct upload portal link: `https://portal.enterprise.gemini/upload?app_id=APP-2026-004`.

---

## 🎬 Demo Scenario 5: Direct GE App Document Ingestion

### 💬 User Prompt in GE App
```text
I am uploading a new commercial loan application for "Horizon Cloud Services Co., Ltd." (DBD: 0105565099887). We are requesting THB 8,000,000 for server infrastructure. Uploaded documents: DBD Certificate, BorOrJor.5, 6-Month Bank Statements, Financial Statements, and Director National ID. Please initiate underwriting.
```

### 🤖 Expected Agent Behavior
1. Calls `ingestGEAppUpload` to register the new case and generate an `application_id`.
2. Automatically triggers `validateDocuments` and runs through the complete 7-stage workflow.
