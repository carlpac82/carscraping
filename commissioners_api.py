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

class CommissionerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    voucher_prefix: Optional[str] = None
    password: Optional[str] = None
    enabled: Optional[bool] = None

class CommissionerLogin(BaseModel):
    username: str
    password: str

class BookingCreate(BaseModel):
    client_name: str
    client_email: str
    client_phone: str
    hotel: Optional[str] = None
    room_number: Optional[str] = None
    pickup_date: str
    pickup_time: str
    dropoff_date: str
    dropoff_time: str
    pickup_location: str
    dropoff_location: str
    vehicle_group: str
    extras: List[str]
    flight_number: Optional[str] = None
    language: str
    observations: Optional[str] = None
    deposit: float = 0.0
    price: float

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
    
    # Get last voucher number for this commissioner and year
    cursor.execute("""
        SELECT voucher_number FROM commission_bookings
        WHERE commissioner_id = %s 
        AND voucher_number LIKE %s
        ORDER BY id DESC LIMIT 1
    """, (commissioner_id, f"{prefix}-%/{current_year}"))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # Extract number from format PREFIX-NNN/YY
        last_voucher = result[0] if isinstance(result, tuple) else result['voucher_number']
        try:
            number_part = last_voucher.split('-')[1].split('/')[0]
            next_number = int(number_part) + 1
        except:
            next_number = 1
    else:
        next_number = 1
    
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
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
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
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Set session
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
        SELECT id, name, email, phone, voucher_prefix, username, enabled
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
        'enabled': result[6]
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
    
    # Get commissioner info
    cursor.execute("""
        SELECT name, email, voucher_prefix
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
        'voucher_prefix': commissioner[2]
    }
    
    # Generate voucher number
    voucher_number = generate_voucher_number(commissioner_id, commissioner_data['voucher_prefix'])
    
    # Insert booking
    cursor.execute("""
        INSERT INTO commission_bookings (
            commissioner_id, voucher_number,
            client_name, client_email, client_phone, hotel, room_number,
            pickup_date, pickup_time, dropoff_date, dropoff_time,
            pickup_location, dropoff_location,
            vehicle_group, extras,
            flight_number, language, observations, deposit, price,
            status
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
    """, (
        commissioner_id, voucher_number,
        booking.client_name, booking.client_email, booking.client_phone, booking.hotel, booking.room_number,
        booking.pickup_date, booking.pickup_time, booking.dropoff_date, booking.dropoff_time,
        booking.pickup_location, booking.dropoff_location,
        booking.vehicle_group, json.dumps(booking.extras),
        booking.flight_number, booking.language, booking.observations, booking.deposit, booking.price,
        'confirmed'
    ))
    
    booking_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    
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
        SELECT id, voucher_number, client_name, client_email,
               pickup_date, dropoff_date, vehicle_group, price, status, created_at
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
            'pickup_date': str(booking[4]),
            'dropoff_date': str(booking[5]),
            'vehicle_group': booking[6],
            'price': float(booking[7]),
            'status': booking[8],
            'created_at': str(booking[9])
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
        SELECT id, name, email, phone, voucher_prefix, username, enabled, created_at
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
            'created_at': str(comm[7])
        })
    
    return result

@router.post("/api/admin/commissioners")
async def create_commissioner(commissioner: CommissionerCreate):
    """Create new commissioner (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    
    password_hash = hash_password(commissioner.password)
    
    try:
        # First insert without voucher_prefix to get the ID
        cursor.execute("""
            INSERT INTO commissioners (name, email, phone, username, password_hash, enabled)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            commissioner.name, commissioner.email, commissioner.phone,
            commissioner.username, password_hash, commissioner.enabled
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
    if update.voucher_prefix is not None:
        updates.append("voucher_prefix = %s")
        params.append(update.voucher_prefix)
    if update.password is not None:
        updates.append("password_hash = %s")
        params.append(hash_password(update.password))
    if update.enabled is not None:
        updates.append("enabled = %s")
        params.append(update.enabled)
    
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
        'B': {'source': 'B2', 'name': 'FIAT PANDA ou similar', 'vehicle': 'fiat panda', 'seats': 5, 'doors': 5, 'ac': True, 'transmission': 'manual'},
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
        
        db_config = get_db()
        groups = get_vehicle_groups_with_photos(db_config)
        
        return JSONResponse({
            "ok": True,
            "groups": groups
        })
    except Exception as e:
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
        
        db_config = get_db()
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Tentar com enabled = TRUE ou enabled = 1
        try:
            cursor.execute("""
                SELECT DISTINCT name 
                FROM commissioners 
                WHERE enabled = TRUE OR enabled = 1
                ORDER BY name
            """)
        except:
            # Se falhar, buscar todos
            cursor.execute("""
                SELECT DISTINCT name 
                FROM commissioners 
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
        return JSONResponse({
            "ok": False,
            "error": str(e)
        }, status_code=500)
