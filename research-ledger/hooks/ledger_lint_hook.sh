#!/usr/bin/env bash
# PostToolUse hook: after an edit to <...>/ledger/*.md, lint that ledger and feed
# findings back to Claude (exit 2 -> stderr is shown to the model). Silent when clean.
# Install: copy to ~/.claude/hooks/ and add to ~/.claude/settings.json:
#   "hooks": {"PostToolUse": [{"matcher": "Edit|Write|MultiEdit",
#     "hooks": [{"type": "command", "command": "~/.claude/hooks/ledger_lint_hook.sh", "timeout": 30}]}]}
f=$(jq -r '.tool_input.file_path // .tool_response.filePath // empty')
case "$f" in
  */ledger/*.md) ;;
  *) exit 0 ;;
esac
dir=${f%/*}
# Where the research-ledger skill is installed (folder holding ledger_lint.py).
skill="${LEDGER_SKILL_DIR:-$HOME/.claude/skills/research-ledger}"
lint="$skill/ledger_lint.py"
[ -f "$lint" ] || exit 0
# research-ledger v0.7: regenerate the page after every ledger update (if the project has one)
render="${lint%/*}/ledger_html.py"
if [ -f "$dir/ledger.html" ] && [ -f "$render" ]; then
  python3 "$render" --ledger "$dir" --out "$dir/ledger.html" >/dev/null 2>&1
fi
out=$(python3 "$lint" --ledger "$dir" --max 15 2>/dev/null)
if [ -n "$out" ]; then
  { echo "ledger lint ($dir):"; echo "$out"; } >&2
  exit 2
fi
exit 0
