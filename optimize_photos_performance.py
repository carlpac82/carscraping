#!/usr/bin/env python3
"""Optimize inspection photos performance"""

import psycopg2
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

cur = conn.cursor()

print("🔧 OPTIMIZING INSPECTION PHOTOS PERFORMANCE...")

# 1. Add index on inspection_id (if not exists)
print("\n1️⃣ Creating index on inspection_photos.inspection_id...")
cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_inspection_photos_inspection_id 
    ON inspection_photos(inspection_id)
""")
print("   ✅ Done")

# 2. Add index on photo_type
print("\n2️⃣ Creating index on inspection_photos.photo_type...")
cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_inspection_photos_photo_type 
    ON inspection_photos(photo_type)
""")
print("   ✅ Done")

# 3. Add composite index for common queries
print("\n3️⃣ Creating composite index on (inspection_id, photo_type)...")
cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_inspection_photos_inspection_photo_type 
    ON inspection_photos(inspection_id, photo_type)
""")
print("   ✅ Done")

# 4. Check table size
print("\n📊 TABLE SIZES:")
cur.execute("""
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
    FROM pg_tables
    WHERE schemaname = 'public'
        AND tablename LIKE '%photo%'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
""")
for schema, table, size in cur.fetchall():
    print(f"   {table:40s}: {size}")

conn.commit()
cur.close()
conn.close()

print("\n✅ OPTIMIZATION COMPLETE!")
print("\n⚠️  RECOMMENDATION: Consider moving images to S3/Cloudinary")
print("   Current DB size (12 GB) is too large for Railway free tier")
