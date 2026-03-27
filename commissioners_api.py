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
