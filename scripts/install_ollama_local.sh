#!/usr/bin/env bash
# ============================================================
# Local Ollama Installer (Sudo-free / User space)
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Local Ollama Setup ==="
cd "$PROJECT_ROOT"

# Create local bin/ directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/bin"

# Get latest release version of Ollama using GitHub API
echo "Fetching latest Ollama version info..."
LATEST_VERSION=$(curl -s https://api.github.com/repos/ollama/ollama/releases/latest | grep -oP '"tag_name": "\K[^"]+')
echo "Latest version is: $LATEST_VERSION"

# Check if ollama binary already exists
if [ -f "$PROJECT_ROOT/bin/ollama" ] && [ "$(cat "$PROJECT_ROOT/bin/ollama" 2>/dev/null)" != "Not Found" ]; then
    echo "Ollama binary already exists in $PROJECT_ROOT/bin/ollama"
else
    echo "Downloading Ollama Linux package ($LATEST_VERSION)..."
    curl -L "https://github.com/ollama/ollama/releases/download/${LATEST_VERSION}/ollama-linux-amd64.tar.zst" -o "ollama-linux-amd64.tar.zst"
    
    echo "Decompressing and extracting Ollama binary..."
    zstd -d "ollama-linux-amd64.tar.zst"
    tar -xf "ollama-linux-amd64.tar" -C "$PROJECT_ROOT"
    
    # Cleanup temporary archive files
    rm "ollama-linux-amd64.tar.zst" "ollama-linux-amd64.tar"
fi

echo "Ollama is installed in: $PROJECT_ROOT/bin/ollama"
echo "To run the server in the background, execute:"
echo "  $PROJECT_ROOT/bin/ollama serve &"
