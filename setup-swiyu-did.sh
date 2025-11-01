#!/bin/bash

# Swiyu DID Registration Setup Script
# Generic script for setting up a Swiyu verifier DID
#
# Prerequisites:
# 1. Java 21+ installed (java -version)
# 2. Register at https://eportal.admin.ch/start
#    - Search for "swiyu Trust Infrastructure" service
#    - Register your organization → get Partner ID
# 3. Subscribe to APIs at http://selfservice.api.admin.ch/api-selfservice
#    - Subscribe to "swiyucorebusiness_identifier" API
#    - Create application and get: Client ID, Client Secret, Refresh Token
# 4. Have a public URL where your verifier will be accessible (for mobile app)

set -e  # Exit on error

echo "=========================================="
echo "Swiyu DID Registration Setup Script"
echo "=========================================="
echo ""
echo "This script will:"
echo "  1. Generate EC P-256 cryptographic keys"
echo "  2. Create identifier entry in Swiyu registry"
echo "  3. Generate DID using DID Toolbox"
echo "  4. Upload DID to Swiyu registry"
echo "  5. Update your .env configuration"
echo ""

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DID_KEYS_DIR="$SCRIPT_DIR/did-keys"
ENV_FILE="$SCRIPT_DIR/.env"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
prompt() { echo -e "${BLUE}[INPUT]${NC} $1"; }

# Check Java
info "Checking prerequisites..."
if ! command -v java &> /dev/null; then
    error "Java not installed. Install Java 21+ first."
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 21 ]; then
    error "Java 21+ required. Current: $JAVA_VERSION"
fi
info "Java $JAVA_VERSION detected ✓"

# Gather inputs
echo ""
echo "=========================================="
echo "API Credentials"
echo "=========================================="
echo ""
echo "Get these from http://selfservice.api.admin.ch/api-selfservice"
echo ""

read -p "$(echo -e ${BLUE}[INPUT]${NC}) Refresh Token: " REFRESH_TOKEN
read -p "$(echo -e ${BLUE}[INPUT]${NC}) Client ID: " CLIENT_ID
read -p "$(echo -e ${BLUE}[INPUT]${NC}) Client Secret: " CLIENT_SECRET
read -p "$(echo -e ${BLUE}[INPUT]${NC}) Partner ID (Business Entity ID): " PARTNER_ID

echo ""
echo "=========================================="
echo "Verifier Configuration"
echo "=========================================="
echo ""

read -p "$(echo -e ${BLUE}[INPUT]${NC}) External URL (where verifier is accessible, e.g., https://swiyu.example.com): " EXTERNAL_URL
read -p "$(echo -e ${BLUE}[INPUT]${NC}) Verifier Name (shown in Swiyu app, e.g., \"My Application\"): " VERIFIER_NAME

echo ""
info "Configuration collected ✓"

# Get fresh access token
echo ""
echo "=========================================="
echo "Step 1/6: Refreshing Access Token"
echo "=========================================="
echo ""

info "Requesting fresh access token..."
TOKEN_RESPONSE=$(curl -s -X POST \
  "https://keymanager-prd.api.admin.ch/keycloak/realms/APIGW/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=$REFRESH_TOKEN" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    error "Failed to get access token. Check credentials. Response: $TOKEN_RESPONSE"
fi

info "Access token obtained ✓"

# Generate EC keys
echo ""
echo "=========================================="
echo "Step 2/6: Generating Cryptographic Keys"
echo "=========================================="
echo ""

mkdir -p "$DID_KEYS_DIR"
cd "$DID_KEYS_DIR"

if [ -f "signing-key.pem" ]; then
    warn "Keys already exist. Backing up..."
    BACKUP_DIR="backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    mv signing-key.pem signing-key-pub.pem "$BACKUP_DIR/" 2>/dev/null || true
fi

info "Generating EC P-256 key pair..."
openssl ecparam -genkey -name prime256v1 -noout -out signing-key.pem
openssl ec -in signing-key.pem -pubout -out signing-key-pub.pem 2>/dev/null

info "Keys generated ✓"
info "  Private: $DID_KEYS_DIR/signing-key.pem"
info "  Public:  $DID_KEYS_DIR/signing-key-pub.pem"

# Download didtoolbox
echo ""
echo "=========================================="
echo "Step 3/6: Download DID Toolbox"
echo "=========================================="
echo ""

if [ ! -f "didtoolbox.jar" ]; then
    info "Downloading DID Toolbox JAR..."
    curl -L -# -o didtoolbox.jar \
      "https://repo1.maven.org/maven2/io/github/swiyu-admin-ch/didtoolbox/1.3.1/didtoolbox-1.3.1-jar-with-dependencies.jar"
    info "Downloaded ✓"
else
    info "DID Toolbox already exists ✓"
fi

# Create identifier entry
echo ""
echo "=========================================="
echo "Step 4/6: Create Identifier Entry"
echo "=========================================="
echo ""

info "Creating identifier entry in Swiyu registry..."
ENTRY_RESPONSE=$(curl -s -X POST \
  "https://identifier-reg-api.trust-infra.swiyu-int.admin.ch/api/v1/identifier/business-entities/$PARTNER_ID/identifier-entries" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

ENTRY_ID=$(echo "$ENTRY_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id', ''))" 2>/dev/null)

if [ -z "$ENTRY_ID" ]; then
    error "Failed to create entry. Response: $ENTRY_RESPONSE"
fi

info "Identifier entry created ✓"
info "  Entry ID: $ENTRY_ID"

# Generate DID
echo ""
echo "=========================================="
echo "Step 5/6: Generate DID"
echo "=========================================="
echo ""

FULL_REGISTRY_URL="https://identifier-reg.trust-infra.swiyu-int.admin.ch/api/v1/did/$ENTRY_ID"

info "Generating DID with your EC P-256 key..."
info "  Registry URL: $FULL_REGISTRY_URL"

rm -rf ~/.didtoolbox
java -jar didtoolbox.jar create \
  --force-overwrite \
  --identifier-registry-url "$FULL_REGISTRY_URL" \
  --assert "assert-key-01,$DID_KEYS_DIR/signing-key-pub.pem" \
  > didlog.jsonl 2>&1

if [ ! -f "didlog.jsonl" ] || [ ! -s "didlog.jsonl" ]; then
    cat didlog.jsonl
    error "DID generation failed. See output above."
fi

# Copy generated keys
cp -r ~/.didtoolbox ./ 2>/dev/null || warn ".didtoolbox not found"

DID=$(cat didlog.jsonl | python3 -c "import json, sys; data=json.load(sys.stdin); print(data[3]['value']['id'])" 2>/dev/null)

if [ -z "$DID" ]; then
    error "Failed to extract DID"
fi

info "DID generated ✓"
echo ""
echo "  📋 Your DID:"
echo "  $DID"
echo ""

# Upload DID
echo ""
echo "=========================================="
echo "Step 6/6: Upload DID to Registry"
echo "=========================================="
echo ""

info "Uploading DID log to registry..."
UPLOAD_HTTP=$(curl -w "%{http_code}" -o /dev/null -X PUT \
  "https://identifier-reg-api.trust-infra.swiyu-int.admin.ch/api/v1/identifier/business-entities/$PARTNER_ID/identifier-entries/$ENTRY_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/jsonl+json" \
  --data-binary @didlog.jsonl 2>&1)

if [ "$UPLOAD_HTTP" != "200" ]; then
    error "Upload failed. HTTP: $UPLOAD_HTTP"
fi

info "DID uploaded ✓"

# Update .env
echo ""
echo "=========================================="
echo "Updating Configuration"
echo "=========================================="
echo ""

SIGNING_KEY_PIPE=$(cat signing-key.pem | tr '\n' '|' | sed 's/|$//')

if [ -f "$ENV_FILE" ]; then
    info "Updating .env file..."

    # Backup
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%s)"

    # Update or add DID configuration
    if grep -q "^VERIFIER_DID=" "$ENV_FILE"; then
        # Update existing
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^VERIFIER_DID=.*|VERIFIER_DID=$DID|" "$ENV_FILE"
            sed -i '' "s|^DID_VERIFICATION_METHOD=.*|DID_VERIFICATION_METHOD=$DID#assert-key-01|" "$ENV_FILE"
            sed -i '' "s|^EXTERNAL_URL=.*|EXTERNAL_URL=$EXTERNAL_URL|" "$ENV_FILE"
            sed -i '' "s|^VERIFIER_NAME=.*|VERIFIER_NAME=$VERIFIER_NAME|" "$ENV_FILE"
            sed -i '' "s|^SIGNING_KEY=.*|SIGNING_KEY=$SIGNING_KEY_PIPE|" "$ENV_FILE"
        else
            sed -i "s|^VERIFIER_DID=.*|VERIFIER_DID=$DID|" "$ENV_FILE"
            sed -i "s|^DID_VERIFICATION_METHOD=.*|DID_VERIFICATION_METHOD=$DID#assert-key-01|" "$ENV_FILE"
            sed -i "s|^EXTERNAL_URL=.*|EXTERNAL_URL=$EXTERNAL_URL|" "$ENV_FILE"
            sed -i "s|^VERIFIER_NAME=.*|VERIFIER_NAME=$VERIFIER_NAME|" "$ENV_FILE"
            sed -i "s|^SIGNING_KEY=.*|SIGNING_KEY=$SIGNING_KEY_PIPE|" "$ENV_FILE"
        fi
    else
        # Append new
        cat >> "$ENV_FILE" << EOF

# DID Configuration (Generated by setup-swiyu-did.sh)
VERIFIER_DID=$DID
DID_VERIFICATION_METHOD=$DID#assert-key-01
VERIFIER_NAME=$VERIFIER_NAME
EXTERNAL_URL=$EXTERNAL_URL
SIGNING_KEY=$SIGNING_KEY_PIPE
EOF
    fi

    info ".env updated ✓"
else
    warn ".env not found. Please create it manually with the values below."
fi

# Summary
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ EC P-256 keys generated and saved"
echo "  ✓ DID created with your keys"
echo "  ✓ DID uploaded to Swiyu identifier registry"
echo "  ✓ Configuration updated in .env"
echo ""
echo "📋 Your DID:"
echo "  $DID"
echo ""
echo "📁 Files created in $DID_KEYS_DIR:"
echo "  - signing-key.pem (🔐 KEEP SECRET!)"
echo "  - signing-key-pub.pem"
echo "  - didlog.jsonl (DID document)"
echo "  - .didtoolbox/ (additional keys)"
echo "  - didtoolbox.jar (DID toolbox)"
echo ""
echo "🔧 Configuration:"
echo "  VERIFIER_DID=$DID"
echo "  DID_VERIFICATION_METHOD=$DID#assert-key-01"
echo "  EXTERNAL_URL=$EXTERNAL_URL"
echo "  VERIFIER_NAME=$VERIFIER_NAME"
echo ""
echo "📝 Next Steps:"
echo "  1. Restart your services:"
echo "     docker compose down && docker compose up -d"
echo ""
echo "  2. Wait ~75 seconds for verifier service to start"
echo ""
echo "  3. Test authentication:"
echo "     Visit your login page and scan QR code with Swiyu mobile app"
echo ""
echo "⚠️  IMPORTANT:"
echo "  - Back up the did-keys/ directory securely!"
echo "  - Never commit signing-key.pem to git"
echo "  - Keep .env file secret (it contains your private key)"
echo ""
echo "✨ Setup complete! Your verifier is ready to use."
echo ""
