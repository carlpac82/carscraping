import psycopg2
from commissioners_api import get_vehicle_groups_with_photos_v2

# Connect to database
conn = psycopg2.connect("postgresql://postgres:OMxLodDbSGnDJUQGVIkXSXYxfiRwQqFo@shortline.proxy.rlwy.net:45408/railway")

print("Testing get_vehicle_groups_with_photos_v2()...")
groups = get_vehicle_groups_with_photos_v2(conn)

print(f"\nReturned {len(groups)} groups:")
for group in groups:
    print(f"  {group}")

conn.close()
