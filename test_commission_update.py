#!/usr/bin/env python3
"""
Script para testar a funcionalidade de atualização manual de comissões
Verifica se as regras de data (1 de abril) são respeitadas
"""

import os
import sys
from datetime import datetime, date
import logging

# Adicionar o diretório atual ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_commission_update():
    """Testar atualização de comissão manual"""
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Data limite: 1 de abril de 2026
        cutoff_date = date(2026, 4, 1)
        
        logging.info("Testando funcionalidade de atualização de comissões...")
        
        # 1. Verificar se existem comissionistas na base de dados
        cursor.execute("SELECT id, name, commission_rate FROM commissioners LIMIT 3")
        commissioners = cursor.fetchall()
        
        if not commissioners:
            logging.warning("Nenhum comissionista encontrado na base de dados")
            return
        
        # Usar o primeiro comissionista para teste
        test_commissioner = commissioners[0]
        commissioner_id = test_commissioner[0]
        commissioner_name = test_commissioner[1]
        current_rate = float(test_commissioner[2])
        
        logging.info(f"Testando com comissionista: {commissioner_name} (ID: {commissioner_id}, Taxa atual: {current_rate}%)")
        
        # 2. Verificar reservas existentes antes e depois da data de corte
        cursor.execute("""
            SELECT COUNT(*) as total_bookings,
                   SUM(CASE WHEN pickup_date <= ? THEN 1 ELSE 0 END) as old_bookings,
                   SUM(CASE WHEN pickup_date > ? THEN 1 ELSE 0 END) as new_bookings
            FROM commission_bookings 
            WHERE commissioner_id = ? AND loyalty_card > 0
        """, (cutoff_date, cutoff_date, commissioner_id))
        
        booking_stats = cursor.fetchone()
        total_bookings, old_bookings, new_bookings = booking_stats
        
        logging.info(f"Reservas do comissionista: {total_bookings} total, {old_bookings} antes de 1/abr, {new_bookings} depois de 1/abr")
        
        if new_bookings == 0:
            logging.warning("Não há reservas após 1 de abril para testar. Criando dados de teste...")
            
            # Criar algumas reservas de teste
            test_bookings = [
                (date(2026, 3, 15), 100.0),  # Antes de 1 de abril
                (date(2026, 4, 15), 200.0),  # Depois de 1 de abril
                (date(2026, 5, 10), 150.0),  # Depois de 1 de abril
            ]
            
            for pickup_date, loyalty_card in test_bookings:
                cursor.execute("""
                    INSERT INTO commission_bookings (
                        commissioner_id, voucher, pickup_date, loyalty_card, 
                        commission_amount, commission_paid
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    commissioner_id,
                    f"TEST_{pickup_date.strftime('%Y%m%d')}",
                    pickup_date,
                    loyalty_card,
                    loyalty_card * (current_rate / 100.0),
                    False
                ))
            
            conn.commit()
            logging.info("Criadas 3 reservas de teste")
        
        # 3. Simular alteração da taxa de comissão para 25%
        new_rate = 25.0
        
        logging.info(f"Simulando alteração da taxa de {current_rate}% para {new_rate}%...")
        
        # Atualizar a taxa do comissionista
        cursor.execute("""
            UPDATE commissioners 
            SET commission_rate = ? 
            WHERE id = ?
        """, (new_rate, commissioner_id))
        
        # Recalcular comissões para reservas após 1 de abril (simulando a lógica do endpoint)
        cursor.execute("""
            UPDATE commission_bookings 
            SET commission_amount = loyalty_card * ?,
                updated_at = datetime('now')
            WHERE commissioner_id = ?
            AND pickup_date > ?
            AND loyalty_card > 0
        """, (new_rate / 100.0, commissioner_id, cutoff_date))
        
        updated_bookings = cursor.rowcount
        conn.commit()
        
        logging.info(f"Atualizadas {updated_bookings} reservas para a nova taxa")
        
        # 4. Verificar resultados
        cursor.execute("""
            SELECT 
                pickup_date,
                loyalty_card,
                commission_amount,
                (commission_amount / loyalty_card * 100) as effective_rate
            FROM commission_bookings 
            WHERE commissioner_id = ? 
            AND loyalty_card > 0
            ORDER BY pickup_date
        """, (commissioner_id,))
        
        results = cursor.fetchall()
        
        logging.info("\nResultados após atualização:")
        logging.info("Data        | Loyalty Card | Comissão | Taxa Efetiva")
        logging.info("-" * 55)
        
        for pickup_date, loyalty_card, commission_amount, effective_rate in results:
            pickup_str = pickup_date.strftime('%Y-%m-%d')
            is_old_date = pickup_date <= cutoff_date
            status = "ANTIGA" if is_old_date else "NOVA"
            
            logging.info(f"{pickup_str} | {loyalty_card:11.2f} | {commission_amount:8.2f} | {effective_rate:8.1f}% ({status})")
        
        # 5. Verificar se as regras foram respeitadas
        cursor.execute("""
            SELECT COUNT(*) FROM commission_bookings 
            WHERE commissioner_id = ? 
            AND pickup_date <= ? 
            AND loyalty_card > 0
            AND ABS(commission_amount - (loyalty_card * ?)) > 0.01
        """, (commissioner_id, cutoff_date, current_rate / 100.0))
        
        old_bookings_unchanged = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM commission_bookings 
            WHERE commissioner_id = ? 
            AND pickup_date > ? 
            AND loyalty_card > 0
            AND ABS(commission_amount - (loyalty_card * ?)) > 0.01
        """, (commissioner_id, cutoff_date, new_rate / 100.0))
        
        new_bookings_updated = cursor.fetchone()[0]
        
        # 6. Resultados do teste
        logging.info(f"\nVerificação de regras:")
        logging.info(f"Reservas antigas (<= 1/abr) mantiveram taxa {current_rate}%: {old_bookings_unchanged == 0}")
        logging.info(f"Reservas novas (> 1/abr) atualizadas para taxa {new_rate}%: {new_bookings_updated == 0}")
        
        if old_bookings_unchanged == 0 and new_bookings_updated == 0:
            logging.info("SUCCESS: Regras de data foram respeitadas! ")
        else:
            logging.error("ERROR: Algumas regras não foram respeitadas!")
        
        # 7. Restaurar taxa original
        cursor.execute("""
            UPDATE commissioners 
            SET commission_rate = ? 
            WHERE id = ?
        """, (current_rate, commissioner_id))
        
        # Recalcular comissões de volta
        cursor.execute("""
            UPDATE commission_bookings 
            SET commission_amount = loyalty_card * ?,
                updated_at = datetime('now')
            WHERE commissioner_id = ?
            AND pickup_date > ?
            AND loyalty_card > 0
        """, (current_rate / 100.0, commissioner_id, cutoff_date))
        
        conn.commit()
        logging.info(f"Restaurada taxa original de {current_rate}%")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error during test: {e}")
        raise
    finally:
        conn.close()

def main():
    """Função principal"""
    logging.info("Iniciando teste de atualização de comissões...")
    test_commission_update()
    logging.info("Teste concluído.")

if __name__ == "__main__":
    main()
