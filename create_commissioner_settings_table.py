#!/usr/bin/env python3

import sys
sys.path.append('.')

try:
    from main import _db_connect
    
    # Test database connection
    conn = _db_connect()
    cursor = conn.cursor()
    
    # Check database type
    db_type = type(conn).__name__
    print(f"Database type: {db_type}")
    
    # Create commissioner_settings table
    if 'sqlite' in db_type.lower():
        # SQLite version
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commissioner_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commissioner_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                setting_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(commissioner_id, setting_key),
                FOREIGN KEY (commissioner_id) REFERENCES commissioners (id)
            )
        ''')
        print('Commissioner_settings table created (SQLite)')
    else:
        # PostgreSQL version
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commissioner_settings (
                id SERIAL PRIMARY KEY,
                commissioner_id INTEGER NOT NULL,
                setting_key VARCHAR(100) NOT NULL,
                setting_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(commissioner_id, setting_key),
                FOREIGN KEY (commissioner_id) REFERENCES commissioners (id)
            )
        ''')
        print('Commissioner_settings table created (PostgreSQL)')
    
    conn.commit()
    conn.close()
    print('Table created successfully')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
