#!/usr/bin/env bash
set -e

PROJECT_ID="hong-ai-demo"
REGION="asia-southeast1"
BASE_DIR="/google/src/cloud/pheeraphong/hong-ai-demo/google3/underwriting_demo/v2_microservices/services"
GCLOUD="/usr/local/google/home/pheeraphong/google-cloud-sdk/bin/gcloud"

services=(
  "gmail_mcp:underwriting-gmail-mcp"
  "doc_mcp:underwriting-doc-mcp"
  "registry_mcp:underwriting-registry-mcp"
  "fraud_mcp:underwriting-fraud-mcp"
  "scoring_mcp:underwriting-scoring-mcp"
  "decision_mcp:underwriting-decision-mcp"
  "notification_mcp:underwriting-notification-mcp"
)

echo "=========================================================="
echo "🚀 DEPLOYING 7 UNDERWRITING v2 MCP MICROSERVICES TO CLOUD RUN"
echo "Project: $PROJECT_ID | Region: $REGION"
echo "=========================================================="

for item in "${services[@]}"; do
  dir="${item%%:*}"
  svc_name="${item##*:}"
  
  echo ""
  echo "📦 Deploying $svc_name from $dir..."
  $GCLOUD run deploy "$svc_name" \
    --source "$BASE_DIR/$dir" \
    --region "$REGION" \
    --project "$PROJECT_ID" \
    --allow-unauthenticated \
    --min-instances 0 \
    --max-instances 5 \
    --memory 512Mi \
    --quiet
    
  url=$($GCLOUD run services describe "$svc_name" --region "$REGION" --project "$PROJECT_ID" --format="value(status.url)")
  echo "✅ $svc_name LIVE AT: $url"
done

echo ""
echo "🎉 ALL 7 MICROSERVICES DEPLOYED TO CLOUD RUN SUCCESSFULLY!"
