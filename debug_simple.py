import sqlite3
import os

# Simple debug for booking 6397
conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute("SELECT id, voucher_number, client_name, language FROM commission_bookings WHERE id = 6397")
result = cur.fetchone()

if result:
    print(f"Booking ID: {result[0]}")
    print(f"Voucher: {result[1]}")
    print(f"Client: {result[2]}")
    print(f"LANGUAGE: '{result[3]}'")
    print(f"Language type: {type(result[3])}")
    print(f"Lower case: '{result[3].lower() if result[3] else 'None'}'")
else:
    print("Booking 6397 not found")

conn.close()
