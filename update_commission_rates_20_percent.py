#!/usr/bin/env python3
"""
Script para atualizar comissões para 20% em reservas com data de entrega superior a 1 de abril
Mantém as comissões anteriores a 1 de abril inalteradas
"""

import os
import sys
from datetime import datetime, date
import logging

# Adicionar o diretório atual ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_commission_rates():
    """Atualiza comissões para 20% em reservas com pickup_date > 2026-04-01"""
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Data limite: 1 de abril de 2026
        cutoff_date = date(2026, 4, 1)
        
        logging.info(f"Data limite para atualização: {cutoff_date}")
        
        # Primeiro, verificar quantas reservas serão afetadas
        # Calculamos se a comissão atual não é 20% do loyalty_card
        cursor.execute("""
            SELECT COUNT(*) as total_count
            FROM commission_bookings 
            WHERE pickup_date > ?
            AND loyalty_card > 0
            AND ABS(commission_amount - (loyalty_card * 0.20)) > 0.01
        """, (cutoff_date,))
        
        result = cursor.fetchone()
        total_to_update = result[0] if result else 0
        
        logging.info(f"Total de reservas a serem atualizadas: {total_to_update}")
        
        if total_to_update == 0:
            logging.info("Nenhuma reserva precisa ser atualizada.")
            return
        
        # Verificar detalhes antes da atualização
        cursor.execute("""
            SELECT 
                id,
                voucher,
                pickup_date,
                loyalty_card,
                commission_amount
            FROM commission_bookings 
            WHERE pickup_date > ?
            AND loyalty_card > 0
            AND ABS(commission_amount - (loyalty_card * 0.20)) > 0.01
            ORDER BY pickup_date
            LIMIT 10
        """, (cutoff_date,))
        
        sample_bookings = cursor.fetchall()
        
        logging.info("Exemplo de reservas que serão atualizadas:")
        for booking in sample_bookings:
            booking_id, voucher, pickup_date, loyalty_card, current_amount = booking
            current_rate = (current_amount / loyalty_card * 100) if loyalty_card > 0 else 0
            new_amount = loyalty_card * 0.20
            logging.info(f"  ID: {booking_id}, Voucher: {voucher}, Data: {pickup_date}, "
                        f"Taxa atual: {current_rate:.1f}%, Nova taxa: 20.0%, "
                        f"Valor atual: {current_amount}, Novo valor: {new_amount}")
        
        # Confirmar antes de prosseguir
        response = input(f"\nDeseja atualizar {total_to_update} reservas para 20% de comissão? (s/N): ")
        if response.lower() != 's':
            logging.info("Operação cancelada pelo usuário.")
            return
        
        # Atualizar as comissões
        cursor.execute("""
            UPDATE commission_bookings 
            SET 
                commission_amount = loyalty_card * 0.20,
                updated_at = datetime('now')
            WHERE pickup_date > ?
            AND loyalty_card > 0
            AND ABS(commission_amount - (loyalty_card * 0.20)) > 0.01
        """, (cutoff_date,))
        
        updated_count = cursor.rowcount
        conn.commit()
        
        logging.info(f"Successfully updated {updated_count} commission bookings to 20% rate")
        
        # Verificar resultados após atualização
        cursor.execute("""
            SELECT COUNT(*) as updated_count
            FROM commission_bookings 
            WHERE pickup_date > ?
            AND loyalty_card > 0
            AND ABS(commission_amount - (loyalty_card * 0.20)) <= 0.01
        """, (cutoff_date,))
        
        result = cursor.fetchone()
        verified_count = result[0] if result else 0
        
        logging.info(f"Verified: {verified_count} bookings now have 20% commission rate")
        
        # Verificar que as comissões anteriores a 1 de abril não foram alteradas
        cursor.execute("""
            SELECT COUNT(*) as old_commissions_count
            FROM commission_bookings 
            WHERE pickup_date <= ?
        """, (cutoff_date,))
        
        result = cursor.fetchone()
        old_commissions_count = result[0] if result else 0
        
        logging.info(f"Commissions before April 1st remain unchanged: {old_commissions_count} bookings")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error updating commission rates: {e}")
        raise
    finally:
        conn.close()

def main():
    """Função principal"""
    logging.info("Iniciando atualização de comissões para 20%...")
    update_commission_rates()
    logging.info("Processo concluído.")

if __name__ == "__main__":
    main()
