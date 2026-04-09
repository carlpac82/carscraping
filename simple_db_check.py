#!/usr/bin/env python3

import sys
sys.path.append('.')

try:
    from main import _db_connect, _get_setting
    
    # Test database connection
    conn = _db_connect()
    cursor = conn.cursor()
    
    # Check database type
    db_type = type(conn).__name__
    print(f"Database type: {db_type}")
    
    # Check if commissioners table exists
    if 'sqlite' in db_type.lower():
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commissioners'")
        table_exists = cursor.fetchone()
        if table_exists:
            print('Commissioners table exists in SQLite')
            cursor.execute('SELECT id, username FROM commissioners ORDER BY username')
            commissioners = cursor.fetchall()
            print(f'Found {len(commissioners)} commissioners:')
            for comm in commissioners:
                print(f'  ID: {comm[0]}, Username: {comm[1]}')
        else:
            print('Commissioners table does not exist in SQLite')
    else:
        # PostgreSQL
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'commissioners')")
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print('Commissioners table exists in PostgreSQL')
            cursor.execute('SELECT id, username FROM commissioners ORDER BY username')
            commissioners = cursor.fetchall()
            print(f'Found {len(commissioners)} commissioners:')
            for comm in commissioners:
                print(f'  ID: {comm[0]}, Username: {comm[1]}')
        else:
            print('Commissioners table does not exist in PostgreSQL')
    
    conn.close()
    
    # Check global setting
    global_setting = _get_setting('group_a_disabled', 'false')
    print(f'Global group_a_disabled setting: {global_setting}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
