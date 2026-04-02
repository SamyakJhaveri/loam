#!/usr/bin/env bash
# setup_claude_for_sam.sh — portable Claude Code bootstrapper
#
# Makes the .claude/ directory (hooks, agents, skills, rules) work on any machine
# after a fresh git clone. Resolves project-root placeholders and generates
# machine-local config files.
#
# Usage: bash scripts/setup_claude_for_sam.sh
# Security: never reads/writes/prompts for API keys, tokens, or .env files

set -euo pipefail

# BSD sed (macOS) needs -i '' ; GNU sed (Linux) needs just -i
if [[ "$(uname)" == "Darwin" ]]; then
    SED_I=(-i '')
else
    SED_I=(-i)
fi

STEP_OK="[OK]"
STEP_SKIP="[SKIP]"
STEP_FAIL="[FAIL]"

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "$STEP_FAIL Not a git repo. Run from inside a git repository."
    exit 1
}

# Build the placeholder string at runtime to avoid self-modification.
# If the literal appeared in this file, Step 3's sed would rewrite this script.
LB='{{'
RB='}}'
PLACEHOLDER="${LB}PROJECT_ROOT${RB}"

echo "=== setup_claude_for_sam.sh ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# ── Step 1: Claude Code ──────────────────────────────────────────────────────
if command -v claude &>/dev/null; then
    echo "$STEP_SKIP Claude Code already installed: $(claude --version 2>/dev/null || echo 'unknown version')"
else
    echo "Installing Claude Code..."
    npm install -g @anthropic-ai/claude-code 2>&1 || {
        echo "$STEP_FAIL npm install failed."
        echo "  Try: npm config set prefix ~/.npm-global && export PATH=\$HOME/.npm-global/bin:\$PATH"
        exit 1
    }
    echo "$STEP_OK Claude Code installed."
fi

# ── Step 2: Superpowers plugin ───────────────────────────────────────────────
if claude plugins list 2>/dev/null | grep -q superpowers; then
    echo "$STEP_SKIP Superpowers plugin already installed."
else
    echo "$STEP_FAIL Superpowers plugin not found — install manually."
    echo "  Run: claude plugins install superpowers@superpowers-dev"
fi

# ── Step 3: Substitute placeholder → actual project root ─────────────────────
echo "Substituting $PLACEHOLDER → $PROJECT_ROOT ..."
SUBST_FILES=()

# Process .claude/ markdown files
while IFS= read -r -d '' f; do
    if grep -q "$PLACEHOLDER" "$f" 2>/dev/null; then
        sed "${SED_I[@]}" "s|$PLACEHOLDER|$PROJECT_ROOT|g" "$f"
        SUBST_FILES+=("$f")
    fi
done < <(find "$PROJECT_ROOT/.claude" -name "*.md" -print0 2>/dev/null)

# Process batch scripts (exclude this setup script)
while IFS= read -r -d '' f; do
    if grep -q "$PLACEHOLDER" "$f" 2>/dev/null; then
        sed "${SED_I[@]}" "s|$PLACEHOLDER|$PROJECT_ROOT|g" "$f"
        SUBST_FILES+=("$f")
    fi
done < <(find "$PROJECT_ROOT/scripts" -name "*.sh" ! -name "setup_claude_for_sam.sh" -print0 2>/dev/null)

if [ ${#SUBST_FILES[@]} -gt 0 ]; then
    # Mark substituted tracked files as skip-worktree so git doesn't show them as dirty
    TRACKED=()
    for f in "${SUBST_FILES[@]}"; do
        REL="${f#$PROJECT_ROOT/}"
        if git -C "$PROJECT_ROOT" ls-files --error-unmatch "$REL" &>/dev/null 2>&1; then
            TRACKED+=("$REL")
        fi
    done
    if [ ${#TRACKED[@]} -gt 0 ]; then
        git -C "$PROJECT_ROOT" update-index --skip-worktree "${TRACKED[@]}"
    fi
    echo "$STEP_OK Substituted ${#SUBST_FILES[@]} file(s), marked ${#TRACKED[@]} as skip-worktree."
else
    echo "$STEP_SKIP No placeholders found (already substituted?)."
fi

# ── Step 4: Write .claude/.local-paths ──────────────────────────────────────
LOCAL_PATHS="$PROJECT_ROOT/.claude/.local-paths"

# Claude Code derives the memory dir from the absolute project path: / and _ become -
PROJ_KEY="$(echo "$PROJECT_ROOT" | sed 's|^/||' | tr '/_' '--')"
MEMORY_DIR="$HOME/.claude/projects/-${PROJ_KEY}/memory"

# Check if it already exists on disk; if not, try to find one
if [ ! -d "$MEMORY_DIR" ]; then
    # Search using hyphenated basename (Claude Code converts _ to -)
    BASENAME_KEY="$(basename "$PROJECT_ROOT" | tr '_' '-')"
    FOUND=$(find "$HOME/.claude/projects/" -maxdepth 2 -name "memory" -type d 2>/dev/null \
        | while read d; do
            if echo "$d" | grep -qF "$BASENAME_KEY"; then
                echo "$d"
            fi
        done | head -1)
    if [ -n "$FOUND" ]; then
        MEMORY_DIR="$FOUND"
    fi
fi

echo "MEMORY_DIR=$MEMORY_DIR" > "$LOCAL_PATHS"
echo "$STEP_OK Wrote .local-paths: MEMORY_DIR=$MEMORY_DIR"

# ── Step 5: Generate config/paths.json from template ─────────────────────────
PATHS_TEMPLATE="$PROJECT_ROOT/config/paths.json.template"
PATHS_OUT="$PROJECT_ROOT/config/paths.json"
if [ -f "$PATHS_TEMPLATE" ]; then
    sed "s|$PLACEHOLDER|$PROJECT_ROOT|g" "$PATHS_TEMPLATE" > "$PATHS_OUT"
    echo "$STEP_OK Generated config/paths.json"
else
    echo "$STEP_SKIP No config/paths.json.template found."
fi

# ── Step 6: settings.local.json ─────────────────────────────────────────────
TEMPLATE="$PROJECT_ROOT/.claude/settings.local.json.template"
TARGET="$PROJECT_ROOT/.claude/settings.local.json"
if [ -f "$TARGET" ]; then
    echo "$STEP_SKIP settings.local.json already exists (not overwritten)."
elif [ -f "$TEMPLATE" ]; then
    cp "$TEMPLATE" "$TARGET"
    echo "$STEP_OK Created settings.local.json from template."
else
    echo "$STEP_SKIP No settings.local.json.template found."
fi

# ── Step 7: Git submodules ──────────────────────────────────────────────────
if [ -f "$PROJECT_ROOT/.gitmodules" ]; then
    echo "Initializing git submodules..."
    git -C "$PROJECT_ROOT" submodule update --init --recursive
    echo "$STEP_OK Submodules initialized."
else
    echo "$STEP_SKIP No .gitmodules found."
fi

# ── Step 8: Python venv ─────────────────────────────────────────────────────
REQUIREMENTS="$PROJECT_ROOT/requirements.txt"
if [ -f "$REQUIREMENTS" ]; then
    VENV_NAME=$(cat "$PROJECT_ROOT/.claude/.venv-name" 2>/dev/null || echo "env")
    VENV_PATH="$PROJECT_ROOT/$VENV_NAME"
    if [ ! -d "$VENV_PATH" ]; then
        python3 -m venv "$VENV_PATH"
        echo "$STEP_OK Created venv at $VENV_PATH"
    else
        echo "$STEP_SKIP venv already exists at $VENV_PATH"
    fi
    "$VENV_PATH/bin/pip" install -r "$REQUIREMENTS" --quiet
    echo "$STEP_OK Python deps installed."
else
    echo "$STEP_SKIP No requirements.txt found."
fi

# ── Step 9: Make hook scripts executable ─────────────────────────────────────
HOOKS_DIR="$PROJECT_ROOT/.claude/hooks"
if [ -d "$HOOKS_DIR" ]; then
    chmod +x "$HOOKS_DIR"/*.sh 2>/dev/null || true
    echo "$STEP_OK Hook scripts marked executable."
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "=== Setup complete. Run 'claude' to start. ==="
