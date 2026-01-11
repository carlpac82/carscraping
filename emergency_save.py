"""
Endpoint de emergência para guardar preços - bypassa cache do Railway
VERSÃO 2026-01-11-15:35 - CÓDIGO INLINE SEM CACHE
"""
import json
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

def emergency_save_prices(conn, location, month, year, prices_data, day_start=1, day_end=31):
    """
    Guarda preços DIRETAMENTE sem usar módulo em cache
    CÓDIGO INLINE - NÃO USA current_prices_module
    """
    try:
        prices_json = json.dumps(prices_data)
        
        # Detectar PostgreSQL
        conn_module = conn.__class__.__module__
        conn_class = conn.__class__.__name__
        is_postgres = 'psycopg' in conn_module or conn_class == 'connection'
        
        logging.info(f"🚨 EMERGENCY SAVE - module: {conn_module}, class: {conn_class}, is_postgres: {is_postgres}")
        logging.info(f"🚨 Saving: {location}, month {month}/{year}, days {day_start}-{day_end}")
        
        if is_postgres:
            # PostgreSQL - SELECT + UPDATE/INSERT (SEM ON CONFLICT)
            with conn.cursor() as cur:
                # Verificar se já existe
                cur.execute("""
                    SELECT id FROM current_prices 
                    WHERE location = %s AND month = %s AND year = %s 
                      AND day_start = %s AND day_end = %s
                """, (location, month, year, day_start, day_end))
                
                existing = cur.fetchone()
                
                if existing:
                    # Atualizar
                    logging.info(f"🔄 Updating existing period {day_start}-{day_end}")
                    cur.execute("""
                        UPDATE current_prices 
                        SET prices_data = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE location = %s AND month = %s AND year = %s 
                          AND day_start = %s AND day_end = %s
                    """, (prices_json, location, month, year, day_start, day_end))
                else:
                    # Inserir NOVO (SEM ON CONFLICT)
                    logging.info(f"➕ Inserting new period {day_start}-{day_end}")
                    cur.execute("""
                        INSERT INTO current_prices (location, month, year, day_start, day_end, prices_data, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """, (location, month, year, day_start, day_end, prices_json))
            
            conn.commit()
            logging.info(f"✅ EMERGENCY SAVE SUCCESS: {location}, {month}/{year}, {day_start}-{day_end}")
            return True
        else:
            # SQLite - INSERT OR REPLACE
            conn.execute("""
                INSERT OR REPLACE INTO current_prices (location, month, year, day_start, day_end, prices_data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (location, month, year, day_start, day_end, prices_json))
            
            conn.commit()
            logging.info(f"✅ EMERGENCY SAVE SUCCESS (SQLite): {location}, {month}/{year}, {day_start}-{day_end}")
            return True
            
    except Exception as e:
        logging.error(f"❌ EMERGENCY SAVE ERROR: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False
