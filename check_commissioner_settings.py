#!/usr/bin/env python3
import sqlite3
import os

def check_commissioner_settings():
    # Check if there's a local SQLite database
    db_files = [f for f in os.listdir('.') if f.endswith('.db') or f.endswith('.sqlite')]
    print('SQLite files found:', db_files)
    
    # Try to connect to the main database
    try:
        conn = sqlite3.connect('rental_prices.db')
        cursor = conn.cursor()
        
        # Check if commissioners table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commissioners'")
        if cursor.fetchone():
            print('Commissioners table exists')
            
            # Get commissioners
            cursor.execute('SELECT id, username FROM commissioners ORDER BY username')
            commissioners = cursor.fetchall()
            print('Commissioners:')
            for comm in commissioners:
                print(f'  {comm}')
            
            # Check if commissioner_settings table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commissioner_settings'")
            if cursor.fetchone():
                print('Commissioner_settings table exists')
                
                # Get Group A settings for all commissioners
                cursor.execute('''
                    SELECT c.id, c.username, cs.setting_key, cs.setting_value 
                    FROM commissioners c 
                    LEFT JOIN commissioner_settings cs ON c.id = cs.commissioner_id 
                    WHERE cs.setting_key = 'group_a_disabled' OR cs.setting_key IS NULL 
                    ORDER BY c.username
                ''')
                results = cursor.fetchall()
                print('\nGroup A settings:')
                for row in results:
                    print(f'  ID: {row[0]}, Username: {row[1]}, Setting: {row[2]}, Value: {row[3]}')
                    
                # Also check for AUTO PRUDENTE and EXPOSE I specifically
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
            else:
                print('Commissioner_settings table does not exist')
        else:
            print('Commissioners table does not exist')
        
        conn.close()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_commissioner_settings()
