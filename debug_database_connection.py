#!/usr/bin/env python3
import os
import sys
sys.path.append('.')

# Import database connection
from database import DatabaseConnection, USE_POSTGRES, DATABASE_URL

def debug_database():
    print(f"DATABASE_URL: {DATABASE_URL}")
    print(f"USE_POSTGRES: {USE_POSTGRES}")
    
    try:
        db = DatabaseConnection()
        conn = db.connect()
        
        if USE_POSTGRES:
            import psycopg2
            cursor = conn.cursor()
            
            # Check if commissioners table exists
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'commissioners')")
            if cursor.fetchone()[0]:
                print('Commissioners table exists in PostgreSQL')
                
                # Get commissioners
                cursor.execute('SELECT id, username FROM commissioners ORDER BY username')
                commissioners = cursor.fetchall()
                print(f'Found {len(commissioners)} commissioners:')
                for comm in commissioners:
                    print(f'  ID: {comm[0]}, Username: {comm[1]}')
                
                # Check if commissioner_settings table exists
                cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'commissioner_settings')")
                if cursor.fetchone()[0]:
                    print('Commissioner_settings table exists')
                    
                    # Get Group A settings for AUTO PRUDENTE and EXPOSE I
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
                        
                    # Check global settings
                    cursor.execute("SELECT setting_key, setting_value FROM settings WHERE setting_key = 'group_a_disabled'")
                    global_setting = cursor.fetchone()
                    print(f'\nGlobal group_a_disabled setting: {global_setting}')
                else:
                    print('Commissioner_settings table does not exist')
            else:
                print('Commissioners table does not exist in PostgreSQL')
                
        else:
            # SQLite
            import sqlite3
            cursor = conn.cursor()
            
            # Check if commissioners table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commissioners'")
            if cursor.fetchone():
                print('Commissioners table exists in SQLite')
                
                # Get commissioners
                cursor.execute('SELECT id, username FROM commissioners ORDER BY username')
                commissioners = cursor.fetchall()
                print(f'Found {len(commissioners)} commissioners:')
                for comm in commissioners:
                    print(f'  ID: {comm[0]}, Username: {comm[1]}')
            else:
                print('Commissioners table does not exist in SQLite')
        
        conn.close()
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_database()
