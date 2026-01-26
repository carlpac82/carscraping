#!/usr/bin/env python3
"""
🔐 AUTO PRUDENTE - BACKUP AUTOMÁTICO DA BASE DE DADOS
Executa backup semanal da base de dados PostgreSQL/SQLite

Funcionalidades:
- Backup completo da base de dados
- Compressão automática
- Rotação de backups (mantém últimos 4 backups semanais)
- Logs de auditoria
- Suporte para PostgreSQL e SQLite

Uso:
    python backup_database.py
    
Agendamento (crontab):
    0 3 * * 0 /usr/bin/python3 /path/to/backup_database.py
    (Executa todos os domingos às 3h da manhã)
"""

import os
import sys
import gzip
import shutil
import logging
from datetime import datetime, timezone
from pathlib import Path
import subprocess

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)

# Diretório de backups
BACKUP_DIR = Path(__file__).parent / 'backups'
BACKUP_DIR.mkdir(exist_ok=True)

# Número máximo de backups a manter
MAX_BACKUPS = 4  # 4 semanas = 1 mês


def get_database_url():
    """Obtém URL da base de dados das variáveis de ambiente"""
    return os.getenv('DATABASE_URL') or os.getenv('DB_URL')


def is_postgresql():
    """Verifica se está a usar PostgreSQL"""
    db_url = get_database_url()
    return db_url and db_url.startswith('postgresql')


def backup_postgresql():
    """Backup da base de dados PostgreSQL usando pg_dump"""
    try:
        db_url = get_database_url()
        if not db_url:
            logging.error("❌ DATABASE_URL não configurado")
            return None
        
        # Gerar nome do ficheiro
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        backup_file = BACKUP_DIR / f'backup_postgresql_{timestamp}.sql'
        backup_file_gz = BACKUP_DIR / f'backup_postgresql_{timestamp}.sql.gz'
        
        logging.info(f"🔄 Iniciando backup PostgreSQL...")
        
        # Executar pg_dump
        cmd = f'pg_dump "{db_url}" > {backup_file}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.error(f"❌ Erro ao executar pg_dump: {result.stderr}")
            return None
        
        # Comprimir backup
        logging.info(f"📦 Comprimindo backup...")
        with open(backup_file, 'rb') as f_in:
            with gzip.open(backup_file_gz, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remover ficheiro não comprimido
        backup_file.unlink()
        
        file_size = backup_file_gz.stat().st_size / (1024 * 1024)  # MB
        logging.info(f"✅ Backup PostgreSQL criado: {backup_file_gz.name} ({file_size:.2f} MB)")
        
        return backup_file_gz
        
    except Exception as e:
        logging.error(f"❌ Erro no backup PostgreSQL: {e}")
        return None


def backup_sqlite():
    """Backup da base de dados SQLite"""
    try:
        # Procurar ficheiro SQLite
        sqlite_files = list(Path(__file__).parent.glob('*.db'))
        
        if not sqlite_files:
            logging.warning("⚠️ Nenhum ficheiro SQLite encontrado")
            return None
        
        sqlite_file = sqlite_files[0]  # Usar primeiro ficheiro encontrado
        
        # Gerar nome do ficheiro
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        backup_file_gz = BACKUP_DIR / f'backup_sqlite_{timestamp}.db.gz'
        
        logging.info(f"🔄 Iniciando backup SQLite: {sqlite_file.name}")
        
        # Comprimir e copiar
        with open(sqlite_file, 'rb') as f_in:
            with gzip.open(backup_file_gz, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        file_size = backup_file_gz.stat().st_size / (1024 * 1024)  # MB
        logging.info(f"✅ Backup SQLite criado: {backup_file_gz.name} ({file_size:.2f} MB)")
        
        return backup_file_gz
        
    except Exception as e:
        logging.error(f"❌ Erro no backup SQLite: {e}")
        return None


def rotate_backups():
    """Remove backups antigos, mantendo apenas os últimos MAX_BACKUPS"""
    try:
        # Listar todos os backups
        backups = sorted(BACKUP_DIR.glob('backup_*.gz'), key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remover backups excedentes
        if len(backups) > MAX_BACKUPS:
            for old_backup in backups[MAX_BACKUPS:]:
                logging.info(f"🗑️ Removendo backup antigo: {old_backup.name}")
                old_backup.unlink()
        
        logging.info(f"📊 Total de backups mantidos: {min(len(backups), MAX_BACKUPS)}")
        
    except Exception as e:
        logging.error(f"❌ Erro na rotação de backups: {e}")


def backup_uploaded_files():
    """Backup de ficheiros importantes (PDFs, fotos)"""
    try:
        # Diretórios a fazer backup
        dirs_to_backup = ['uploads', 'static/damage_photos', 'static/inspection_photos']
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        
        for dir_name in dirs_to_backup:
            dir_path = Path(__file__).parent / dir_name
            
            if not dir_path.exists():
                continue
            
            # Criar arquivo tar.gz
            backup_file = BACKUP_DIR / f'backup_files_{dir_name.replace("/", "_")}_{timestamp}.tar.gz'
            
            logging.info(f"🔄 Backup de ficheiros: {dir_name}")
            
            cmd = f'tar -czf {backup_file} -C {dir_path.parent} {dir_path.name}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = backup_file.stat().st_size / (1024 * 1024)  # MB
                logging.info(f"✅ Backup de ficheiros criado: {backup_file.name} ({file_size:.2f} MB)")
            else:
                logging.warning(f"⚠️ Erro ao fazer backup de {dir_name}: {result.stderr}")
        
    except Exception as e:
        logging.error(f"❌ Erro no backup de ficheiros: {e}")


def main():
    """Função principal de backup"""
    logging.info("=" * 80)
    logging.info("🔐 AUTO PRUDENTE - BACKUP AUTOMÁTICO")
    logging.info(f"📅 Data: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logging.info("=" * 80)
    
    # Backup da base de dados
    if is_postgresql():
        backup_file = backup_postgresql()
    else:
        backup_file = backup_sqlite()
    
    if backup_file:
        logging.info(f"✅ Backup da base de dados concluído com sucesso")
    else:
        logging.error(f"❌ Falha no backup da base de dados")
        sys.exit(1)
    
    # Backup de ficheiros
    backup_uploaded_files()
    
    # Rotação de backups
    rotate_backups()
    
    logging.info("=" * 80)
    logging.info("✅ BACKUP CONCLUÍDO COM SUCESSO")
    logging.info("=" * 80)


if __name__ == '__main__':
    main()
