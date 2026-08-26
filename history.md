# 📜 Project Interaction History & User Prompts Timeline

> **Project**: Autonomous SME Loan Underwriting with Gemini Enterprise & MCP  
> **Total User Directives Recorded**: 33  
> **Chronological Record**: From initial project workspace setup to final deployment & GitHub publishing.  

---

## ⏱️ Chronological Prompt Log

### Prompt #01 — `2026-08-24T03:32:47Z`
```text
create new workspace , just for the project hong-ai-demo, i'll use it to deploy live demo solution in this project
```

### Prompt #02 — `2026-08-24T06:24:40Z`
```text
build demo of agent . use agent designer v2 in gemini enterprise appid : ge_demo

build all the surrounding mock to demonstrate the complete use cases . so write clear and concise tools ( python) for external api.  then package it to run on cloud run ( local terminal docker build and deploy) 

validate all the tools .
then build the main agent using agent designer v2.

here's the overall instruction. you can enrich it to be more comprehensive
# AGENT ROLE & SCOPE
You are the Underwriting Multi-Agent Orchestrator designed for enterprise-grade automated credit and business underwriting within the Gemini Enterprise platform. Your objective is to manage ingestion, document verification, registry enrichment, fraud scoring, credit policy evaluation, pre-approval decisioning, and customer communication.

---

## 1. INGESTION & SUBMISSION HANDLING
Accept application triggers from three ingestion vectors:
- Direct Document Ingestion (PDF, Scanned Images)
- GE Frontline (GE FL) Internal Staff Submissions
- External Frontend Customer Portal Submissions

When a submission is received:
1. Generate a unique `application_id` and timestamp.
2. Initialize the Underwriting Case State Machine.

---

## 2. SPECIALIZED SUB-AGENT WORKFLOW

### Step 1: Document Check (`DocIntakeAgent`)
- Verify presence of all required documents based on entity type (Individual vs. Corporate):
  - Corporate: DBD Certificate (Affidavit <= 3 months), Form BorOrJor.5, 6-Month Bank Statements, Financial Statements, Director National IDs.
  - Individual: National ID Card, Proof of Income / Payslips, 6-Month Bank Statements.
- Check legibility, resolution, and expiration dates.
- Output: `DOCS_VALIDATED` or `DOCS_MISSING [list of missing items]`.

### Step 2: Document Extraction (`DocParserAgent`)
- Parse semi-structured and unstructured documents into strict JSON schema:
  - Financials: Monthly average balance, total inflow/outflow, overdraft utilization, bounced checks.
  - Corporate Data: Registration number, registered capital, authorized signatories, authorized signing conditions.
- Format all numeric values to standard currency (THB) float values.

### Step 3: Verification & External Enrichment (`VerificationAgent`)
- Execute mock tool integrations:
  - `verify_dbd_registry`: Check corporate existence, active status, registered capital, and authorized directors.
  - `verify_dopa_identity`: Validate national ID validity and status of authorized directors.
  - `screen_aml_sanctions`: Run entity and individuals against mock AMLO, UN, and PEP sanction lists.
- Output: Structured verification score and validation flags (`DBD_ACTIVE`, `DOPA_VALID`, `AML_CLEAR`).

### Step 4: Fraud & Risk Signal Detection (`FraudRiskAgent`)
- Analyze extracted financials for anomaly markers:
  - High velocity / round-trip fund transfers.
  - High revenue concentration on single counterparties.
  - Non-operating revenue inflation.
- Flag behavioral anomalies: repeated submissions with mismatched company IDs.
- Output: `FRAUD_SCORE` (0-100) and risk tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

### Step 5: Underwriting Rule Engine (`ScoringEngineAgent`)
- Compute quantitative ratios:
  - Debt Service Coverage Ratio (DSCR): $\text{DSCR} \ge 1.25$ required for baseline approval.
  - Inflow to Installment Ratio: Average monthly inflow must be $\ge 3\times$ requested monthly installment.
  - Bounced Check Rule: Maximum 0 bounced checks within 6 months.
- Assign Credit Grade (A, B, C, D) based on weighted score.

### Step 6: Final Pre-Approval Decision (`DecisionAgent`)
- Formulate decision matrix:
  - `PRE_APPROVED`: Passed verification, fraud score < 25, DSCR >= 1.25, grade A/B.
  - `REFERRED_TO_UW`: Edge case, medium fraud (25-50), or DSCR between 1.0 and 1.25, or high credit limit request (> 20M THB). Requires human underwriter sign-off.
  - `DOCS_INCOMPLETE`: Missing critical documentation.
  - `CONDITIONALLY_APPROVED`: Minor covenant requirements (e.g., additional guarantor or collateral requirement).
  - `DECLINED`: Fraud score >= 50, AML hit, DOPA invalid, DSCR < 1.0, or severe credit impairment.

---

## 3. NOTIFICATION & AUDIT DISPATCH
Generate outbound notifications and audit trails via `NotificationAgent`:
- Customer Notification: Send formal Thai/English pre-approval notification or missing document request with secure upload token.
- Underwriter Memo: Produce structured underwriting decision memorandum.
- Core Banking System (CBS) Mock: Stage approved facility limits into core banking ledger.

build architecture diagram of the agent during grill me.

/grill-me
```

### Prompt #03 — `2026-08-24T06:29:00Z`
```text
customer( underwriter) will upload everything through GE App. trigger -> scan email for subject "[underwriting] " and get the attachment from gmail to feed the agent system.
```

### Prompt #04 — `2026-08-24T06:59:10Z`
```text
create overall architecture and spec.md
```

### Prompt #05 — `2026-08-24T07:15:06Z`
```text
look ok . setup agent in agent designer v2 for me  use ge-demo1
```

### Prompt #06 — `2026-08-24T07:22:00Z`
```text
what's the agent name ?
```

### Prompt #07 — `2026-08-24T07:23:47Z`
```text
have you register in ge-demo1 ?
```

### Prompt #08 — `2026-08-24T07:27:40Z`
```text
i can't see it in ge-demo1 or even in agent platform console.
```

### Prompt #09 — `2026-08-24T07:52:00Z`
```text
which agent that I need to add gmail connector ?
```

### Prompt #10 — `2026-08-24T07:54:30Z`
```text
i'm using admin@pheeraphong.altostrat.com and it don't have gmail, how can i have gmail, can i use pheeraphong@demospace.altostrat.com ?
```

### Prompt #11 — `2026-08-24T07:58:19Z`
```text
implement mock gmail scanner 1st. i'll think about gmail connector later.
```

### Prompt #12 — `2026-08-24T08:00:24Z`
```text
think about v2 microservices, seperate all the api backend to each cloud run instance , then register it to agentplatform mcp server. 
i want to use it as utility.
```

### Prompt #13 — `2026-08-24T08:07:35Z`
```text
do it.
```

### Prompt #14 — `2026-08-24T08:30:40Z`
```text
/goal 
1. upgrade the agent in agent designerv2 to use tools via  mcp server directly. 
2. update agent prompt , i want all answer in Thai languge.
```

### Prompt #15 — `2026-08-24T08:34:40Z`
```text
i don't see any mcp server in agent registry.
```

### Prompt #16 — `2026-08-24T08:35:39Z`
```text
upgrade all agent node to use gemini 3.7 flash.
```

### Prompt #17 — `2026-08-24T09:10:18Z`
```text
i saw a lot of mcp server created . great.
next -> register it in the ge-demo1 , and add it to each of the agent&subagent.
```

### Prompt #18 — `2026-08-24T09:12:46Z`
```text
to be clear , add datastore -> specify mcp server that you created. create nessary o-auth if required. 
so think about agent gateway in agent platform implement it.
```

### Prompt #19 — `2026-08-24T09:21:49Z`
```text
you just register existing mcp tool via "add datastore" in GE.
```

### Prompt #20 — `2026-08-25T04:00:18Z`
```text
re-evaluate again, i don't see it in my no-code agent
```

### Prompt #21 — `2026-08-25T14:53:43Z`
```text
test all the mcp server. make sure agent can use it .
```

### Prompt #22 — `2026-08-25T15:09:43Z`
```text
tested and it all went well in demo , 
next is conclude everything , create final presentation of the usecases ( can be html ) , architecture.md , setup guide, sample prompt .  package it into reusable asset that my peer CE or my customer can take it and deploy in their gcp project.
```

### Prompt #23 — `2026-08-25T15:18:19Z`
```text
create readme and push to https://github.com/pheeraphongaj
```

### Prompt #24 — `2026-08-25T15:22:30Z`
```text
created. push it for me.
```

### Prompt #25 — `2026-08-25T15:27:41Z`
```text
pheeraphong@pheeraphong:~/gemini-enterprise-mcp-underwriting$ git push -u origin main
Username for 'https://github.com': pheeraphongaj
Password for 'https://pheeraphongaj@github.com': 
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed for 'https://github.com/pheeraphongaj/gemini-enterprise-mcp-underwriting.git/'
pheeraphong@pheeraphong:~/gemini-enterprise-mcp-underwriting$
```

### Prompt #26 — `2026-08-25T15:28:10Z`
```text
here's my PAT. use it in cloudtop ghp_[REDACTED_FOR_SECURITY]
```

### Prompt #27 — `2026-08-25T15:29:34Z`
```text
scan this repo and make sure there's no confidential data leak ?
```

### Prompt #28 — `2026-08-25T15:31:03Z`
```text
i think you should render html presentation in readme , can you ?
```

### Prompt #29 — `2026-08-25T15:33:26Z`
```text
@[/usr/local/google/home/pheeraphong/gemini-enterprise-mcp-underwriting/README.md] this look better but failed to launch https://htmlpreview.github.io/?https://github.com/pheeraphongaj/gemini-enterprise-mcp-underwriting/blob/main/underwriting_solution_presentation.html
```

### Prompt #30 — `2026-08-25T15:40:48Z`
```text
switch branchpy'w' หาไม่เจอ
```

### Prompt #31 — `2026-08-25T15:43:26Z`
```text
ไม่ได้ใช้ public repo เพราะมันติด link cloud run เต็มเลย เลย deploy to branchไม่ได้
```

### Prompt #32 — `2026-08-25T15:49:00Z`
```text
มันจะรู้ได้ไงว่า กด html แล้วได้ render
```

### Prompt #33 — `2026-08-26T02:50:23Z`
```text
record all my prompt from the beginning in the history.md
```
