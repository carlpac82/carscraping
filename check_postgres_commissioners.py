#!/usr/bin/env python3
import psycopg2
import os

def check_postgres_commissioners():
    try:
        # Try to connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            user="postgres", 
            password="",
            database="rental_prices"
        )
        cursor = conn.cursor()
        
        # Check if commissioners table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'commissioners')")
        if cursor.fetchone()[0]:
            print('Commissioners table exists in PostgreSQL')
            
            # Get commissioners
            cursor.execute('SELECT id, username FROM commissioners ORDER BY username')
            commissioners = cursor.fetchall()
            print('Commissioners:')
            for comm in commissioners:
                print(f'  ID: {comm[0]}, Username: {comm[1]}')
            
            # Check if commissioner_settings table exists
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'commissioner_settings')")
            if cursor.fetchone()[0]:
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
                    
                # Check global settings
                cursor.execute("SELECT setting_key, setting_value FROM settings WHERE setting_key = 'group_a_disabled'")
                global_setting = cursor.fetchone()
                print(f'\nGlobal group_a_disabled setting: {global_setting}')
            else:
                print('Commissioner_settings table does not exist')
        else:
            print('Commissioners table does not exist in PostgreSQL')
        
        conn.close()
    except Exception as e:
        print(f'Error connecting to PostgreSQL: {e}')

if __name__ == '__main__':
    check_postgres_commissioners()
