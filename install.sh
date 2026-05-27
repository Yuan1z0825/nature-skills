#!/usr/bin/env bash
# Academic Search Skill + MCP Server Installer for Claude Code
# Usage: bash install.sh [PUBMED_EMAIL]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"
MCP_TARGET="${CLAUDE_DIR}/mcp_servers/academic-search"
SKILL_TARGET="${CLAUDE_DIR}/skills/academic-search"
MCP_JSON="${CLAUDE_DIR}/.mcp.json"

PUBMED_EMAIL="${1:-user@example.com}"

echo "=== Academic Search Installer ==="
echo "Target: ${CLAUDE_DIR}"
echo "PubMed email: ${PUBMED_EMAIL}"
echo

# 1. Install Python dependencies
echo "[1/5] Installing Python dependencies..."
pip install --quiet -r "${SCRIPT_DIR}/mcp-server/requirements.txt" 2>/dev/null || {
    echo "  pip failed, trying pip3..."
    pip3 install --quiet -r "${SCRIPT_DIR}/mcp-server/requirements.txt" 2>/dev/null || {
        echo "  WARNING: Could not install Python deps. Install manually:"
        echo "    pip install -r mcp-server/requirements.txt"
    }
}

# 2. Copy MCP server
echo "[2/5] Copying MCP server..."
mkdir -p "${MCP_TARGET}"
cp -r "${SCRIPT_DIR}/mcp-server/"* "${MCP_TARGET}/"

# 3. Copy Skill
echo "[3/5] Copying Skill..."
mkdir -p "${SKILL_TARGET}"
cp "${SCRIPT_DIR}/README.md" "${SKILL_TARGET}/"
cp "${SCRIPT_DIR}/SKILL.md" "${SKILL_TARGET}/"
cp -r "${SCRIPT_DIR}/references" "${SKILL_TARGET}/"
cp -r "${SCRIPT_DIR}/scripts" "${SKILL_TARGET}/"
cp -r "${SCRIPT_DIR}/config" "${SKILL_TARGET}/"

# 4. Merge .mcp.json
echo "[4/5] Configuring .mcp.json..."
if [ -f "${MCP_JSON}" ]; then
    # Check if academic-search already exists
    if grep -q '"academic-search"' "${MCP_JSON}" 2>/dev/null; then
        echo "  academic-search already in .mcp.json, skipping merge."
    else
        # Inject into existing mcpServers object
        python3 -c "
import json, sys
with open('${MCP_JSON}', 'r') as f:
    cfg = json.load(f)
cfg.setdefault('mcpServers', {})['academic-search'] = {
    'command': 'python3',
    'args': ['${MCP_TARGET}/academic_search_server.py'],
    'env': {'PUBMED_EMAIL': '${PUBMED_EMAIL}'}
}
with open('${MCP_JSON}', 'w') as f:
    json.dump(cfg, f, indent=2)
    f.write('\n')
print('  Merged academic-search into existing .mcp.json')
"
    fi
else
    cat > "${MCP_JSON}" <<MCPJSON
{
  "mcpServers": {
    "academic-search": {
      "command": "python3",
      "args": ["${MCP_TARGET}/academic_search_server.py"],
      "env": {
        "PUBMED_EMAIL": "${PUBMED_EMAIL}"
      }
    }
  }
}
MCPJSON
    echo "  Created new .mcp.json"
fi

# 5. Enable in settings.json
echo "[5/5] Enabling in settings.json..."
SETTINGS_JSON="${CLAUDE_DIR}/settings.json"
if [ -f "${SETTINGS_JSON}" ]; then
    python3 -c "
import json
with open('${SETTINGS_JSON}', 'r') as f:
    cfg = json.load(f)
enabled = cfg.setdefault('enabledMcpjsonServers', [])
if 'academic-search' not in enabled:
    enabled.append('academic-search')
    with open('${SETTINGS_JSON}', 'w') as f:
        json.dump(cfg, f, indent=2)
        f.write('\n')
    print('  Added academic-search to enabledMcpjsonServers')
else:
    print('  academic-search already enabled')
"
else
    echo '  WARNING: settings.json not found. Manually add "academic-search" to enabledMcpjsonServers.'
fi

echo
echo "=== Done ==="
echo
echo "Installed:"
echo "  MCP server : ${MCP_TARGET}/"
echo "  Skill      : ${SKILL_TARGET}/"
echo
echo "Next steps:"
echo "  1. Restart Claude Code (or /clear)"
echo "  2. Set your PubMed email in config.toml or PUBMED_EMAIL env var"
echo "  3. (Optional) Add NCBI_API_KEY for higher rate limits"
echo "  4. Test: ask Claude 'search papers about CRISPR'"
echo
echo "Optional: copy triggers to your data/triggers.toml"
echo "  See: config/triggers-academic-search.toml"
