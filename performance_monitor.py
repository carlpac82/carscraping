#!/usr/bin/env python3
"""
Monitor de performance para identificar gargalos e bloqueios
"""
import time
import threading
import logging
import psutil
import os
from datetime import datetime, timedelta
from functools import wraps

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [PERF] %(message)s'
)

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.slow_queries = []
        self.high_memory_usage = []
        
    def log_slow_query(self, query, duration):
        """Registra queries lentas"""
        if duration > 2.0:  # Mais de 2 segundos
            self.slow_queries.append({
                'query': query[:100],
                'duration': duration,
                'timestamp': datetime.now()
            })
            logging.warning(f"🐌 Slow query ({duration:.2f}s): {query[:100]}")
    
    def check_memory_usage(self):
        """Verifica uso de memória"""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > 500:  # Mais de 500MB
                self.high_memory_usage.append({
                    'memory_mb': memory_mb,
                    'timestamp': datetime.now()
                })
                logging.warning(f"💾 High memory usage: {memory_mb:.1f} MB")
                
            return memory_mb
        except:
            return 0
    
    def check_thread_count(self):
        """Verifica número de threads"""
        thread_count = len(threading.enumerate())
        if thread_count > 50:
            logging.warning(f"🧵 High thread count: {thread_count}")
        return thread_count
    
    def generate_report(self):
        """Gera relatório de performance"""
        uptime = time.time() - self.start_time
        
        report = f"""
📊 PERFORMANCE REPORT
{'='*50}
Uptime: {uptime/3600:.1f} hours
Slow queries: {len(self.slow_queries)}
High memory events: {len(self.high_memory_usage)}
Current memory: {self.check_memory_usage():.1f} MB
Current threads: {self.check_thread_count()}

🐌 SLOW QUERIES:
"""
        for i, query in enumerate(self.slow_queries[-5:]):  # Últimas 5
            report += f"{i+1}. {query['duration']:.2f}s - {query['query']}\n"
        
        return report

# Instância global do monitor
monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator para monitorar performance de funções"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > 5.0:  # Funções muito lentas
                logging.warning(f"🐌 Slow function {func.__name__}: {duration:.2f}s")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"❌ Error in {func.__name__} ({duration:.2f}s): {e}")
            raise
    
    return wrapper

def check_database_performance():
    """Verifica performance da base de dados"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return
        
        import psycopg2
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar queries ativas
        start_time = time.time()
        cursor.execute("""
            SELECT query, now() - query_start AS duration
            FROM pg_stat_activity 
            WHERE datname = current_database()
            AND state = 'active'
            AND now() - query_start > interval '5 seconds'
            ORDER BY duration DESC
            LIMIT 10
        """)
        
        active_queries = cursor.fetchall()
        duration = time.time() - start_time
        
        if active_queries:
            logging.warning(f"🔍 {len(active_queries)} long queries detected:")
            for query, q_duration in active_queries:
                logging.warning(f"   {q_duration}: {str(query)[:80]}...")
        
        # Verificar locks
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pg_locks 
            WHERE NOT granted
        """)
        waiting_locks = cursor.fetchone()[0]
        
        if waiting_locks > 0:
            logging.warning(f"🔒 {waiting_locks} locks waiting")
        
        conn.close()
        
    except Exception as e:
        logging.error(f"❌ Database performance check failed: {e}")

def monitor_system_resources():
    """Monitor recursos do sistema"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            logging.warning(f"🔥 High CPU usage: {cpu_percent}%")
        
        # Memória
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            logging.warning(f"💾 High memory usage: {memory.percent}%")
        
        # Disco
        disk = psutil.disk_usage('/')
        if disk.percent > 80:
            logging.warning(f"💿 High disk usage: {disk.percent}%")
        
    except Exception as e:
        logging.error(f"❌ System resource check failed: {e}")

def start_background_monitoring():
    """Inicia monitoramento em background"""
    def monitor_loop():
        while True:
            try:
                monitor.check_memory_usage()
                monitor.check_thread_count()
                check_database_performance()
                monitor_system_resources()
                
                # Gerar relatório a cada hora
                if time.time() % 3600 < 60:  # Aproximadamente a cada hora
                    logging.info(monitor.generate_report())
                
                time.sleep(300)  # Verificar a cada 5 minutos
                
            except Exception as e:
                logging.error(f"❌ Monitoring error: {e}")
                time.sleep(60)  # Esperar 1 minuto em caso de erro
    
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    logging.info("🔍 Performance monitoring started")

if __name__ == "__main__":
    start_background_monitoring()
    
    # Teste
    print("🔍 Performance monitor iniciado")
    print("📊 Relatório será gerado a cada hora")
    print("🔍 Logs serão escritos para o console")
