"""
Commissioners API Endpoints
Handles commissioner management and booking creation
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date, time
import hashlib
import json
import psycopg2
from database import get_db

router = APIRouter()

# ============================================================
# MODELS
# ============================================================

class CommissionerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    voucher_prefix: Optional[str] = None
    username: str
    password: str
    enabled: bool = True
    is_hotel: bool = False

class CommissionerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    voucher_prefix: Optional[str] = None
    default_location: Optional[str] = None
    password: Optional[str] = None
    enabled: Optional[bool] = None
    commission_rate: Optional[float] = None
    is_hotel: Optional[bool] = None

class CommissionerLogin(BaseModel):
    username: str
    password: str

class BookingCreate(BaseModel):
    commissioner_id: Optional[int] = None
    voucher_number: Optional[str] = None
    client_name: str
    client_email: str
    client_phone: Optional[str] = None
    hotel: Optional[str] = None
    room_number: Optional[str] = None
    pickup_date: str
    pickup_time: str
    dropoff_date: str
    dropoff_time: str
    pickup_location: str
    dropoff_location: str
    vehicle_group: str
    insurance_type: str = "premium"
    extras: List[dict]
    flight_number: Optional[str] = None
    language: str = "pt"
    observations: Optional[str] = None
    deposit: float = 0.0
    price: float
    base_price: float = 0.0
    premium_insurance: float = 0.0
    road_tax: float = 0.0
    extras_total: float = 0.0
    rental_days: int = 0
    total_amount: float
    value_adjustment: float = 0.0

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def hash_password(password: str, salt: str = "") -> str:
    """Hash password using SHA256 with salt - same method as main.py"""
    if not salt:
        import secrets
        salt = secrets.token_hex(8)
    digest = hashlib.sha256((salt + ":" + password).encode("utf-8")).hexdigest()
    return f"{salt}:{digest}"

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash with salt"""
    if ":" not in password_hash:
        # Old format without salt
        return hashlib.sha256(password.encode()).hexdigest() == password_hash
    
    # New format with salt
    salt, stored_hash = password_hash.split(":", 1)
    computed_hash = hashlib.sha256((salt + ":" + password).encode("utf-8")).hexdigest()
    return computed_hash == stored_hash

def get_current_commissioner(request: Request):
    """Get current logged in commissioner from session"""
    commissioner_id = request.session.get("commissioner_id")
    if not commissioner_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return commissioner_id

def generate_voucher_number(commissioner_id: int, prefix: str) -> str:
    """Generate next voucher number for commissioner"""
    conn = get_db()
    cursor = conn.cursor()
    
    current_year = datetime.now().year % 100  # Get last 2 digits
    
    # Get ALL voucher numbers for this commissioner and year to find the max
    cursor.execute("""
        SELECT voucher_number FROM commission_bookings
        WHERE commissioner_id = %s 
        AND voucher_number LIKE %s
    """, (commissioner_id, f"{prefix}-%/{current_year}"))
    
    results = cursor.fetchall()
    conn.close()
    
    max_number = 0
    for result in results:
        voucher = result[0] if isinstance(result, tuple) else result['voucher_number']
        try:
            # Extract number from format PREFIX-NNN/YY
            number_part = voucher.split('-')[1].split('/')[0]
            num = int(number_part)
            if num > max_number:
                max_number = num
        except:
            continue
    
    next_number = max_number + 1
    
    return f"{prefix}-{next_number:03d}/{current_year}"

# ============================================================
# COMMISSIONER AUTHENTICATION
# ============================================================

@router.post("/api/commissioners/login")
async def commissioner_login(login: CommissionerLogin, request: Request):
    """Commissioner login endpoint"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, email, voucher_prefix, password_hash, enabled
        FROM commissioners
        WHERE username = %s
    """, (login.username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return JSONResponse(
            {"ok": False, "error": "Utilizador ou palavra passe errados"}, 
            status_code=401
        )
    
    commissioner = dict(result) if hasattr(result, 'keys') else {
        'id': result[0],
        'name': result[1],
        'email': result[2],
        'voucher_prefix': result[3],
        'password_hash': result[4],
        'enabled': result[5]
    }
    
    if not commissioner['enabled']:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    if not verify_password(login.password, commissioner['password_hash']):
        return JSONResponse(
            {"ok": False, "error": "Utilizador ou palavra passe errados"}, 
            status_code=401
        )
    
    # Set session
    request.session["auth"] = True  # Required for require_auth() to work
    request.session["commissioner_id"] = commissioner['id']
    request.session["commissioner_name"] = commissioner['name']
    request.session["commissioner_prefix"] = commissioner['voucher_prefix']
    
    return {
        "ok": True,
        "needs_email": commissioner['email'] is None,
        "commissioner_id": commissioner['id'],
        "commissioner": {
            "id": commissioner['id'],
            "name": commissioner['name'],
            "email": commissioner['email'],
            "voucher_prefix": commissioner['voucher_prefix']
        }
    }

@router.post("/api/commissioners/logout")
async def commissioner_logout(request: Request):
    """Commissioner logout endpoint"""
    request.session.clear()
    return {"success": True}

@router.get("/api/commissioners/me")
async def get_current_commissioner_info(request: Request):
    """Get current commissioner info"""
    commissioner_id = get_current_commissioner(request)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, email, phone, voucher_prefix, username, enabled, default_location, is_hotel
        FROM commissioners
        WHERE id = %s
    """, (commissioner_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Commissioner not found")
    
    commissioner = dict(result) if hasattr(result, 'keys') else {
        'id': result[0],
        'name': result[1],
        'email': result[2],
        'phone': result[3],
        'voucher_prefix': result[4],
        'username': result[5],
        'enabled': result[6],
        'default_location': result[7] if len(result) > 7 else None,
        'is_hotel': result[8] if len(result) > 8 else False
    }
    
    return {
        "ok": True,
        "commissioner": commissioner
    }

class EmailUpdate(BaseModel):
    email: str
    commissioner_id: Optional[int] = None

@router.post("/api/commissioners/update-email")
async def update_commissioner_email(data: EmailUpdate, request: Request):
    """Update commissioner email (for first login)"""
    commissioner_id = get_current_commissioner(request)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE commissioners
        SET email = %s
        WHERE id = %s
    """, (data.email, commissioner_id))
    
    conn.commit()
    conn.close()
    
    return {"ok": True}

# ============================================================
# BOOKINGS
# ============================================================

@router.post("/api/commissioners/bookings")
async def create_booking(booking: BookingCreate, request: Request):
    """Create a new booking"""
    commissioner_id = get_current_commissioner(request)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get commissioner info including commission_rate
    cursor.execute("""
        SELECT name, email, voucher_prefix, commission_rate
        FROM commissioners
        WHERE id = %s
    """, (commissioner_id,))
    
    commissioner = cursor.fetchone()
    if not commissioner:
        conn.close()
        raise HTTPException(status_code=404, detail="Commissioner not found")
    
    commissioner_data = dict(commissioner) if hasattr(commissioner, 'keys') else {
        'name': commissioner[0],
        'email': commissioner[1],
        'voucher_prefix': commissioner[2],
        'commission_rate': commissioner[3] if len(commissioner) > 3 else 15.0
    }
    
    # Generate voucher number
    voucher_number = generate_voucher_number(commissioner_id, commissioner_data['voucher_prefix'])
    
    # Calculate commission: base_price without VAT (23%) * commission_rate (15%)
    # Formula: (base_price / 1.23) * 0.15
    commission_rate = float(commissioner_data.get('commission_rate', 15.0))
    base_price_without_vat = booking.base_price / 1.23
    commission_amount = base_price_without_vat * (commission_rate / 100.0)
    
    # Insert booking
    cursor.execute("""
        INSERT INTO commission_bookings (
            commissioner_id, voucher_number,
            client_name, client_email, client_phone, hotel, room_number,
            pickup_date, pickup_time, dropoff_date, dropoff_time,
            pickup_location, dropoff_location,
            vehicle_group, insurance_type, extras,
            flight_number, language, observations, deposit, price,
            base_price, premium_insurance, road_tax, extras_total, rental_days,
            total_amount, value_adjustment, commission_rate, commission_amount, status
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
    """, (
        commissioner_id, voucher_number,
        booking.client_name, booking.client_email, booking.client_phone, booking.hotel, booking.room_number,
        booking.pickup_date, booking.pickup_time, booking.dropoff_date, booking.dropoff_time,
        booking.pickup_location, booking.dropoff_location,
        booking.vehicle_group, booking.insurance_type, json.dumps(booking.extras),
        booking.flight_number, booking.language, booking.observations, booking.deposit, booking.price,
        booking.base_price, booking.premium_insurance, booking.road_tax, booking.extras_total, booking.rental_days,
        booking.total_amount, booking.value_adjustment, commission_rate, commission_amount, 'pending'
    ))
    
    booking_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    
    # Send notification to Auto Prudente
    try:
        from voucher_api import get_booking_data, send_new_booking_notification
        import asyncio
        booking_data = get_booking_data(booking_id)
        if booking_data:
            asyncio.create_task(send_new_booking_notification(booking_id, booking_data))
    except Exception as e:
        print(f"[BOOKING] Error sending notification: {e}")
        # Don't fail the booking creation if notification fails
    
    return {
        "ok": True,
        "booking_id": booking_id,
        "voucher_number": voucher_number,
        "commissioner_name": commissioner_data['name']
    }

@router.get("/api/commissioners/bookings")
async def get_commissioner_bookings(request: Request):
    """Get all bookings for current commissioner"""
    commissioner_id = get_current_commissioner(request)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, voucher_number, client_name, client_email, client_phone,
               pickup_date, pickup_time, dropoff_date, dropoff_time,
               pickup_location, dropoff_location, vehicle_group, extras,
               price, status, created_at, updated_at, deposit,
               hotel, room_number, flight_number, observations,
               commission_rate, commission_amount,
               base_price, premium_insurance, road_tax, extras_total, 
               rental_days, total_amount, value_adjustment,
               commission_paid, commission_paid_date, commission_paid_by
        FROM commission_bookings
        WHERE commissioner_id = %s
        ORDER BY created_at DESC
    """, (commissioner_id,))
    
    bookings = cursor.fetchall()
    conn.close()
    
    result = []
    for booking in bookings:
        result.append(dict(booking) if hasattr(booking, 'keys') else {
            'id': booking[0],
            'voucher_number': booking[1],
            'client_name': booking[2],
            'client_email': booking[3],
            'client_phone': booking[4],
            'pickup_date': str(booking[5]),
            'pickup_time': str(booking[6]),
            'dropoff_date': str(booking[7]),
            'dropoff_time': str(booking[8]),
            'pickup_location': booking[9],
            'dropoff_location': booking[10],
            'vehicle_group': booking[11],
            'extras': booking[12],
            'price': float(booking[13]),
            'status': booking[14],
            'created_at': str(booking[15]),
            'updated_at': str(booking[16]),
            'deposit': float(booking[17]) if booking[17] else 0.0,
            'hotel': booking[18],
            'room_number': booking[19],
            'flight_number': booking[20],
            'observations': booking[21],
            'commission_rate': float(booking[22]) if len(booking) > 22 and booking[22] else 0.0,
            'commission_amount': float(booking[23]) if len(booking) > 23 and booking[23] else 0.0,
            'base_price': float(booking[24]) if len(booking) > 24 and booking[24] else 0.0,
            'premium_insurance': float(booking[25]) if len(booking) > 25 and booking[25] else 0.0,
            'road_tax': float(booking[26]) if len(booking) > 26 and booking[26] else 0.0,
            'extras_total': float(booking[27]) if len(booking) > 27 and booking[27] else 0.0,
            'rental_days': booking[28] if len(booking) > 28 else 0,
            'total_amount': float(booking[29]) if len(booking) > 29 and booking[29] else 0.0,
            'value_adjustment': float(booking[30]) if len(booking) > 30 and booking[30] else 0.0,
            'commission_paid': bool(booking[31]) if len(booking) > 31 else False,
            'commission_paid_date': booking[32] if len(booking) > 32 else None,
            'commission_paid_by': booking[33] if len(booking) > 33 else None
        })
    
    return {"ok": True, "bookings": result}

# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@router.get("/api/admin/commissioners")
async def get_all_commissioners():
    """Get all commissioners (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, email, phone, voucher_prefix, username, enabled, created_at, default_location, commission_rate, is_hotel
        FROM commissioners
        ORDER BY name
    """)
    
    commissioners = cursor.fetchall()
    conn.close()
    
    result = []
    for comm in commissioners:
        result.append(dict(comm) if hasattr(comm, 'keys') else {
            'id': comm[0],
            'name': comm[1],
            'email': comm[2],
            'phone': comm[3],
            'voucher_prefix': comm[4],
            'username': comm[5],
            'enabled': comm[6],
            'created_at': str(comm[7]),
            'default_location': comm[8] if len(comm) > 8 else None,
            'commission_rate': float(comm[9]) if len(comm) > 9 and comm[9] else 15.0,
            'is_hotel': comm[10] if len(comm) > 10 else False,
            'total_bookings': 0
        })
    
    return {"ok": True, "commissioners": result}

@router.post("/api/admin/commissioners")
async def create_commissioner(commissioner: CommissionerCreate):
    """Create new commissioner (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    
    password_hash = hash_password(commissioner.password)
    
    try:
        # First insert without voucher_prefix to get the ID
        cursor.execute("""
            INSERT INTO commissioners (name, email, phone, username, password_hash, enabled, is_hotel)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            commissioner.name, commissioner.email, commissioner.phone,
            commissioner.username, password_hash, commissioner.enabled, commissioner.is_hotel
        ))
        
        commissioner_id = cursor.fetchone()[0]
        
        # Generate voucher_prefix if not provided
        if commissioner.voucher_prefix:
            voucher_prefix = commissioner.voucher_prefix
        else:
            # Generate prefix: first 3 letters of name + ID padded to 3 digits
            prefix_base = commissioner.name[:3].upper().replace(" ", "")
            voucher_prefix = prefix_base + str(commissioner_id).zfill(3)
        
        # Update with voucher_prefix
        cursor.execute("""
            UPDATE commissioners SET voucher_prefix = %s WHERE id = %s
        """, (voucher_prefix, commissioner_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "id": commissioner_id, "voucher_prefix": voucher_prefix}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/api/admin/commissioners/{commissioner_id}")
async def update_commissioner(commissioner_id: int, update: CommissionerUpdate):
    """Update commissioner (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if update.name is not None:
        updates.append("name = %s")
        params.append(update.name)
    if update.email is not None:
        updates.append("email = %s")
        params.append(update.email)
    if update.phone is not None:
        updates.append("phone = %s")
        params.append(update.phone)
    if update.username is not None:
        updates.append("username = %s")
        params.append(update.username)
    if update.voucher_prefix is not None:
        updates.append("voucher_prefix = %s")
        params.append(update.voucher_prefix)
    if update.default_location is not None:
        updates.append("default_location = %s")
        params.append(update.default_location)
    if update.commission_rate is not None:
        updates.append("commission_rate = %s")
        params.append(update.commission_rate)
    if update.password is not None:
        updates.append("password_hash = %s")
        params.append(hash_password(update.password))
    if update.enabled is not None:
        updates.append("enabled = %s")
        params.append(update.enabled)
    if update.is_hotel is not None:
        updates.append("is_hotel = %s")
        params.append(update.is_hotel)
    
    if not updates:
        conn.close()
        return {"success": True, "message": "No updates"}
    
    params.append(commissioner_id)
    
    cursor.execute(f"""
        UPDATE commissioners
        SET {', '.join(updates)}
        WHERE id = %s
    """, params)
    
    conn.commit()
    conn.close()
    
    return {"success": True}

@router.delete("/api/admin/commissioners/{commissioner_id}")
async def delete_commissioner(commissioner_id: int):
    """Delete commissioner (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM commissioners WHERE id = %s", (commissioner_id,))
    conn.commit()
    conn.close()
    
    return {"success": True}

@router.get("/api/admin/bookings")
async def get_all_bookings():
    """Get all bookings (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            cb.id, cb.voucher_number, cb.client_name, cb.client_email,
            cb.pickup_date, cb.dropoff_date, cb.vehicle_group, cb.price,
            cb.status, cb.created_at,
            c.name as commissioner_name
        FROM commission_bookings cb
        JOIN commissioners c ON cb.commissioner_id = c.id
        ORDER BY cb.created_at DESC
    """)
    
    bookings = cursor.fetchall()
    conn.close()
    
    result = []
    for booking in bookings:
        result.append(dict(booking) if hasattr(booking, 'keys') else {
            'id': booking[0],
            'voucher_number': booking[1],
            'client_name': booking[2],
            'client_email': booking[3],
            'pickup_date': str(booking[4]),
            'dropoff_date': str(booking[5]),
            'vehicle_group': booking[6],
            'price': float(booking[7]),
            'status': booking[8],
            'created_at': str(booking[9]),
            'commissioner_name': booking[10]
        })
    
    return result

# ============================================================
# VEHICLE GROUPS ENDPOINT
# ============================================================

def get_vehicle_groups_with_photos_v2(conn):
    """Get vehicle groups with their photos from car_groups table (accepts connection object)"""
    try:
        cursor = conn.cursor()
        
        # Buscar todos os grupos da tabela car_groups
        # Tentar com filtro enabled primeiro (coluna é INTEGER, não BOOLEAN)
        try:
            cursor.execute("""
                SELECT code, brand, model, photo_url 
                FROM car_groups 
                WHERE enabled = 1
                ORDER BY code
            """)
            rows = cursor.fetchall()
            if len(rows) == 0:
                # Se não houver resultados, tentar sem filtro
                cursor.execute("""
                    SELECT code, brand, model, photo_url 
                    FROM car_groups 
                    ORDER BY code
                """)
                rows = cursor.fetchall()
        except Exception as e:
            print(f"Error with enabled filter: {e}, trying without filter")
            # Fazer rollback da transação falhada
            conn.rollback()
            cursor.execute("""
                SELECT code, brand, model, photo_url 
                FROM car_groups 
                ORDER BY code
            """)
            rows = cursor.fetchall()
        
        # Dados específicos de cada grupo (baseado na imagem Auto Prudente)
        group_specs = {
            'A': {'seats': '4', 'doors': '5', 'ac': False, 'transmission': 'manual'},
            'B': {'seats': '4-5', 'doors': '5', 'ac': True, 'transmission': 'manual'},
            'D': {'seats': '5', 'doors': '5', 'ac': True, 'transmission': 'manual'},
            'E1': {'seats': '5', 'doors': '5', 'ac': True, 'transmission': 'automatic'},
            'E2': {'seats': '5', 'doors': '5', 'ac': True, 'transmission': 'automatic'},
            'F': {'seats': '5', 'doors': '5', 'ac': True, 'transmission': 'manual'},
            'G': {'seats': '4', 'doors': '3', 'ac': True, 'transmission': 'manual'},
            'J1': {'seats': '5', 'doors': '5', 'ac': True, 'transmission': 'manual'},
            'J2': {'seats': '5', 'doors': '5', 'ac': True, 'transmission': 'manual'},
            'L1': {'seats': '5', 'doors': '5', 'ac': True, 'transmission': 'automatic'},
            'L2': {'seats': '5', 'doors': '5', 'ac': True, 'transmission': 'automatic'},
            'M1': {'seats': '7', 'doors': '5', 'ac': True, 'transmission': 'manual'},
            'M2': {'seats': '7', 'doors': '5', 'ac': True, 'transmission': 'automatic'},
            'N': {'seats': '9', 'doors': '5', 'ac': True, 'transmission': 'manual'}
        }
        
        car_groups_data = []
        for row in rows:
            code = row[0]
            brand = row[1] or ''
            model = row[2] or ''
            photo_url = row[3] or ''
            
            # Filtrar B1 e B2 - manter apenas B
            if code in ['B1', 'B2']:
                continue
            
            # Obter especificações do grupo
            specs = group_specs.get(code, {'seats': '5', 'doors': '5', 'ac': True, 'transmission': 'manual'})
            
            car_groups_data.append({
                'code': code,
                'brand': brand,
                'model': model,
                'image': photo_url or f'/api/vehicles/{brand.lower()} {model.lower()}/photo',
                'name': f"{brand} {model}".strip() or code,
                'seats': specs['seats'],
                'doors': specs['doors'],
                'ac': specs['ac'],
                'transmission': specs['transmission']
            })
        
        return car_groups_data
    except Exception as e:
        print(f"Error loading car_groups: {e}")
        return []

def get_vehicle_groups_with_photos(db_config: dict):
    """Get vehicle groups with their photos from car_groups table (same as automated prices)"""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Buscar todos os grupos da tabela car_groups
        # Usar enabled = 1 ou enabled = TRUE dependendo do tipo
        try:
            cursor.execute("""
                SELECT code, brand, model, photo_url 
                FROM car_groups 
                WHERE enabled = 1 OR enabled = TRUE
                ORDER BY code
            """)
        except:
            # Se falhar, tentar sem filtro enabled
            cursor.execute("""
                SELECT code, brand, model, photo_url 
                FROM car_groups 
                ORDER BY code
            """)
        
        car_groups_data = {}
        for row in cursor.fetchall():
            code = row[0]
            brand = row[1] or ''
            model = row[2] or ''
            photo_url = row[3] or ''
            car_groups_data[code] = {
                'brand': brand,
                'model': model,
                'photo_url': photo_url
            }
        
        conn.close()
    except Exception as e:
        print(f"Error loading car_groups: {e}")
        car_groups_data = {}
    
    # Mapeamento de grupos para comissionistas com nomes de veículos e características
    # Grupo B junta B1 e B2, usa foto do B2
    # Grupo A usa foto do Kia Picanto
    group_mapping = {
        'A': {'source': 'A', 'name': 'KIA PICANTO ou similar', 'vehicle': 'kia picanto', 'seats': 4, 'doors': 5, 'ac': False, 'transmission': 'manual'},
        'B': {'source': 'B2', 'name': 'FIAT PANDA ou similar', 'vehicle': 'fiat panda', 'seats': '4-5', 'doors': 5, 'ac': True, 'transmission': 'manual'},
        'D': {'source': 'D', 'name': 'SEAT IBIZA ou similar', 'vehicle': 'seat ibiza', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'manual'},
        'E1': {'source': 'E1', 'name': 'HYUNDAI i10 ou similar', 'vehicle': 'hyundai i10', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'automatic'},
        'E2': {'source': 'E2', 'name': 'CITROEN C3 ou similar', 'vehicle': 'citroen c3', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'automatic'},
        'F': {'source': 'F', 'name': 'SEAT ARONA ou similar', 'vehicle': 'seat arona', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'manual'},
        'G': {'source': 'G', 'name': 'FIAT 500 cabrio', 'vehicle': 'fiat 500', 'seats': 4, 'doors': 3, 'ac': True, 'transmission': 'manual'},
        'J1': {'source': 'J1', 'name': 'PEUGEOT 2008 ou similar', 'vehicle': 'peugeot 2008', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'manual'},
        'J2': {'source': 'J2', 'name': 'PEUGEOT 308 SW', 'vehicle': 'peugeot 308 sw', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'manual'},
        'L1': {'source': 'L1', 'name': 'CITROEN C3 AIRCROSS ou similar', 'vehicle': 'citroen c3 aircross', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'automatic'},
        'L2': {'source': 'L2', 'name': 'PEUGEOT 308 SW', 'vehicle': 'peugeot 308 sw', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'automatic'},
        'M1': {'source': 'M1', 'name': 'DACIA JOGGER ou similar', 'vehicle': 'dacia jogger', 'seats': 7, 'doors': 5, 'ac': True, 'transmission': 'manual'},
        'M2': {'source': 'M2', 'name': 'CITROEN C4 PICASSO', 'vehicle': 'citroen c4 picasso', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'automatic'},
        'N': {'source': 'N', 'name': 'TOYOTA PROACE ou similar', 'vehicle': 'toyota proace', 'seats': 9, 'doors': 5, 'ac': True, 'transmission': 'manual'}
    }
    
    groups = []
    for code, mapping in group_mapping.items():
        source_code = mapping['source']
        name = mapping['name']
        vehicle_name = mapping['vehicle']
        seats = mapping.get('seats', 5)
        doors = mapping.get('doors', 5)
        ac = mapping.get('ac', True)
        transmission = mapping.get('transmission', 'manual')
        
        # Buscar foto do grupo correspondente em car_groups
        photo_url = ''
        if source_code in car_groups_data:
            photo_url = car_groups_data[source_code]['photo_url']
        
        # Fallback: usar endpoint de fotos de veículos com nome completo
        if not photo_url:
            photo_url = f'/api/vehicles/{vehicle_name}/photo'
        
        groups.append({
            'code': code,
            'name': name,
            'image': photo_url,
            'seats': seats,
            'doors': doors,
            'ac': ac,
            'transmission': transmission
        })
    
    return groups

@router.get("/api/commissioners/vehicle-groups")
async def get_vehicle_groups_endpoint(request: Request):
    """Get vehicle groups with photos for commissioners"""
    try:
        # Verificar se há sessão ativa
        commissioner_id = request.session.get('commissioner_id')
        if not commissioner_id:
            return JSONResponse({"ok": False, "error": "Not authenticated"}, status_code=401)
        
        conn = get_db()
        groups = get_vehicle_groups_with_photos_v2(conn)
        conn.close()
        
        return JSONResponse({
            "ok": True,
            "groups": groups
        })
    except Exception as e:
        import traceback
        print(f"Error loading car_groups: {e}")
        print(traceback.format_exc())
        try:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
        except:
            pass
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)

@router.get("/api/commissioners/locations")
async def get_commissioner_locations(request: Request):
    """Get all commissioner locations (names) for dropdowns"""
    try:
        # Verificar se há sessão ativa
        commissioner_id = request.session.get('commissioner_id')
        if not commissioner_id:
            return JSONResponse({"ok": False, "error": "Not authenticated"}, status_code=401)
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT name 
            FROM commissioners 
            WHERE enabled = TRUE
            ORDER BY name
        """)
        
        locations = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        
        return JSONResponse({
            "ok": True,
            "locations": locations
        })
    except Exception as e:
        import traceback
        print(f"Error in get_commissioner_locations: {e}")
        print(traceback.format_exc())
        try:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
        except:
            pass
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)

@router.get("/api/commissioners/schedule-settings")
async def get_schedule_settings(request: Request):
    """Get schedule settings for current commissioner"""
    try:
        commissioner_id = get_current_commissioner(request)
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                weekday_start_morning, weekday_end_morning,
                weekday_start_afternoon, weekday_end_afternoon,
                sunday_start_morning, sunday_end_morning,
                sunday_start_afternoon, sunday_end_afternoon,
                time_interval_minutes
            FROM commissioners
            WHERE id = %s
        """, (commissioner_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            # Return defaults if not found
            return JSONResponse({
                "ok": True,
                "settings": {
                    "weekday_start_morning": "09:30",
                    "weekday_end_morning": "12:30",
                    "weekday_start_afternoon": "15:00",
                    "weekday_end_afternoon": "17:00",
                    "sunday_start_morning": "09:30",
                    "sunday_end_morning": "12:30",
                    "sunday_start_afternoon": "15:30",
                    "sunday_end_afternoon": "17:00",
                    "time_interval_minutes": 15
                }
            })
        
        # Convert time objects to strings
        settings = {
            "weekday_start_morning": str(result[0]) if result[0] else "09:30",
            "weekday_end_morning": str(result[1]) if result[1] else "12:30",
            "weekday_start_afternoon": str(result[2]) if result[2] else "15:00",
            "weekday_end_afternoon": str(result[3]) if result[3] else "17:00",
            "sunday_start_morning": str(result[4]) if result[4] else "09:30",
            "sunday_end_morning": str(result[5]) if result[5] else "12:30",
            "sunday_start_afternoon": str(result[6]) if result[6] else "15:30",
            "sunday_end_afternoon": str(result[7]) if result[7] else "17:00",
            "time_interval_minutes": result[8] if result[8] else 15
        }
        
        return JSONResponse({
            "ok": True,
            "settings": settings
        })
        
    except Exception as e:
        import traceback
        print(f"Error in get_schedule_settings: {e}")
        print(traceback.format_exc())
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)

class ScheduleSettings(BaseModel):
    weekday_start_morning: str
    weekday_end_morning: str
    weekday_start_afternoon: str
    weekday_end_afternoon: str
    sunday_start_morning: str
    sunday_end_morning: str
    sunday_start_afternoon: str
    sunday_end_afternoon: str
    time_interval_minutes: int

@router.post("/api/commissioners/schedule-settings")
async def update_schedule_settings(settings: ScheduleSettings, request: Request):
    """Update schedule settings for current commissioner"""
    try:
        commissioner_id = get_current_commissioner(request)
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE commissioners
            SET weekday_start_morning = %s,
                weekday_end_morning = %s,
                weekday_start_afternoon = %s,
                weekday_end_afternoon = %s,
                sunday_start_morning = %s,
                sunday_end_morning = %s,
                sunday_start_afternoon = %s,
                sunday_end_afternoon = %s,
                time_interval_minutes = %s
            WHERE id = %s
        """, (
            settings.weekday_start_morning,
            settings.weekday_end_morning,
            settings.weekday_start_afternoon,
            settings.weekday_end_afternoon,
            settings.sunday_start_morning,
            settings.sunday_end_morning,
            settings.sunday_start_afternoon,
            settings.sunday_end_afternoon,
            settings.time_interval_minutes,
            commissioner_id
        ))
        
        conn.commit()
        conn.close()
        
        return JSONResponse({
            "ok": True,
            "message": "Schedule settings updated successfully"
        })
        
    except Exception as e:
        import traceback
        print(f"Error in update_schedule_settings: {e}")
        print(traceback.format_exc())
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)

# Commission Payment Management Endpoints

@router.post("/admin/commissions/mark-paid")
async def mark_commissions_paid(request: Request, payload: dict):
    """Mark multiple commissions as paid or unpaid - Admin only"""
    try:
        require_admin(request)
        
        booking_ids = payload.get("booking_ids", [])
        paid = payload.get("paid", True)  # True for paid, False for unpaid
        
        if not booking_ids:
            return JSONResponse({
                "ok": False,
                "error": "No booking IDs provided"
            }, status_code=400)
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user_id from session
        user_id = request.session.get("user_id")
        if not user_id:
            return JSONResponse({
                "ok": False,
                "error": "User not authenticated"
            }, status_code=401)
        
        updated_count = 0
        
        for booking_id in booking_ids:
            try:
                if paid:
                    # Mark as paid
                    cursor.execute("""
                        UPDATE commission_bookings 
                        SET commission_paid = TRUE, 
                            commission_paid_date = NOW(),
                            commission_paid_by = %s
                        WHERE id = %s
                    """, (user_id, booking_id))
                else:
                    # Mark as unpaid
                    cursor.execute("""
                        UPDATE commission_bookings 
                        SET commission_paid = FALSE, 
                            commission_paid_date = NULL,
                            commission_paid_by = NULL
                        WHERE id = %s
                    """, (booking_id,))
                
                if cursor.rowcount > 0:
                    updated_count += 1
                    
            except Exception as e:
                print(f"Error updating booking {booking_id}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return JSONResponse({
            "ok": True,
            "message": f"Updated {updated_count} commissions",
            "updated_count": updated_count
        })
        
    except HTTPException:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=403)
    except Exception as e:
        import traceback
        print(f"Error in mark_commissions_paid: {e}")
        print(traceback.format_exc())
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)

@router.get("/admin/commissions/summary")
async def get_commissions_summary(request: Request):
    """Get commission summary for admin dashboard - Admin only"""
    try:
        require_admin(request)
        
        # Get query parameters
        month = request.query_params.get("month")  # Format: YYYY-MM
        commissioner_id = request.query_params.get("commissioner_id")
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if month:
            where_conditions.append("EXTRACT(YEAR FROM cb.pickup_date) = %s AND EXTRACT(MONTH FROM cb.pickup_date) = %s")
            year, month_num = month.split('-')
            params.extend([year, month_num])
        
        if commissioner_id:
            where_conditions.append("cb.commissioner_id = %s")
            params.append(commissioner_id)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get commission summary
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_bookings,
                SUM(CASE WHEN cb.commission_paid THEN cb.commission_amount ELSE 0 END) as total_paid,
                SUM(CASE WHEN NOT cb.commission_paid THEN cb.commission_amount ELSE 0 END) as total_unpaid,
                SUM(cb.commission_amount) as total_commission,
                COUNT(DISTINCT cb.commissioner_id) as active_commissioners
            FROM commission_bookings cb
            {where_clause}
        """, params)
        
        summary = cursor.fetchone()
        
        # Get pending bookings (not completed)
        cursor.execute(f"""
            SELECT COUNT(*) as pending_count
            FROM commission_bookings cb
            {where_clause}
            AND cb.status != 'completed'
        """, params)
        
        pending = cursor.fetchone()
        
        conn.close()
        
        return JSONResponse({
            "ok": True,
            "summary": {
                "total_bookings": summary[0] or 0,
                "total_paid": float(summary[1] or 0),
                "total_unpaid": float(summary[2] or 0),
                "total_commission": float(summary[3] or 0),
                "active_commissioners": summary[4] or 0,
                "pending_bookings": pending[0] or 0
            }
        })
        
    except HTTPException:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=403)
    except Exception as e:
        import traceback
        print(f"Error in get_commissions_summary: {e}")
        print(traceback.format_exc())
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)

@router.get("/commissioners/my-commissions")
async def get_my_commissions(request: Request):
    """Get current commissioner's commissions with payment status"""
    try:
        commissioner_id = request.session.get("commissioner_id")
        if not commissioner_id:
            return JSONResponse({
                "ok": False,
                "error": "Not authenticated as commissioner"
            }, status_code=401)
        
        # Get query parameters
        status_filter = request.query_params.get("status")  # paid, unpaid, or all
        month_filter = request.query_params.get("month")  # Format: YYYY-MM
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_conditions = ["cb.commissioner_id = %s"]
        params = [commissioner_id]
        
        if status_filter == "paid":
            where_conditions.append("cb.commission_paid = TRUE")
        elif status_filter == "unpaid":
            where_conditions.append("cb.commission_paid = FALSE")
        
        if month_filter:
            where_conditions.append("EXTRACT(YEAR FROM cb.pickup_date) = %s AND EXTRACT(MONTH FROM cb.pickup_date) = %s")
            year, month_num = month_filter.split('-')
            params.extend([year, month_num])
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Get bookings with commission payment info
        cursor.execute(f"""
            SELECT 
                cb.id,
                cb.voucher_number,
                cb.client_name,
                cb.vehicle_group,
                cb.pickup_date,
                cb.price,
                cb.deposit,
                cb.commission_amount,
                cb.commission_rate,
                cb.commission_paid,
                cb.commission_paid_date,
                cb.status
            FROM commission_bookings cb
            {where_clause}
            ORDER BY cb.pickup_date DESC
        """, params)
        
        bookings = []
        for row in cursor.fetchall():
            bookings.append({
                "id": row[0],
                "voucher_number": row[1],
                "client_name": row[2],
                "vehicle_group": row[3],
                "pickup_date": row[4],
                "price": float(row[5]) if row[5] else 0,
                "deposit": float(row[6]) if row[6] else 0,
                "commission_amount": float(row[7]) if row[7] else 0,
                "commission_rate": float(row[8]) if row[8] else 0,
                "commission_paid": bool(row[9]),
                "commission_paid_date": row[10],
                "status": row[11]
            })
        
        conn.close()
        
        return JSONResponse({
            "ok": True,
            "bookings": bookings
        })
        
    except Exception as e:
        import traceback
        print(f"Error in get_my_commissions: {e}")
        print(traceback.format_exc())
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)

@router.get("/admin/commissions/list")
async def get_commissions_list(request: Request):
    """Get list of commissions for admin table - Admin only"""
    try:
        require_admin(request)
        
        # Get query parameters
        status_filter = request.query_params.get("status")  # paid, unpaid, or all
        month_filter = request.query_params.get("month")  # Format: YYYY-MM
        commissioner_id = request.query_params.get("commissioner_id")
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if status_filter == "paid":
            where_conditions.append("cb.commission_paid = TRUE")
        elif status_filter == "unpaid":
            where_conditions.append("cb.commission_paid = FALSE")
        
        if month_filter:
            where_conditions.append("EXTRACT(YEAR FROM cb.pickup_date) = %s AND EXTRACT(MONTH FROM cb.pickup_date) = %s")
            year, month_num = month_filter.split('-')
            params.extend([year, month_num])
        
        if commissioner_id:
            where_conditions.append("cb.commissioner_id = %s")
            params.append(commissioner_id)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get commissions with commissioner info
        cursor.execute(f"""
            SELECT 
                cb.id,
                cb.voucher_number,
                cb.client_name,
                cb.vehicle_group,
                cb.pickup_date,
                cb.price,
                cb.commission_amount,
                cb.commission_paid,
                cb.commission_paid_date,
                cb.status,
                c.name as commissioner_name
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            {where_clause}
            ORDER BY cb.pickup_date DESC
        """, params)
        
        commissions = []
        for row in cursor.fetchall():
            commissions.append({
                "id": row[0],
                "voucher_number": row[1],
                "client_name": row[2],
                "vehicle_group": row[3],
                "pickup_date": row[4],
                "price": float(row[5]) if row[5] else 0,
                "commission_amount": float(row[6]) if row[6] else 0,
                "commission_paid": bool(row[7]),
                "commission_paid_date": row[8],
                "status": row[9],
                "commissioner_name": row[10]
            })
        
        conn.close()
        
        return JSONResponse({
            "ok": True,
            "commissions": commissions
        })
        
    except HTTPException:
        return JSONResponse({"ok": False, "error": "Unauthorized"}, status_code=403)
    except Exception as e:
        import traceback
        print(f"Error in get_commissions_list: {e}")
        print(traceback.format_exc())
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)
async def get_agentes_manual_pdf_bytes():
    """Generate and return Agentes Portal Manual PDF as bytes"""
    try:
        print("[AGENTES MANUAL] Starting PDF generation")
        
        # Load the HTML template
        template_path = "/app/templates/agentes_manual.html"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            # Fallback for local development
            template_path = "templates/agentes_manual.html"
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
        print("[AGENTES MANUAL] Template loaded successfully")
        
        # Convert relative URLs to absolute URLs
        import re
        base_url = "https://rentalprices.pt"
        
        # Convert logo URL
        html_content = re.sub(
            r'src="https://rentalprices\.pt/static/',
            f'src="{base_url}/static/',
            html_content
        )
        
        # Convert other URLs
        html_content = re.sub(
            r'href="https://auto-prudente\.com/',
            f'href="https://auto-prudente.com/',
            html_content
        )
        
        print("[AGENTES MANUAL] URLs converted to absolute")
        
        # Generate PDF using Playwright
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set content and wait for images
            await page.set_content(html_content)
            await page.wait_for_timeout(2000)
            
            # Generate PDF
            pdf_content = await page.pdf(
                format='A4',
                print_background=True,
                margin={
                    'top': '10mm',
                    'bottom': '10mm',
                    'left': '10mm',
                    'right': '10mm'
                }
            )
            
            await browser.close()
        
        print(f"[AGENTES MANUAL] PDF generated successfully, size: {len(pdf_content)} bytes")
        return pdf_content
        
    except Exception as e:
        import traceback
        print(f"[AGENTES MANUAL] Error generating PDF: {e}")
        print(traceback.format_exc())
        raise e

@router.get('/api/agentes/manual-pdf')
async def generate_agentes_manual_pdf():
    """Generate and return Agentes Portal Manual PDF"""
    try:
        pdf_content = await get_agentes_manual_pdf_bytes()
        
        # Return PDF
        from fastapi.responses import StreamingResponse
        import io
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=Manual_Portal_Agentes_AutoPrudente.pdf"}
        )
        
    except Exception as e:
        import traceback
        print(f"[AGENTES MANUAL] Error generating PDF: {e}")
        print(traceback.format_exc())
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@router.post('/api/admin/commissioners/send-instructions')
async def send_commissioner_instructions(request: Request):
    """Send instructions email to commissioner with access data and manual PDF"""
    try:
        data = await request.json()
        commissioner_id = data.get('commissioner_id')
        name = data.get('name')
        username = data.get('username')
        
        if not commissioner_id or not name or not username:
            return JSONResponse({"ok": False, "error": "Missing required fields"}, status_code=400)
        
        # Get commissioner details including email
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT email, username, password_hash 
            FROM commissioners 
            WHERE id = %s
        """, (commissioner_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return JSONResponse({"ok": False, "error": "Commissioner not found"}, status_code=404)
        
        email, db_username, existing_password_hash = result
        
        if not email:
            conn.close()
            return JSONResponse({"ok": False, "error": "Commissioner has no email address"}, status_code=400)
        
        # Check if commissioner already has a password
        if existing_password_hash and existing_password_hash.strip():
            # Use existing password (we need to decode it or generate a new one)
            # For now, generate a new temporary password for simplicity
            import random
            import string
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Update the commissioner with the new password hash
            new_password_hash = hash_password(temp_password)
            cursor.execute("""
                UPDATE commissioners 
                SET password_hash = %s 
                WHERE id = %s
            """, (new_password_hash, commissioner_id))
            
            print(f"[EMAIL INSTRUCTIONS] Generated new password for {email}")
        else:
            # Generate a temporary password
            import random
            import string
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Update the commissioner with the new password hash
            new_password_hash = hash_password(temp_password)
            cursor.execute("""
                UPDATE commissioners 
                SET password_hash = %s 
                WHERE id = %s
            """, (new_password_hash, commissioner_id))
            
            print(f"[EMAIL INSTRUCTIONS] Generated new password for {email}")
        
        conn.commit()
        
        # Load email template
        template_path = "/app/templates/email_commissioner_instructions.html"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            template_path = "templates/email_commissioner_instructions.html"
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        
        # Replace placeholders
        html_content = template_content.replace('{{username}}', db_username)
        html_content = html_content.replace('{{password}}', temp_password)
        
        # Generate PDF manual attachment
        try:
            pdf_content = await get_agentes_manual_pdf_bytes()
            print(f"[EMAIL INSTRUCTIONS] PDF generated successfully: {len(pdf_content)} bytes")
        except Exception as pdf_error:
            print(f"[EMAIL INSTRUCTIONS] Error generating PDF: {pdf_error}")
            pdf_content = None
        
        # Send email using Gmail OAuth (same method as commissioner vouchers)
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        import base64
        
        # Get Gmail OAuth credentials (same as voucher_api.py)
        print(f"[EMAIL INSTRUCTIONS] Loading Gmail OAuth credentials")
        
        # Import the get_gmail_credentials function from voucher_api
        import sys
        sys.path.append('/app')
        from voucher_api import get_gmail_credentials
        
        credentials = get_gmail_credentials()
        
        if not credentials:
            print(f"[EMAIL INSTRUCTIONS] Gmail OAuth not configured")
            conn.close()
            return JSONResponse({"ok": False, "error": "Gmail não está configurado. Vá a Admin Settings -> Email e conecte o Gmail."}, status_code=500)
        
        # Create email message with HTML template body
        print(f"[EMAIL INSTRUCTIONS] Creating email message")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Instruções Portal de Agentes - Auto Prudente"
        msg['From'] = "info@auto-prudente.com"
        msg['To'] = email
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Attach PDF manual if generated successfully
        if pdf_content:
            pdf_part = MIMEApplication(pdf_content, Name="Manual_Portal_Agentes_AutoPrudente.pdf")
            pdf_part['Content-Disposition'] = f'attachment; filename="Manual_Portal_Agentes_AutoPrudente.pdf"'
            msg.attach(pdf_part)
            print(f"[EMAIL INSTRUCTIONS] PDF attached successfully")
        else:
            print(f"[EMAIL INSTRUCTIONS] Email sent without PDF attachment due to generation error")
        
        # Create message with attachment (same as voucher_api.py)
        from email.mime.base import MIMEBase
        from email import encoders
        
        # Convert message to raw format for Gmail API
        message = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
        
        # Send email
        print(f"[EMAIL INSTRUCTIONS] Sending email via Gmail API")
        try:
            from googleapiclient.discovery import build
            service = build('gmail', 'v1', credentials=credentials)
            
            sent_message = service.users().messages().send(userId='me', body=message).execute()
            print(f"[EMAIL INSTRUCTIONS] Email sent successfully: {sent_message['id']}")
            
            conn.close()
            return JSONResponse({
                "ok": True, 
                "message": f"Instruções enviadas para {email}",
                "temp_password": temp_password
            })
            
        except Exception as e:
            print(f"[EMAIL INSTRUCTIONS] Error sending email: {e}")
            conn.close()
            return JSONResponse({"ok": False, "error": f"Erro ao enviar email: {str(e)}"}, status_code=500)
            
    except Exception as e:
        import traceback
        print(f"Error sending instructions email: {e}")
        print(traceback.format_exc())
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
