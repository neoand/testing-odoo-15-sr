---
name: odoo-ops
description: Automatically handle Odoo server operations like restart, logs, status checks, and service management. Use when user mentions Odoo services, checking logs, restarting server, or troubleshooting Odoo issues.
allowed-tools: |
  Bash(sudo systemctl:*),
  Bash(gcloud compute ssh:*),
  Bash(ssh:*),
  Read(*.log)
---

# Odoo Operations Skill

## Purpose
Automate common Odoo server operations across both testing and production environments.

## Server Context

### Testing Server (odoo-sr-tensting)
- **Access:** `gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b`
- **Service:** `odoo` or `odoo-server`
- **Logs:** `/var/log/odoo/odoo-server.log`

### Production Server (odoo-rc)
- **Access:** `ssh odoo-rc` or `ssh andlee21@35.199.79.229`
- **Service:** `odoo-server`
- **Logs:** `/var/log/odoo/odoo-server.log`

## Common Operations

### 1. Check Odoo Status

**Testing:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo systemctl status odoo"
```

**Production:**
```bash
ssh odoo-rc "sudo systemctl status odoo-server"
```

### 2. Restart Odoo

**Testing:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo systemctl restart odoo"
```

**Production:**
```bash
ssh odoo-rc "sudo systemctl restart odoo-server"
```

### 3. View Logs (real-time)

**Testing:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo tail -f /var/log/odoo/odoo-server.log"
```

**Production:**
```bash
ssh odoo-rc "sudo tail -f /var/log/odoo/odoo-server.log"
```

### 4. View Last 100 Log Lines

**Testing:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo tail -n 100 /var/log/odoo/odoo-server.log"
```

**Production:**
```bash
ssh odoo-rc "sudo tail -n 100 /var/log/odoo/odoo-server.log"
```

### 5. Check PostgreSQL Status

**Testing:**
```bash
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b --command="sudo systemctl status postgresql"
```

**Production:**
```bash
ssh odoo-rc "sudo systemctl status postgresql@12-main"
```

### 6. Check All Services

**Production (Complete Check):**
```bash
ssh odoo-rc "sudo systemctl status odoo-server postgresql@12-main nginx"
```

### 7. Restart All Services (Safe Order)

**Production:**
```bash
ssh odoo-rc "sudo systemctl restart postgresql@12-main && sleep 5 && sudo systemctl restart odoo-server && sudo systemctl restart nginx"
```

## Troubleshooting Patterns

### Odoo Not Starting
1. Check PostgreSQL first: `systemctl status postgresql`
2. Check logs for errors: `tail -n 200 /var/log/odoo/odoo-server.log`
3. Check config file: `/etc/odoo-server.conf`
4. Check permissions: `ls -la /odoo/`

### Performance Issues
1. Check RAM usage: `free -h`
2. Check disk space: `df -h`
3. Check Odoo workers: `ps aux | grep odoo`
4. Check database connections: `sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"`

### Log Analysis
Common errors to look for:
- `OperationalError` - Database connection issues
- `MemoryError` - Out of memory
- `PermissionError` - File/directory permission issues
- `ModuleNotFoundError` - Missing Python dependencies

## Safety Rules

1. **Always check status before restarting**
2. **PostgreSQL must start before Odoo**
3. **Wait 5 seconds between service restarts**
4. **Never force kill (-9) unless absolutely necessary**
5. **Always check logs after restart**

## Script Reference

Before creating new scripts, check if these exist:
- `.claude/scripts/bash/odoo-restart.sh`
- `.claude/scripts/bash/odoo-logs.sh`
- `.claude/scripts/bash/odoo-health-check.sh`

Use the `tool-inventory` skill to check availability.

## Memory Integration

- Document successful troubleshooting in `.claude/memory/errors/ERRORS-SOLVED.md`
- Save new sudo patterns in `.claude/memory/commands/COMMAND-HISTORY.md`
- Record server-specific quirks in `.claude/memory/context/servidores.md`
