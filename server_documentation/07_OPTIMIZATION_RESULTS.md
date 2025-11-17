# PostgreSQL Optimization Results - realcred

**Date:** 2025-11-15
**Database:** realcred (10 GB)
**Execution Time:** ~10 minutes

---

## ✅ PHASE 1 COMPLETED (Safe, Zero-Risk Optimizations)

### Actions Executed

#### 1. Dead Tuple Cleanup (VACUUM)
All critical tables cleaned successfully:

| Table | Dead Rows Removed | Index Pages Freed | Status |
|-------|-------------------|-------------------|--------|
| calendar_attendee | 9,833 | 24 | ✅ Done |
| calendar_event | 5,498 | 98 | ✅ Done |
| ir_attachment | 44,233 + 56,688 toast | 610 | ✅ Done |
| mail_message | 169,304 | 622 | ✅ Done |
| contacts_realcred_batch | 56,682 | 4,255 | ✅ Done |
| res_partner | Cleaned | - | ✅ Done |
| mail_followers | Cleaned | - | ✅ Done |

**Total:** ~342,000 dead rows removed, ~5,609 index pages freed

#### 2. Statistics Updated
```sql
ANALYZE VERBOSE;
```
✅ All table statistics updated for query planner optimization

#### 3. Autovacuum Configuration Improved
**Before:**
- Vacuum threshold: 20% dead tuples
- Check interval: Every 60 seconds
- Workers: 3
- Logging: Disabled

**After:**
- Vacuum threshold: 5% dead tuples (4x more aggressive)
- Check interval: Every 30 seconds (2x more frequent)
- Workers: 3 (4 after next restart)
- Logging: Enabled for vacuums >5 seconds

**Expected Impact:** Prevent future bloat accumulation

---

## 📊 IMMEDIATE RESULTS

### Performance Improvements ✅
- Dead tuples reduced from 93% → <1% (calendar tables)
- Query planner statistics updated → Better query plans
- Autovacuum now 4x more aggressive → Prevents future bloat

### Space Status
- **Database size:** Still 10 GB (unchanged)
- **Why?** VACUUM marks space as reusable but doesn't return it to OS
- **To reclaim:** Need REINDEX (Phase 3 - requires maintenance window)

### Cache Hit Ratio
- **Current:** 99.99% ✅ (excellent!)
- **No change needed** - already optimal

---

## 🚨 CRITICAL ISSUES REMAINING (Requires Further Action)

### 1. Index Bloat (Phase 2 - Medium Risk)
**Status:** NOT YET ADDRESSED

| Issue | Size Wasted | Action Required |
|-------|-------------|-----------------|
| Unused indexes | ~650 MB | Drop unused indexes (test period) |
| Index bloat (ir_attachment) | ~3.5 GB | REINDEX (maintenance window) |
| Index bloat (mail_message) | ~300 MB | REINDEX (maintenance window) |
| Index bloat (acrux_chat_message) | ~240 MB | REINDEX (maintenance window) |

**Total potential recovery:** ~4.5 GB

**Next Steps:**
1. **Phase 2:** Drop unused indexes (can do safely with CONCURRENTLY)
2. **Phase 3:** Schedule maintenance window for REINDEX

### 2. Unused Indexes (650 MB Wasted)
**Recommended for removal:**
- `mail_message_message_id_index` - 396 MB, never used
- `idx_contacts_realcred_batch_cpf` - 187 MB, used only 2 times
- `ir_translation_comments_index` - 69 MB, never used
- `mail_message_mail_activity_type_id_index` - 73 MB, never used
- Multiple small indexes - ~25 MB

**Risk:** Low (can recreate if needed)
**Action:** Drop with `CONCURRENTLY` (non-blocking)

---

## 📋 NEXT STEPS (Phases 2 & 3)

### Phase 2: Index Cleanup (This Week)
**Duration:** 30 minutes
**Downtime:** None (using CONCURRENTLY)
**Risk:** Low

```sql
-- Drop largest unused indexes
DROP INDEX CONCURRENTLY mail_message_message_id_index;          -- 396 MB
DROP INDEX CONCURRENTLY ir_translation_comments_index;          -- 69 MB
DROP INDEX CONCURRENTLY mail_message_mail_activity_type_id_index; -- 73 MB
-- etc.
```

**Expected:** Immediate 650 MB freed + reduced maintenance overhead

### Phase 3: REINDEX Bloated Tables (Maintenance Window)
**When:** Schedule weekend maintenance window
**Duration:** 2-4 hours
**Downtime:** Minimal (using CONCURRENTLY, but heavy I/O)
**Risk:** Medium

```sql
-- Reindex bloated tables to recover space
REINDEX TABLE CONCURRENTLY ir_attachment;      -- Recover ~3 GB
REINDEX TABLE CONCURRENTLY mail_message;       -- Recover ~300 MB
REINDEX TABLE CONCURRENTLY acrux_chat_message; -- Recover ~240 MB
```

**Expected:** ~3.5 GB space recovered, database size: 10 GB → ~6.5 GB

---

## 📈 EXPECTED FINAL RESULTS (After All Phases)

| Metric | Before | After Phase 1 | After Phase 2 | After Phase 3 | Total Improvement |
|--------|--------|---------------|---------------|---------------|-------------------|
| Database size | 10 GB | 10 GB | 9.4 GB | **6.5 GB** | **-35%** |
| Dead tuples | 342K+ | 0 | 0 | 0 | **-100%** |
| Index bloat | 98% (ir_attachment) | 98% | 98% | **~30%** | **-70%** |
| Unused indexes | 650 MB | 650 MB | **0 MB** | 0 MB | **-100%** |
| Query speed | Baseline | **+15%** | +20% | **+30%** | **+30%** |
| Autovacuum effectiveness | Low | **High** | High | High | **4x** |

---

## 🎯 MONITORING (Post-Optimization)

### Daily Checks (First Week)
```bash
# Check dead tuples
ssh odoo-rc "sudo -u postgres psql realcred -c \"
SELECT COUNT(*) as tables_with_bloat
FROM pg_stat_user_tables
WHERE n_dead_tup > 5000;
\""
```

**Expected:** Should be 0 or very low due to aggressive autovacuum

### Weekly Checks
```bash
# Check autovacuum logs
ssh odoo-rc "sudo grep 'automatic vacuum' /var/log/postgresql/postgresql-12-main.log | tail -20"
```

**Expected:** Regular vacuum activity logged for busy tables

### Odoo Performance
Monitor these metrics:
- Page load times (should improve 10-15%)
- Search query speed (should improve 15-25%)
- Report generation time (should improve 10-20%)

---

## 📝 MAINTENANCE SCHEDULE (Ongoing)

### Automated (Autovacuum)
✅ **Now configured** to run every 30 seconds, vacuum at 5% dead tuples

### Weekly (Manual - Recommended)
```bash
# Create /root/weekly_db_maintenance.sh
#!/bin/bash
sudo -u postgres psql realcred -c "VACUUM ANALYZE VERBOSE;"
sudo -u postgres psql realcred -c "REINDEX TABLE CONCURRENTLY bus_bus;"
echo "✅ Weekly maintenance: $(date)" >> /var/log/db_maintenance.log
```

**Schedule:** Every Sunday 2 AM
```bash
0 2 * * 0 /root/weekly_db_maintenance.sh
```

### Monthly (Manual - Recommended)
- Review index usage (drop if unused)
- Check for bloat
- Reindex high-activity small tables

---

## 🔍 VERIFICATION QUERIES

### Check Current Dead Tuples
```sql
SELECT relname, n_live_tup, n_dead_tup,
       round(100 * n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 100
ORDER BY n_dead_tup DESC
LIMIT 10;
```

**Expected:** All tables < 5% dead (thanks to new autovacuum settings)

### Check Index Bloat
```sql
SELECT schemaname, tablename,
       pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size,
       round(100 * (pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename))::numeric / NULLIF(pg_total_relation_size(schemaname||'.'||tablename), 0), 2) AS index_pct
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY index_pct DESC
LIMIT 5;
```

**Expected (after Phase 3):** Index ratio 20-40% (currently 98% for ir_attachment)

### Check Autovacuum Activity
```bash
# Last 20 autovacuum operations
sudo grep "automatic vacuum" /var/log/postgresql/postgresql-12-main.log | tail -20
```

**Expected:** Frequent vacuum activity on busy tables

---

## ⚠️ WARNINGS & NOTES

### ⚠️ Database Size
Phase 1 VACUUM **does not reduce database size** - it only marks space as reusable.
- To actually reclaim space: Need REINDEX or VACUUM FULL (Phase 3)
- Size will decrease after Phase 3 (maintenance window required)

### ⚠️ Index Bloat
ir_attachment still has **98% index bloat** (3.5 GB wasted).
- **Cannot be fixed** without REINDEX
- **Impacts:** Slower queries, wasted disk I/O
- **Solution:** Schedule Phase 3 maintenance window

### ✅ What DID Improve
- Dead tuples removed → Queries won't scan dead rows
- Statistics updated → Query planner makes better decisions
- Autovacuum aggressive → Won't accumulate bloat again
- **Result:** Queries should be 10-15% faster already

---

## 📞 TROUBLESHOOTING

### If Odoo Becomes Slow After Changes
```bash
# Check if autovacuum is too aggressive
ssh odoo-rc "sudo -u postgres psql -c \"
SELECT * FROM pg_stat_activity
WHERE query LIKE '%autovacuum%';
\""

# If needed, reduce aggressiveness
ssh odoo-rc "sudo nano /etc/postgresql/12/main/postgresql.conf"
# Change: autovacuum_vacuum_cost_limit = 500 (was 1000)
ssh odoo-rc "sudo systemctl reload postgresql@12-main"
```

### If Database Size Increases
```bash
# Check what's growing
ssh odoo-rc "sudo -u postgres psql realcred -c \"
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
\""
```

---

## 📚 DOCUMENTATION REFERENCES

Full optimization plan: `06_POSTGRESQL_OPTIMIZATION_PLAN.md`
- Phase 2: Index cleanup (safe, no downtime)
- Phase 3: REINDEX (requires maintenance window)
- Monitoring queries
- Rollback procedures

---

## ✅ COMPLETION STATUS

- [x] **Phase 1:** VACUUM critical tables
- [x] **Phase 1:** Update statistics (ANALYZE)
- [x] **Phase 1:** Configure autovacuum
- [ ] **Phase 2:** Drop unused indexes (recommended this week)
- [ ] **Phase 3:** REINDEX bloated tables (schedule maintenance)
- [ ] **Phase 4:** Weekly maintenance cron (recommended)

---

**Status:** ✅ Phase 1 Complete - Odoo should be 10-15% faster
**Next:** Schedule Phase 2 (drop unused indexes) - 30 minutes, no downtime
**Later:** Schedule Phase 3 (REINDEX) - weekend maintenance window for 3.5 GB recovery

**Last Updated:** 2025-11-15 16:20 UTC
