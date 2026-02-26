import sys
sys.path.insert(0, '/Users/filipepacheco/CascadeProjects/carscraping')

from database import _db_connect, _db_lock

with _db_lock:
    conn = _db_connect()
    try:
        if hasattr(conn, '_conn'):
            # PostgreSQL
            with conn._conn.cursor() as cur:
                cur.execute("SELECT username, first_name, last_name FROM users WHERE username = %s", ('admin',))
                result = cur.fetchone()
                print(f"PostgreSQL - User data: {result}")
        else:
            # SQLite
            cur = conn.execute("SELECT username, first_name, last_name FROM users WHERE username = ?", ('admin',))
            result = cur.fetchone()
            print(f"SQLite - User data: {result}")
    finally:
        conn.close()
