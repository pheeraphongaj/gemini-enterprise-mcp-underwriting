# 🚀 Setup & Replication Guide: Autonomous Underwriting Platform

This guide provides step-by-step instructions for Google Cloud Customer Engineers (CEs) and enterprise customers to deploy and replicate the entire **Autonomous SME Underwriting Platform** in any GCP project in **~10 minutes**.

---

## 📋 Prerequisites & IAM Requirements

### 1. GCP Project & User Permissions
Ensure you have the following IAM roles on your target project:
* `roles/editor` or `roles/owner`
* `roles/discoveryengine.admin`
* `roles/run.admin`
* `roles/orgpolicy.policyAdmin` (or Project-level Org Policy override permissions)

### 2. Required GCP APIs
Enable the necessary services with `gcloud`:
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  discoveryengine.googleapis.com \
  iam.googleapis.com
```

---

## 🛠️ Step 1: Configure Organization Policy (MCP Connector)

Gemini Enterprise blocks custom MCP server connectors by default. You must disable this constraint:

```bash
cat << 'EOF' > /tmp/disable_mcp_policy.yaml
name: projects/YOUR_PROJECT_ID/policies/discoveryengine.managed.disableCustomMcpServerConnector
spec:
  rules:
  - enforce: false
EOF

gcloud org-policies set-policy /tmp/disable_mcp_policy.yaml --project=YOUR_PROJECT_ID
```

*(Note: If you have Organization Administrator access, you can also set `enforce: false` at the Organization level).*

---

## 🐳 Step 2: Deploy All 7 Cloud Run MCP Microservices

Run the automated deployment script located in `v2_microservices/`:

```bash
cd v2_microservices
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="asia-southeast1" # e.g. asia-southeast1 (Singapore) or us-central1

chmod +x deploy_v2_microservices.sh
./deploy_v2_microservices.sh
```

This deploys 7 serverless microservices:
1. `underwriting-gmail-mcp`
2. `underwriting-doc-mcp`
3. `underwriting-registry-mcp`
4. `underwriting-fraud-mcp`
5. `underwriting-scoring-mcp`
6. `underwriting-decision-mcp`
7. `underwriting-notification-mcp`

Verify all services with the test harness:
```bash
python3 test_all_mcp_servers.py
```

---

## 📦 Step 3: Register MCP Data Stores in Gemini Enterprise

Execute `setup_all_7_mcp_datastores.py` to create the 7 Data Connectors and attach them to your Gemini Enterprise Engine (`ge-demo1`):

```bash
python3 setup_all_7_mcp_datastores.py
```

This script automatically:
* Calls `SetUpDataConnector` with `dataSource: "custom_mcp"` and `connectorModes: ["FEDERATED", "ACTIONS"]`.
* Provisions 7 corresponding DataStores under `collections/default_collection/dataStores/`.
* Patches your Engine (`ge-demo1`) to include all 7 Data Store IDs in `engine.dataStoreIds`.
* Sets human-readable display names for each DataStore in the Google Cloud Console.

---

## 🧠 Step 4: Import & Deploy Multi-Agent Orchestrator

Deploy the 8-node multi-agent orchestrator powered by **Gemini 3.7 Flash** with 100% Thai prompt instructions:

```bash
python3 update_agent_designer_v2_mcp_thai.py
```

This binds all 7 MCP DataStores to both top-level agent specs and specialized sub-agent nodes:
* `root_agent` ➔ Underwriting Orchestrator (`gemini-3.7-flash`)
* `doc_intake_agent` ➔ Gmail Scanner & Attachment Handler
* `doc_parser_agent` ➔ Checklist & Financial Document Parser
* `verification_agent` ➔ DBD Registry, DOPA ID, and AML Screening
* `fraud_risk_agent` ➔ Revenue Anomaly & Statement Tampering
* `scoring_engine_agent` ➔ DSCR & Credit Scoring Engine
* `decision_agent` ➔ Fast-Track Decision Engine
* `notification_agent` ➔ Pre-Approval & Memo Generator

---

## 🧪 Step 5: End-to-End Verification

Run the live agent stream assist test to verify end-to-end multi-agent execution:

```bash
python3 test_agent_stream_assist.py
```

Expected output:
* Streaming multi-agent thoughts and tool executions.
* Final loan underwriting decision memorandum generated in Thai.

---

## 🔧 Troubleshooting Playbook

| Symptom | Root Cause | Solution |
| :--- | :--- | :--- |
| **HTTP 400: Custom MCP server connector is disabled by policy** | Org policy constraint active | Run Step 1 to set `enforce: false` on `discoveryengine.managed.disableCustomMcpServerConnector`. |
| **Data Stores not visible in Agent Designer UI** | Missing from `engine.dataStoreIds` | Ensure `ge-demo1.dataStoreIds` includes all 7 MCP data stores (handled by `setup_all_7_mcp_datastores.py`). |
| **Tool call returns 404** | Cloud Run service URL mismatch | Verify service URLs in `v2_microservices/mcp_catalog.json` and ensure services allow unauthenticated or appropriate IAM invoker access. |
| **Agent responds in English** | Prompt template override | Run `update_agent_designer_v2_mcp_thai.py` to re-apply Thai instructions and trigger `:deployLowCode`. |
