"""
FORÇA EXECUÇÃO DE CÓDIGO NOVO - BYPASS TOTAL DE CACHE
Versão: 2026-01-11-16:05
"""
import json
import logging

def force_save_prices(conn, location, month, year, prices_data, day_start=1, day_end=31):
    """
    Salva preços FORÇANDO código novo - BYPASS TOTAL DE CACHE
    """
    try:
        prices_json = json.dumps(prices_data)
        
        # Detectar PostgreSQL
        conn_module = conn.__class__.__module__
        is_postgres = 'psycopg' in conn_module
        
        logging.info(f"🔥 FORCE SAVE VERSION 2026-01-11-16:05")
        logging.info(f"🔥 Database: {'PostgreSQL' if is_postgres else 'SQLite'}")
        
        if is_postgres:
            # GARANTIR que colunas existem
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'current_prices'
                      AND column_name IN ('day_start', 'day_end')
                """)
                existing_cols = [row[0] for row in cur.fetchall()]
                
                if 'day_start' not in existing_cols:
                    logging.info("➕ Adding day_start column...")
                    cur.execute("ALTER TABLE current_prices ADD COLUMN day_start INTEGER DEFAULT 1")
                
                if 'day_end' not in existing_cols:
                    logging.info("➕ Adding day_end column...")
                    cur.execute("ALTER TABLE current_prices ADD COLUMN day_end INTEGER DEFAULT 31")
                
                conn.commit()
            
            # Salvar dados
            with conn.cursor() as cur:
                # Verificar se existe
                cur.execute("""
                    SELECT id FROM current_prices 
                    WHERE location = %s AND month = %s AND year = %s 
                      AND day_start = %s AND day_end = %s
                """, (location, month, year, day_start, day_end))
                
                existing = cur.fetchone()
                
                if existing:
                    logging.info(f"🔄 Updating existing period")
                    cur.execute("""
                        UPDATE current_prices 
                        SET prices_data = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE location = %s AND month = %s AND year = %s 
                          AND day_start = %s AND day_end = %s
                    """, (prices_json, location, month, year, day_start, day_end))
                else:
                    logging.info(f"➕ Inserting new period")
                    cur.execute("""
                        INSERT INTO current_prices (location, month, year, day_start, day_end, prices_data, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """, (location, month, year, day_start, day_end, prices_json))
            
            conn.commit()
            logging.info(f"✅ FORCE SAVE SUCCESS")
            return True
        else:
            # SQLite
            conn.execute("""
                INSERT OR REPLACE INTO current_prices (location, month, year, day_start, day_end, prices_data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (location, month, year, day_start, day_end, prices_json))
            
            conn.commit()
            logging.info(f"✅ FORCE SAVE SUCCESS (SQLite)")
            return True
            
    except Exception as e:
        logging.error(f"❌ FORCE SAVE ERROR: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False
