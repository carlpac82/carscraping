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
    
    # Check if commissioner_settings table exists
    if 'sqlite' in db_type.lower():
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commissioner_settings'")
        table_exists = cursor.fetchone()
        if table_exists:
            print('Commissioner_settings table exists in SQLite')
        else:
            print('Commissioner_settings table does not exist in SQLite')
    else:
        # PostgreSQL
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'commissioner_settings')")
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print('Commissioner_settings table exists in PostgreSQL')
            
            # Get AUTO PRUDENTE and EXPOSE I settings
            cursor.execute('''
                SELECT c.id, c.username, cs.setting_key, cs.setting_value 
                FROM commissioners c 
                LEFT JOIN commissioner_settings cs ON c.id = cs.commissioner_id 
                WHERE c.username IN ('AUTO PRUDENTE', 'EXPOSE I') 
                ORDER BY c.username
            ''')
            results = cursor.fetchall()
            print('\nAUTO PRUDENTE and EXPOSE I settings:')
            for row in results:
                print(f'  ID: {row[0]}, Username: {row[1]}, Setting: {row[2]}, Value: {row[3]}')
                
            # Get all commissioners with Group A settings
            cursor.execute('''
                SELECT c.id, c.username, cs.setting_key, cs.setting_value 
                FROM commissioners c 
                LEFT JOIN commissioner_settings cs ON c.id = cs.commissioner_id 
                WHERE cs.setting_key = 'group_a_disabled'
                ORDER BY c.username
            ''')
            results = cursor.fetchall()
            print(f'\nFound {len(results)} commissioners with Group A settings:')
            for row in results:
                print(f'  ID: {row[0]}, Username: {row[1]}, Value: {row[3]}')
        else:
            print('Commissioner_settings table does not exist in PostgreSQL')
    
    conn.close()
    
    # Check global setting
    global_setting = _get_setting('group_a_disabled', 'false')
    print(f'\nGlobal group_a_disabled setting: {global_setting}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
