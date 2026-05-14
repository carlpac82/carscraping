#!/usr/bin/env python3
"""
📧 AGENDAMENTO AUTOMÁTICO DE EMAILS DE SELF-CHECKOUT

Funções para agendar e enviar emails de self-checkout automaticamente
2 dias antes da data de checkout, apenas para recolhas no Aeroporto de Faro.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

def schedule_checkout_email(
    inspection_number: str,
    checkout_date: str,
    pickup_location: str,
    client_email: str,
    client_name: Optional[str] = None,
    vehicle_plate: Optional[str] = None,
    conn = None
) -> bool:
    """
    Agenda email de self-checkout 2 dias antes da data de checkout.
    
    Args:
        inspection_number: Número da inspeção (check-in)
        checkout_date: Data de checkout (formato: DD/MM/YYYY ou YYYY-MM-DD)
        pickup_location: Local de recolha
        client_email: Email do cliente
        client_name: Nome do cliente (opcional)
        vehicle_plate: Matrícula do veículo (opcional)
        conn: Conexão à base de dados (se None, cria nova)
    
    Returns:
        True se agendado com sucesso, False caso contrário
    """
    try:
        # Verificar se é Aeroporto de Faro
        if not pickup_location:
            logging.info(f"⏭️ No pickup location for {inspection_number}, skipping schedule")
            return False
        
        pickup_lower = pickup_location.lower()
        is_faro_airport = 'aeroporto' in pickup_lower and 'faro' in pickup_lower
        
        if not is_faro_airport:
            logging.info(f"⏭️ Pickup location '{pickup_location}' is not Faro Airport, skipping schedule")
            return False
        
        # Converter data de checkout para datetime
        checkout_dt = None
        try:
            if '/' in checkout_date:
                # Formato DD/MM/YYYY
                checkout_dt = datetime.strptime(checkout_date, '%d/%m/%Y')
            elif '-' in checkout_date:
                # Tentar formato DD - MM - YYYY (com espaços) primeiro
                date_clean = checkout_date.strip()
                if ' - ' in date_clean:
                    # Formato: "28 - 01 - 2026"
                    checkout_dt = datetime.strptime(date_clean, '%d - %m - %Y')
                else:
                    # Formato YYYY-MM-DD
                    checkout_dt = datetime.strptime(date_clean, '%Y-%m-%d')
            else:
                logging.error(f"❌ Invalid date format: {checkout_date}")
                return False
        except ValueError as e:
            logging.error(f"❌ Error parsing checkout date '{checkout_date}': {e}")
            return False
        
        # Calcular data de envio (2 dias antes, às 20:00)
        scheduled_send_dt = checkout_dt - timedelta(days=2)
        scheduled_send_dt = scheduled_send_dt.replace(hour=20, minute=0, second=0, microsecond=0)
        
        # Se a data de envio já passou ou é muito próxima, agendar para agora
        now = datetime.now()
        if scheduled_send_dt <= now:
            scheduled_send_dt = now
            logging.warning(f"⚠️ Checkout date is very close! Scheduling email for immediate delivery")
        
        logging.info(f"📅 Scheduling email for {inspection_number}: checkout={checkout_dt.date()}, send={scheduled_send_dt}")
        
        # Conectar à base de dados se não foi fornecida conexão
        close_conn = False
        if conn is None:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                logging.error("❌ DATABASE_URL not set")
                return False
            
            import psycopg2
            conn = psycopg2.connect(database_url)
            close_conn = True
        
        try:
            cursor = conn.cursor()
            
            # Cancelar agendamentos anteriores para esta inspeção
            cursor.execute("""
                UPDATE scheduled_checkout_emails
                SET status = 'cancelled',
                    updated_at = NOW()
                WHERE inspection_number = %s
                  AND status = 'pending'
            """, (inspection_number,))
            
            cancelled_count = cursor.rowcount
            if cancelled_count > 0:
                logging.info(f"🗑️ Cancelled {cancelled_count} previous schedule(s) for {inspection_number}")
            
            # Inserir novo agendamento
            cursor.execute("""
                INSERT INTO scheduled_checkout_emails
                (inspection_number, checkout_date, scheduled_send_date, pickup_location,
                 client_email, client_name, vehicle_plate, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', NOW(), NOW())
                ON CONFLICT (inspection_number) 
                DO UPDATE SET
                    checkout_date = EXCLUDED.checkout_date,
                    scheduled_send_date = EXCLUDED.scheduled_send_date,
                    pickup_location = EXCLUDED.pickup_location,
                    client_email = EXCLUDED.client_email,
                    client_name = EXCLUDED.client_name,
                    vehicle_plate = EXCLUDED.vehicle_plate,
                    status = 'pending',
                    updated_at = NOW()
            """, (
                inspection_number,
                checkout_dt.date(),
                scheduled_send_dt,
                pickup_location,
                client_email,
                client_name,
                vehicle_plate
            ))
            
            conn.commit()
            logging.info(f"✅ Email scheduled for {inspection_number} to be sent on {scheduled_send_dt}")
            return True
            
        finally:
            if close_conn:
                conn.close()
    
    except Exception as e:
        logging.error(f"❌ Error scheduling checkout email: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False


def cancel_scheduled_email(inspection_number: str, conn = None) -> bool:
    """
    Cancela agendamento de email para uma inspeção.
    
    Args:
        inspection_number: Número da inspeção
        conn: Conexão à base de dados (se None, cria nova)
    
    Returns:
        True se cancelado com sucesso, False caso contrário
    """
    try:
        close_conn = False
        if conn is None:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                logging.error("❌ DATABASE_URL not set")
                return False
            
            import psycopg2
            conn = psycopg2.connect(database_url)
            close_conn = True
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE scheduled_checkout_emails
                SET status = 'cancelled',
                    updated_at = NOW()
                WHERE inspection_number = %s
                  AND status = 'pending'
            """, (inspection_number,))
            
            cancelled_count = cursor.rowcount
            conn.commit()
            
            if cancelled_count > 0:
                logging.info(f"✅ Cancelled schedule for {inspection_number}")
                return True
            else:
                logging.info(f"ℹ️ No pending schedule found for {inspection_number}")
                return False
            
        finally:
            if close_conn:
                conn.close()
    
    except Exception as e:
        logging.error(f"❌ Error cancelling scheduled email: {e}")
        return False


def get_pending_emails() -> list:
    """
    Obtém lista de emails agendados que devem ser enviados agora.
    
    Returns:
        Lista de dicionários com dados dos emails pendentes
    """
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logging.error("❌ DATABASE_URL not set")
            return []
        
        import psycopg2
        conn = psycopg2.connect(database_url)
        
        try:
            cursor = conn.cursor()
            
            # DEBUG: Verificar quantos emails existem na tabela
            cursor.execute("SELECT COUNT(*) FROM scheduled_checkout_emails")
            total_count = cursor.fetchone()[0]
            logging.info(f"🔍 DEBUG: Total emails in table: {total_count}")
            
            # DEBUG: Verificar quantos têm status = 'pending'
            cursor.execute("SELECT COUNT(*) FROM scheduled_checkout_emails WHERE status = 'pending'")
            pending_count = cursor.fetchone()[0]
            logging.info(f"🔍 DEBUG: Emails with status='pending': {pending_count}")
            
            # DEBUG: Verificar se a coluna 'status' existe
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'scheduled_checkout_emails'
            """)
            columns = [row[0] for row in cursor.fetchall()]
            logging.info(f"🔍 DEBUG: Table columns: {columns}")
            
            # Buscar emails agendados para envio (até 5 minutos no futuro para evitar perder)
            query = """
                SELECT inspection_number, checkout_date, scheduled_send_date,
                       pickup_location, client_email, client_name, vehicle_plate
                FROM scheduled_checkout_emails
                WHERE status = 'pending'
                  AND scheduled_send_date <= NOW() + INTERVAL '5 minutes'
                ORDER BY scheduled_send_date ASC
            """
            logging.info(f"🔍 DEBUG: Executing query: {query}")
            cursor.execute(query)
            
            rows = cursor.fetchall()
            logging.info(f"🔍 DEBUG: Query returned {len(rows)} row(s)")
            
            pending = []
            for row in rows:
                pending.append({
                    'inspection_number': row[0],
                    'checkout_date': row[1],
                    'scheduled_send_date': row[2],
                    'pickup_location': row[3],
                    'client_email': row[4],
                    'client_name': row[5],
                    'vehicle_plate': row[6]
                })
            
            return pending
            
        finally:
            conn.close()
    
    except Exception as e:
        logging.error(f"❌ Error getting pending emails: {e}")
        return []


def mark_email_sent(inspection_number: str, success: bool = True, error_message: str = None) -> bool:
    """
    Marca email como enviado ou com erro.
    
    Args:
        inspection_number: Número da inspeção
        success: True se enviado com sucesso, False se erro
        error_message: Mensagem de erro (se success=False)
    
    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logging.error("❌ DATABASE_URL not set")
            return False
        
        import psycopg2
        conn = psycopg2.connect(database_url)
        
        try:
            cursor = conn.cursor()
            
            if success:
                cursor.execute("""
                    UPDATE scheduled_checkout_emails
                    SET status = 'sent',
                        sent_at = NOW(),
                        updated_at = NOW()
                    WHERE inspection_number = %s
                """, (inspection_number,))
            else:
                cursor.execute("""
                    UPDATE scheduled_checkout_emails
                    SET status = 'error',
                        error_message = %s,
                        updated_at = NOW()
                    WHERE inspection_number = %s
                """, (error_message, inspection_number))
            
            conn.commit()
            return True
            
        finally:
            conn.close()
    
    except Exception as e:
        logging.error(f"❌ Error marking email status: {e}")
        return False


def reschedule_old_pending_emails():
    """
    Re-agenda emails pendentes que foram agendados para as 09:00 (hora antiga)
    para as 20:00 de hoje, para serem enviados hoje à noite.
    """
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logging.error("❌ DATABASE_URL not set")
            return 0
        
        import psycopg2
        from datetime import datetime, timedelta
        
        conn = psycopg2.connect(database_url)
        
        try:
            cursor = conn.cursor()
            
            # Encontrar emails pendentes com scheduled_send_date no passado
            cursor.execute("""
                SELECT inspection_number, checkout_date, scheduled_send_date
                FROM scheduled_checkout_emails
                WHERE status = 'pending'
                  AND scheduled_send_date < NOW()
                ORDER BY scheduled_send_date ASC
            """)
            
            old_emails = cursor.fetchall()
            
            if not old_emails:
                logging.info("✅ No old pending emails to reschedule")
                return 0
            
            logging.info(f"🔄 Found {len(old_emails)} old pending emails to reschedule")
            
            # Re-agendar cada um para hoje às 20:00
            today_20h = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
            
            rescheduled_count = 0
            for inspection_number, checkout_date, old_scheduled_date in old_emails:
                try:
                    cursor.execute("""
                        UPDATE scheduled_checkout_emails
                        SET scheduled_send_date = %s
                        WHERE inspection_number = %s
                    """, (today_20h, inspection_number))
                    
                    logging.info(f"✅ Rescheduled {inspection_number}: {old_scheduled_date} → {today_20h}")
                    rescheduled_count += 1
                    
                except Exception as e:
                    logging.error(f"❌ Error rescheduling {inspection_number}: {e}")
            
            conn.commit()
            logging.info(f"✅ Successfully rescheduled {rescheduled_count} emails to today at 20:00")
            return rescheduled_count
            
        finally:
            conn.close()
    
    except Exception as e:
        logging.error(f"❌ Error in reschedule_old_pending_emails: {e}")
        return 0
