"""
Database Connection Manager
Supports both SQLite (local development) and PostgreSQL (production)
"""

import os
import sqlite3
from typing import Optional
from contextlib import contextmanager
import logging

# Check if we're in production (Railway) or local development
DATABASE_URL = os.getenv("DATABASE_URL")  # Railway PostgreSQL URL

# Fix for Render environment variable issue
if not DATABASE_URL:
    # Try to extract from printenv output (Render stores it as Key/Value)
    try:
        import subprocess
        result = subprocess.run(['printenv'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if line.startswith('Value=postgresql://'):
                DATABASE_URL = line.split('=', 1)[1]
                os.environ['DATABASE_URL'] = DATABASE_URL
                logging.info(f"✅ Extracted DATABASE_URL from environment")
                break
    except Exception as e:
        logging.warning(f"Could not extract DATABASE_URL: {e}")

USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    from urllib.parse import urlparse
    
    # Parse DATABASE_URL
    result = urlparse(DATABASE_URL)
    DB_CONFIG = {
        'host': result.hostname,
        'port': result.port,
        'database': result.path[1:],
        'user': result.username,
        'password': result.password,
        'sslmode': 'require',  # Force SSL for stable connections
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 10,
        'keepalives_interval': 5,
        'keepalives_count': 5,
        'options': '-c statement_timeout=120000 -c idle_in_transaction_session_timeout=60000',
    }
    
    # Connection Pool (1-10 per worker, 6 workers = max 60 total)
    try:
        connection_pool = pool.ThreadedConnectionPool(
            minconn=1,  # Reduced from 2 to minimize idle connections being terminated
            maxconn=10,
            **DB_CONFIG
        )
        logging.info(f"🐘 PostgreSQL connection pool created: {result.hostname}/{result.path[1:]}")
    except Exception as e:
        logging.error(f"❌ Failed to create connection pool: {e}")
        connection_pool = None
    
    logging.info(f"🐘 Using PostgreSQL: {result.hostname}/{result.path[1:]}")
else:
    connection_pool = None
    logging.info("📁 Using SQLite (local development)")

class DatabaseConnection:
    """Unified database connection that works with both SQLite and PostgreSQL"""
    
    def __init__(self):
        self.conn = None
        self.is_postgres = USE_POSTGRES
    
    def connect(self, retry_count=3):
        """Establish database connection with retry logic for SSL errors"""
        import time
        
        for attempt in range(retry_count):
            try:
                if self.is_postgres:
                    # Use connection pool if available
                    if connection_pool:
                        try:
                            self.conn = connection_pool.getconn()
                            self.conn.autocommit = True  # CRITICAL: Prevent idle-in-transaction timeouts
                            
                            # Validate connection is alive
                            try:
                                cursor = self.conn.cursor()
                                cursor.execute("SELECT 1")
                                cursor.close()
                            except Exception as health_err:
                                logging.warning(f"Connection from pool is stale: {health_err}. Getting new connection...")
                                # Return bad connection to pool and get a new one
                                try:
                                    connection_pool.putconn(self.conn, close=True)
                                except:
                                    pass
                                self.conn = connection_pool.getconn()
                                self.conn.autocommit = True
                                # Validate new connection is alive
                                try:
                                    cursor = self.conn.cursor()
                                    cursor.execute("SELECT 1")
                                    cursor.close()
                                except Exception as new_health_err:
                                    logging.warning(f"New connection from pool is also stale: {new_health_err}. Getting another one...")
                                    try:
                                        connection_pool.putconn(self.conn, close=True)
                                    except:
                                        pass
                                    self.conn = connection_pool.getconn()
                                    self.conn.autocommit = True
                            
                            return self.conn
                        except Exception as e:
                            logging.error(f"Failed to get connection from pool (attempt {attempt+1}/{retry_count}): {e}")
                            if attempt < retry_count - 1:
                                time.sleep(1)  # Wait 1 second before retry
                                continue
                    # Fallback to direct connection
                    self.conn = psycopg2.connect(**DB_CONFIG)
                    self.conn.autocommit = True  # CRITICAL: Prevent idle-in-transaction timeouts
                else:
                    self.conn = sqlite3.connect("data.db", check_same_thread=False)
                    self.conn.row_factory = sqlite3.Row
                return self.conn
            except Exception as e:
                if attempt < retry_count - 1:
                    logging.warning(f"Connection attempt {attempt+1} failed: {e}. Retrying...")
                    time.sleep(1)
                else:
                    logging.error(f"Failed to connect after {retry_count} attempts: {e}")
                    raise
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            if self.is_postgres and connection_pool:
                # Return connection to pool
                try:
                    connection_pool.putconn(self.conn)
                except Exception as e:
                    logging.error(f"Failed to return connection to pool: {e}")
                    self.conn.close()
            else:
                self.conn.close()
            self.conn = None
    
    def execute(self, query: str, params: tuple = None):
        """Execute a query with automatic dialect conversion and SSL error retry"""
        import time
        
        if not self.conn:
            self.connect()
        
        # Convert SQLite syntax to PostgreSQL if needed
        if self.is_postgres:
            query = self._convert_to_postgres(query)
        
        # PASSO 3: Retry logic para SSL errors durante queries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                cursor = self.conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor
            except Exception as e:
                error_msg = str(e).lower()
                is_ssl_error = any(x in error_msg for x in [
                    'ssl connection has been closed',
                    'connection already closed',
                    'server closed the connection',
                    'connection was killed',
                    'connection reset'
                ])
                
                if is_ssl_error and attempt < max_retries - 1:
                    logging.warning(f"⚠️ SSL error during query (attempt {attempt+1}/{max_retries}): {e}")
                    logging.warning(f"🔄 Reconnecting with fresh connection from pool...")
                    # Fechar conexão morta e reconectar
                    try:
                        self.close()
                    except:
                        pass
                    time.sleep(1)  # Aumentado de 0.5s para 1s
                    self.connect()
                    continue
                else:
                    # Não é SSL error ou já esgotou retries
                    if is_ssl_error:
                        logging.error(f"❌ SSL error persiste após {max_retries} tentativas: {e}")
                    raise
    
    def commit(self):
        """Commit transaction"""
        if self.conn:
            self.conn.commit()
    
    def rollback(self):
        """Rollback transaction"""
        if self.conn:
            self.conn.rollback()
    
    def _convert_to_postgres(self, query: str) -> str:
        """Convert SQLite-specific syntax to PostgreSQL"""
        # AUTOINCREMENT -> SERIAL
        query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        query = query.replace("AUTOINCREMENT", "")
        
        # TEXT -> VARCHAR/TEXT (PostgreSQL is more strict)
        # Keep TEXT as is, it works in PostgreSQL
        
        # REAL -> DOUBLE PRECISION
        query = query.replace("REAL", "DOUBLE PRECISION")
        
        # BLOB -> BYTEA
        query = query.replace("BLOB", "BYTEA")
        
        # CURRENT_TIMESTAMP works in both
        
        # IF NOT EXISTS works in both
        
        return query

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    db = DatabaseConnection()
    try:
        conn = db.connect()
        yield conn
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Database error: {e}")
        raise
    finally:
        db.close()

class PostgreSQLConnectionWrapper:
    """Wrapper to add execute() method to PostgreSQL connection"""
    def __init__(self, conn):
        self._conn = conn
        self._cursor = None
    
    def execute(self, query, params=None):
        """Execute query using cursor"""
        # Convert SQLite ? placeholders to PostgreSQL %s
        if '?' in query:
            # Count number of ? to ensure we have right number of params
            num_placeholders = query.count('?')
            query = query.replace('?', '%s')
            
            # Ensure params is a tuple
            if params is not None:
                if not isinstance(params, (tuple, list)):
                    params = (params,)
                elif isinstance(params, list):
                    params = tuple(params)
        
        # Convert SQLite AUTOINCREMENT to PostgreSQL SERIAL
        if 'AUTOINCREMENT' in query.upper():
            query = query.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
            query = query.replace('AUTOINCREMENT', '')
        
        # Convert SQLite INSERT OR REPLACE to PostgreSQL INSERT ... ON CONFLICT
        if 'INSERT OR REPLACE INTO' in query.upper():
            import re
            # Extract table name and columns
            match = re.search(r'INSERT OR REPLACE INTO\s+(\w+)\s*\(([^)]+)\)', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                columns = [col.strip() for col in match.group(2).split(',')]
                
                # Determine primary key column (usually first column or one ending with _key/id)
                pk_column = columns[0]  # Default to first column
                for col in columns:
                    if col.endswith('_key') or col.endswith('_id') or col == 'id' or col == 'key' or col == 'setting_key':
                        pk_column = col
                        break
                
                # Convert to PostgreSQL syntax
                query = re.sub(
                    r'INSERT OR REPLACE INTO',
                    'INSERT INTO',
                    query,
                    flags=re.IGNORECASE
                )
                
                # Add ON CONFLICT clause if not already present
                if 'ON CONFLICT' not in query.upper():
                    # Find the VALUES clause
                    values_match = re.search(r'VALUES\s*\([^)]+\)', query, re.IGNORECASE)
                    if values_match:
                        values_end = values_match.end()
                        # Build UPDATE SET clause for all columns except primary key
                        update_cols = [f"{col} = EXCLUDED.{col}" for col in columns if col != pk_column]
                        on_conflict = f"\nON CONFLICT ({pk_column}) DO UPDATE SET\n    {', '.join(update_cols)}"
                        query = query[:values_end] + on_conflict + query[values_end:]
        
        # Retry for connection errors
        import logging
        for attempt in range(2):
            try:
                self._cursor = self._conn.cursor()
                if params:
                    self._cursor.execute(query, params)
                else:
                    self._cursor.execute(query)
                return self._cursor
            except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
                err_msg = str(e).lower()
                if 'connection already closed' in err_msg or 'ssl syscall' in err_msg:
                    if attempt == 0:
                        logging.warning(f"Connection error, retrying: {e}")
                        try:
                            if connection_pool:
                                connection_pool.putconn(self._conn, close=True)
                                self._conn = connection_pool.getconn()
                                # Validate new connection is alive
                                try:
                                    cursor = self._conn.cursor()
                                    cursor.execute("SELECT 1")
                                    cursor.close()
                                except Exception as health_err:
                                    logging.warning(f"New connection from pool is also stale: {health_err}. Getting another one...")
                                    try:
                                        connection_pool.putconn(self._conn, close=True)
                                    except:
                                        pass
                                    self._conn = connection_pool.getconn()
                        except:
                            pass
                        continue
                logging.error(f"PostgreSQL execute error: {e}")
                logging.error(f"Query: {query}")
                logging.error(f"Params: {params}")
                raise
            except Exception as e:
                err_msg = str(e).lower()
                if 'already exists' in err_msg or 'duplicate column' in err_msg:
                    logging.debug(f"PostgreSQL migration (expected): {e}")
                else:
                    logging.error(f"PostgreSQL execute error: {e}")
                    logging.error(f"Query: {query}")
                    logging.error(f"Params: {params}")
                raise
    
    def cursor(self):
        """Retorna um cursor da conexão PostgreSQL"""
        return self._conn.cursor()
    
    def commit(self):
        return self._conn.commit()
    
    def rollback(self):
        return self._conn.rollback()
    
    def close(self):
        if self._cursor:
            try:
                self._cursor.close()
            except:
                pass
        if connection_pool and self._conn:
            try:
                connection_pool.putconn(self._conn)
            except:
                try:
                    self._conn.close()
                except:
                    pass
        elif self._conn:
            try:
                self._conn.close()
            except:
                pass
        self._conn = None
        self._cursor = None
    
    def __del__(self):
        """Auto-close connection when object is garbage collected"""
        try:
            self.close()
        except:
            pass  # Silently ignore all errors in destructor
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            try:
                self.rollback()
            except:
                pass
        self.close()

def get_db():
    """Get a database connection (for backward compatibility) with health check"""
    if USE_POSTGRES:
        if connection_pool:
            # Always use pool - never create direct connections
            conn = connection_pool.getconn()
            
            # Health check: verify connection is alive
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            except Exception as health_err:
                logging.warning(f"⚠️ Connection from pool is stale: {health_err}. Getting fresh connection...")
                # Return bad connection and get new one
                try:
                    connection_pool.putconn(conn, close=True)
                except:
                    pass
                conn = connection_pool.getconn()
        else:
            # Fallback only if pool creation failed at startup
            conn = psycopg2.connect(**DB_CONFIG)
        # Wrap to add execute() method
        return PostgreSQLConnectionWrapper(conn)
    else:
        conn = sqlite3.connect("data.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

# Legacy support - keep existing _db_connect function working
def _db_connect():
    """Legacy database connection function"""
    return get_db()
