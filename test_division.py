#!/usr/bin/env python3
"""Test if division is working correctly"""

# Simulate vans_pricing_db from database
vans_pricing_db = {
    'C3': {'1': 112.0, '2': 144.0, '3': 180.0},
    'C4': {'1': 152.0, '2': 170.0, '3': 210.0},
    'C5': {'1': 175.0, '2': 190.0, '3': 240.0}
}

prices_data = {}

print("=" * 60)
print("TESTING DIVISION LOGIC")
print("=" * 60)

for grupo, prices in vans_pricing_db.items():
    prices_data[grupo] = {}
    
    print(f"\n{grupo}:")
    for day, total_price in prices.items():
        day_num = int(day)
        per_day_price = total_price / day_num
        prices_data[grupo][day] = {'net': per_day_price, 'commission': per_day_price}
        print(f"  Day {day}: {total_price} / {day_num} = {per_day_price}")

print("\n" + "=" * 60)
print("FINAL prices_data:")
print("=" * 60)
for grupo in ['C3', 'C4', 'C5']:
    print(f"\n{grupo}:")
    for day in ['1', '2', '3']:
        data = prices_data[grupo][day]
        print(f"  Day {day}: net={data['net']}, commission={data['commission']}")

print("\n" + "=" * 60)
print("EXPECTED VALUES:")
print("=" * 60)
print("C3: 112, 72, 60")
print("C4: 152, 85, 70")
print("C5: 175, 95, 80")
