#!/usr/bin/env python3
"""Unified One-Click Deployment Script for Gemini Enterprise Autonomous Underwriting Platform.

Usage:
  python3 deploy_all.py --project-id <PROJECT_ID> [--region asia-southeast1] [--engine-id ge-demo1]
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

def run_cmd(cmd, cwd=None):
    print(f"⚙️ Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Command failed: {res.stderr.strip()}")
        raise RuntimeError(res.stderr)
    return res.stdout.strip()

def get_access_token():
    return run_cmd(["/usr/local/google/home/pheeraphong/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"])

def main():
    parser = argparse.ArgumentParser(description="Deploy Autonomous Underwriting Platform on GCP")
    parser.add_argument("--project-id", default="hong-ai-demo", help="Target GCP Project ID")
    parser.add_argument("--region", default="asia-southeast1", help="GCP Region for Cloud Run")
    parser.add_argument("--engine-id", default="ge-demo1", help="Discovery Engine / Gemini Enterprise Engine ID")
    args = parser.parse_args()

    project_id = args.project_id
    region = args.region
    engine_id = args.engine_id

    print("===================================================================")
    print("🚀 ONE-CLICK DEPLOYMENT: GEMINI ENTERPRISE UNDERWRITING PLATFORM")
    print(f"   Project: {project_id}")
    print(f"   Region:  {region}")
    print(f"   Engine:  {engine_id}")
    print("===================================================================")

    # 1. Enable APIs
    print("\n[Step 1/5] Enabling GCP APIs...")
    apis = [
        "run.googleapis.com",
        "cloudbuild.googleapis.com",
        "artifactregistry.googleapis.com",
        "discoveryengine.googleapis.com"
    ]
    run_cmd(["/usr/local/google/home/pheeraphong/google-cloud-sdk/bin/gcloud", "services", "enable"] + apis + ["--project", project_id])
    print("✅ APIs enabled.")

    # 2. Deploy Cloud Run Microservices
    print("\n[Step 2/5] Building & Deploying 7 Cloud Run MCP Microservices...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    v2_dir = os.path.join(script_dir, "v2_microservices")
    env = os.environ.copy()
    env["PROJECT_ID"] = project_id
    env["REGION"] = region
    
    deploy_script = os.path.join(v2_dir, "deploy_v2_microservices.sh")
    run_cmd(f"bash {deploy_script}", cwd=v2_dir)
    print("✅ All 7 Cloud Run Microservices deployed.")

    # 3. Setup MCP Data Connectors & Data Stores
    print("\n[Step 3/5] Provisioning & Binding MCP Data Stores in Gemini Enterprise...")
    setup_ds_script = os.path.join(script_dir, "setup_all_7_mcp_datastores.py")
    run_cmd(["python3", setup_ds_script])
    print("✅ MCP Data Stores registered and attached to Engine.")

    # 4. Import & Deploy Multi-Agent Orchestrator
    print("\n[Step 4/5] Deploying Multi-Agent Orchestrator (Gemini 3.7 Flash Thai)...")
    update_agent_script = os.path.join(script_dir, "update_agent_designer_v2_mcp_thai.py")
    run_cmd(["python3", update_agent_script])
    print("✅ Multi-Agent Orchestrator deployed.")

    # 5. Run Verification Harness
    print("\n[Step 5/5] Running Verification Tests...")
    test_script = os.path.join(script_dir, "test_all_mcp_servers.py")
    run_cmd(["python3", test_script])
    print("✅ All verification tests passed.")

    print("\n===================================================================")
    print("🎉 DEPLOYMENT COMPLETE! Platform is ready for live demonstrations.")
    print("===================================================================")

if __name__ == "__main__":
    main()
