#!/usr/bin/env python3
"""
🔄 BACKGROUND JOBS MANAGER - AUTO PRUDENTE
Sistema de jobs assíncronos para scraping sem bloquear inspeções

Funcionalidades:
- Scraping em background (não bloqueia servidor)
- Job queue com status tracking
- Inspeções funcionam independentemente
- Thread pool para múltiplos jobs simultâneos
"""

import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Callable, Optional
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job:
    """Representa um job de background"""
    
    def __init__(self, job_id: str, job_type: str, func: Callable, args: tuple, kwargs: dict):
        self.job_id = job_id
        self.job_type = job_type
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = JobStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Any = None
        self.error: Optional[str] = None
        self.progress: int = 0  # 0-100%
        self.message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte job para dict (para API)"""
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress": self.progress,
            "message": self.message,
            "error": self.error,
            "has_result": self.result is not None
        }


class BackgroundJobManager:
    """
    Gestor de jobs em background
    Thread-safe, permite múltiplos jobs simultâneos
    """
    
    def __init__(self, max_workers: int = 2):
        self.jobs: Dict[str, Job] = {}
        self.max_workers = max_workers
        self.active_workers = 0
        self.lock = threading.Lock()
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False
        
    def start(self):
        """Inicia o worker thread"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info(f"✅ BackgroundJobManager started with {self.max_workers} workers")
    
    def stop(self):
        """Para o worker thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("🛑 BackgroundJobManager stopped")
    
    def submit_job(self, job_type: str, func: Callable, *args, **kwargs) -> str:
        """
        Submete um job para execução em background
        
        Args:
            job_type: Tipo do job (ex: "scraping", "export", etc)
            func: Função a executar
            *args, **kwargs: Argumentos para a função
            
        Returns:
            job_id: ID único do job
        """
        job_id = str(uuid.uuid4())
        
        with self.lock:
            job = Job(job_id, job_type, func, args, kwargs)
            self.jobs[job_id] = job
            logger.info(f"📥 Job submitted: {job_id} ({job_type})")
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status de um job"""
        with self.lock:
            job = self.jobs.get(job_id)
            return job.to_dict() if job else None
    
    def get_job_result(self, job_id: str) -> Any:
        """Obtém resultado de um job completado"""
        with self.lock:
            job = self.jobs.get(job_id)
            if job and job.status == JobStatus.COMPLETED:
                return job.result
            return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancela um job pendente"""
        with self.lock:
            job = self.jobs.get(job_id)
            if job and job.status == JobStatus.PENDING:
                job.status = JobStatus.CANCELLED
                logger.info(f"❌ Job cancelled: {job_id}")
                return True
            return False
    
    def get_all_jobs(self, job_type: Optional[str] = None) -> list:
        """Lista todos os jobs (opcionalmente filtrados por tipo)"""
        with self.lock:
            jobs = list(self.jobs.values())
            if job_type:
                jobs = [j for j in jobs if j.job_type == job_type]
            return [j.to_dict() for j in jobs]
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove jobs antigos completados/falhados"""
        now = datetime.now(timezone.utc)
        with self.lock:
            to_remove = []
            for job_id, job in self.jobs.items():
                if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    age_hours = (now - job.created_at).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        to_remove.append(job_id)
            
            for job_id in to_remove:
                del self.jobs[job_id]
            
            if to_remove:
                logger.info(f"🧹 Cleaned up {len(to_remove)} old jobs")
    
    def _worker_loop(self):
        """Loop principal do worker - processa jobs pendentes"""
        logger.info("🔄 Worker loop started")
        
        while self.running:
            try:
                job_to_run = None
                
                # Procurar próximo job pendente
                with self.lock:
                    for job in self.jobs.values():
                        if job.status == JobStatus.PENDING:
                            job_to_run = job
                            job.status = JobStatus.RUNNING
                            job.started_at = datetime.now(timezone.utc)
                            break
                
                # Executar job fora do lock
                if job_to_run:
                    self._execute_job(job_to_run)
                else:
                    # Sem jobs pendentes, aguardar
                    time.sleep(1)
                
                # Cleanup periódico (a cada 100 iterações)
                if int(time.time()) % 100 == 0:
                    self.cleanup_old_jobs()
                    
            except Exception as e:
                logger.error(f"❌ Error in worker loop: {e}", exc_info=True)
                time.sleep(1)
    
    def _execute_job(self, job: Job):
        """Executa um job em thread separada"""
        def run():
            try:
                logger.info(f"▶️ Executing job: {job.job_id} ({job.job_type})")
                job.message = "Processando..."
                
                # Executar função
                result = job.func(*job.args, **job.kwargs)
                
                # Marcar como completado
                with self.lock:
                    job.result = result
                    job.status = JobStatus.COMPLETED
                    job.completed_at = datetime.now(timezone.utc)
                    job.progress = 100
                    job.message = "Concluído com sucesso"
                    self.active_workers -= 1
                
                logger.info(f"✅ Job completed: {job.job_id}")
                
            except Exception as e:
                logger.error(f"❌ Job failed: {job.job_id} - {e}", exc_info=True)
                
                with self.lock:
                    job.status = JobStatus.FAILED
                    job.error = str(e)
                    job.completed_at = datetime.now(timezone.utc)
                    job.message = f"Erro: {str(e)}"
                    self.active_workers -= 1
        
        # Executar em thread separada
        thread = threading.Thread(target=run, daemon=True)
        thread.start()


# Instância global do job manager
job_manager = BackgroundJobManager(max_workers=3)


def start_job_manager():
    """Inicia o job manager (chamar no startup do FastAPI)"""
    job_manager.start()


def stop_job_manager():
    """Para o job manager (chamar no shutdown do FastAPI)"""
    job_manager.stop()


# Funções auxiliares para uso fácil
def submit_scraping_job(func: Callable, *args, **kwargs) -> str:
    """Submete job de scraping"""
    return job_manager.submit_job("scraping", func, *args, **kwargs)


def submit_export_job(func: Callable, *args, **kwargs) -> str:
    """Submete job de export"""
    return job_manager.submit_job("export", func, *args, **kwargs)


def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Obtém status de um job"""
    return job_manager.get_job_status(job_id)


def get_job_result(job_id: str) -> Any:
    """Obtém resultado de um job"""
    return job_manager.get_job_result(job_id)
