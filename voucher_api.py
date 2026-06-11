from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import os
import logging
import io
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
from playwright.async_api import async_playwright
from googleapiclient.discovery import build
import os
import json

router = APIRouter()

class EmailRequest(BaseModel):
    email: str

DATABASE_URL = os.environ.get('DATABASE_URL')

# Vehicle model mapping
vehicle_models = {
    'B': 'Fiat Panda ou Similar',
    'B1': 'Peugeot 108 ou Similar',
    'B2': 'Fiat Panda ou Similar',
    'D': 'Opel Corsa ou Similar',
    'E1': 'Kia Picanto ou Similar',
    'E2': 'Citroen C3 ou Similar',
    'F': 'Ford Focus ou Similar',
    'G': 'Volkswagen Golf ou Similar',
    'I': 'Volkswagen Passat ou Similar',
    'J': 'Skoda Octavia ou Similar',
    'K': 'Opel Insignia ou Similar',
    'L': 'Volkswagen Tiguan ou Similar',
    'M': 'Nissan Qashqai ou Similar',
    'N': 'Toyota RAV4 ou Similar',
    'O': 'Volkswagen Sharan ou Similar',
    'P': 'Citroen Berlingo ou Similar'
}

# Vehicle name mapping for API - NOMES EXATOS DO COMMISSIONER DASHBOARD
vehicle_api_names = {
    'A': 'kia picanto',         # ✅
    'B': 'fiat panda',          # ✅
    'D': 'seat ibiza',          # ✅
    'E1': 'hyundai i10',        # ✅
    'E2': 'citroen c3',         # ✅
    'F': 'seat arona',          # ✅
    'G': 'fiat 500',            # ✅
    'J1': 'peugeot 2008',       # ✅
    'J2': 'peugeot 308 sw',     # ✅
    'L1': 'citroen c3 aircross', # ✅
    'L2': 'peugeot 308 sw',     # ✅
    'M1': 'dacia jogger',       # ✅
    'M2': 'citroen c4 picasso', # ✅
    'N': 'toyota proace'        # ✅
}

def format_vehicle_name(vehicle_name):
    """Format vehicle name with uppercase initials"""
    if not vehicle_name:
        return vehicle_name
    
    # Split by space and capitalize each word
    words = vehicle_name.split(' ')
    formatted_words = []
    
    for word in words:
        if word.upper() in ['FIAT', 'PEUGEOT', 'CITROEN', 'DACIA', 'HYUNDAI', 'SEAT', 'TOYOTA', 'KIA']:
            formatted_words.append(word.upper())
        elif word.lower() in ['c4', 'c3', 'i10', 'ibiza', 'arona', '500', '2008', '308', 'sw', 'aircross', 'jogger', 'picasso', 'proace', 'picanto']:
            formatted_words.append(word.upper())
        else:
            formatted_words.append(word.capitalize())
    
    return ' '.join(formatted_words)

async def send_new_booking_notification(booking_id: int, booking_data: dict):
    """Send notification email to Auto Prudente about new booking"""
    try:
        print(f"[NOTIFICATION] Sending new booking notification for {booking_data.get('voucher_number')}")
        
        # Load notification template
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'email_new_booking_notification.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Prepare template data
        notification_data = booking_data.copy()
        notification_data['booking_id'] = booking_id
        notification_data['booking_date'] = booking_data.get('created_date', '')
        
        # Render template
        from jinja2 import Template
        template = Template(template_content)
        html_content = template.render(**notification_data)
        
        # Generate PDF voucher for attachment - use same method as voucher email
        print(f"[NOTIFICATION] Generating PDF voucher for {booking_data.get('voucher_number')}")
        
        # Render HTML template for PDF (force Portuguese for Auto Prudente)
        # Override language to always use Portuguese for Auto Prudente notifications
        booking_data_for_pdf = booking_data.copy()
        booking_data_for_pdf['language'] = 'pt'
        pdf_html_content = render_voucher_template(booking_data_for_pdf)
        print(f"[NOTIFICATION] PDF HTML template rendered (PT), length: {len(pdf_html_content)}")
        
        # Converter para URL absoluta para Playwright carregar imagem (same as voucher)
        pdf_html_content = pdf_html_content.replace('src="/api/vehicles/', 'src="https://rentalprices.pt/api/vehicles/')
        # Fix encoding para espaços
        pdf_html_content = pdf_html_content.replace('/fiat panda/photo', '/fiat%20panda/photo')
        pdf_html_content = pdf_html_content.replace('/seat ibiza/photo', '/seat%20ibiza/photo')
        pdf_html_content = pdf_html_content.replace('/hyundai i10/photo', '/hyundai%20i10/photo')
        pdf_html_content = pdf_html_content.replace('/citroen c3/photo', '/citroen%20c3/photo')
        pdf_html_content = pdf_html_content.replace('/seat arona/photo', '/seat%20arona/photo')
        pdf_html_content = pdf_html_content.replace('/fiat 500/photo', '/fiat%20500/photo')
        pdf_html_content = pdf_html_content.replace('/peugeot 2008/photo', '/peugeot%202008/photo')
        pdf_html_content = pdf_html_content.replace('/peugeot 308 sw/photo', '/peugeot%20308%20sw/photo')
        pdf_html_content = pdf_html_content.replace('/citroen c3 aircross/photo', '/citroen%20c3%20aircross/photo')
        pdf_html_content = pdf_html_content.replace('/dacia jogger/photo', '/dacia%20jogger/photo')
        pdf_html_content = pdf_html_content.replace('/citroen c4 picasso/photo', '/citroen%20c4%20picasso/photo')
        pdf_html_content = pdf_html_content.replace('/toyota proace/photo', '/toyota%20proace/photo')
        pdf_html_content = pdf_html_content.replace('/kia picanto/photo', '/kia%20picanto/photo')
        
        print(f"[NOTIFICATION] Converted to absolute URLs with encoding")
        
        # Generate PDF using synchronous approach - use the original voucher template
        print(f"[NOTIFICATION] Generating PDF voucher using original template for {booking_data.get('voucher_number')}")
        
        try:
            # Load the original voucher template (Portuguese) as requested by user
            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'voucher_template_pt.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                voucher_template_content = f.read()
            
            # Prepare template data with all required fields
            voucher_data = booking_data.copy()
            voucher_data['language'] = 'pt'  # Force Portuguese
            
            # Render the voucher template
            from jinja2 import Template
            template = Template(voucher_template_content)
            voucher_html = template.render(**voucher_data)
            
            print(f"[NOTIFICATION] Original voucher template rendered, length: {len(voucher_html)}")
            
            # Convert URLs for PDF generation
            voucher_html = voucher_html.replace('src="/api/vehicles/', 'src="https://rentalprices.pt/api/vehicles/')
            voucher_html = voucher_html.replace('src="https://rentalprices.pt/api/vehicles/', 'src="https://rentalprices.pt/api/vehicles/')
            
            # Fix encoding para espaços
            voucher_html = voucher_html.replace('/fiat panda/photo', '/fiat%20panda/photo')
            voucher_html = voucher_html.replace('/seat ibiza/photo', '/seat%20ibiza/photo')
            voucher_html = voucher_html.replace('/hyundai i10/photo', '/hyundai%20i10/photo')
            voucher_html = voucher_html.replace('/citroen c3/photo', '/citroen%20c3/photo')
            voucher_html = voucher_html.replace('/seat arona/photo', '/seat%20arona/photo')
            voucher_html = voucher_html.replace('/fiat 500/photo', '/fiat%20500/photo')
            voucher_html = voucher_html.replace('/peugeot 2008/photo', '/peugeot%202008/photo')
            voucher_html = voucher_html.replace('/peugeot 308 sw/photo', '/peugeot%20308%20sw/photo')
            voucher_html = voucher_html.replace('/citroen c3 aircross/photo', '/citroen%20c3%20aircross/photo')
            voucher_html = voucher_html.replace('/dacia jogger/photo', '/dacia%20jogger/photo')
            voucher_html = voucher_html.replace('/citroen c4 picasso/photo', '/citroen%20c4%20picasso/photo')
            voucher_html = voucher_html.replace('/toyota proace/photo', '/toyota%20proace/photo')
            voucher_html = voucher_html.replace('/kia picanto/photo', '/kia%20picanto/photo')
            
            print(f"[NOTIFICATION] URLs converted for PDF generation")
            
            # Generate PDF using Playwright async (same as email_voucher that works)
            from playwright.async_api import async_playwright
            
            # Use await directly since function is now async
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Set content and wait for images to load
                await page.set_content(voucher_html)
                await page.wait_for_timeout(2000)  # Wait for images to load
                
                # Generate PDF
                pdf_content = await page.pdf(
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '20px',
                        'right': '20px',
                        'bottom': '20px',
                        'left': '20px'
                    }
                )
                
                await browser.close()
            
            print(f"[NOTIFICATION] Original voucher PDF generated with Playwright, size: {len(pdf_content)} bytes")
            
        except ImportError:
            print(f"[NOTIFICATION] WeasyPrint not available, using fallback")
            # Fallback: create a simple text-based PDF
            import reportlab
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO
            
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            
            # Add content
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, 800, f"VOUCHER {booking_data.get('voucher_number')}")
            
            p.setFont("Helvetica", 12)
            y_pos = 750
            p.drawString(50, y_pos, f"Agente: {booking_data.get('agent_name', 'N/A')}")
            y_pos -= 20
            p.drawString(50, y_pos, f"Cliente: {booking_data.get('client_name', 'N/A')}")
            y_pos -= 20
            p.drawString(50, y_pos, f"Veículo: GRUPO {booking_data.get('vehicle_group', 'N/A')} - {booking_data.get('vehicle_model', 'N/A')}")
            y_pos -= 20
            p.drawString(50, y_pos, f"Levantamento: {booking_data.get('pickup_date', 'N/A')} {booking_data.get('pickup_time', 'N/A')}")
            y_pos -= 20
            p.drawString(50, y_pos, f"Local: {booking_data.get('pickup_location', 'N/A')}")
            y_pos -= 20
            p.drawString(50, y_pos, f"Entrega: {booking_data.get('dropoff_date', 'N/A')} {booking_data.get('dropoff_time', 'N/A')}")
            y_pos -= 20
            p.drawString(50, y_pos, f"Local: {booking_data.get('dropoff_location', 'N/A')}")
            y_pos -= 20
            p.drawString(50, y_pos, f"Total: €{booking_data.get('total_price', 'N/A')}")
            y_pos -= 20
            p.drawString(50, y_pos, f"Depósito: €{booking_data.get('deposit', 'N/A')}")
            y_pos -= 20
            p.drawString(50, y_pos, f"A Pagar: €{booking_data.get('amount_to_pay', 'N/A')}")
            
            p.save()
            pdf_content = buffer.getvalue()
            buffer.close()
            
            print(f"[NOTIFICATION] Fallback PDF generated, size: {len(pdf_content)} bytes")
            
        except Exception as e:
            print(f"[NOTIFICATION] Error generating PDF: {e}")
            pdf_content = None
        
        # Get Gmail OAuth credentials
        print(f"[NOTIFICATION] Loading Gmail OAuth credentials")
        credentials = get_gmail_credentials()
        
        if not credentials:
            print(f"[NOTIFICATION] Gmail OAuth not configured")
            return False
        
        # Create email message using same method as voucher
        print(f"[NOTIFICATION] Creating email message with PDF attachment")
        
        if pdf_content:
            # Use the same create_message_with_attachment function as voucher
            message = create_message_with_attachment(
                credentials,
                'info@auto-prudente.com',
                f"Nova Reserva - {booking_data.get('voucher_number', '')}",
                html_content,  # HTML notification body
                pdf_content,
                f"voucher_{booking_data.get('voucher_number', '')}.pdf"
            )
            print(f"[NOTIFICATION] PDF attached: voucher_{booking_data.get('voucher_number', '')}.pdf")
        else:
            # Send without PDF if generation failed
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            import base64
            
            message_obj = MIMEMultipart()
            message_obj['to'] = 'info@auto-prudente.com'
            message_obj['subject'] = f"Nova Reserva - {booking_data.get('voucher_number', '')}"
            message_obj.attach(MIMEText(html_content, 'html'))
            message = {'raw': base64.urlsafe_b64encode(message_obj.as_bytes()).decode()}
            print(f"[NOTIFICATION] Sending email without PDF attachment")
        
        # Send email via Gmail API (same as voucher)
        print(f"[NOTIFICATION] Sending email via Gmail API")
        try:
            service = build('gmail', 'v1', credentials=credentials)
            voucher_num = booking_data.get('voucher_number', '')
            subject = f"Nova Reserva - {voucher_num}"

            # Collect recipients: Auto Prudente + commissioner + client
            recipients = ['info@auto-prudente.com']
            agent_email = booking_data.get('agent_email', '')
            client_email = booking_data.get('client_email', '')
            if agent_email and agent_email != 'N/A' and agent_email not in recipients:
                recipients.append(agent_email)
            if client_email and client_email != 'N/A' and client_email not in recipients:
                recipients.append(client_email)

            # Generate client-language PDF for client email
            client_lang = booking_data.get('language', 'pt') or 'pt'
            client_pdf_content = pdf_content  # fallback to PT
            if client_lang != 'pt' and client_email and client_email != 'N/A':
                try:
                    lang_template_path = os.path.join(os.path.dirname(__file__), 'templates', f'voucher_template_{client_lang}.html')
                    if not os.path.exists(lang_template_path):
                        lang_template_path = os.path.join(os.path.dirname(__file__), 'templates', 'voucher_template_en.html')
                    with open(lang_template_path, 'r', encoding='utf-8') as f:
                        lang_template_content = f.read()
                    from jinja2 import Template as _T
                    lang_voucher_html = _T(lang_template_content).render(**{**booking_data, 'language': client_lang})
                    lang_voucher_html = lang_voucher_html.replace('src="/api/vehicles/', 'src="https://rentalprices.pt/api/vehicles/')
                    async with async_playwright() as _p:
                        _browser = await _p.chromium.launch()
                        _page = await _browser.new_page()
                        await _page.set_content(lang_voucher_html)
                        await _page.wait_for_timeout(2000)
                        client_pdf_content = await _page.pdf(format='A4', print_background=True, margin={'top':'20px','right':'20px','bottom':'20px','left':'20px'})
                        await _browser.close()
                    print(f"[NOTIFICATION] Client PDF generated in '{client_lang}'")
                except Exception as e:
                    print(f"[NOTIFICATION] Error generating client-lang PDF, using PT fallback: {e}")

            # Build client-specific email body using dedicated template
            client_i18n = {
                'pt': {
                    'greeting': 'Olá',
                    'intro_text': 'Recebemos o seu pedido de reserva. Segue abaixo um resumo.',
                    'pending_text': 'A sua reserva está pendente de confirmação. Iremos verificar a disponibilidade e entrar em contacto brevemente.',
                    'summary_title': 'Resumo da Reserva',
                    'group_label': 'GRUPO',
                    'pickup_label': 'Levantamento',
                    'dropoff_label': 'Devolução',
                    'total_label': 'Valor Total',
                    'deposit_label': 'Depósito',
                    'contact_text': 'Dúvidas? Ligue-nos:',
                    'footer_auto': 'Este email foi gerado automaticamente pelo sistema de reservas da Auto Prudente.',
                    'subject_line': f"Pedido de Reserva Recebido - {voucher_num}",
                    'price_base_label': 'Preço Base',
                    'price_insurance_label': 'Seguro Premium',
                    'price_roadtax_label': 'Taxa de Estrada',
                    'total_label': 'Total',
                },
                'en': {
                    'greeting': 'Hello',
                    'intro_text': 'We have received your booking request. Please find a summary below.',
                    'pending_text': 'Your booking is pending confirmation. We will check availability and contact you shortly.',
                    'summary_title': 'Booking Summary',
                    'group_label': 'GROUP',
                    'pickup_label': 'Pickup',
                    'dropoff_label': 'Return',
                    'total_label': 'Total Amount',
                    'deposit_label': 'Deposit',
                    'contact_text': 'Questions? Call us:',
                    'footer_auto': 'This email was automatically generated by the Auto Prudente booking system.',
                    'subject_line': f"Booking Request Received - {voucher_num}",
                    'price_base_label': 'Base Price',
                    'price_insurance_label': 'Premium Insurance',
                    'price_roadtax_label': 'Road Tax',
                    'total_label': 'Total',
                },
                'fr': {
                    'greeting': 'Bonjour',
                    'intro_text': 'Nous avons bien reçu votre demande de réservation. Veuillez trouver un résumé ci-dessous.',
                    'pending_text': 'Votre réservation est en attente de confirmation. Nous vérifierons la disponibilité et vous contacterons prochainement.',
                    'summary_title': 'Résumé de la Réservation',
                    'group_label': 'GROUPE',
                    'pickup_label': 'Départ',
                    'dropoff_label': 'Retour',
                    'total_label': 'Montant Total',
                    'deposit_label': 'Dépôt',
                    'contact_text': 'Des questions? Appelez-nous:',
                    'footer_auto': 'Cet email a été généré automatiquement par le système de réservation Auto Prudente.',
                    'subject_line': f"Demande de Réservation Reçue - {voucher_num}",
                    'price_base_label': 'Prix de Base',
                    'price_insurance_label': 'Assurance Premium',
                    'price_roadtax_label': 'Taxe Routière',
                    'total_label': 'Total',
                },
                'de': {
                    'greeting': 'Hallo',
                    'intro_text': 'Wir haben Ihre Buchungsanfrage erhalten. Nachfolgend finden Sie eine Zusammenfassung.',
                    'pending_text': 'Ihre Buchung wartet auf Bestätigung. Wir prüfen die Verfügbarkeit und melden uns in Kürze.',
                    'summary_title': 'Buchungsübersicht',
                    'group_label': 'GRUPPE',
                    'pickup_label': 'Abholung',
                    'dropoff_label': 'Rückgabe',
                    'total_label': 'Gesamtbetrag',
                    'deposit_label': 'Kaution',
                    'contact_text': 'Fragen? Rufen Sie uns an:',
                    'footer_auto': 'Diese E-Mail wurde automatisch vom Buchungssystem der Auto Prudente generiert.',
                    'subject_line': f"Buchungsanfrage Eingegangen - {voucher_num}",
                    'price_base_label': 'Grundpreis',
                    'price_insurance_label': 'Premium-Versicherung',
                    'price_roadtax_label': 'Straßensteuer',
                    'total_label': 'Gesamt',
                },
            }
            ci = client_i18n.get(client_lang, client_i18n['en'])

            client_template_path = os.path.join(os.path.dirname(__file__), 'templates', 'email_booking_client.html')
            with open(client_template_path, 'r', encoding='utf-8') as f:
                client_tpl = f.read()
            from jinja2 import Template as _Tc
            client_html = _Tc(client_tpl).render(**{**booking_data, **ci, 'language': client_lang})

            for recipient in recipients:
                is_client = recipient == client_email
                use_pdf = client_pdf_content if is_client else pdf_content
                use_subject = ci['subject_line'] if is_client else subject
                use_html = client_html if is_client else html_content
                if use_pdf:
                    msg = create_message_with_attachment(
                        credentials,
                        recipient,
                        use_subject,
                        use_html,
                        use_pdf,
                        f"voucher_{voucher_num}.pdf"
                    )
                else:
                    from email.mime.multipart import MIMEMultipart as _MM
                    from email.mime.text import MIMEText as _MT
                    import base64 as _b64
                    mo = _MM()
                    mo['to'] = recipient
                    mo['subject'] = use_subject
                    mo.attach(_MT(use_html, 'html'))
                    msg = {'raw': _b64.urlsafe_b64encode(mo.as_bytes()).decode()}
                result = service.users().messages().send(userId='me', body=msg).execute()
                print(f"[NOTIFICATION] Email sent to {recipient} (lang={client_lang if is_client else 'pt'}), ID: {result.get('id')}")

            return True
            
        except Exception as e:
            print(f"[NOTIFICATION] Error sending via Gmail API: {e}")
            return False
        
    except Exception as e:
        print(f"[NOTIFICATION] Error sending notification: {e}")
        return False

async def _generate_pdf_async(pdf_html_content):
    """Async function to generate PDF"""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Set content and wait for images to load
        await page.set_content(pdf_html_content)
        await page.wait_for_timeout(2000)  # Wait for images to load
        
        # Generate PDF
        pdf_content = await page.pdf(
            format='A4',
            print_background=True,
            margin={
                'top': '20px',
                'right': '20px',
                'bottom': '20px',
                'left': '20px'
            }
        )
        
        await browser.close()
        return pdf_content

def render_email_template(booking_data):
    """Render email template with booking data and language support"""
    # Get language from booking data, default to 'pt'
    language = booking_data.get('language', 'pt').lower()
    
    # Map language codes to template files
    language_templates = {
        'pt': 'email_voucher_pt.html',
        'en': 'email_voucher_en.html', 
        'fr': 'email_voucher_fr.html',
        'es': 'email_voucher_es.html',
        'de': 'email_voucher_de.html'
    }
    
    # Get template file for language, fallback to Portuguese
    template_file = language_templates.get(language, 'email_voucher_pt.html')
    template_path = os.path.join(os.path.dirname(__file__), 'templates', template_file)
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Extract first name from client name
        client_name = booking_data.get('client_name', '')
        client_first_name = client_name.split(' ')[0] if client_name else 'Cliente'
        
        # Format vehicle name with uppercase initials
        vehicle_name = format_vehicle_name(booking_data.get('vehicle_name', ''))
        
        # Get vehicle group
        vehicle_group = booking_data.get('vehicle_group', '')
        
        # Format dates
        pickup_date = booking_data.get('pickup_date', '')
        pickup_time = booking_data.get('pickup_time', '')
        dropoff_date = booking_data.get('dropoff_date', '')
        dropoff_time = booking_data.get('dropoff_time', '')
        
        # Get vehicle image URL (absolute)
        vehicle_image_url = f"https://rentalprices.pt/api/vehicles/{booking_data.get('vehicle_name', '').replace(' ', '%20')}/photo"
        
        # Calculate pricing correctly
        total_price = float(booking_data.get('total_price', '0').replace('€', '').replace(',', '.'))
        deposit_amount = float(booking_data.get('deposit_amount', '0').replace('€', '').replace(',', '.'))
        
        # If there's a deposit, amount to pay is total - deposit
        if deposit_amount > 0:
            amount_to_pay = total_price - deposit_amount
        else:
            amount_to_pay = total_price
        
        # Replace template variables
        template_content = template_content.replace('{{CLIENT_FIRST_NAME}}', client_first_name)
        template_content = template_content.replace('{{CLIENT_NAME}}', client_name)
        template_content = template_content.replace('{{VOUCHER_NUMBER}}', booking_data.get('voucher_number', ''))
        template_content = template_content.replace('{{VEHICLE_GROUP}}', vehicle_group)
        template_content = template_content.replace('{{VEHICLE_NAME}}', vehicle_name)
        template_content = template_content.replace('{{VEHICLE_IMAGE_URL}}', vehicle_image_url)
        template_content = template_content.replace('{{PICKUP_LOCATION}}', booking_data.get('pickup_location', ''))
        template_content = template_content.replace('{{PICKUP_DATE}}', pickup_date)
        template_content = template_content.replace('{{PICKUP_TIME}}', pickup_time)
        template_content = template_content.replace('{{DROPOFF_DATE}}', dropoff_date)
        template_content = template_content.replace('{{DROPOFF_TIME}}', dropoff_time)
        template_content = template_content.replace('{{TOTAL_PRICE}}', f"{total_price:.2f}")
        template_content = template_content.replace('{{DEPOSIT_AMOUNT}}', f"{deposit_amount:.2f}")
        template_content = template_content.replace('{{AMOUNT_TO_PAY}}', f"{amount_to_pay:.2f}")
        template_content = template_content.replace('{{LOGO_URL}}', 'http://rentalprices.pt/static/ap-heather.png')
        
        print(f"[VOUCHER EMAIL] Using template: {template_file} for language: {language}")
        
        return template_content
        
    except Exception as e:
        print(f"[VOUCHER EMAIL] Error rendering email template: {e}")
        # Fallback to simple HTML
        return f"""
        <html>
        <body>
            <h2>Olá {client_first_name},</h2>
            <p>Agradecemos a sua reserva na Auto Prudente Rent a Car!</p>
            <p>Voucher: {booking_data.get('voucher_number', '')}</p>
            <p>Veículo: {booking_data.get('vehicle_name', '')}</p>
            <p>Entrega: {pickup_date} {pickup_time}</p>
            <p>Recolha: {dropoff_date} {dropoff_time}</p>
            <p>Valor a pagar: €{booking_data.get('amount_to_pay', '0')}</p>
            <p>O voucher está em anexo.</p>
        </body>
        </html>
        """

def render_voucher_template(booking_data):
    """Render voucher template with booking data and language support"""
    # Get language from booking data, default to 'pt'
    language = booking_data.get('language', 'pt').lower()
    
    # Map language codes to template files
    language_templates = {
        'pt': 'voucher_template_pt.html',
        'en': 'voucher_template_en.html', 
        'fr': 'voucher_template_fr.html',
        'es': 'voucher_template_es.html',
        'de': 'voucher_template_de.html'
    }
    
    # Get template file for language, fallback to Portuguese
    template_file = language_templates.get(language, 'voucher_template_pt.html')
    template_path = os.path.join(os.path.dirname(__file__), 'templates', template_file)
    
    print(f"[VOUCHER PDF] Language: {language}")
    print(f"[VOUCHER PDF] Template file: {template_file}")
    print(f"[VOUCHER PDF] Template path: {template_path}")
    print(f"[VOUCHER PDF] Template exists: {os.path.exists(template_path)}")
    
    # List all templates available
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    available_templates = [f for f in os.listdir(templates_dir) if f.startswith('voucher_template_')]
    print(f"[VOUCHER PDF] Available templates: {available_templates}")
    
    # Fallback to Portuguese if template doesn't exist
    if not os.path.exists(template_path):
        print(f"[VOUCHER PDF] Template not found, falling back to Portuguese")
        template_file = 'voucher_template_pt.html'
        template_path = os.path.join(os.path.dirname(__file__), 'templates', template_file)
        print(f"[VOUCHER PDF] Fallback template path: {template_path}")
        print(f"[VOUCHER PDF] Fallback template exists: {os.path.exists(template_path)}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # DEBUG: Print all booking data
        print(f"[VOUCHER PDF] DEBUG - Booking data keys: {list(booking_data.keys())}")
        print(f"[VOUCHER PDF] DEBUG - Sample data:")
        for key in ['voucher_number', 'client_name', 'vehicle_group', 'total_price', 'deposit', 'agent_name', 'booking_date']:
            if key in booking_data:
                print(f"   {key}: {booking_data[key]} (type: {type(booking_data[key])})")
        
        # DEBUG: Check specific problematic fields
        print(f"[VOUCHER PDF] DEBUG - Agent details:")
        print(f"   agent_name: '{booking_data.get('agent_name', 'NOT_FOUND')}'")
        print(f"   agent_email: '{booking_data.get('agent_email', 'NOT_FOUND')}'")
        print(f"   agent_phone: '{booking_data.get('agent_phone', 'NOT_FOUND')}'")
        print(f"   booking_date: '{booking_data.get('booking_date', 'NOT_FOUND')}'")
        print(f"   created_date: '{booking_data.get('created_date', 'NOT_FOUND')}'")
        print(f"[VOUCHER PDF] DEBUG - Price details:")
        print(f"   total_price: '{booking_data.get('total_price', 'NOT_FOUND')}'")
        print(f"   deposit: '{booking_data.get('deposit', 'NOT_FOUND')}'")
        print(f"   amount_to_pay: '{booking_data.get('amount_to_pay', 'NOT_FOUND')}'")
        
        # Use Jinja2 Template instead of replace()
        print(f"[VOUCHER PDF] DEBUG - Using Jinja2 Template engine...")
        from jinja2 import Template
        template = Template(template_content)
        rendered_content = template.render(**booking_data)
        
        print(f"[VOUCHER PDF] DEBUG - Template rendered successfully")
        print(f"[VOUCHER PDF] DEBUG - Rendered length: {len(rendered_content)}")
        
        return rendered_content
        
    except Exception as e:
        print(f"[VOUCHER PDF] Error rendering voucher template: {e}")
        # Fallback to simple HTML
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Voucher - AutoPrudente</title>
        </head>
        <body>
            <h1>Voucher {booking_data.get('voucher_number', '')}</h1>
            <p>Cliente: {booking_data.get('client_name', '')}</p>
            <p>Veículo: {booking_data.get('vehicle_name', '')}</p>
            <p>Entrega: {booking_data.get('pickup_date', '')} {booking_data.get('pickup_time', '')}</p>
            <p>Recolha: {booking_data.get('dropoff_date', '')} {booking_data.get('dropoff_time', '')}</p>
            <p>Valor a pagar: €{booking_data.get('amount_to_pay', '0')}</p>
        </body>
        </html>
        """

def create_message_with_attachment(credentials, to_email, subject, body, attachment_content, filename):
    """Create email message with attachment"""
    # Create message
    message = MIMEMultipart('related')
    message['to'] = to_email
    message['subject'] = subject
    
    # Create HTML body
    html_part = MIMEText(body, 'html')
    message.attach(html_part)
    
    # Add attachment
    part = MIMEBase('application', 'pdf')
    part.set_payload(attachment_content)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    message.attach(part)
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

def get_gmail_credentials():
    """Load Gmail OAuth credentials from database (same as main.py)"""
    from google.oauth2.credentials import Credentials
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT access_token, refresh_token 
            FROM oauth_tokens 
            WHERE provider = 'google' 
            ORDER BY updated_at DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        
        if not row:
            logging.error("❌ No OAuth access token found in database")
            return None
        
        access_token = row[0]
        refresh_token = row[1] if len(row) > 1 else None
        
        if not refresh_token or refresh_token.strip() == '':
            logging.error("❌ No refresh_token found - Gmail must be reconnected in Admin Settings")
            return None
        
        # Load OAuth client credentials from environment
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logging.error("❌ GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not configured")
            return None
        
        # Create credentials with refresh capability
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        
        logging.info("✅ Gmail credentials loaded successfully")
        return credentials
        
    finally:
        cur.close()
        conn.close()

def get_booking_data(booking_id):
    """Get booking data with commissioner info"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get booking with commissioner data
        cur.execute("""
            SELECT 
                cb.id,
                cb.voucher_number,
                cb.client_name,
                cb.client_email,
                cb.client_phone,
                cb.hotel,
                cb.room_number,
                cb.pickup_date,
                cb.pickup_time,
                cb.dropoff_date,
                cb.dropoff_time,
                cb.pickup_location,
                cb.dropoff_location,
                cb.vehicle_group,
                cb.extras,
                cb.flight_number,
                cb.language,
                cb.observations,
                cb.deposit,
                cb.price,
                cb.created_at,
                c.name as agent_name,
                c.email as agent_email,
                c.phone as agent_phone,
                cb.base_price,
                cb.premium_insurance,
                cb.road_tax,
                cb.extras_total,
                cb.insurance_type
            FROM commission_bookings cb
            LEFT JOIN commissioners c ON cb.commissioner_id = c.id
            WHERE cb.id = %s
        """, (booking_id,))
        
        result = cur.fetchone()
        
        if not result:
            return None
        
        # Calculate rental days
        pickup_date = result[7]
        dropoff_date = result[9]
        rental_days = (dropoff_date - pickup_date).days if pickup_date and dropoff_date else 0
        
        # Calculate amount to pay
        total_price = float(result[19]) if result[19] else 0  # cb.price is at index 19
        deposit = float(result[18]) if result[18] else 0       # cb.deposit is at index 18
        amount_to_pay = total_price - deposit
        
        # Parse extras
        extras = result[14] if result[14] else []
        if isinstance(extras, str):
            import json
            try:
                extras = json.loads(extras)
            except:
                extras = []
        
        booking_data = {
            'id': result[0],
            'voucher_number': result[1],
            'client_name': result[2],
            'client_email': result[3],
            'client_phone': result[4],
            'hotel': result[5],
            'room_number': result[6],
            'pickup_date': result[7].strftime('%d/%m/%Y') if result[7] else '',
            'pickup_time': str(result[8]) if result[8] else '',
            'dropoff_date': result[9].strftime('%d/%m/%Y') if result[9] else '',
            'dropoff_time': str(result[10]) if result[10] else '',
            'pickup_location': result[11],
            'dropoff_location': result[12],
            'vehicle_group': result[13],
            'vehicle_name': vehicle_api_names.get(result[13], result[13]),  # Add vehicle name
            'vehicle_model': vehicle_models.get(result[13], f'{result[13]} ou Similar'),
            'extras': extras,
            'flight_number': result[15],
            'language': result[16] or 'pt',  # Add language field
            'observations': result[17],
            'deposit': f"{deposit:.2f}",
            'total_price': f"{total_price:.2f}",
            'amount_to_pay': f"{amount_to_pay:.2f}",
            'rental_days': rental_days,
            'created_date': result[20].strftime('%d/%m/%Y %H:%M') if result[20] else '',  # Format datetime without seconds
            'agent_name': result[21] or 'N/A',
            'agent_email': result[22] or 'N/A',
            'agent_phone': result[23] or 'N/A',
            'base_price': f"{float(result[24]):.2f}" if result[24] else '0.00',
            'premium_insurance': f"{float(result[25]):.2f}" if result[25] else '0.00',
            'road_tax': f"{float(result[26]):.2f}" if result[26] else '0.00',
            'extras_total': f"{float(result[27]):.2f}" if result[27] else '0.00',
            'insurance_type': result[28] or 'base',
            'booking_date': result[20].strftime('%d/%m/%Y %H:%M') if result[20] else '',  # Clean format without seconds
            'vehicle_image': f'/api/vehicles/{vehicle_api_names.get(result[13], result[13])}/photo' if result[13] else ''
        }
        
        return booking_data
        
    finally:
        cur.close()
        conn.close()

@router.get('/api/commissioner/voucher/print/{booking_id}')
async def print_voucher(booking_id: int):
    """Generate and return voucher PDF using Playwright"""
    try:
        print(f"[VOUCHER PRINT] Starting PDF generation for booking {booking_id}")
        booking_data = get_booking_data(booking_id)
        
        if not booking_data:
            print(f"[VOUCHER PRINT] Booking not found: {booking_id}")
            raise HTTPException(status_code=404, detail='Reserva não encontrada')
        
        print(f"[VOUCHER PRINT] Booking data loaded: {booking_data.get('voucher_number')}")
        print(f"[VOUCHER PRINT] Vehicle image URL: {booking_data.get('vehicle_image')}")
        
        # Render HTML template
        html_content = render_voucher_template(booking_data)
        print(f"[VOUCHER PRINT] HTML template rendered, length: {len(html_content)}")
        
        # Converter para URL absoluta para Playwright carregar imagem
        html_content = html_content.replace('src="/api/vehicles/', 'src="https://rentalprices.pt/api/vehicles/')
        # Fix encoding para espaços
        html_content = html_content.replace('/fiat panda/photo', '/fiat%20panda/photo')
        html_content = html_content.replace('/seat ibiza/photo', '/seat%20ibiza/photo')
        html_content = html_content.replace('/hyundai i10/photo', '/hyundai%20i10/photo')
        html_content = html_content.replace('/citroen c3/photo', '/citroen%20c3/photo')
        html_content = html_content.replace('/seat arona/photo', '/seat%20arona/photo')
        html_content = html_content.replace('/fiat 500/photo', '/fiat%20500/photo')
        html_content = html_content.replace('/peugeot 2008/photo', '/peugeot%202008/photo')
        html_content = html_content.replace('/peugeot 308 sw/photo', '/peugeot%20308%20sw/photo')
        html_content = html_content.replace('/citroen c3 aircross/photo', '/citroen%20c3%20aircross/photo')
        html_content = html_content.replace('/dacia jogger/photo', '/dacia%20jogger/photo')
        html_content = html_content.replace('/citroen c4 picasso/photo', '/citroen%20c4%20picasso/photo')
        html_content = html_content.replace('/toyota proace/photo', '/toyota%20proace/photo')
        html_content = html_content.replace('/kia picanto/photo', '/kia%20picanto/photo')
        
        print(f"[VOUCHER PRINT] Converted to absolute URLs with encoding")
        print(f"[VOUCHER PRINT] Starting PDF generation with Playwright")
        
        # Generate PDF using Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set content and wait for images to load
            await page.set_content(html_content)
            
            # Wait for images to load (timeout 10 seconds)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                print("[VOUCHER PRINT] Network timeout, continuing anyway")
            
            # Generate PDF
            pdf_content = await page.pdf(
                format='A4',
                print_background=True,
                margin={
                    'top': '1cm',
                    'right': '1cm',
                    'bottom': '1cm',
                    'left': '1cm'
                }
            )
            
            await browser.close()
        
        print(f"[VOUCHER PRINT] PDF generated successfully with Playwright, size: {len(pdf_content)} bytes")
        
        # Return PDF
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type='application/pdf',
            headers={
                'Content-Disposition': f'inline; filename="voucher_{booking_data["voucher_number"]}.pdf"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[VOUCHER PRINT] Error generating voucher PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'Erro ao gerar PDF: {str(e)}')

@router.get('/api/vehicles/list-images')
async def list_vehicle_images():
    """Lista todos os veículos com imagens na base de dados"""
    try:
        import psycopg2
        import os
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT vehicle_key, content_type, downloaded_at 
            FROM vehicle_images 
            ORDER BY vehicle_key
        """)
        
        vehicles = []
        for row in cur.fetchall():
            vehicles.append({
                'vehicle_key': row[0],
                'content_type': row[1], 
                'downloaded_at': row[2]
            })
        
        cur.close()
        conn.close()
        
        return {
            'count': len(vehicles),
            'vehicles': vehicles
        }
        
    except Exception as e:
        print(f"[VEHICLES] Error listing images: {e}")
        return {'error': str(e), 'vehicles': []}

@router.post('/api/vehicles/download-group-photos')
async def download_group_photos():
    """Baixa imagens para grupos específicos do CarJet"""
    try:
        import httpx
        import os
        from datetime import datetime, timedelta
        import random
        
        print("[GROUP PHOTOS] Starting download for vehicle groups...")
        
        # Mapeamento de grupos para modelos CarJet
        group_models = {
            'A': 'kia picanto',
            'B': 'fiat panda', 
            'D': 'seat ibiza',
            'E1': 'hyundai i10',
            'E2': 'citroen c3',
            'F': 'seat arona',
            'G': 'fiat 500',
            'J1': 'peugeot 2008',
            'J2': 'peugeot 308 sw',
            'L1': 'citroen c3 aircross',
            'L2': 'peugeot 308 sw',
            'M1': 'dacia jogger',
            'M2': 'citroen c4 picasso',
            'N': 'toyota proace'
        }
        
        # Datas para scraping (hoje + 5 dias)
        days_offset = 5
        start_date = datetime.now() + timedelta(days=days_offset)
        end_date = start_date + timedelta(days=1)
        
        # Usar CarJet scraping
        try:
            from carjet_direct import scrape_carjet_direct
            
            print(f"[GROUP PHOTOS] Scraping CarJet for {start_date.strftime('%d/%m/%Y')}...")
            results = scrape_carjet_direct("Faro", start_date, end_date, quick=1)
            
            downloaded = 0
            for item in results:
                car_name = item.get('car', '').strip().lower()
                photo_url = item.get('photo', '')
                
                if not photo_url:
                    continue
                    
                # Verificar se este carro corresponde a algum grupo
                for group, model in group_models.items():
                    if model in car_name or car_name in model:
                        # Download da imagem
                        try:
                            response = httpx.get(photo_url, timeout=10)
                            if response.status_code == 200:
                                # Salvar na base de dados
                                import psycopg2
                                DATABASE_URL = os.environ.get('DATABASE_URL')
                                conn = psycopg2.connect(DATABASE_URL)
                                cur = conn.cursor()
                                
                                cur.execute("""
                                    INSERT OR REPLACE INTO vehicle_images 
                                    (vehicle_key, image_data, content_type, source_url, downloaded_at)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (model, response.content, 'image/jpeg', photo_url, datetime.now()))
                                
                                conn.commit()
                                cur.close()
                                conn.close()
                                
                                downloaded += 1
                                print(f"[GROUP PHOTOS] Downloaded {model} for group {group}")
                                break
                                
                        except Exception as e:
                            print(f"[GROUP PHOTOS] Error downloading {car_name}: {e}")
                            continue
            
            print(f"[GROUP PHOTOS] Download complete: {downloaded} images")
            return {
                'success': True,
                'downloaded': downloaded,
                'message': f'Downloaded {downloaded} vehicle group images'
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'carjet_direct module not available'
            }
            
    except Exception as e:
        print(f"[GROUP PHOTOS] Error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@router.get('/api/debug/vehicle-images/{vehicle_name}')
async def debug_vehicle_images(vehicle_name: str):
    """Debug endpoint to check vehicle images in database"""
    try:
        import psycopg2
        import os
        
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Normalize like the main endpoint
        vehicle_key = vehicle_name.lower().strip()
        
        # Check exact match
        cur.execute("SELECT vehicle_key, content_type, length(image_data) as size FROM vehicle_images WHERE vehicle_key = %s", (vehicle_key,))
        exact = cur.fetchone()
        
        # Check partial matches
        cur.execute("SELECT vehicle_key, length(image_data) as size FROM vehicle_images WHERE vehicle_key ILIKE %s ORDER BY vehicle_key LIMIT 5", (f'%{vehicle_name}%',))
        partial = cur.fetchall()
        
        # Check all similar
        cur.execute("SELECT vehicle_key, length(image_data) as size FROM vehicle_images WHERE vehicle_key ILIKE %s ORDER BY vehicle_key LIMIT 10", (f'%{vehicle_key.split()[0]}%',))
        similar = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            'searching_for': vehicle_name,
            'normalized_key': vehicle_key,
            'exact_match': {
                'found': exact is not None,
                'data': exact
            },
            'partial_matches': partial,
            'similar_matches': similar
        }
        
    except Exception as e:
        return {'error': str(e)}

@router.get('/api/commissioner-booking/confirm-and-print/{booking_id}')
async def confirm_and_print_booking(booking_id: int):
    """Confirm booking and redirect to PDF for printing"""
    try:
        print(f"[CONFIRM PRINT] Confirming booking {booking_id}")
        
        # Update booking status to confirmed
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE commission_bookings 
            SET status = 'confirmed', updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (booking_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"[CONFIRM PRINT] Booking {booking_id} confirmed successfully")
        
        # Redirect to PDF generation
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/api/commissioner-booking-pdf/generate/{booking_id}")
        
    except Exception as e:
        print(f"[CONFIRM PRINT] Error confirming booking: {e}")
        raise HTTPException(status_code=500, detail='Erro ao confirmar reserva')

@router.post('/api/commissioner/voucher/email/{booking_id}')
async def email_voucher(booking_id: int, email_request: EmailRequest):
    """Send voucher by email"""
    try:
        print(f"[VOUCHER EMAIL] Starting email send for booking {booking_id}")
        recipient_email = email_request.email
        
        if not recipient_email:
            print(f"[VOUCHER EMAIL] No email provided")
            raise HTTPException(status_code=400, detail='Email não fornecido')
        
        print(f"[VOUCHER EMAIL] Fetching booking data for ID {booking_id}")
        booking_data = get_booking_data(booking_id)
        
        if not booking_data:
            print(f"[VOUCHER EMAIL] Booking not found: {booking_id}")
            raise HTTPException(status_code=404, detail='Reserva não encontrada')
        
        print(f"[VOUCHER EMAIL] Generating PDF for voucher {booking_data.get('voucher_number')}")
        
        # Render HTML template
        html_content = render_voucher_template(booking_data)
        print(f"[VOUCHER EMAIL] HTML template rendered, length: {len(html_content)}")
        
        # Generate ultra-simple PDF - always works
        import base64
        
        # Create simple HTML content
        simple_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Voucher {booking_data.get('voucher_number')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #009cb6; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>VOUCHER {booking_data.get('voucher_number')}</h1>
            </div>
            
            <div class="section">
                <div class="label">Agente:</div>
                <p>{booking_data.get('agent_name', 'N/A')}<br>
                {booking_data.get('agent_email', 'N/A')}<br>
                {booking_data.get('agent_phone', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Cliente:</div>
                <p>{booking_data.get('client_name', 'N/A')}<br>
                {booking_data.get('client_email', 'N/A')}<br>
                {booking_data.get('client_phone', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Veículo:</div>
                <p>Grupo: {booking_data.get('vehicle_group', 'N/A')}<br>
                Modelo: {booking_data.get('vehicle_model', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Datas:</div>
                <p>Levantamento: {booking_data.get('pickup_date', 'N/A')} as {booking_data.get('pickup_time', 'N/A')}<br>
                Entrega: {booking_data.get('dropoff_date', 'N/A')} as {booking_data.get('dropoff_time', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Valores:</div>
                <p>Total: EUR {booking_data.get('total_price', 'N/A')}<br>
                Valor a pagar: EUR {booking_data.get('amount_to_pay', 'N/A')}</p>
            </div>
            
            <div class="section">
                <div class="label">Check-in Online:</div>
                <p>Escaneie o QR code ou aceda a auto-prudente.com/online-checkin/</p>
                <p>Localização: Ver no Google Maps</p>
                <p>Telefone: +351 289 542 160</p>
                <p>Email: info@auto-prudente.com</p>
            </div>
        </body>
        </html>
        """
        
        # Convert HTML to bytes (simple approach)
        html_bytes = simple_html.encode('utf-8')
        
        # Generate real PDF with Playwright (same as print function)
        print(f"[VOUCHER EMAIL] Generating real PDF for voucher {booking_data['voucher_number']}")
        
        # Render HTML template
        html_content = render_voucher_template(booking_data)
        print(f"[VOUCHER EMAIL] HTML template rendered, length: {len(html_content)}")
        
        # Converter para URL absoluta para Playwright carregar imagem
        html_content = html_content.replace('src="/api/vehicles/', 'src="https://rentalprices.pt/api/vehicles/')
        # Fix encoding para espaços
        html_content = html_content.replace('/fiat panda/photo', '/fiat%20panda/photo')
        html_content = html_content.replace('/seat ibiza/photo', '/seat%20ibiza/photo')
        html_content = html_content.replace('/hyundai i10/photo', '/hyundai%20i10/photo')
        html_content = html_content.replace('/citroen c3/photo', '/citroen%20c3/photo')
        html_content = html_content.replace('/seat arona/photo', '/seat%20arona/photo')
        html_content = html_content.replace('/fiat 500/photo', '/fiat%20500/photo')
        html_content = html_content.replace('/peugeot 2008/photo', '/peugeot%202008/photo')
        html_content = html_content.replace('/peugeot 308 sw/photo', '/peugeot%20308%20sw/photo')
        html_content = html_content.replace('/citroen c3 aircross/photo', '/citroen%20c3%20aircross/photo')
        html_content = html_content.replace('/dacia jogger/photo', '/dacia%20jogger/photo')
        html_content = html_content.replace('/citroen c4 picasso/photo', '/citroen%20c4%20picasso/photo')
        html_content = html_content.replace('/toyota proace/photo', '/toyota%20proace/photo')
        html_content = html_content.replace('/kia picanto/photo', '/kia%20picanto/photo')
        
        print(f"[VOUCHER EMAIL] Converted to absolute URLs with encoding")
        
        # Generate PDF using Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set content and wait for images to load
            await page.set_content(html_content)
            await page.wait_for_timeout(2000)  # Wait for images to load
            
            # Generate PDF
            pdf_content = await page.pdf(
                format='A4',
                print_background=True,
                margin={
                    'top': '20px',
                    'right': '20px',
                    'bottom': '20px',
                    'left': '20px'
                }
            )
            
            await browser.close()
        
        print(f"[VOUCHER EMAIL] Real PDF generated, size: {len(pdf_content)} bytes")
        
        # Get Gmail OAuth credentials
        print(f"[VOUCHER EMAIL] Loading Gmail OAuth credentials")
        credentials = get_gmail_credentials()
        
        if not credentials:
            print(f"[VOUCHER EMAIL] Gmail OAuth not configured")
            raise HTTPException(status_code=500, detail='Gmail não está configurado. Vá a Admin Settings → Email e conecte o Gmail.')
        
        # Create email message with HTML template body
        print(f"[VOUCHER EMAIL] Rendering email template")
        email_body = render_email_template(booking_data)
        
        message = create_message_with_attachment(
            credentials, 
            email_request.email, 
            f"Voucher {booking_data['voucher_number']}", 
            email_body,  # HTML template body
            pdf_content,  
            f"voucher_{booking_data['voucher_number']}.pdf"
        )
        
        # Send email
        print(f"[VOUCHER EMAIL] Sending email via Gmail API")
        try:
            service = build('gmail', 'v1', credentials=credentials)
            # message['raw'] já está codificado pela create_message_with_attachment
            message_body = {'raw': message['raw']}
            
            sent_message = service.users().messages().send(userId='me', body=message_body).execute()
            print(f"[VOUCHER EMAIL] Email sent successfully: {sent_message['id']}")
            
            return {"success": True, "message": "Voucher enviado com sucesso", "message_id": sent_message['id']}
            
        except Exception as e:
            print(f"[VOUCHER EMAIL] Error sending email: {e}")
            raise HTTPException(status_code=500, detail='Erro ao enviar email: ' + str(e))
        
    except HTTPException as he:
        print(f"[VOUCHER EMAIL] HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        print(f"[VOUCHER EMAIL] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail='Erro inesperado: ' + str(e))
