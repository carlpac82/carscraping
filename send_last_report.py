#!/usr/bin/env python3
"""
Script para enviar o último relatório de inspeção por email
"""
import sys
import os
import logging
import base64

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """Get database connection"""
    # Force PostgreSQL from Railway (public host)
    database_url = "postgresql://postgres:qlMCiMjAjxQzKNhxMcVUhpvwLbgLlDjZ@autorental-db.proxy.rlwy.net:24428/railway"
    
    # PostgreSQL
    import psycopg2
    from urllib.parse import urlparse
    
    result = urlparse(database_url)
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    logging.info("✅ Connected to PostgreSQL")
    return conn, True

def get_last_inspection():
    """Get the last inspection from database"""
    conn, is_postgres = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get last inspection
        cursor.execute("""
            SELECT id, inspection_number, inspection_type, vehicle_plate, contract_number,
                   inspector_name, inspector_notes, damage_count, odometer_reading, fuel_level,
                   created_at
            FROM vehicle_inspections
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        inspection = cursor.fetchone()
        if not inspection:
            logging.error("❌ No inspections found in database")
            return None
        
        inspection_id = inspection[0]
        logging.info(f"✅ Found inspection: {inspection[1]}")
        
        # Get photos
        cursor.execute("""
            SELECT photo_type, image_data
            FROM inspection_photos
            WHERE inspection_id = %s
            ORDER BY photo_order
        """ if is_postgres else """
            SELECT photo_type, image_data
            FROM inspection_photos
            WHERE inspection_id = ?
            ORDER BY photo_order
        """, (inspection_id,))
        
        photos = {}
        for row in cursor.fetchall():
            photo_type = row[0]
            image_data = row[1]
            if image_data:
                # Convert bytes to base64
                if isinstance(image_data, bytes):
                    photos[photo_type] = base64.b64encode(image_data).decode('utf-8')
                else:
                    photos[photo_type] = image_data
        
        logging.info(f"✅ Found {len(photos)} photos")
        
        # Get damages
        cursor.execute("""
            SELECT damage_type, severity, location, description
            FROM inspection_damages
            WHERE inspection_id = %s
        """ if is_postgres else """
            SELECT damage_type, severity, location, description
            FROM inspection_damages
            WHERE inspection_id = ?
        """, (inspection_id,))
        
        damages = []
        for row in cursor.fetchall():
            damages.append({
                'type': row[0],
                'severity': row[1],
                'location': row[2],
                'description': row[3]
            })
        
        logging.info(f"✅ Found {len(damages)} damages")
        
        return {
            'inspection_number': inspection[1],
            'inspection_type': inspection[2],
            'plate': inspection[3],
            'ra': inspection[4],
            'inspector': inspection[5],
            'observations': inspection[6] or '',
            'damage_count': inspection[7],
            'odometer': inspection[8],
            'fuel_level': inspection[9],
            'created_at': inspection[10],
            'photos': photos,
            'damages': damages
        }
        
    finally:
        conn.close()

def send_email(inspection_data, recipient_email):
    """Send inspection report email"""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import base64 as b64
    
    # Get Gmail credentials from database
    conn, is_postgres = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT access_token, refresh_token FROM gmail_oauth WHERE id = 1")
        oauth_row = cursor.fetchone()
        
        if not oauth_row:
            logging.error("❌ Gmail OAuth not configured")
            return False
        
        access_token = oauth_row[0]
        refresh_token = oauth_row[1]
        
        # Get client credentials
        cursor.execute("SELECT client_id, client_secret FROM gmail_oauth WHERE id = 1")
        client_row = cursor.fetchone()
        client_id = client_row[0] if client_row else os.getenv('GMAIL_CLIENT_ID')
        client_secret = client_row[1] if client_row else os.getenv('GMAIL_CLIENT_SECRET')
        
    finally:
        conn.close()
    
    # Create credentials
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret
    )
    
    # Build Gmail service
    service = build('gmail', 'v1', credentials=creds)
    
    # Read logo
    logo_base64 = ''
    logo_path = '/Users/filipepacheco/CascadeProjects/carscraping/logo_autoprudente 1.png'
    try:
        with open(logo_path, 'rb') as f:
            logo_base64 = base64.b64encode(f.read()).decode('utf-8')
        logging.info("✅ Logo loaded")
    except Exception as e:
        logging.warning(f"⚠️ Could not load logo: {e}")
    
    # Generate fuel gauge SVG
    fuel_percentage = int(inspection_data['fuel_level'])
    fuel_color = '#10b981' if fuel_percentage >= 75 else '#f59e0b' if fuel_percentage >= 50 else '#ef4444'
    tank_height = 100
    fill_height = tank_height * fuel_percentage / 100
    fill_y = tank_height - fill_height
    
    fuel_gauge_svg = f"""
    <svg width="80" height="120" viewBox="0 0 80 120" style="display: block; margin: 0 auto;">
        <rect x="20" y="10" width="40" height="100" rx="5" fill="none" stroke="#64748b" stroke-width="3"/>
        <rect x="23" y="{10 + fill_y}" width="34" height="{fill_height}" rx="3" fill="{fuel_color}"/>
        <path d="M 60 40 L 70 35 L 70 45 Z" fill="#64748b"/>
    </svg>
    """
    
    # Generate photos HTML
    photos_html = ""
    photo_labels = {
        'front': 'Frente',
        'back': 'Traseira',
        'left': 'Lado Esquerdo',
        'right': 'Lado Direito',
        'interior': 'Interior',
        'odometer': 'Conta-Quilómetros'
    }
    
    for photo_type, label in photo_labels.items():
        if photo_type in inspection_data['photos']:
            photo_data = inspection_data['photos'][photo_type]
            if not photo_data.startswith('data:'):
                photo_data = f"data:image/jpeg;base64,{photo_data}"
            
            photos_html += f"""
            <div style="margin-bottom: 20px;">
                <h4 style="color: #009cb6; margin-bottom: 10px; font-size: 16px;">{label}</h4>
                <img class="photo-img" src="{photo_data}" alt="{label}" style="max-width: 100%; width: 100%; height: auto; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: block;" />
            </div>
            """
    
    # Create HTML email
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="x-apple-disable-message-reformatting">
        <title>Relatório de Entrega</title>
        <style type="text/css">
            @media only screen and (max-width: 600px) {{
                .container {{ width: 100% !important; }}
                .header {{ padding: 20px 15px !important; }}
                .header h1 {{ font-size: 22px !important; }}
                .header p {{ font-size: 16px !important; }}
                .content {{ padding: 20px 15px !important; }}
                .info-row {{ display: block !important; width: 100% !important; }}
                .info-cell {{ display: block !important; width: 100% !important; padding: 10px 0 !important; }}
                table {{ font-size: 14px !important; }}
                h3 {{ font-size: 18px !important; }}
                .photo-img {{ width: 100% !important; }}
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background-color: #f3f4f6;">
        <div class="container" style="max-width: 600px; width: 100%; margin: 0 auto; background-color: #ffffff;">
            <div class="header" style="background: linear-gradient(135deg, #009cb6 0%, #007a8c 100%); color: white; padding: 30px; text-align: center;">
                {"<img src='data:image/png;base64," + logo_base64 + "' alt='Auto Prudente' style='max-width: 200px; height: auto; margin-bottom: 20px;' />" if logo_base64 else ""}
                <h1 style="margin: 0; font-size: 28px; font-weight: 600;">Relatório de Entrega</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.95;">RA: {inspection_data['ra']}</p>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">{inspection_data['created_at']}</p>
            </div>
            
            <div class="content" style="padding: 30px;">
                <div class="info-row" style="display: table; width: 100%; margin-bottom: 25px;">
                    <div class="info-cell" style="display: table-cell; width: 50%; padding-right: 15px;">
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">Colaborador</p>
                        <p style="margin: 5px 0 0 0; color: #111827; font-size: 16px; font-weight: 600;">{inspection_data['inspector']}</p>
                    </div>
                    <div class="info-cell" style="display: table-cell; width: 50%; padding-left: 15px;">
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">Local de Entrega</p>
                        <p style="margin: 5px 0 0 0; color: #111827; font-size: 16px; font-weight: 600;">Local não especificado</p>
                    </div>
                </div>
                
                <h3 style="color: #009cb6; margin-bottom: 15px; font-size: 20px;">Detalhes do Veículo</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 15px;">
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280;">Matrícula:</td>
                        <td style="padding: 12px 0; color: #111827; font-weight: 600; text-align: right;">{inspection_data['plate']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280;">Quilómetros:</td>
                        <td style="padding: 12px 0; color: #111827; font-weight: 600; text-align: right;">{inspection_data['odometer']} km</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280;">Tipo de Inspeção:</td>
                        <td style="padding: 12px 0; color: #111827; font-weight: 600; text-align: right;">Entrega</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px 0; color: #6b7280;">Danos Identificados:</td>
                        <td style="padding: 12px 0; color: #111827; font-weight: 600; text-align: right;">{inspection_data['damage_count']}</td>
                    </tr>
                </table>
                
                <h3 style="color: #009cb6; margin-bottom: 15px; font-size: 20px;">Nível de Combustível</h3>
                <div style="text-align: center; margin-bottom: 25px;">
                    {fuel_gauge_svg}
                    <p style="margin: 10px 0 0 0; color: #6b7280; font-size: 14px;">{fuel_percentage}%</p>
                </div>
                
                <h3 style="color: #009cb6; margin-bottom: 15px; font-size: 20px;">Fotografias do Veículo</h3>
                {photos_html}
                
                {"<h3 style='color: #009cb6; margin-top: 30px; margin-bottom: 15px; font-size: 20px;'>Observações</h3><p style='color: #374151; line-height: 1.6;'>" + inspection_data['observations'] + "</p>" if inspection_data['observations'] else ""}
                
                <div style="margin-top: 40px; padding-top: 25px; border-top: 2px solid #e5e7eb; text-align: center;">
                    <p style="margin: 0; color: #6b7280; font-size: 13px;">Auto Prudente © 2026 · Sistema de Gestão de Frotas</p>
                    <p style="margin: 8px 0 0 0; color: #9ca3af; font-size: 12px;">Relatório gerado automaticamente · Número: {inspection_data['inspection_number']}</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create message
    message = MIMEMultipart('alternative')
    message['To'] = recipient_email
    message['From'] = 'info@auto-prudente.com'
    message['Subject'] = f"Relatório de Entrega - RA {inspection_data['ra']}"
    
    html_part = MIMEText(html_message, 'html')
    message.attach(html_part)
    
    # Send email
    try:
        raw_message = b64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        send_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        logging.info(f"✅ Email sent successfully! Message ID: {send_message['id']}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to send email: {e}")
        return False

if __name__ == '__main__':
    logging.info("=" * 80)
    logging.info("📧 SENDING LAST INSPECTION REPORT")
    logging.info("=" * 80)
    
    # Get last inspection
    inspection = get_last_inspection()
    if not inspection:
        sys.exit(1)
    
    # Send email
    success = send_email(inspection, 'carlpac82@hotmail.com')
    
    if success:
        logging.info("✅ Report sent successfully!")
        sys.exit(0)
    else:
        logging.error("❌ Failed to send report")
        sys.exit(1)
