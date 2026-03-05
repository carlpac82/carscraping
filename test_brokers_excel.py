#!/usr/bin/env python3
"""
Test Brokers Excel generation with vans pricing
"""
import sys
sys.path.insert(0, '/Users/filipepacheco/CascadeProjects/carscraping')

from current_prices_module import generate_brokers_excel

# Test data - empty prices (will be filled by vans pricing)
prices_data = {
    'B1': {
        '1': {'net': 36.42, 'commission': 41.39},
        '7': {'net': 254.94, 'commission': 289.78}
    }
}

print("🧪 Testing Brokers Excel generation...")
print(f"📋 Input prices_data keys: {list(prices_data.keys())}")
print(f"📋 C3 in prices_data before: {'C3' in prices_data}")

# Generate Excel
excel_file, filename = generate_brokers_excel('Albufeira', 3, 2026, prices_data)

print(f"📋 C3 in prices_data after: {'C3' in prices_data}")
if 'C3' in prices_data:
    print(f"📋 C3 data: {prices_data['C3']}")
if 'C4' in prices_data:
    print(f"📋 C4 data: {prices_data['C4']}")
if 'C5' in prices_data:
    print(f"📋 C5 data: {prices_data['C5']}")

# Save to file
with open('/tmp/test_brokers.xlsx', 'wb') as f:
    f.write(excel_file.getvalue())

print(f"\n✅ Excel saved to /tmp/test_brokers.xlsx")
print(f"📂 Filename: {filename}")
print("\n🔍 Open the file and check if C3, C4, C5 columns have values!")
