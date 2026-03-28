import psycopg2

# Connect to database
conn = psycopg2.connect("postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway")
cursor = conn.cursor()

print("Connected to database")

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS car_groups (
        code VARCHAR(10) PRIMARY KEY,
        brand VARCHAR(100),
        model VARCHAR(100),
        photo_url TEXT,
        enabled INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
print("Table created/verified")

# Delete existing data
cursor.execute("DELETE FROM car_groups")
print("Existing data cleared")

# Insert vehicle groups
groups_data = [
    ('A', 'KIA', 'PICANTO', '', 1),
    ('B', 'FIAT', 'PANDA', '', 1),
    ('B1', 'FIAT', 'PANDA', '', 1),
    ('B2', 'FIAT', 'PANDA', '', 1),
    ('D', 'SEAT', 'IBIZA', '', 1),
    ('E1', 'HYUNDAI', 'i10', '', 1),
    ('E2', 'CITROEN', 'C3', '', 1),
    ('F', 'SEAT', 'ARONA', '', 1),
    ('G', 'FIAT', '500 CABRIO', '', 1),
    ('J1', 'PEUGEOT', '2008', '', 1),
    ('J2', 'PEUGEOT', '308 SW', '', 1),
    ('L1', 'CITROEN', 'C3 AIRCROSS', '', 1),
    ('L2', 'PEUGEOT', '308 SW', '', 1),
    ('M1', 'DACIA', 'JOGGER', '', 1),
    ('M2', 'CITROEN', 'C4 PICASSO', '', 1),
    ('N', 'TOYOTA', 'PROACE', '', 1)
]

cursor.executemany("""
    INSERT INTO car_groups (code, brand, model, photo_url, enabled)
    VALUES (%s, %s, %s, %s, %s)
""", groups_data)

print(f"Inserted {len(groups_data)} groups")

# Commit changes
conn.commit()

# Verify insertion
cursor.execute("SELECT code, brand, model, enabled FROM car_groups ORDER BY code")
rows = cursor.fetchall()

print(f"\nVerification - Total groups in database: {len(rows)}")
for row in rows:
    print(f"  {row[0]}: {row[1]} {row[2]} (enabled={row[3]})")

cursor.close()
conn.close()

print("\nDone! car_groups table populated successfully.")
