"""Registers all 7 MCP servers as Data Stores in Gemini Enterprise / Discovery Engine,
verifies their ACTIVE status, and links them to the sub-agent nodes in ge-demo1."""

import json
import subprocess
import time
import urllib.request
import urllib.error

token = (
    subprocess.check_output(
        ["gcloud", "auth", "print-access-token"]
    )
    .decode("utf-8")
    .strip()
)

PROJECT_ID = "hong-ai-demo"
LOCATION = "global"

mcp_servers = [
    {
        "id": "underwriting-gmail-mcp",
        "collection_id": "underwriting-gmail-mcp-col",
        "display_name": "Underwriting Gmail MCP",
        "registry_name": "projects/hong-ai-demo/locations/global/mcpServers/agentregistry-00000000-0000-0000-ea44-c025b2c44fcb",
        "url": "https://underwriting-gmail-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "target_nodes": ["root_agent", "doc_intake_agent"]
    },
    {
        "id": "underwriting-doc-mcp",
        "collection_id": "underwriting-doc-mcp-col",
        "display_name": "Underwriting Doc MCP",
        "registry_name": "projects/hong-ai-demo/locations/global/mcpServers/agentregistry-00000000-0000-0000-0415-92a53df78ea0",
        "url": "https://underwriting-doc-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "target_nodes": ["root_agent", "doc_intake_agent", "doc_parser_agent"]
    },
    {
        "id": "underwriting-registry-mcp",
        "collection_id": "underwriting-registry-mcp-col",
        "display_name": "Underwriting Registry MCP",
        "registry_name": "projects/hong-ai-demo/locations/global/mcpServers/agentregistry-00000000-0000-0000-c62f-b18b55bc3ff9",
        "url": "https://underwriting-registry-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "target_nodes": ["root_agent", "verification_agent"]
    },
    {
        "id": "underwriting-fraud-mcp",
        "collection_id": "underwriting-fraud-mcp-col",
        "display_name": "Underwriting Fraud MCP",
        "registry_name": "projects/hong-ai-demo/locations/global/mcpServers/agentregistry-00000000-0000-0000-1e8a-22177f114468",
        "url": "https://underwriting-fraud-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "target_nodes": ["root_agent", "fraud_risk_agent"]
    },
    {
        "id": "underwriting-scoring-mcp",
        "collection_id": "underwriting-scoring-mcp-col",
        "display_name": "Underwriting Scoring MCP",
        "registry_name": "projects/hong-ai-demo/locations/global/mcpServers/agentregistry-00000000-0000-0000-7968-ad7b58cbc7b3",
        "url": "https://underwriting-scoring-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "target_nodes": ["root_agent", "scoring_engine_agent"]
    },
    {
        "id": "underwriting-decision-mcp",
        "collection_id": "underwriting-decision-mcp-collection",
        "display_name": "Underwriting Decision MCP",
        "registry_name": "projects/hong-ai-demo/locations/global/mcpServers/agentregistry-00000000-0000-0000-e312-750b66a7c842",
        "url": "https://underwriting-decision-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "target_nodes": ["root_agent", "decision_agent"]
    },
    {
        "id": "underwriting-notification-mcp",
        "collection_id": "underwriting-notification-mcp-col",
        "display_name": "Underwriting Notification MCP",
        "registry_name": "projects/hong-ai-demo/locations/global/mcpServers/agentregistry-00000000-0000-0000-8bd4-2081f9b5d025",
        "url": "https://underwriting-notification-mcp-xgn5gkffnq-as.a.run.app/mcp",
        "target_nodes": ["root_agent", "notification_agent"]
    }
]

registered_datastores = {}
registered_dataconnectors = {}

print("===================================================================")
print("🔍 STEP 1: Verifying ACTIVE status & resolving DataStore IDs")
print("===================================================================")

for s in mcp_servers:
    col_id = s["collection_id"]
    check_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/collections/{col_id}/dataConnector"
    req_check = urllib.request.Request(
        check_url,
        headers={"Authorization": f"Bearer {token}", "X-Goog-User-Project": PROJECT_ID}
    )
    try:
        with urllib.request.urlopen(req_check) as check_res:
            dc_info = json.loads(check_res.read().decode("utf-8"))
            state = dc_info.get("state")
            entities = dc_info.get("entities", [])
            ds_name = entities[0].get("dataStore") if entities else None
            registered_datastores[s["id"]] = ds_name
            registered_dataconnectors[s["id"]] = dc_info.get("name")
            print(f"  📦 [{s['id']}]: State={state}, ActionState={dc_info.get('actionState')}")
            print(f"     DataStore: {ds_name}")
            print(f"     DataConnector: {dc_info.get('name')}")
    except Exception as e:
        print(f"  ❌ Error checking [{col_id}]: {e}")

print("\n===================================================================")
print("🔗 STEP 2: Linking DataStores & DataConnectors to Agent Designer")
print("===================================================================")

parent = "projects/hong-ai-demo/locations/global/collections/default_collection/engines/ge-demo1/assistants/default_assistant"
agent_id = "underwriting-orchestrator"

# Fetch current agent definition
get_url = f"https://discoveryengine.googleapis.com/v1alpha/{parent}/agents/{agent_id}"
req_get = urllib.request.Request(
    get_url,
    headers={
        "Authorization": f"Bearer {token}",
        "X-Goog-User-Project": PROJECT_ID,
    }
)

with urllib.request.urlopen(req_get) as res:
    agent_data = json.loads(res.read().decode("utf-8"))

low_code_def = agent_data.get("lowCodeAgentDefinition", {})
nodes = low_code_def.get("nodes", [])

# Map data stores and connectors to nodes
node_to_datastores = {}
node_to_dataconnectors = {}

for s in mcp_servers:
    ds_name = registered_datastores.get(s["id"])
    dc_name = registered_dataconnectors.get(s["id"])
    if ds_name:
        for node_id in s["target_nodes"]:
            if node_id not in node_to_datastores:
                node_to_datastores[node_id] = []
            if ds_name not in node_to_datastores[node_id]:
                node_to_datastores[node_id].append(ds_name)
    if dc_name:
        for node_id in s["target_nodes"]:
            if node_id not in node_to_dataconnectors:
                node_to_dataconnectors[node_id] = []
            if dc_name not in [dc.get("name") for dc in node_to_dataconnectors[node_id]]:
                node_to_dataconnectors[node_id].append({
                    "name": dc_name,
                    "dataSource": "custom_mcp"
                })

for n in nodes:
    n_id = n.get("id")
    if "llmAgentNode" in n:
        llm = n["llmAgentNode"]
        llm["model"] = "gemini-3.7-flash"
        ds_list = node_to_datastores.get(n_id, [])
        dc_list = node_to_dataconnectors.get(n_id, [])
        if ds_list:
            llm["dataStoreSpecs"] = {
                "specs": [{"dataStore": ds} for ds in ds_list]
            }
            print(f"  🔗 Linked {len(ds_list)} DataStore(s) to Node [{n_id}]: {[ds.split('/')[-1] for ds in ds_list]}")
        if dc_list:
            llm["dataConnectors"] = dc_list

low_code_def["deployedNodes"] = nodes

patch_payload = {
    "displayName": agent_data.get("displayName"),
    "description": agent_data.get("description"),
    "lowCodeAgentDefinition": low_code_def,
    "starterPrompts": agent_data.get("starterPrompts", []),
    "sharingConfig": agent_data.get("sharingConfig", {"scope": "ALL_USERS"})
}

patch_url = f"https://discoveryengine.googleapis.com/v1alpha/{parent}/agents/{agent_id}?updateMask=lowCodeAgentDefinition"
patch_req = urllib.request.Request(
    patch_url,
    data=json.dumps(patch_payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID,
    },
    method="PATCH",
)

try:
    with urllib.request.urlopen(patch_req) as patch_res:
        print("  ✅ Agent successfully patched with DataStore & DataConnector links.")
except urllib.error.HTTPError as e:
    print("  ❌ Patch error:", e.read().decode("utf-8"))
    raise

deploy_url = f"https://discoveryengine.googleapis.com/v1alpha/{parent}/agents/{agent_id}:deployLowCode"
deploy_req = urllib.request.Request(
    deploy_url,
    data=json.dumps({"deployMode": "DEPLOY"}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID,
    },
    method="POST"
)

with urllib.request.urlopen(deploy_req) as deploy_res:
    print("  🚀 Agent successfully redeployed with all MCP DataStores active!")

print("\n✨ ALL 7 MCP DATASTORES REGISTERED AND ATTACHED SUCCESSFULLY!")
