# PostgreSQL Optimization Plan - realcred Database

**Date:** 2025-11-15
**Database:** realcred (10 GB)
**System:** PostgreSQL 12 on odoo-rc

---

## 🚨 CRITICAL ISSUES FOUND

### 1. **SEVERE INDEX BLOAT** (Priority: CRITICAL)
**Impact:** Wasting ~3.5 GB of storage, slowing down queries

| Table | Total Size | Table Data | Index Size | Index Ratio | Status |
|-------|------------|------------|------------|-------------|--------|
| ir_attachment | 3.6 GB | 73 MB | 3.5 GB | **98%** | 🔴 CRITICAL |
| acrux_chat_message | 298 MB | 27 MB | 271 MB | **91%** | 🔴 CRITICAL |
| bus_bus | 23 MB | 48 KB | 22 MB | **99.8%** | 🔴 CRITICAL |
| crm_lead | 78 MB | 19 MB | 60 MB | **76%** | 🟡 HIGH |

**Normal index ratio:** 20-40%
**Current:** Up to 99.8%!

### 2. **MASSIVE DEAD TUPLES** (Priority: CRITICAL)
**Impact:** Wasting space, preventing index usage, slowing queries

| Table | Live Rows | Dead Rows | Dead % | Status |
|-------|-----------|-----------|--------|--------|
| calendar_attendee | 166 | 2,125 | **93%** | 🔴 CRITICAL |
| calendar_event | 144 | 1,921 | **93%** | 🔴 CRITICAL |
| ir_attachment | 7,178 | 5,111 | **42%** | 🔴 HIGH |
| res_partner | 232K | 44K | **16%** | 🟡 MEDIUM |
| mail_followers | 425K | 54K | **11%** | 🟡 MEDIUM |

**Cause:** Autovacuum not aggressive enough for Odoo workload.

### 3. **UNUSED INDEXES** (Priority: HIGH)
**Impact:** Wasting ~1 GB storage + maintenance overhead

| Index | Size | Scans | Status |
|-------|------|-------|--------|
| mail_message_message_id_index | 396 MB | 0 | NEVER USED |
| idx_contacts_realcred_batch_cpf | 187 MB | 2 | BARELY USED |
| mail_message_model_index | 101 MB | 82 | RARELY USED |
| ir_translation_comments_index | 69 MB | 0 | NEVER USED |
| mail_message_mail_activity_type_id_index | 73 MB | 0 | NEVER USED |
| ir_attachment_checksum_index | 23 MB | 0 | NEVER USED |
| mail_message_pkey | 63 MB | 0 | DUPLICATE (see note) |

**Note:** `mail_message_pkey` is not used because `idx_mail_message_id` exists and is used instead (1B+ scans). This is a duplicate index situation.

### 4. **SUBOPTIMAL AUTOVACUUM SETTINGS** (Priority: HIGH)
**Impact:** Delays cleanup, allows bloat to accumulate

Current settings are PostgreSQL defaults, not tuned for Odoo:
- `autovacuum_vacuum_scale_factor = 0.2` (20% dead tuples required)
- `autovacuum_naptime = 60s` (checks only every minute)
- `autovacuum_max_workers = 3` (could be higher)
- `log_autovacuum_min_duration = -1` (no logging)

**Result:** Tables like `calendar_attendee` reach 93% dead tuples before cleanup!

---

## 📊 CURRENT DATABASE STATS

### Performance Metrics
- **Cache hit ratio:** 99.99% ✅ (excellent!)
- **Temp files created:** 10,978 (16 GB) ⚠️ (suggests low work_mem)
- **Current connections:** 23 ✅
- **Commits:** 78M
- **Rollbacks:** 13M (17% rollback ratio) ⚠️

### Size Breakdown
- **Total database:** 10 GB
- **Largest table data:** mail_message (1.2 GB)
- **Largest indexes:** ir_attachment indexes (3.5 GB - BLOATED!)
- **Wasted space estimate:** 3-4 GB in bloat

---

## 🎯 OPTIMIZATION PLAN

### Phase 1: IMMEDIATE FIXES (Safe, High-Impact)

#### 1.1. Vacuum Critical Tables (SAFE)
```sql
-- Vacuum tables with highest dead tuple count
VACUUM VERBOSE ANALYZE calendar_attendee;
VACUUM VERBOSE ANALYZE calendar_event;
VACUUM VERBOSE ANALYZE ir_attachment;
VACUUM VERBOSE ANALYZE mail_message;
VACUUM VERBOSE ANALYZE res_partner;
VACUUM VERBOSE ANALYZE mail_followers;
```

**Expected:** Recover ~500 MB, improve query speed
**Downtime:** None
**Risk:** None

#### 1.2. Update Table Statistics (SAFE)
```sql
-- Update query planner statistics
ANALYZE VERBOSE;
```

**Expected:** Better query plans, faster queries
**Downtime:** None
**Risk:** None

#### 1.3. Improve Autovacuum Settings (SAFE)
Add to `/etc/postgresql/12/main/postgresql.conf`:

```ini
# More aggressive autovacuum for Odoo
autovacuum_vacuum_scale_factor = 0.05       # Vacuum at 5% dead (was 20%)
autovacuum_analyze_scale_factor = 0.05      # Analyze at 5% changes
autovacuum_vacuum_cost_limit = 1000         # Faster vacuum (was -1)
autovacuum_naptime = 30                     # Check every 30s (was 60s)
autovacuum_max_workers = 4                  # More workers (was 3)

# Log slow autovacuums for monitoring
log_autovacuum_min_duration = 5000          # Log vacuums taking > 5s
```

**Expected:** Prevent future bloat
**Downtime:** Reload config (no restart needed)
**Risk:** Very low

---

### Phase 2: INDEX CLEANUP (Medium Risk, High Impact)

#### 2.1. Drop Unused Indexes (REQUIRES TESTING)

**⚠️ WARNING:** Test in low-traffic period first. Can always recreate if needed.

```sql
-- Drop completely unused indexes (0 scans)
DROP INDEX CONCURRENTLY mail_message_message_id_index;          -- 396 MB
DROP INDEX CONCURRENTLY ir_translation_comments_index;          -- 69 MB
DROP INDEX CONCURRENTLY mail_message_mail_activity_type_id_index; -- 73 MB
DROP INDEX CONCURRENTLY ir_attachment_checksum_index;           -- 23 MB

-- Drop barely used indexes (< 10 scans)
DROP INDEX CONCURRENTLY crm_lead_date_last_stage_update_index;  -- 7 MB, 0 scans
DROP INDEX CONCURRENTLY crm_lead_name_index;                    -- 4 MB, 0 scans
DROP INDEX CONCURRENTLY crm_lead_website_index;                 -- 2 MB, 0 scans
DROP INDEX CONCURRENTLY crm_lead_company_id_index;              -- 2 MB, 0 scans
DROP INDEX CONCURRENTLY crm_lead_priority_index;                -- 2 MB, 0 scans
DROP INDEX CONCURRENTLY crm_lead_email_from_index;              -- 2 MB, 0 scans

-- res_partner unused indexes
DROP INDEX CONCURRENTLY res_partner_company_id_index;           -- 12 MB, 0 scans
DROP INDEX CONCURRENTLY res_partner_website_id_index;           -- 11 MB, 0 scans
DROP INDEX CONCURRENTLY res_partner_date_index;                 -- 11 MB, 0 scans
DROP INDEX CONCURRENTLY res_partner_vat_index;                  -- 11 MB, 0 scans
DROP INDEX CONCURRENTLY res_partner_ref_index;                  -- 11 MB, 0 scans
```

**Expected Recovery:** ~650 MB immediately
**Downtime:** None (CONCURRENTLY)
**Risk:** Medium - monitor for 1 week, recreate if needed

#### 2.2. Investigate Duplicate Index
```sql
-- Check if mail_message_pkey is truly unused vs idx_mail_message_id
-- DO NOT DROP YET - investigate why primary key not used
```

---

### Phase 3: REINDEX BLOATED TABLES (Requires Downtime Window)

#### 3.1. Reindex Severely Bloated Tables

**⚠️ REQUIRES MAINTENANCE WINDOW** - Schedule during low-traffic period.

```sql
-- Reindex bloated tables to recover space
REINDEX TABLE CONCURRENTLY ir_attachment;      -- Recover ~3 GB
REINDEX TABLE CONCURRENTLY mail_message;       -- Recover ~300 MB
REINDEX TABLE CONCURRENTLY acrux_chat_message; -- Recover ~240 MB
REINDEX TABLE CONCURRENTLY bus_bus;            -- Recover ~22 MB
```

**Expected Recovery:** ~3.5 GB
**Duration:** 1-4 hours depending on table
**Downtime:** Minimal with CONCURRENTLY, but heavy I/O
**Risk:** Medium - test in maintenance window

#### 3.2. Full Vacuum for Maximum Recovery (REQUIRES DOWNTIME)

**Only if above steps insufficient:**

```sql
-- Stop Odoo first!
VACUUM FULL VERBOSE ir_attachment;
VACUUM FULL VERBOSE mail_message;
```

**Expected Recovery:** Maximum space reclaim
**Downtime:** YES - Table locked during operation
**Duration:** 2-6 hours
**Risk:** High - only use as last resort

---

### Phase 4: ONGOING MAINTENANCE

#### 4.1. Weekly Maintenance Script
```bash
#!/bin/bash
# /root/weekly_db_maintenance.sh

# Vacuum analyze all tables
sudo -u postgres psql realcred -c "VACUUM ANALYZE VERBOSE;"

# Reindex small high-activity tables
sudo -u postgres psql realcred -c "REINDEX TABLE CONCURRENTLY bus_bus;"
sudo -u postgres psql realcred -c "REINDEX TABLE CONCURRENTLY calendar_event;"
sudo -u postgres psql realcred -c "REINDEX TABLE CONCURRENTLY calendar_attendee;"

echo "✅ Weekly maintenance completed: $(date)"
```

**Schedule:** Every Sunday 2 AM
```bash
0 2 * * 0 /root/weekly_db_maintenance.sh >> /var/log/db_maintenance.log 2>&1
```

#### 4.2. Monthly Deep Maintenance
```bash
#!/bin/bash
# /root/monthly_db_maintenance.sh

# Check for bloat
sudo -u postgres psql realcred -c "
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
  AND pg_total_relation_size(schemaname||'.'||tablename) > 104857600
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Reindex large tables
sudo -u postgres psql realcred -c "REINDEX TABLE CONCURRENTLY contacts_realcred_batch;"

echo "✅ Monthly maintenance completed: $(date)"
```

**Schedule:** First Sunday of month, 2 AM

#### 4.3. Monitoring Queries

**Check dead tuples:**
```sql
SELECT schemaname, relname, n_live_tup, n_dead_tup,
       round(100 * n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY dead_pct DESC;
```

**Check index bloat:**
```sql
SELECT schemaname, tablename,
       pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size,
       round(100 * (pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename))::numeric / NULLIF(pg_total_relation_size(schemaname||'.'||tablename), 0), 2) AS index_pct
FROM pg_tables
WHERE schemaname = 'public'
  AND pg_total_relation_size(schemaname||'.'||tablename) > 10485760
ORDER BY index_pct DESC
LIMIT 10;
```

**Check unused indexes:**
```sql
SELECT schemaname, relname, indexrelname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size,
       idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan < 100
  AND pg_relation_size(indexrelid) > 10485760
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## 📋 EXECUTION CHECKLIST

### Before Starting
- [ ] Backup database: `pg_dump -Fc realcred > backup_pre_optimization.dump`
- [ ] Verify backup: `pg_restore -l backup_pre_optimization.dump`
- [ ] Document current sizes (completed above)
- [ ] Notify team of maintenance window

### Phase 1 (Safe - Can Do Now)
- [ ] Run VACUUM ANALYZE on critical tables
- [ ] Update autovacuum configuration
- [ ] Reload PostgreSQL config
- [ ] Monitor autovacuum logs for 24 hours

### Phase 2 (Test Period Required)
- [ ] Drop unused indexes (one at a time)
- [ ] Monitor for 7 days
- [ ] Check Odoo logs for errors
- [ ] Recreate if issues found

### Phase 3 (Maintenance Window)
- [ ] Schedule low-traffic window (weekend)
- [ ] Notify users
- [ ] Execute REINDEX CONCURRENTLY
- [ ] Monitor duration and I/O

### Post-Optimization
- [ ] Verify database size reduction
- [ ] Check Odoo performance (page load times)
- [ ] Monitor autovacuum logs
- [ ] Document results

---

## 🎯 EXPECTED RESULTS

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Database size | 10 GB | ~6.5 GB | **35% reduction** |
| Index bloat (ir_attachment) | 98% | ~30% | **Recovery of 3 GB** |
| Dead tuples (calendar tables) | 93% | <5% | **Cleanup 99%** |
| Unused indexes | 650 MB | 0 MB | **650 MB freed** |
| Query performance | Baseline | +20-40% | **Faster queries** |
| Odoo page loads | Baseline | +15-30% | **Faster UI** |

---

## ⚠️ RISKS & MITIGATION

### Risk 1: Index Drop Breaks Queries
**Mitigation:**
- Drop with CONCURRENTLY (non-blocking)
- Monitor for 7 days
- Recreate if needed: `CREATE INDEX CONCURRENTLY ...`

### Risk 2: REINDEX Takes Too Long
**Mitigation:**
- Use CONCURRENTLY option
- Schedule during low-traffic
- Monitor progress: `SELECT * FROM pg_stat_progress_create_index;`

### Risk 3: Disk Space During VACUUM FULL
**Mitigation:**
- Ensure 15 GB free space
- Use regular VACUUM + REINDEX instead
- Or: drop/recreate table in chunks

---

## 📞 ROLLBACK PROCEDURES

### If Index Drop Causes Issues
```sql
-- Recreate specific index
CREATE INDEX CONCURRENTLY mail_message_message_id_index
ON mail_message(message_id);
```

### If Performance Degrades
```sql
-- Restore previous autovacuum settings
ALTER SYSTEM RESET autovacuum_vacuum_scale_factor;
ALTER SYSTEM RESET autovacuum_naptime;
SELECT pg_reload_conf();
```

### If Critical Failure
```bash
# Restore from backup
sudo systemctl stop odoo-server
sudo -u postgres dropdb realcred
sudo -u postgres createdb -O odoo realcred
sudo -u postgres pg_restore -d realcred backup_pre_optimization.dump
sudo systemctl start odoo-server
```

---

## 📈 MONITORING POST-OPTIMIZATION

### Daily (First Week)
```bash
# Check dead tuples
sudo -u postgres psql realcred -c "
SELECT COUNT(*) FROM pg_stat_user_tables WHERE n_dead_tup > 5000;
"

# Check database size
sudo -u postgres psql -c "
SELECT pg_size_pretty(pg_database_size('realcred'));
"
```

### Weekly (First Month)
- Review autovacuum logs: `sudo grep autovacuum /var/log/postgresql/*.log`
- Check Odoo error logs: `sudo grep -i index /var/log/odoo/odoo-server.log`
- Measure query performance: Check slowest queries

### Monthly (Ongoing)
- Run bloat check queries
- Review unused indexes report
- Update optimization plan

---

## 🔗 REFERENCES

- PostgreSQL Autovacuum Tuning: https://www.postgresql.org/docs/12/routine-vacuuming.html
- Odoo Database Optimization: https://www.odoo.com/documentation/15.0/administration/maintain/postgresql.html
- Index Bloat Management: https://wiki.postgresql.org/wiki/Index_Maintenance

---

**Created:** 2025-11-15
**Next Review:** 2025-11-22
**Status:** READY FOR EXECUTION
