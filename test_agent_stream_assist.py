"""Test live invocation of underwriting-orchestrator agent in ge-demo1 via streamAssist."""

import json
import subprocess
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
ENGINE_ID = "ge-demo1"
ASSISTANT_ID = "default_assistant"
AGENT_ID = "underwriting-orchestrator"

agent_resource = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/{ASSISTANT_ID}/agents/{AGENT_ID}"
assistant_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/{ASSISTANT_ID}:streamAssist"

prompt_th = (
    "ช่วยตรวจสอบและวิเคราะห์การขอสินเชื่อธุรกิจ SME ให้กับ:\n"
    "- ชื่อบริษัท: บริษัท สยาม ซอฟต์แวร์ โซลูชั่น จำกัด\n"
    "- เลขทะเบียนนิติบุคคล (DBD): 0105558000001\n"
    "- วงเงินที่ขอกู้: 10,000,000 บาท\n"
    "- ผู้มีอำนาจลงนาม: นายสมชาย ใจดี (บัตรประชาชน: 1100500123456)\n"
    "กรุณาเรียกใช้เครื่องมือ MCP เพื่อตรวจสอบข้อมูล DBD, ตรวจสอบรายชื่อ AML, คำนวณ DSCR, วิเคราะห์ความเสี่ยง และออกหนังสือสรุปผลการพิจารณาเป็นภาษาไทย"
)

payload = {
    "query": {
        "text": prompt_th
    },
    "answerGenerationMode": "AGENT",
    "agentsConfig": {
        "agent": agent_resource
    }
}

print("===================================================================")
print(f"🤖 Invoking Live Agent [{AGENT_ID}] in {ENGINE_ID} via StreamAssist")
print("===================================================================")
print(f"Prompt (Thai):\n{prompt_th}\n")

req = urllib.request.Request(
    assistant_url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=60) as res:
        response_data = res.read().decode("utf-8")
        print("✅ Response Received:")
        print(response_data[:1500])
        if len(response_data) > 1500:
            print(f"\n... [Truncated {len(response_data) - 1500} bytes] ...")
except urllib.error.HTTPError as e:
    print(f"❌ HTTPError {e.code}: {e.reason}")
    print(e.read().decode("utf-8"))
except Exception as e:
    print(f"❌ Error: {e}")
