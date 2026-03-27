"""
Script to add all commissioners to the database
Run via admin route: /admin/add-all-commissioners
"""

import hashlib
import secrets
from database import get_db

def _hash_password(pw: str, salt: str = ""):
    """Hash password using sha256 - same method as main.py"""
    if not salt:
        salt = secrets.token_hex(8)
    digest = hashlib.sha256((salt + ":" + pw).encode("utf-8")).hexdigest()
    return f"{salt}:{digest}"

COMMISSIONERS = [
    "ADRIANA BEACH CLUB", "QUINTA PEDRA DOS BICOS", "AQUA PEDRA DOS BICOS", "ALASSANE CAFÉ",
    "ALBUFEIRA JARDIM I", "ALBUFEIRA SOL", "ALDEIA DA FALESIA", "ALFAGAR", "ALFAMAR",
    "ALGARVE & COMPANHIA", "ALISIOS", "ALMAR", "PATIO SUITE HOTEL", "ALTO DA COLINA",
    "ALTO MOINHO", "AO RUBRO", "APARTAMENTOS DA BALAIA", "APARTAMENTOS DO PARQUE", "AQUAMAR",
    "AREIAS VILLAGE", "AURAMAR", "BALAIA ATLANTICO", "BALAIA GOLF VILLAGE", "BALAIA PLAZA",
    "BALAIA SOL", "HOTEL BOAVISTA", "BORDA D´AGUA", "BRISA SOL", "CAMPING ALBUFEIRA",
    "CASA DO CANTO", "CASA VELHA", "CERRO MAR GARDEM", "CERRO NOVO", "CHOROMAR",
    "CLUBE ALBUFEIRA", "CLUBE MONACO", "CLUBE OCEANO", "COLINA MAR", "NAU ATLANTICO",
    "NAU DUNAS", "NAU PALACIO DE CONGRESSOS", "NAU PALMS VILLAGE", "NAU SAO RAFAEL SUITES",
    "NAU VILAS LAGOAS", "EDEN RESORT", "EIRASOL", "ELSA SIDETOUR", "PTO", "EPIC SANA",
    "EXPOSE I", "EXPOSE II", "FALESIA HOTEL", "FALESIA MAR", "FARM VILLAGE",
    "SON OF THE BEACH HOSTEL", "LOJA MAR", "FLIGHT LINK", "FORTE DA OURA", "FRENTE AO MAR",
    "GALE HOLIDAYS I", "GALE HOLIDAYS II", "GUEST HOUSE SÃO RAFAEL", "GOLDEN BEACH", "HILDE",
    "HOTEL DA ALDEIA", "HOTEL DA GALE", "HOTEL DO CERRO", "HOTEL JUPITER", "INATEL",
    "INATEL PRAIA", "IRENA", "JANELAS DO MAR", "JARDINS DE VALE DE PARRA", "KAISER",
    "KR HOTELS", "MAR A VISTA", "CLUBE MARIA LUISA", "MARTIN VILAMOURA", "MIRAMAR LUNA",
    "MONTRAMAR", "NATURA", "NELSON TOUR", "NOVO CHORO", "O LEANDRO", "OC VILLAS", "OCEANUS",
    "ONDA MAR", "APARTAMENTOS DA ORADA", "OURA ATLANTICO", "OURA BAY", "OURA HOTEL", "PALADIM",
    "PARAISO DE ALBUFEIRA", "PATEO VILLAGE", "PINHEIROS DA BALAIA", "POPULAR VILLAS",
    "PORTO BAY FALESIA", "PORTUGAL GO", "POSTO TURISMO ALBUFEIRA", "QUINTA DA BALAIA",
    "QUINTA DO SOL", "RCM TRAVEL", "HOLIDAY IN (REAL BELA VISTA)", "REAL SANTA EULALIA",
    "APARTAMENTOS CABRITA", "AGUA MARINHA", "RESIDENCIAL CAPRI", "SANTA EULALIA PRAIA",
    "RIU GUARANA", "ROCAMAR", "RUTE ALFAMAR", "SANTOMERO", "TUI BLUE FALESIA",
    "SEREIA DA OURA", "SOL E MAR", "SOLAR DO SOL", "SOLAR DE SÃO JOÃO",
    "SANTA EULALIA BEACH & SPA", "HAPY TRAVEL", "SUNCHINE RESTAURANTE", "SOL E MIO",
    "TOPAZIO", "TORRE VELHA", "TOURS N´TRAKS", "TRIPS FOR FUN", "TROPICAL SOL",
    "TTO ALFAMAR", "TTO VELAMAR", "TTO FALESIA", "TTO OLHOS DE AGUA", "VALE CARRO",
    "VALMANGUDE", "VAN KESTER", "VARANDAS MODELO", "VELAMAR", "VERDE INVESTE AVIS",
    "VERDE INVESTE IGREJA I", "VERDE INVESTE IGREJA II", "VERDE INVESTE PERCADORES",
    "VERDE INVESTE TUNEL I", "VIDAMAR", "VILA BRANCA", "VILA CASTELO",
    "VILA GALE CERRO ALAGOA", "VILA NOVA", "VILA PETRA", "VILA RECIFE", "VILAS BARROCAL",
    "VILAS SÃO VICENTE", "VILLA CERRO", "VILLAS D´AGUA", "VICTORIA", "CLUBE MED - SAMIRIAN",
    "CLUBE MED - LAURENT", "CLUBE MED - HELIA", "CLUBE MED - MANUELA", "AP",
    "CLUBE MED - CAMILE", "CLUBE MED - ALEXANDRA", "CLUBE MED - ALINA", "CLUBE MED - CARLA",
    "THINGSTODO", "SILCHORO", "PARAISO DA BALAIA - SANDRA", "SEM COMISSÃO",
    "TROPICALSUNBAY MARINA", "TROPICANSUNBAY SÃO RAFAEL", "TROPICANSUNBAY MONTECHOURO",
    "MONICA ISABEL", "JUST EVENTS", "VIVIEN", "MIGUEL JET2", "ST. EULALIA PRAIA - AVELINO",
    "ST. EULALIA PRAIA - SONIA", "BAIA GRANDE", "CLUB ALGARVE", "NICOLA",
    "OC VILLAS GABRIELA", "OCEAN VIEW", "VARANDAS ATLANTICO", "CLAUDIA VILA BALAIA",
    "NELLY TRAVEL", "SANDRA SANTOS", "KIOSKE ALBUFEIRA", "PINE CLIFFS", "D. LEONOR",
    "ALL GALE", "CLAUDIA CLUB 3000", "AVENTURA 21", "CLUBE MED-MARIUM", "RENTALCARS",
    "CLUB MED- EMMA", "CLUB MED-MIGUEL", "CLUB MED-AMARITA", "CLUB MED- LAURA",
    "RUI GARCIA", "LURDES VICENTE", "PEDRO FERREIRA", "PAULO FERREIRA", "API-WEB",
    "ANABELA CATUNA", "GRAZINA", "VILA GALE ATLANTICO", "ASSISTUR LDA (FERNANDO AFONSO)",
    "TICKET TO RIDE", "ALGARVE TICKETS", "BALAIA SENSE", "BALAIA SENSES", "CLUBE MED RITA",
    "AGEAS PORTUGAL, COMPANHIA DE SEGUROS, S.A.", "RIA PARQUE HOTEL", "OURA VIEW BEACH CLUB",
    "VILA JOYA", "CLUBE MED - MATILDE", "CRISTINA ANA PAULA", "HOTEL CALIFORNIA",
    "ALBERTINA VALE NAVIO", "CLUBE MED LUIS", "CLUB MED NÁDIA SILVA", "PAULA SARAIVA",
    "FORTE VALE", "JOAO RODRIGUES", "KAREN PRIME TRAVEL", "W HOTELS", "RUBEN BOLIQUEIME",
    "ZOYA", "VILA MIMOSA", "VILA MARIA", "JOAO FERREIRA", "FILIPE MARTINS TRANSFERS",
    "BELA VISTA JARDIM II", "VIP CARS-POA", "REGENCY SALGADOS", "BELA VISTA AVENIDA",
    "DISCOVERCARS-POA", "ABBYCAR-PREPAID", "CARJET-PREPAID", "AMARANTE VILLAS",
    "VILA GALE PRAIA", "ALGARVE BEACH TRANSFER", "EMERALDS HOTEL", "ATLANTIC COAST PROPERTIES",
    "OURA PRAIA", "G TRANSFERES", "ABBYCAR-POA", "DISCOVERCARS-PREPAID", "MASANA",
    "ALGAVE MOTORHOME PARK", "PORTO BAY BLUE OCEAN", "ZEBRA SAFARIS II", "CERRO ATLANTICO",
    "BROKERS - DIRECTOS", "CARALLIANCE-POA", "CARALLIANCE-PREPAID", "INDIGO HOTEL",
    "RUBEN MARTINS, ALGARVE T", "HOTEL MARIOTT RESIDENCES SALGADOS"
]

def generate_username(name):
    """Generate a simple username from commissioner name"""
    # Remove special chars, convert to lowercase, replace spaces with underscore
    username = name.lower()
    username = username.replace('´', '').replace('ã', 'a').replace('á', 'a').replace('é', 'e')
    username = username.replace('í', 'i').replace('ó', 'o').replace('õ', 'o').replace('ú', 'u')
    username = username.replace('ç', 'c').replace('&', 'and').replace(',', '')
    username = username.replace(' - ', '_').replace(' ', '_').replace('(', '').replace(')', '')
    username = username.replace('.', '').replace('/', '_')
    
    # Limit to 50 chars
    if len(username) > 50:
        username = username[:50]
    
    return username

def add_all_commissioners(default_password="autoprudente2026"):
    """Add all commissioners to database"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Hash the default password
    password_hash = _hash_password(default_password)
    
    added = 0
    skipped = 0
    errors = []
    
    for name in COMMISSIONERS:
        username = generate_username(name)
        
        try:
            cursor.execute("""
                INSERT INTO commissioners (name, username, password_hash, commission_rate, enabled)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (name, username, password_hash, 10.00, True))
            
            if cursor.rowcount > 0:
                added += 1
            else:
                skipped += 1
                
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    return {
        "added": added,
        "skipped": skipped,
        "total": len(COMMISSIONERS),
        "errors": errors
    }
