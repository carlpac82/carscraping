#!/usr/bin/env python3
"""Check PostgreSQL performance and active connections"""

import psycopg2
import os
from urllib.parse import urlparse

DATABASE_URL = "postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway"

result = urlparse(DATABASE_URL)
conn = psycopg2.connect(
    host=result.hostname,
    port=result.port,
    database=result.path[1:],
    user=result.username,
    password=result.password,
    sslmode='prefer',
    connect_timeout=10
)

print("=" * 60)
print("📊 POSTGRESQL PERFORMANCE CHECK")
print("=" * 60)

# 1. Active connections
cur = conn.cursor()
cur.execute("""
    SELECT 
        state,
        COUNT(*) as count,
        MAX(EXTRACT(EPOCH FROM (NOW() - state_change))) as max_duration_sec
    FROM pg_stat_activity
    WHERE datname = 'railway'
    GROUP BY state
    ORDER BY count DESC
""")
print("\n🔌 ACTIVE CONNECTIONS:")
for row in cur.fetchall():
    state, count, max_duration = row
    print(f"  {state or 'NULL':20s}: {count:3d} conexões (max {max_duration:.1f}s)")

# 2. Long running queries
cur.execute("""
    SELECT 
        pid,
        state,
        EXTRACT(EPOCH FROM (NOW() - query_start)) as duration_sec,
        LEFT(query, 100) as query_preview
    FROM pg_stat_activity
    WHERE datname = 'railway'
        AND state != 'idle'
        AND query NOT LIKE '%pg_stat_activity%'
    ORDER BY duration_sec DESC
    LIMIT 10
""")
print("\n⏱️  LONG RUNNING QUERIES:")
rows = cur.fetchall()
if rows:
    for pid, state, duration, query in rows:
        print(f"  PID {pid}: {duration:.1f}s - {state}")
        print(f"    {query}...")
else:
    print("  ✅ Nenhuma query lenta")

# 3. Total connections vs limit
cur.execute("SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'railway'")
total = cur.fetchone()[0]
print(f"\n📈 TOTAL CONNECTIONS: {total}/~50 (Railway limit)")

# 4. Database size
cur.execute("SELECT pg_size_pretty(pg_database_size('railway'))")
size = cur.fetchone()[0]
print(f"💾 DATABASE SIZE: {size}")

# 5. Slow queries from pg_stat_statements (if available)
try:
    cur.execute("""
        SELECT 
            LEFT(query, 80) as query,
            calls,
            ROUND(mean_exec_time::numeric, 2) as avg_ms,
            ROUND(max_exec_time::numeric, 2) as max_ms
        FROM pg_stat_statements
        WHERE mean_exec_time > 100
        ORDER BY mean_exec_time DESC
        LIMIT 5
    """)
    print("\n🐌 SLOWEST QUERIES (avg > 100ms):")
    for query, calls, avg_ms, max_ms in cur.fetchall():
        print(f"  {avg_ms}ms avg ({max_ms}ms max) - {calls} calls")
        print(f"    {query}...")
except:
    print("\n⚠️  pg_stat_statements not available")

cur.close()
conn.close()

print("\n" + "=" * 60)
