#!/usr/bin/env bash
# Cloud Run deploy TEMPLATE for the two MCP services (Cop / Thief).
#
# This is a SAFE TEMPLATE. It does nothing unless RUN_CLOUD_DEPLOY=1 is set, and it
# contains only placeholders (no real project IDs, regions, tokens, or URLs).
# It is never executed by the test suite or any validation step. Review and fill
# in placeholders, authenticate yourself (gcloud auth login), then run manually.
#
# Prerequisites you run yourself (NOT run here): gcloud auth login, enable Cloud
# Run + Secret Manager, create secrets for COP_MCP_TOKEN / THIEF_MCP_TOKEN.
set -euo pipefail

if [ "${RUN_CLOUD_DEPLOY:-0}" != "1" ]; then
  echo '{"status":"skipped","reason":"RUN_CLOUD_DEPLOY != 1 (template is inert by default)"}'
  exit 0
fi

PROJECT_ID="<GOOGLE_CLOUD_PROJECT_ID>"
REGION="<REGION>"
COP_SERVICE_NAME="<COP_SERVICE_NAME>"      # e.g. mars777-cop-mcp
THIEF_SERVICE_NAME="<THIEF_SERVICE_NAME>"  # e.g. mars777-thief-mcp
IMAGE="<REGION>-docker.pkg.dev/<GOOGLE_CLOUD_PROJECT_ID>/mars777/mcp:latest"
COP_SECRET_NAME="<SECRET_NAME>"            # Secret Manager name for COP_MCP_TOKEN
THIEF_SECRET_NAME="<SECRET_NAME>"          # Secret Manager name for THIEF_MCP_TOKEN

# Build & push the single role-aware image (placeholders only):
#   gcloud builds submit --tag "${IMAGE}" --project "${PROJECT_ID}"

# Deploy the Cop service (token injected from Secret Manager, never committed):
#   gcloud run deploy "${COP_SERVICE_NAME}" --image "${IMAGE}" --region "${REGION}" \
#     --platform managed --set-env-vars MCP_ROLE=cop \
#     --set-secrets COP_MCP_TOKEN="${COP_SECRET_NAME}:latest"

# Deploy the Thief service:
#   gcloud run deploy "${THIEF_SERVICE_NAME}" --image "${IMAGE}" --region "${REGION}" \
#     --platform managed --set-env-vars MCP_ROLE=thief \
#     --set-secrets THIEF_MCP_TOKEN="${THIEF_SECRET_NAME}:latest"

echo '{"status":"template","note":"Fill placeholders and uncomment the gcloud commands to deploy manually."}'
