#!/usr/bin/env python3
"""
Script para corrigir dropoff_date nos registos de 2025 onde dropoff_date = pickup_date
Lê os dias dos ficheiros Excel de 2025 e atualiza
"""
import os
import pandas as pd
import psycopg2
from urllib.parse import urlparse
from datetime import datetime, timedelta

def fix_2025_dropoff_dates():
    """Atualiza dropoff_date para registos de 2025 onde dropoff_date = pickup_date"""
    
    # Obter DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        database_url = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    # Parse da URL
    result = urlparse(database_url)
    
    try:
        # Conectar à base de dados
        print(f"🔌 Conectando a {result.hostname}...")
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        print("✅ Conectado à base de dados")
        
        # Verificar quantos registos têm o problema
        cursor.execute("""
            SELECT COUNT(*) 
            FROM commission_bookings 
            WHERE EXTRACT(YEAR FROM pickup_date) = 2025
              AND dropoff_date = pickup_date
        """)
        total_to_fix = cursor.fetchone()[0]
        print(f"\n📊 Registos de 2025 com dropoff_date = pickup_date: {total_to_fix}")
        
        if total_to_fix == 0:
            print("✅ Nenhum registo precisa de correção!")
            return True
        
        # Ficheiros Excel de 2025 (se existirem)
        excel_files = []
        for month in range(1, 13):
            filename = f'CM-{month:02d}-2025.xlsx'
            if os.path.exists(filename):
                excel_files.append((filename, month, 2025))
        
        if not excel_files:
            print("\n⚠️  Nenhum ficheiro Excel de 2025 encontrado")
            print("Vou calcular dropoff_date assumindo 7 dias por defeito para registos problemáticos")
            
            # Atualizar com 7 dias por defeito
            cursor.execute("""
                UPDATE commission_bookings
                SET dropoff_date = pickup_date + INTERVAL '7 days'
                WHERE EXTRACT(YEAR FROM pickup_date) = 2025
                  AND dropoff_date = pickup_date
            """)
            updated = cursor.rowcount
            conn.commit()
            print(f"✅ {updated} registos atualizados com 7 dias por defeito")
            return True
        
        total_updated = 0
        
        for filename, month, year in excel_files:
            print(f"\n📄 Processando {filename}...")
            df = pd.read_excel(filename)
            
            # Buscar todos os comissionistas
            cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
            commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}
            
            # Processar dados do Excel
            current_hotel = None
            updated_count = 0
            
            for idx, row in df.iterrows():
                # Identificar nome do hotel
                if pd.notna(row.get('Voucher')) and pd.isna(row.get('Data Entrega')):
                    current_hotel = str(row['Voucher']).strip().upper()
                    continue
                
                # Processar reserva
                if pd.notna(row.get('Data Entrega')) and current_hotel:
                    # Extrair dados
                    try:
                        pickup_date = pd.to_datetime(row['Data Entrega'])
                        days = int(row['Dias']) if pd.notna(row.get('Dias')) else 7
                        
                        # Verificar se há voucher manual
                        manual_voucher = None
                        if pd.notna(row.get('Voucher')):
                            voucher_str = str(row['Voucher']).strip()
                            if voucher_str and voucher_str != 'nan' and voucher_str != current_hotel:
                                manual_voucher = voucher_str
                        
                        # Calcular dropoff date
                        dropoff_date = pickup_date + timedelta(days=days)
                        
                        # Atualizar registro na base de dados
                        if manual_voucher:
                            cursor.execute("""
                                UPDATE commission_bookings
                                SET dropoff_date = %s
                                WHERE voucher_number = %s
                                  AND pickup_date = %s
                                  AND dropoff_date = pickup_date
                            """, (dropoff_date.date(), manual_voucher, pickup_date.date()))
                        else:
                            # Atualizar primeiro registo que corresponda
                            cursor.execute("""
                                UPDATE commission_bookings
                                SET dropoff_date = %s
                                WHERE ctid = (
                                    SELECT ctid
                                    FROM commission_bookings
                                    WHERE pickup_date = %s
                                      AND dropoff_date = pickup_date
                                      AND voucher_number IS NULL
                                    LIMIT 1
                                )
                            """, (dropoff_date.date(), pickup_date.date()))
                        
                        if cursor.rowcount > 0:
                            updated_count += 1
                            print(f"  ✅ {pickup_date.strftime('%d/%m/%Y')} - {days} dias")
                            
                    except Exception as e:
                        print(f"  ⚠️  Erro ao processar linha {idx}: {e}")
                        continue
            
            conn.commit()
            print(f"  📊 {updated_count} registos atualizados em {filename}")
            total_updated += updated_count
        
        print("\n" + "=" * 80)
        print(f"✅ Atualização concluída!")
        print(f"  - Total de registos atualizados: {total_updated}")
        print("=" * 80)
        
        # Verificar quantos ainda têm o problema
        cursor.execute("""
            SELECT COUNT(*) 
            FROM commission_bookings 
            WHERE EXTRACT(YEAR FROM pickup_date) = 2025
              AND dropoff_date = pickup_date
        """)
        remaining = cursor.fetchone()[0]
        
        if remaining > 0:
            print(f"\n⚠️  Ainda existem {remaining} registos de 2025 com dropoff_date = pickup_date")
            print("Vou atualizar com 7 dias por defeito...")
            cursor.execute("""
                UPDATE commission_bookings
                SET dropoff_date = pickup_date + INTERVAL '7 days'
                WHERE EXTRACT(YEAR FROM pickup_date) = 2025
                  AND dropoff_date = pickup_date
            """)
            final_updated = cursor.rowcount
            conn.commit()
            print(f"✅ {final_updated} registos adicionais atualizados com 7 dias por defeito")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = fix_2025_dropoff_dates()
    exit(0 if success else 1)
