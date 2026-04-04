@app.post("/api/admin/commissions/upload")
async def upload_commissions_excel(request: Request, file: UploadFile = File(...)):
    """Upload and import commissions from Excel file"""
    try:
        require_admin(request)
        
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Get current year
        current_year = datetime.now().year
        
        # Connect to PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        result = urlparse(database_url)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        
        # Hotel mapping
        hotel_mapping = {
            'AQUA PEDRA DOS BICOS': 'AQUA PEDRA DOS BICOS',
            'AQUAMAR': 'AQUAMAR',
            'BAIA GRANDE': 'BAIA GRANDE',
            'CERRO MAR GARDEM': 'CERRO MAR GARDEM',
            'CLUBE MARIA LUISA': 'CLUBE MARIA LUISA',
            'EPIC SANA': 'EPIC SANA',
            'EXPOSE I': 'EXPOSE I',
            'FALESIA HOTEL': 'FALESIA HOTEL',
            'HOLIDAY IN (REAL BELA VISTA)': 'HOLIDAY IN (REAL BELA VISTA)',
            'INDIGO HOTEL': 'INDIGO HOTEL',
            'INATEL': 'INATEL',
            'MASANA': 'MASANA',
            'NAU SAO RAFAEL SUITES': 'NAU SAO RAFAEL SUITES',
            'OCEANUS': 'OCEANUS',
            'OURA ATLANTICO': 'OURA ATLANTICO',
            'OURA VIEW BEACH CLUB': 'OURA VIEW BEACH CLUB',
            'PALADIM': 'PALADIM',
            'PATEO VILLAGE': 'PATEO VILLAGE',
            'PATIO SUITE HOTEL': 'PATIO SUITE HOTEL',
            'PORTO BAY BLUE OCEAN': 'PORTO BAY BLUE OCEAN',
            'PTO': 'PTO',
            'ROCAMAR': 'ROCAMAR',
            'RUBEN MARTINS': 'RUBEN MARTINS, ALGARVE T',
            'SOL E MAR': 'SOL E MAR',
            'ZEBRA SAFARIS II': 'ZEBRA SAFARIS II'
        }
        
        # Get commissioners
        cursor.execute("SELECT id, name FROM commissioners ORDER BY name")
        commissioners = {row[1].upper(): row[0] for row in cursor.fetchall()}
        
        current_hotel = None
        imported_count = 0
        skipped_count = 0
        
        for idx, row in df.iterrows():
            # Identify hotel name
            if pd.notna(row.get('Voucher')) and pd.isna(row.get('Data Entrega')):
                current_hotel = str(row['Voucher']).strip().upper()
                continue
            
            # Process booking
            if pd.notna(row.get('Data Entrega')) and current_hotel:
                # Find commissioner ID
                commissioner_id = None
                for hotel_name, comm_name in hotel_mapping.items():
                    if hotel_name in current_hotel:
                        commissioner_id = commissioners.get(comm_name.upper())
                        break
                
                if not commissioner_id:
                    # Try direct match
                    commissioner_id = commissioners.get(current_hotel)
                
                if not commissioner_id:
                    skipped_count += 1
                    continue
                
                try:
                    # Extract data - use current year with month/day from Excel
                    pickup_datetime = pd.to_datetime(row['Data Entrega'])
                    pickup_date = datetime(current_year, pickup_datetime.month, pickup_datetime.day)
                    
                    days = int(row['Dias']) if pd.notna(row.get('Dias')) else 1
                    
                    # Get base_price
                    base_price = 0
                    if 'Preço Base' in row and pd.notna(row['Preço Base']):
                        base_price_str = str(row['Preço Base']).replace(',', '.')
                        try:
                            base_price = float(base_price_str)
                        except:
                            base_price = 0
                    elif 'Loyalty Card' in row and pd.notna(row['Loyalty Card']):
                        base_price_str = str(row['Loyalty Card']).replace(',', '.')
                        try:
                            base_price = float(base_price_str)
                        except:
                            base_price = 0
                    
                    # Calculate commission
                    commission_amount = (base_price / 1.23) * 0.15
                    
                    # Check for manual voucher
                    manual_voucher = None
                    if pd.notna(row.get('Voucher')):
                        voucher_str = str(row['Voucher']).strip()
                        if voucher_str and voucher_str != 'nan' and voucher_str.upper() != current_hotel:
                            manual_voucher = voucher_str
                    
                    # Calculate dropoff date
                    dropoff_date = pickup_date + timedelta(days=days)
                    
                    # Insert booking
                    cursor.execute("""
                        INSERT INTO commission_bookings (
                            commissioner_id, voucher_number, client_name, client_email, client_phone,
                            pickup_date, pickup_time, dropoff_date, dropoff_time,
                            pickup_location, dropoff_location, vehicle_group, extras,
                            price, base_price, deposit, status, commission_rate, commission_amount,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                    """, (
                        commissioner_id, manual_voucher, 'Loyalty Card', '', '',
                        pickup_date.date(), pickup_datetime.strftime('%H:%M'), 
                        dropoff_date.date(), '00:00',
                        '', '', '', '[]',
                        base_price, base_price, 0, 'confirmed', 15.0, commission_amount
                    ))
                    
                    imported_count += 1
                    
                except Exception as e:
                    print(f"Error importing row {idx}: {e}")
                    skipped_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse({
            "ok": True,
            "imported": imported_count,
            "skipped": skipped_count
        })
        
    except HTTPException as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=403)
    except Exception as e:
        import traceback
        print(f"Error uploading file: {e}")
        traceback.print_exc()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
