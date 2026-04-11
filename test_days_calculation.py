#!/usr/bin/env python3
"""
Testar o cálculo de dias para o exemplo do usuário
"""
from datetime import datetime, timedelta

def calculate_days_test():
    # Exemplo do usuário
    pickup_date = "2026-04-12"
    pickup_time = "10:00"
    dropoff_date = "2026-04-15"
    dropoff_time = "10:15"
    
    # Simular o cálculo do JavaScript
    pickup = datetime.strptime(pickup_date + 'T' + pickup_time, '%Y-%m-%dT%H:%M')
    dropoff = datetime.strptime(dropoff_date + 'T' + dropoff_time, '%Y-%m-%dT%H:%M')
    
    diff_ms = (dropoff - pickup).total_seconds() * 1000
    ms_per_day = 24 * 60 * 60 * 1000
    
    days = int(diff_ms // ms_per_day)
    if diff_ms % ms_per_day > 0:
        days += 1
    
    print(f"Entrega: {pickup} ({pickup.strftime('%d/%m %H:%M')})")
    print(f"Recolha: {dropoff} ({dropoff.strftime('%d/%m %H:%M')})")
    print(f"Diferença: {diff_ms / (1000*60*60)} horas")
    print(f"Dias calculados: {days}")
    print()
    
    # Verificar manualmente
    print("Verificação manual:")
    print("Dia 1: 12/04 (10:00) - 13/04 (10:00)")
    print("Dia 2: 13/04 (10:00) - 14/04 (10:00)")
    print("Dia 3: 14/04 (10:00) - 15/04 (10:00)")
    print("Dia 4: 15/04 (10:00) - 15/04 (10:15) <- 15 minutos extra")
    print(f"Total: 4 dias")
    
    # Testar com exatamente 72 horas (3 dias)
    print("\n--- Teste com exatamente 72 horas ---")
    pickup_test = datetime(2026, 4, 12, 10, 0)
    dropoff_test = datetime(2026, 4, 15, 10, 0)  # Exatamente 72 horas depois
    
    diff_ms_test = (dropoff_test - pickup_test).total_seconds() * 1000
    days_test = int(diff_ms_test // ms_per_day)
    if diff_ms_test % ms_per_day > 0:
        days_test += 1
    
    print(f"Entrega: {pickup_test}")
    print(f"Recolha: {dropoff_test}")
    print(f"Dias calculados: {days_test} (deveria ser 3)")

if __name__ == "__main__":
    calculate_days_test()
