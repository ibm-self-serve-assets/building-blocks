#!/usr/bin/env bash
# backup.sh - Creates a timestamped backup of all source files for factory-pulse-streamhouse.
# Run from the workspace root:  bash scripts/backup.sh

WORKSPACE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
DEST="$WORKSPACE_ROOT/backups/backup_$TIMESTAMP"

ITEMS=(
    # ── Server (backend) ─────────────────────────────────────────────────────
    "server/app.py"
    "server/kafka.py"
    "server/simulation.py"
    "server/context.py"
    "server/mcp.py"
    "server/plants.py"
    "server/schemas.py"

    # ── Frontend ─────────────────────────────────────────────────────────────
    "frontend/index.html"
    "frontend/vite.config.js"
    "frontend/package.json"
    "frontend/src/App.jsx"
    "frontend/src/main.jsx"
    "frontend/src/styles.scss"
    "frontend/src/sql.js"
    "frontend/src/components/FactoryTwin.jsx"
    "frontend/src/components/PlantMap.jsx"
    "frontend/src/components/Login.jsx"
    "frontend/src/sim/api.js"
    "frontend/src/sim/localBackend.js"
    "frontend/src/twin/lineControl.js"
    "frontend/src/twin/plantProfiles.js"
    "frontend/src/twin/plantSim.js"

    # ── Docs site ─────────────────────────────────────────────────────────────
    "docs/architecture.md"
    "docs/cloud-setup.md"
    "docs/confluent-feature-matrix.md"
    "docs/demo-script.md"
    "docs/digital-twin-explained.md"
    "docs/digital-twin-creation-guide.html"
    "docs/factory-pulse-full-ui-component-anatomy.html"
    "docs/factory-pulse-ui-anatomy.html"
    "docs/one-click-terraform.md"
    "docs/robot-arm-preview.html"
    "docs/robot-arm-preview-v2.html"
    "docs/streamhouse-capabilities.md"
    "docs/watsonx-orchestrate-agent-spec.md"

    # ── Deploy ────────────────────────────────────────────────────────────────
    "deploy/Dockerfile"
    "deploy/requirements.txt"
    "deploy/.dockerignore"
    "deploy/deploy-local.sh"
    "deploy/deploy-local.cmd"
    "deploy/deploy-confluent.sh"
    "deploy/deploy-confluent.cmd"
    "deploy/deploy-ce.sh"

    # ── Scripts ───────────────────────────────────────────────────────────────
    "scripts/start.sh"
    "scripts/start.cmd"
    "scripts/start.py"
    "scripts/backup.sh"
    "scripts/backup.ps1"
    "scripts/deploy.py"
    "scripts/e2e_test.py"
    "scripts/e2e_full_test.py"
    "scripts/sse_test.py"
    "scripts/sse_verify_test.py"
    "scripts/browser_path_test.py"
    "scripts/_check_state.py"

    # ── Tests ─────────────────────────────────────────────────────────────────
    "tests/simulation.test.js"
    "tests/test_deploy.py"

    # ── Root config / docs ────────────────────────────────────────────────────
    ".env.example"
    ".dockerignore"
    ".gitignore"
    "README.md"
)

echo ""
echo "Factory Pulse -- Source Backup"
echo "Workspace  : $WORKSPACE_ROOT"
echo "Destination: $DEST"
echo ""

OK=0
SKIP=0
SKIPPED=()

for REL in "${ITEMS[@]}"; do
    SRC="$WORKSPACE_ROOT/$REL"

    if [ ! -f "$SRC" ]; then
        echo "  SKIP  $REL"
        SKIP=$((SKIP + 1))
        SKIPPED+=("$REL")
        continue
    fi

    TARGET="$DEST/$REL"
    TARGET_DIR="$(dirname "$TARGET")"
    mkdir -p "$TARGET_DIR"
    cp "$SRC" "$TARGET"
    echo "  OK    $REL"
    OK=$((OK + 1))
done

# Write manifest
MANIFEST="$DEST/MANIFEST.txt"
{
    echo "Factory Pulse Streamhouse - Backup Manifest"
    echo "Created    : $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Timestamp  : $TIMESTAMP"
    echo "Files OK   : $OK"
    echo "Files Skip : $SKIP"
    echo ""
    echo "Backed-up files:"
    for REL in "${ITEMS[@]}"; do
        SKIPPED_FLAG=false
        for S in "${SKIPPED[@]}"; do
            [ "$S" = "$REL" ] && SKIPPED_FLAG=true && break
        done
        if $SKIPPED_FLAG; then
            echo "  [SKIP] $REL"
        else
            echo "  [OK]   $REL"
        fi
    done
} > "$MANIFEST"

echo ""
echo "Done. $OK file(s) backed up, $SKIP skipped."
echo "Backup folder: $DEST"
echo ""
