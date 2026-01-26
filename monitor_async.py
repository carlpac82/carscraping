#!/usr/bin/env python3
"""
🔍 MONITOR DE MODO ASSÍNCRONO - AUTO PRUDENTE
Monitoriza logs do servidor para verificar se scraping está em modo assíncrono
"""

import requests
import time
import sys
from datetime import datetime

# URL do servidor
SERVER_URL = "https://rentalprices-production.up.railway.app"

def check_async_mode():
    """Verifica se o modo assíncrono está ativo"""
    print("=" * 80)
    print("🔍 MONITOR DE MODO ASSÍNCRONO")
    print("=" * 80)
    print(f"Servidor: {SERVER_URL}")
    print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Verificar se servidor está online
    try:
        print("📡 Verificando conexão com servidor...", flush=True)
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor online e acessível", flush=True)
        else:
            print(f"⚠️ Servidor respondeu com status {response.status_code}", flush=True)
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}", flush=True)
        return
    
    print()
    print("=" * 80)
    print("📋 INSTRUÇÕES:")
    print("=" * 80)
    print("1. Vai ao Automated Pricing no navegador")
    print("2. Inicia uma nova pesquisa")
    print("3. Enquanto a pesquisa corre, abre outro separador")
    print("4. Tenta aceder às Inspeções")
    print()
    print("✅ Se carregar INSTANTANEAMENTE → Modo assíncrono FUNCIONA")
    print("❌ Se ficar bloqueado → Modo assíncrono NÃO FUNCIONA")
    print("=" * 80)
    print()
    
    # Verificar jobs ativos
    print("🔄 Verificando jobs em background...", flush=True)
    try:
        response = requests.get(f"{SERVER_URL}/api/jobs", timeout=10)
        if response.status_code == 200:
            jobs = response.json()
            if isinstance(jobs, list):
                print(f"📊 Total de jobs: {len(jobs)}", flush=True)
                
                # Filtrar jobs por status
                pending = [j for j in jobs if j.get('status') == 'pending']
                running = [j for j in jobs if j.get('status') == 'running']
                completed = [j for j in jobs if j.get('status') == 'completed']
                failed = [j for j in jobs if j.get('status') == 'failed']
                
                print(f"  ⏳ Pending: {len(pending)}", flush=True)
                print(f"  🔄 Running: {len(running)}", flush=True)
                print(f"  ✅ Completed: {len(completed)}", flush=True)
                print(f"  ❌ Failed: {len(failed)}", flush=True)
                
                # Mostrar jobs em execução
                if running:
                    print()
                    print("🔄 JOBS EM EXECUÇÃO:", flush=True)
                    for job in running:
                        job_id = job.get('job_id', 'N/A')
                        job_type = job.get('job_type', 'N/A')
                        created = job.get('created_at', 'N/A')
                        print(f"  • {job_id} ({job_type}) - Criado: {created}", flush=True)
            else:
                print(f"⚠️ Resposta inesperada: {jobs}", flush=True)
        else:
            print(f"⚠️ Erro ao obter jobs: HTTP {response.status_code}", flush=True)
    except Exception as e:
        print(f"⚠️ Erro ao verificar jobs: {e}", flush=True)
    
    print()
    print("=" * 80)
    print("💡 DICA:")
    print("=" * 80)
    print("Se vires jobs em 'Running', significa que o modo assíncrono está ATIVO!")
    print("O servidor deve estar responsivo mesmo com jobs a correr.")
    print("=" * 80)
    print()

def monitor_jobs_realtime():
    """Monitoriza jobs em tempo real"""
    print()
    print("=" * 80)
    print("🔄 MODO DE MONITORIZAÇÃO EM TEMPO REAL")
    print("=" * 80)
    print("Atualizando a cada 2 segundos... (Ctrl+C para parar)")
    print("=" * 80)
    print()
    
    try:
        while True:
            try:
                response = requests.get(f"{SERVER_URL}/api/jobs", timeout=5)
                if response.status_code == 200:
                    jobs = response.json()
                    if isinstance(jobs, list):
                        running = [j for j in jobs if j.get('status') == 'running']
                        
                        # Limpar linha anterior
                        sys.stdout.write('\r' + ' ' * 100 + '\r')
                        
                        if running:
                            job = running[0]
                            job_id = job.get('job_id', 'N/A')[:20]
                            progress = job.get('progress', 0)
                            message = job.get('message', 'Processing...')[:40]
                            sys.stdout.write(f"🔄 {job_id} | {progress}% | {message}")
                            sys.stdout.flush()
                        else:
                            sys.stdout.write(f"⏸️  Nenhum job em execução | {datetime.now().strftime('%H:%M:%S')}")
                            sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(f"\r⚠️ Erro: {str(e)[:50]}")
                sys.stdout.flush()
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\n✅ Monitorização interrompida")

if __name__ == "__main__":
    check_async_mode()
    
    # Perguntar se quer monitorizar em tempo real
    try:
        print()
        resposta = input("Quer monitorizar jobs em tempo real? (s/n): ").strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            monitor_jobs_realtime()
    except KeyboardInterrupt:
        print("\n\n✅ Programa terminado")
