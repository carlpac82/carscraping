"""
Populate Commissioners Database
Creates all commissioners with auto-generated usernames, prefixes and passwords
"""

import os
import sys
import re
from database import get_db
import logging
import hashlib

logging.basicConfig(level=logging.INFO)

# List of all commissioners
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
    """Generate username from commissioner name"""
    # Remove special characters and convert to lowercase
    username = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    username = username.lower().strip()
    username = re.sub(r'\s+', '_', username)
    # Limit to 50 characters
    return username[:50]

def generate_prefix(name):
    """Generate voucher prefix from commissioner name"""
    # Get first letters of each word (max 5 letters)
    words = re.sub(r'[^a-zA-Z0-9\s]', '', name).split()
    prefix = ''.join([w[0].upper() for w in words if w])[:5]
    return prefix if prefix else name[:3].upper()

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def populate_commissioners():
    """Populate commissioners table with all commissioners"""
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Track used usernames and prefixes to avoid duplicates
    used_usernames = set()
    used_prefixes = set()
    
    created = 0
    skipped = 0
    
    for name in COMMISSIONERS:
        try:
            # Generate username
            username = generate_username(name)
            original_username = username
            counter = 1
            while username in used_usernames:
                username = f"{original_username}_{counter}"
                counter += 1
            used_usernames.add(username)
            
            # Generate prefix
            prefix = generate_prefix(name)
            original_prefix = prefix
            counter = 1
            while prefix in used_prefixes:
                prefix = f"{original_prefix}{counter}"
                counter += 1
            used_prefixes.add(prefix)
            
            # Generate default password (same as username for initial setup)
            default_password = "autoprudente2026"
            password_hash = hash_password(default_password)
            
            # Insert commissioner
            cursor.execute("""
                INSERT INTO commissioners (name, email, phone, voucher_prefix, username, password_hash, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, None, None, prefix, username, password_hash, True))
            
            if cursor.rowcount > 0:
                created += 1
                logging.info(f"✅ Created: {name} | Username: {username} | Prefix: {prefix}")
            else:
                skipped += 1
                logging.debug(f"⏭️  Skipped (already exists): {name}")
                
        except Exception as e:
            logging.error(f"❌ Error creating {name}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    logging.info(f"\n🎉 Commissioners populated!")
    logging.info(f"   Created: {created}")
    logging.info(f"   Skipped: {skipped}")
    logging.info(f"   Total: {len(COMMISSIONERS)}")
    logging.info(f"\n🔑 Default password for all: autoprudente2026")

if __name__ == "__main__":
    populate_commissioners()
