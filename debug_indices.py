#!/usr/bin/env python3

# Debug script to check SQL indices mapping
def debug_sql_indices():
    print("=== SQL QUERY INDICES MAPPING ===")
    print()
    
    # From the SQL query
    sql_fields = [
        "cb.id",                    # 0
        "cb.voucher_number",        # 1
        "cb.client_name",           # 2
        "cb.client_email",          # 3
        "cb.client_phone",          # 4
        "cb.hotel",                 # 5
        "cb.room_number",           # 6
        "cb.pickup_date",           # 7
        "cb.pickup_time",           # 8
        "cb.dropoff_date",          # 9
        "cb.dropoff_time",          # 10
        "cb.pickup_location",       # 11
        "cb.dropoff_location",      # 12
        "cb.vehicle_group",         # 13
        "cb.extras",                # 14
        "cb.flight_number",         # 15
        "cb.language",              # 16
        "cb.observations",          # 17
        "cb.deposit",               # 18
        "cb.price",                 # 19
        "cb.created_at",            # 20
        "c.name as agent_name",     # 21
        "c.email as agent_email",   # 22
        "c.phone as agent_phone"   # 23
    ]
    
    print("SQL Query fields by index:")
    for i, field in enumerate(sql_fields):
        print(f"  result[{i}] = {field}")
    
    print()
    print("=== BOOKING_DATA MAPPING ===")
    print()
    
    # From the booking_data dictionary
    booking_mapping = {
        'id': 0,
        'voucher_number': 1,
        'client_name': 2,
        'client_email': 3,
        'client_phone': 4,
        'hotel': 5,
        'room_number': 6,
        'pickup_date': 7,
        'pickup_time': 8,
        'dropoff_date': 9,
        'dropoff_time': 10,
        'pickup_location': 11,
        'dropoff_location': 12,
        'vehicle_group': 13,
        'vehicle_name': 13,  # Uses same index
        'vehicle_model': 13,  # Uses same index
        'extras': 14,
        'flight_number': 15,
        'language': 16,
        'observations': 17,
        'deposit': 18,
        'total_price': 19,
        'created_date': 20,
        'agent_name': 21,
        'agent_email': 22,
        'agent_phone': 23,
        'booking_date': 20,  # Uses same as created_date
        'vehicle_image': 13  # Uses same as vehicle_group
    }
    
    print("Booking_data field mapping:")
    for field, index in booking_mapping.items():
        sql_field = sql_fields[index] if index < len(sql_fields) else "OUT_OF_RANGE"
        print(f"  {field} = result[{index}] = {sql_field}")
    
    print()
    print("=== POTENTIAL ISSUES ===")
    print()
    
    # Check for issues
    issues = []
    
    # Check duplicate indices
    used_indices = {}
    for field, index in booking_mapping.items():
        if index in used_indices:
            issues.append(f"Duplicate index {index}: {used_indices[index]} and {field}")
        else:
            used_indices[index] = field
    
    # Check out of range
    for field, index in booking_mapping.items():
        if index >= len(sql_fields):
            issues.append(f"Out of range index {index} for field {field}")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("✅ No index issues found")
    
    print()
    print("=== EXPECTED VALUES ===")
    print()
    print("Based on the voucher showing wrong values:")
    print("- AGENT NAME shows timestamp → Should be result[21] (c.name)")
    print("- BOOKING DATE shows price → Should be result[20] (cb.created_at)")
    print("- Check if indices are swapped in booking_data")

if __name__ == "__main__":
    debug_sql_indices()
