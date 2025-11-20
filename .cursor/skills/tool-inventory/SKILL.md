---
name: tool-inventory
description: Automatically check available scripts and tools before creating new ones. Use this when you need to execute bash, python, or npm scripts to avoid duplicating existing tools. This skill lists all tools in .claude/scripts/ and helps you discover reusable scripts.
---

# Tool Inventory Skill

## Purpose
This skill helps Claude discover and reuse existing scripts instead of creating duplicates.

## When to Use
- **Before creating any bash/python/npm script**
- When asked to execute common tasks (backup, deploy, test, etc.)
- When you're about to write a script that might already exist

## How It Works

### Step 1: Check Inventory
First, list all available tools:

```bash
# List bash scripts
ls -1 .claude/scripts/bash/*.sh 2>/dev/null || echo "No bash scripts yet"

# List python scripts
ls -1 .claude/scripts/python/*.py 2>/dev/null || echo "No python scripts yet"

# List npm scripts from package.json
if [ -f package.json ]; then
  cat package.json | grep -A 50 '"scripts"' | grep ':' || echo "No npm scripts"
fi
```

### Step 2: Read Script Documentation
Each script should have a header comment explaining:
- What it does
- What parameters it accepts
- Example usage

Use `head -n 20` to read script headers.

### Step 3: Decision
- If script exists: Use it!
- If script doesn't exist: Create it and save to appropriate directory

## Script Organization

### Bash Scripts (.claude/scripts/bash/)
Common operations:
- `odoo-restart.sh` - Restart Odoo service
- `db-backup.sh` - Backup PostgreSQL database
- `deploy.sh` - Deploy to server
- `health-check.sh` - Check all services

### Python Scripts (.claude/scripts/python/)
Python utilities:
- `odoo_module_creator.py` - Create Odoo modules
- `db_query.py` - Query database
- `log_analyzer.py` - Analyze Odoo logs

### NPM Scripts (package.json)
If project has Node.js, scripts like:
- `npm run test`
- `npm run lint`
- `npm run build`

## Best Practices

1. **Always check inventory first** before creating scripts
2. **Document new scripts** with clear header comments
3. **Make scripts reusable** with parameters instead of hardcoded values
4. **Use consistent naming** (verb-noun.sh/py pattern)
5. **Add executable permissions** to bash scripts

## Example Workflow

```markdown
User: "Create a script to restart Odoo"

Claude (thinking):
1. Check inventory first: ls .claude/scripts/bash/odoo-restart.sh
2. If exists: "I found an existing script! Let me use it."
3. If not exists: "Creating new script and saving to .claude/scripts/bash/"
```

## Script Template Header

Every new script should start with:

```bash
#!/bin/bash
# Script: script-name.sh
# Description: What this script does
# Usage: ./script-name.sh [param1] [param2]
# Author: Claude
# Created: YYYY-MM-DD
```

## Integration with Memory

New scripts should be documented in:
- `.claude/memory/commands/COMMAND-HISTORY.md` (if they use sudo or special permissions)
- `.claude/memory/learnings/` (if they solve a specific problem)
