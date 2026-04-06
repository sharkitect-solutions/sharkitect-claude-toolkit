---
alwaysApply: true
---

# API & MCP Limitation Protocol

When you encounter or recall that an API or MCP tool does not support an operation:

1. **Never just say "not supported" and stop.** Always provide a manual workaround.
2. Check `~/.claude/lessons-learned.md` under "## API Limitations" for documented solutions.
3. If a solution exists: follow it exactly (rename with prefix, add to HUMAN-ACTION-REQUIRED.md, provide step-by-step UI instructions).
4. If no solution exists: provide best-guess manual instructions AND ask: "This appears to be an API limitation. Should I add it to lessons-learned.md so all future sessions know about it?"
5. When writing manual instructions, be specific: include exact UI navigation paths, button names, and field values.

## Known Limitations (check lessons-learned.md for full list)

- **Airtable**: Cannot create formula, rollup, or lookup fields via API/MCP. Provide Airtable UI steps.
- **Airtable**: Cannot delete tables via API. Rename with `DEPRECATED_` prefix, add to HUMAN-ACTION-REQUIRED.md.
- **Airtable**: Cannot delete fields/columns via API. Document for manual deletion in Airtable UI.