# 🏦 Gemini Enterprise Autonomous SME Underwriting Platform

> **Google Cloud Customer Engineering Asset Package**  
> An enterprise-grade, turn-key demonstration and replication suite showcasing **Gemini Enterprise (Agent Designer v2)**, **Gemini 3.7 Flash**, and **Model Context Protocol (MCP)** microservices on **Google Cloud Run**.

---

## 📂 Deliverables & Asset Index

| Asset | File / Path | Description |
| :--- | :--- | :--- |
| 📊 **Interactive HTML Presentation & Live Simulator** | [`underwriting_solution_presentation.html`](file:///google/src/cloud/pheeraphong/hong-ai-demo/google3/underwriting_demo/underwriting_solution_presentation.html) | Executive & technical slide deck with a live interactive underwriting flow simulator. |
| 🏛️ **Technical Architecture Blueprint** | [`ARCHITECTURE.md`](file:///google/src/cloud/pheeraphong/hong-ai-demo/google3/underwriting_demo/ARCHITECTURE.md) | In-depth topology, multi-agent hierarchy, sequence diagrams, and security architecture. |
| 🚀 **Step-by-Step Setup & Deployment Guide** | [`SETUP_GUIDE.md`](file:///google/src/cloud/pheeraphong/hong-ai-demo/google3/underwriting_demo/SETUP_GUIDE.md) | Complete replication guide to deploy into any GCP project in ~10 minutes. |
| 💬 **Sample Prompts & Test Scenarios** | [`SAMPLE_PROMPTS.md`](file:///google/src/cloud/pheeraphong/hong-ai-demo/google3/underwriting_demo/SAMPLE_PROMPTS.md) | Ready-to-use demo prompts in Thai with expected tool executions and sample outputs. |
| ⚡ **One-Click Deploy Script** | [`deploy_all.py`](file:///google/src/cloud/pheeraphong/hong-ai-demo/google3/underwriting_demo/deploy_all.py) | Automated orchestration script for end-to-end deployment. |
| 📄 **Exported Agent Definition** | [`export_agent_definition.json`](file:///google/src/cloud/pheeraphong/hong-ai-demo/google3/underwriting_demo/export_agent_definition.json) | Declarative JSON configuration of the 8-node multi-agent orchestrator. |
| 🧪 **MCP Microservices Test Harness** | [`test_all_mcp_servers.py`](file:///google/src/cloud/pheeraphong/hong-ai-demo/google3/underwriting_demo/test_all_mcp_servers.py) | Unit test suite testing all 15 tools across 7 Cloud Run microservices. |

---

## 🌟 Key Capabilities Demonstrated

1. **Autonomous Multi-Agent Orchestration**: Root orchestrator delegates sub-tasks across 7 domain agents.
2. **Standardized Protocol (MCP)**: All banking tools interact via Model Context Protocol over HTTPS.
3. **Multi-Step Forensic Audit**: Automatically checks DBD corporate registry, DOPA ID, AMLO sanctions, and calculates DSCR debt service coverage.
4. **Fraud & Tampering Defense**: Uncovers financial statement tampering and revenue inflation.
5. **100% Thai Language Native**: System prompts, reasoning outputs, and generated customer documents in professional Thai banking language.
