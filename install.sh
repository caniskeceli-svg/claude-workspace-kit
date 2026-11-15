#!/usr/bin/env bash
# claude-workspace-kit kurulum script'i.
#
# Kullanim: bu repo klonlanmis bir klasorden, hedef repo kokunu argumanla ver
# (vermezsen bulundugun dizin hedef sayilir):
#
#   cd /path/to/claude-workspace-kit
#   ./install.sh /path/to/hedef-repo
#
# Ne yapar:
#   - .claude/agents/denetci.md kopyalar (uzerine yazar, kit'in kaynagi dogru kabul edilir)
#   - .claude/hooks/silme_kilidi.py kopyalar
#   - CLAUDE.md'ye genel kurallar bolumunu EKLER (repoya-ozel icerigi SILMEZ,
#     tekrar calistirilirsa ayni bolumu yerinde gunceller - idempotent)
#   - .claude/settings.json'a hook girdisini MERGE eder (var olan hook'lara DOKUNMAZ)
#
# Hicbir sey SILMEZ, hicbir repoya-ozel dosyanin uzerine kortusuz yazmaz.
set -euo pipefail

KIT_KOK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEDEF="${1:-$(pwd)}"
HEDEF="$(cd "$HEDEF" && pwd)"

if [ ! -d "$HEDEF/.git" ]; then
  echo "UYARI: $HEDEF bir git deposu gibi gorunmuyor (.git yok). Yine de devam ediliyor." >&2
fi

echo "Kit kaynagi : $KIT_KOK"
echo "Hedef repo  : $HEDEF"
echo

mkdir -p "$HEDEF/.claude/agents" "$HEDEF/.claude/hooks"

cp "$KIT_KOK/denetci.md" "$HEDEF/.claude/agents/denetci.md"
echo "OK  .claude/agents/denetci.md"

cp "$KIT_KOK/silme_kilidi.py" "$HEDEF/.claude/hooks/silme_kilidi.py"
chmod +x "$HEDEF/.claude/hooks/silme_kilidi.py"
echo "OK  .claude/hooks/silme_kilidi.py"

python3 "$KIT_KOK/merge_kurulum.py" "$HEDEF"

echo
echo "Kurulum tamamlandi. Dogrulamak icin:"
echo "  echo '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git push --force origin main\"}}' | CLAUDE_PROJECT_DIR=\"$HEDEF\" python3 \"$HEDEF/.claude/hooks/silme_kilidi.py\"; echo \"exit=\$?\"   # exit=2 beklenir"
echo "  echo '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"git status\"}}' | CLAUDE_PROJECT_DIR=\"$HEDEF\" python3 \"$HEDEF/.claude/hooks/silme_kilidi.py\"; echo \"exit=\$?\"   # exit=0 beklenir"
