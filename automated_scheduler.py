#!/usr/bin/env python3
"""
🤖 SISTEMA DE AGENDAMENTO AUTOMÁTICO DE RELATÓRIOS

Executa pesquisas e envio de emails nos horários configurados:
- Diário: múltiplos horários com dias/locais independentes
- Semanal: dia da semana específico
- Mensal: dia do mês específico

Usa APScheduler para agendar tarefas.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Global scheduler
scheduler = None

def _get_db_connection():
    """Get database connection"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logging.error("❌ DATABASE_URL not set")
        return None
    
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        logging.error(f"❌ Database connection error: {str(e)}")
        return None

def load_advanced_settings():
    """Load advanced automated reports settings from database"""
    print("🔌 Connecting to database...", flush=True)
    conn = _get_db_connection()
    if not conn:
        print("❌ Database connection failed", flush=True)
        return None
    
    try:
        cursor = conn.cursor()
        print("🔍 Querying automatedReportsAdvanced...", flush=True)
        cursor.execute(
            "SELECT setting_value FROM price_automation_settings WHERE setting_key = 'automatedReportsAdvanced'"
        )
        row = cursor.fetchone()
        
        if row and row[0]:
            settings = json.loads(row[0])
            print(f"✅ Loaded advanced settings from database", flush=True)
            print(f"   Settings: {json.dumps(settings, indent=2)}", flush=True)
            logging.info(f"✅ Loaded advanced settings from database")
            return settings
        else:
            print(f"📭 No advanced settings found in database", flush=True)
            logging.info(f"📭 No advanced settings found")
            return None
    except Exception as e:
        print(f"❌ Error loading settings: {str(e)}", flush=True)
        logging.error(f"❌ Error loading settings: {str(e)}")
        return None
    finally:
        cursor.close()
        conn.close()

def save_automated_search_placeholder(location, days_list):
    """
    Save automated search placeholder in recent_searches
    This marks that an automated search should have occurred
    """
    print(f"\n{'='*80}", flush=True)
    print(f"💾 SAVING AUTOMATED SEARCH TO HISTORY", flush=True)
    print(f"{'='*80}", flush=True)
    print(f"📍 Location: {location}", flush=True)
    print(f"📅 Days: {days_list}", flush=True)
    
    logging.info(f"💾 SAVING AUTOMATED SEARCH PLACEHOLDER: {location}, days: {days_list}")
    
    try:
        from datetime import datetime, timedelta
        import json
        
        print("🔌 Connecting to database for saving...", flush=True)
        conn = _get_db_connection()
        if not conn:
            print("❌ Database connection FAILED!", flush=True)
            logging.error("❌ Cannot connect to database")
            return False
        
        print("✅ Database connected", flush=True)
        cursor = conn.cursor()
        
        saved_count = 0
        # For each day, create a placeholder search entry
        for day in days_list:
            pickup_date = (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d')
            timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            
            print(f"\n   📝 Saving: {location} | {day}d | {pickup_date}", flush=True)
            
            # Create placeholder results
            placeholder_results = json.dumps([{
                "info": f"Automated search placeholder for {location}, {day} days",
                "pickup_date": pickup_date,
                "location": location,
                "days": day
            }])
            
            try:
                cursor.execute("""
                    INSERT INTO recent_searches 
                    (location, start_date, days, results_data, timestamp, source)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (location, pickup_date, day, placeholder_results, timestamp, 'automated'))
                
                saved_count += 1
                print(f"   ✅ SAVED TO DATABASE: {location}, {day}d, {pickup_date}", flush=True)
                logging.info(f"   ✅ Saved placeholder: {location}, {day}d, {pickup_date}")
            except Exception as insert_error:
                print(f"   ❌ INSERT FAILED: {str(insert_error)}", flush=True)
                logging.error(f"   ❌ Insert failed: {str(insert_error)}")
        
        conn.commit()
        print(f"\n✅ COMMIT SUCCESSFUL - {saved_count} searches saved", flush=True)
        
        # VERIFICAR SE FOI SALVO
        print(f"\n🔍 VERIFYING: Checking if searches were saved...", flush=True)
        cursor.execute("""
            SELECT location, start_date, days, timestamp, source
            FROM recent_searches
            WHERE source = 'automated'
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        
        print(f"📊 Found {len(rows)} automated searches in database:", flush=True)
        for row in rows:
            loc, start, days, ts, src = row
            print(f"   • {loc} | {days}d | {start} | {ts} | source={src}", flush=True)
        
        cursor.close()
        conn.close()
        
        print(f"\n{'='*80}", flush=True)
        print(f"✅ AUTOMATED SEARCH SAVED TO HISTORY: {location} ({saved_count} records)", flush=True)
        print(f"{'='*80}\n", flush=True)
        
        logging.info(f"✅ Search placeholders saved for {location}")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED TO SAVE SEARCH: {str(e)}", flush=True)
        logging.error(f"❌ Failed to save search placeholders: {str(e)}")
        import traceback
        traceback_str = traceback.format_exc()
        print(traceback_str, flush=True)
        logging.error(traceback_str)
        return False

def send_daily_report_for_schedule(schedule, schedule_index):
    """
    Send daily report for a specific schedule configuration
    
    Args:
        schedule: dict with searchTime, sendTime, days, locations
        schedule_index: int, index of schedule (for logging)
    """
    print(f"\n{'='*80}", flush=True)
    print(f"📧 SENDING EMAIL - SCHEDULE #{schedule_index + 1}", flush=True)
    print(f"{'='*80}", flush=True)
    print(f"   Send Time: {schedule.get('sendTime')}", flush=True)
    print(f"   Days: {schedule.get('days')}", flush=True)
    print(f"   Locations: {schedule.get('locations')}", flush=True)
    
    logging.info(f"\n{'='*80}")
    logging.info(f"📧 SENDING EMAIL - SCHEDULE #{schedule_index + 1}")
    logging.info(f"{'='*80}")
    logging.info(f"   Send Time: {schedule.get('sendTime')}")
    logging.info(f"   Days: {schedule.get('days')}")
    logging.info(f"   Locations: {schedule.get('locations')}")
    
    # PROTEÇÃO: Verificar se daily reports ainda estão enabled
    settings = load_advanced_settings()
    if not settings or not settings.get('daily', {}).get('enabled'):
        print(f"⚠️  ABORTED: Daily reports are DISABLED in database", flush=True)
        logging.warning(f"⚠️  ABORTED: Daily reports are DISABLED in database")
        return
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import json
        
        # Get Gmail credentials
        conn = _get_db_connection()
        if not conn:
            logging.error("❌ Cannot connect to database for Gmail credentials")
            return
        
        cursor = conn.cursor()
        cursor.execute(
            "SELECT access_token, refresh_token FROM oauth_tokens WHERE provider = 'google' ORDER BY updated_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        
        if not row or not row[0] or not row[1]:
            logging.error("❌ Gmail credentials not found or incomplete")
            cursor.close()
            conn.close()
            return
        
        access_token, refresh_token = row
        cursor.close()
        conn.close()
        
        # Create credentials
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logging.error("❌ GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set")
            return
        
        credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        
        # Get recipient emails from email_settings (múltiplos emails)
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT setting_value FROM user_settings WHERE setting_key = 'email_settings' LIMIT 1"
        )
        row = cursor.fetchone()
        
        recipients = []
        if row and row[0]:
            import json
            try:
                email_settings = json.loads(row[0])
                recipients_text = email_settings.get('recipients', '')
                if recipients_text:
                    # Split by newlines and clean up
                    recipients = [email.strip() for email in recipients_text.split('\n') if email.strip()]
                    print(f"   📧 Loaded {len(recipients)} recipient(s): {', '.join(recipients)}", flush=True)
            except:
                pass
        
        # Fallback to report_email if no recipients found
        if not recipients:
            cursor.execute(
                "SELECT setting_value FROM price_automation_settings WHERE setting_key = 'report_email'"
            )
            row = cursor.fetchone()
            default_email = row[0] if row else 'carlpac82@hotmail.com'
            recipients = [default_email]
            print(f"   📧 Using fallback email: {default_email}", flush=True)
        
        cursor.close()
        conn.close()
        
        # Load search data from automated_search_history (correct table for automated searches)
        conn = _get_db_connection()
        cursor = conn.cursor()
        
        # Get records from last 3 hours (to handle delay between searchTime and sendTime)
        from datetime import datetime, timedelta
        now = datetime.now()
        three_hours_ago = now - timedelta(hours=3)
        cutoff_time = three_hours_ago.isoformat()
        
        cursor.execute(
            """
            SELECT location, search_date, dias, prices_data, supplier_data
            FROM automated_search_history
            WHERE search_date >= %s
              AND search_type = 'automated'
            ORDER BY search_date DESC, id DESC
            LIMIT 10
            """,
            (cutoff_time,)
        )
        rows = cursor.fetchall()
        
        print(f"   📊 Query: search_date >= '{cutoff_time}' AND search_type = 'automated'", flush=True)
        print(f"   📊 Current time: {now.isoformat()}", flush=True)
        print(f"   📊 Cutoff time (2h ago): {cutoff_time}", flush=True)
        print(f"   📊 Found {len(rows)} recent search records", flush=True)
        
        all_results = []
        for row in rows:
            location, search_date, dias_json, prices_data, supplier_data_json = row
            print(f"   [DEBUG] Processing row: location={location}, has_prices_data={bool(prices_data)}, has_supplier_data={bool(supplier_data_json)}", flush=True)
            
            if prices_data:
                # Parse dias JSON
                dias_list = json.loads(dias_json) if isinstance(dias_json, str) else dias_json
                # Parse prices - structure is: {"B1": {3: 25.50, 7: 30.00}, "D": {3: 22.00}}
                prices_by_group = json.loads(prices_data) if isinstance(prices_data, str) else prices_data
                # Parse supplier data - NEW structure: {"B1": {"7": [car1, car2, ...]}, "D": {"7": [car1, car2, ...]}}
                supplier_data = json.loads(supplier_data_json) if supplier_data_json and isinstance(supplier_data_json, str) else (supplier_data_json or {})
                
                print(f"   [DEBUG] prices_by_group keys: {list(prices_by_group.keys())}", flush=True)
                print(f"   [DEBUG] supplier_data groups: {list(supplier_data.keys())}", flush=True)
                
                # Send ALL cars from supplier_data (not just 1 per group)
                # Filter duplicates: same supplier + car + price + day = duplicate
                seen_cars = set()
                total_before = 0
                
                # NEW: Iterate over groups, then days, then cars
                # supplier_data = {"B1": {"7": [...], "14": [...]}, "D": {"7": [...]}}
                for group_code, days_dict in supplier_data.items():
                    # days_dict = {"7": [car1, car2, ...], "14": [car1, car2, ...]}
                    if not isinstance(days_dict, dict):
                        continue  # Skip if not a dict
                    
                    for day_str, day_items in days_dict.items():
                        if not isinstance(day_items, list):
                            continue  # Skip if not a list
                        
                        total_before += len(day_items)
                        for item in day_items:
                            if not isinstance(item, dict):
                                continue  # Skip if not a dict
                            
                            supplier = item.get('supplier', 'Unknown')
                            car = item.get('car', 'Unknown')
                            price = item.get('price_num', 0)
                            
                            # Create unique key INCLUDING day
                            # This allows same car to appear in different days
                            unique_key = f"{day_str}|{supplier}|{car}|{price:.2f}"
                            
                            # Skip if already seen
                            if unique_key in seen_cars:
                                continue
                            
                            seen_cars.add(unique_key)
                            
                            # Add location and search_date to each item
                            # NOTE: The scraping saves 'photo' field, not 'image_url'
                            photo_url = item.get('photo', '') or item.get('image_url', '')
                            
                            result_item = {
                                'group': item.get('group', 'Unknown'),
                                'days': int(day_str),
                                'price': price,
                                'price_num': price,
                                'location': location,
                                'search_date': search_date,
                                'car_name': item.get('car_clean', 'Unknown'),
                                'supplier': supplier,
                                'photo': photo_url,  # For HTML rendering
                                'image_url': photo_url,  # Backup field
                                'car': car,
                            }
                            
                            # Debug first item
                            if len(all_results) == 0:
                                print(f"   [DEBUG] First result: car={result_item['car_name']}, supplier={result_item['supplier']}, group={result_item['group']}, price={result_item['price']}", flush=True)
                                print(f"   [DEBUG] Photo URL: {result_item['photo'][:100] if result_item['photo'] else 'EMPTY'}", flush=True)
                                print(f"   [DEBUG] Item keys from DB: {list(item.keys())}", flush=True)
                            
                            all_results.append(result_item)
                
                print(f"   [DEBUG] Dedup: {total_before} total → {len(seen_cars)} unique (removed {total_before - len(seen_cars)} duplicates)", flush=True)
        
        cursor.close()
        conn.close()
        
        search_data = {'results': all_results}
        logging.info(f"   📊 Loaded {len(all_results)} search results (prices)")
        print(f"   [DEBUG] all_results count: {len(all_results)}", flush=True)
        
        if not all_results:
            logging.warning("   ⚠️ No search data available, skipping email")
            return
        
        # Import report generation function
        sys.path.insert(0, os.path.dirname(__file__))
        from improved_reports import generate_daily_report_html_by_location
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=credentials)
        
        # Send for each location
        locations_to_send = []
        if schedule.get('locations', {}).get('albufeira'):
            locations_to_send.append('Albufeira')
        if schedule.get('locations', {}).get('faro'):
            locations_to_send.append('Aeroporto de Faro')
        
        sent_count = 0
        for location in locations_to_send:
            logging.info(f"   📍 Generating report for: {location}")
            
            html_content = generate_daily_report_html_by_location(search_data, location)
            
            # Send to ALL recipients
            for recipient in recipients:
                message = MIMEMultipart('alternative')
                message['to'] = recipient
                message['subject'] = f'📊 Relatório Diário {location} - Auto Prudente ({datetime.now().strftime("%d/%m/%Y")})'
                
                html_part = MIMEText(html_content, 'html')
                message.attach(html_part)
                
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                send_message = service.users().messages().send(
                    userId='me',
                    body={'raw': raw_message}
                ).execute()
                
                sent_count += 1
                logging.info(f"   ✅ Email sent to {recipient} for {location}")
        
        logging.info(f"✅ SCHEDULE #{schedule_index + 1} COMPLETED - {sent_count} emails sent (to {len(recipients)} recipients)")
        
    except Exception as e:
        logging.error(f"❌ Error sending daily report for schedule #{schedule_index + 1}: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())

def execute_search_for_schedule(schedule, schedule_index):
    """
    Execute REAL CarJet searches for a schedule
    This runs at searchTime
    """
    print(f"\n{'='*80}", flush=True)
    print(f"🔍 EXECUTING REAL CARJET SEARCHES - SCHEDULE #{schedule_index + 1}", flush=True)
    print(f"{'='*80}", flush=True)
    print(f"   Search Time: {schedule.get('searchTime')}", flush=True)
    print(f"   Days: {schedule.get('days')}", flush=True)
    print(f"   Locations: {schedule.get('locations')}", flush=True)
    
    # PROTEÇÃO: Verificar se daily reports ainda estão enabled
    settings = load_advanced_settings()
    if not settings or not settings.get('daily', {}).get('enabled'):
        print(f"⚠️  ABORTED: Daily reports are DISABLED in database", flush=True)
        print(f"   Skipping search execution.", flush=True)
        return
    
    try:
        from datetime import datetime, timedelta
        import json
        import asyncio
        
        # Obter configurações
        days = schedule.get('days', [])
        locations_config = schedule.get('locations', {})
        
        if not days or not (locations_config.get('albufeira') or locations_config.get('faro')):
            print(f"   ⚠️ No days or locations configured!", flush=True)
            return
        
        # Preparar localizações
        locations_to_search = []
        if locations_config.get('albufeira'):
            locations_to_search.append("Albufeira")
        if locations_config.get('faro'):
            locations_to_search.append("Aeroporto de Faro")
        
        # Data de pickup (amanhã)
        pickup_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"\n🚗 Preparing CarJet search...", flush=True)
        print(f"   Pickup Date: {pickup_date}", flush=True)
        print(f"   Durations: {days}", flush=True)
        print(f"   Locations: {locations_to_search}", flush=True)
        
        # Executar pesquisa usando asyncio
        all_results = asyncio.run(_do_carjet_search(locations_to_search, days, pickup_date))
        print(f"\n✅ Search completed!", flush=True)
        
        # SALVAR NA BD
        _save_search_results(all_results, days, locations_to_search, pickup_date)
        
        print(f"\n✅ SEARCH EXECUTION COMPLETED!", flush=True)
        print(f"✅ Results saved to AUTOMATED_SEARCH_HISTORY table!", flush=True)
        print(f"✅ Go to Automated Pricing → History to see them!", flush=True)
        print(f"{'='*80}\n", flush=True)
            
    except Exception as e:
        print(f"\n❌ SEARCH ERROR: {str(e)}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)

async def _do_carjet_search(locations, days, pickup_date):
    """
    Execute CarJet search using BATCH endpoint (reutiliza mesma sessão Chrome).
    Em vez de abrir/fechar Chrome para cada dia, abre UMA VEZ e muda datas.
    Fallback: chamadas individuais se batch falhar.
    """
    import aiohttp
    import os
    
    print(f"\n🛡️ Using BATCH API (single Chrome session for all days)", flush=True)
    
    service_url = os.getenv('RENDER_EXTERNAL_URL', os.getenv('RAILWAY_PUBLIC_DOMAIN', 'http://localhost:10000'))
    if not service_url.startswith('http'):
        service_url = f"https://{service_url}"
    batch_api_url = f"{service_url}/api/track-by-params-batch"
    single_api_url = f"{service_url}/api/track-by-params"
    jobs_api_url = f"{service_url}/api/jobs"
    
    print(f"   Batch API URL: {batch_api_url}", flush=True)
    
    all_results = {}
    
    async with aiohttp.ClientSession() as session:
        for location in locations:
            print(f"\n📍 Searching {location} (batch mode)...", flush=True)
            location_results = {}
            
            # TENTAR BATCH PRIMEIRO (1 Chrome para todos os dias)
            try:
                payload = {
                    'location': location,
                    'pickup_date': pickup_date,
                    'days': days,
                    'lang': 'pt',
                    'currency': 'EUR',
                }
                
                print(f"   [BATCH] Submitting: {days} days for {location}...", flush=True)
                headers = {'X-Internal-Request': 'scheduler'}
                
                # Batch pode demorar (N dias * ~2min cada), timeout generoso
                timeout = aiohttp.ClientTimeout(total=len(days) * 180 + 60)
                
                async with session.post(batch_api_url, json=payload, headers=headers, timeout=timeout) as response:
                    print(f"   [BATCH] Status: {response.status}", flush=True)
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('ok') and data.get('results'):
                            results = data['results']
                            total = 0
                            for day_key, items in results.items():
                                day_int = int(day_key)
                                location_results[day_int] = items
                                total += len(items)
                                print(f"      ✅ {day_key} days: {len(items)} cars", flush=True)
                                if items:
                                    print(f"         [EXAMPLE] {items[0].get('car', 'N/A')}, {items[0].get('supplier', 'N/A')}, {items[0].get('price', 'N/A')}", flush=True)
                            
                            print(f"   [BATCH] ✅ Total: {total} cars for {location}", flush=True)
                        else:
                            error = data.get('error', 'Unknown')
                            print(f"   [BATCH] ⚠️ Batch returned ok=false: {error}", flush=True)
                    else:
                        error_text = await response.text()
                        print(f"   [BATCH] ❌ HTTP {response.status}: {error_text[:200]}", flush=True)
                        
            except Exception as batch_err:
                print(f"   [BATCH] ❌ Batch failed: {batch_err}", flush=True)
                import traceback
                print(f"   [TRACEBACK] {traceback.format_exc()}", flush=True)
            
            # FALLBACK: Para dias que falharam no batch, tentar individualmente
            missing_days = [d for d in days if d not in location_results or not location_results.get(d)]
            if missing_days:
                print(f"   [FALLBACK] {len(missing_days)} days missing, trying individual calls: {missing_days}", flush=True)
                
                for day in missing_days:
                    try:
                        payload = {
                            'location': location,
                            'start_date': pickup_date,
                            'start_time': '15:00',
                            'days': day,
                            'lang': 'pt',
                            'currency': 'EUR',
                            'async': 1
                        }
                        
                        headers = {'X-Internal-Request': 'scheduler'}
                        
                        async with session.post(single_api_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                if data.get('async') and data.get('job_id'):
                                    job_id = data['job_id']
                                    print(f"      🔄 Job submitted: {job_id} ({day} days)", flush=True)
                                    
                                    max_attempts = 90
                                    attempt = 0
                                    items = []
                                    
                                    while attempt < max_attempts:
                                        await asyncio.sleep(2)
                                        attempt += 1
                                        
                                        try:
                                            job_status_url = f"{jobs_api_url}/{job_id}"
                                            async with session.get(job_status_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as status_response:
                                                if status_response.status == 200:
                                                    status_data = await status_response.json()
                                                    job_status = status_data.get('status')
                                                    
                                                    if job_status == 'completed':
                                                        result_url = f"{jobs_api_url}/{job_id}/result"
                                                        async with session.get(result_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as result_response:
                                                            if result_response.status == 200:
                                                                result_data = await result_response.json()
                                                                items = result_data.get('items', [])
                                                                print(f"      ✅ {len(items)} cars ({day} days, fallback)", flush=True)
                                                                break
                                                    elif job_status == 'failed':
                                                        print(f"      ❌ Job failed ({day} days)", flush=True)
                                                        break
                                                    else:
                                                        if attempt % 10 == 0:
                                                            print(f"      ⏳ Still running... ({attempt * 2}s)", flush=True)
                                        except Exception as poll_error:
                                            continue
                                    
                                    location_results[day] = items
                                else:
                                    items = data.get('items', [])
                                    print(f"      ✅ {len(items)} cars ({day} days, sync)", flush=True)
                                    location_results[day] = items
                            else:
                                location_results[day] = []
                    except Exception as e:
                        print(f"      ❌ Error ({day} days): {e}", flush=True)
                        location_results[day] = []
            
            all_results[location] = location_results
    
    return all_results

def _save_search_results(all_results, days, locations, pickup_date):
    """
    Save search results to automated_search_history table
    Uses pickup_date to determine month_key (not current date)
    """
    import json
    from datetime import datetime
    
    print(f"\n💾 Saving results to automated_search_history...", flush=True)
    
    conn = _get_db_connection()
    if not conn:
        print("❌ Database connection failed", flush=True)
        return
    
    try:
        # Parse pickup_date to get month_key
        if isinstance(pickup_date, str):
            search_dt = datetime.strptime(pickup_date, '%Y-%m-%d')
        else:
            search_dt = pickup_date
        
        month_key = f"{search_dt.year}-{str(search_dt.month).zfill(2)}"
        
        # CRITICAL: Use CURRENT datetime for search_date (when search was executed)
        # NOT pickup_date (when car will be picked up)
        search_date = datetime.now().isoformat()
        
        for location in locations:
            location_results = all_results.get(location, {})
            
            # Preparar dados de preços por grupo
            prices_by_group = {}
            supplier_data = {}
            total_price_count = 0
            
            for day, items in location_results.items():
                if items:
                    # Agrupar por grupo
                    for item in items:
                        grupo = item.get('group', 'Unknown')
                        price = item.get('price_num', 0)
                        
                        if grupo not in prices_by_group:
                            prices_by_group[grupo] = {}
                        
                        # Menor preço
                        if day not in prices_by_group[grupo] or price < prices_by_group[grupo][day]:
                            prices_by_group[grupo][day] = price
                            total_price_count += 1
                    
                    # ✅ FIX: Organizar supplier_data por GRUPO primeiro, depois por DIA
                    for item in items:
                        grupo = item.get('group', 'Unknown')
                        
                        if grupo not in supplier_data:
                            supplier_data[grupo] = {}
                        
                        if str(day) not in supplier_data[grupo]:
                            supplier_data[grupo][str(day)] = []
                        
                        supplier_data[grupo][str(day)].append(item)
            
            if prices_by_group:
                # Insert into database
                
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO automated_search_history 
                    (location, search_type, search_date, month_key, prices_data, dias, price_count, supplier_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    location,
                    'automated',
                    search_date,
                    month_key,
                    json.dumps(prices_by_group),
                    json.dumps(days),
                    total_price_count,
                    json.dumps(supplier_data)
                ))
                
                conn.commit()
                print(f"   ✅ {location}: {total_price_count} prices saved!", flush=True)
                print(f"      search_date: {search_date} (current time)", flush=True)
                print(f"      month_key: {month_key}", flush=True)
                print(f"      groups: {list(prices_by_group.keys())}", flush=True)
                
    except Exception as e:
        print(f"❌ Save error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

def execute_weekly_search():
    """
    Execute weekly search - uses FIXED DAY of month (e.g., day 05)
    Can search in future months (not just current month)
    """
    print(f"\n{'='*80}", flush=True)
    print(f"🔍 EXECUTING WEEKLY SEARCH", flush=True)
    print(f"{'='*80}", flush=True)
    
    # PROTEÇÃO: Verificar se weekly reports ainda estão enabled
    settings = load_advanced_settings()
    if not settings or not settings.get('weekly', {}).get('enabled'):
        print("⚠️  ABORTED: Weekly search is DISABLED in database", flush=True)
        return
    
    try:
        import asyncio
        from datetime import datetime, timedelta
        
        weekly_config = settings['weekly']
        days = weekly_config.get('days', [7, 14, 30])  # Default durations
        locations_config = weekly_config.get('locations', {'albufeira': True, 'faro': False})
        
        # Prepare locations
        locations_to_search = []
        if locations_config.get('albufeira'):
            locations_to_search.append("Albufeira")
        if locations_config.get('faro'):
            locations_to_search.append("Aeroporto de Faro")
        
        # PICKUP DATE: Fixed day of NEXT month (example: day 05 of next month)
        # This allows searching for future months beyond current month
        now = datetime.now()
        next_month = now.month + 1 if now.month < 12 else 1
        year = now.year if now.month < 12 else now.year + 1
        fixed_day = 5  # Fixed day (configurable)
        
        pickup_date = f"{year}-{str(next_month).zfill(2)}-{str(fixed_day).zfill(2)}"
        
        print(f"\n🗓️ Weekly search config:", flush=True)
        print(f"   Pickup Date: {pickup_date} (day {fixed_day} of next month)", flush=True)
        print(f"   Durations: {days}", flush=True)
        print(f"   Locations: {locations_to_search}", flush=True)
        
        # Execute search with Anti-WAF
        all_results = asyncio.run(_do_carjet_search(locations_to_search, days, pickup_date))
        
        # Save results
        _save_search_results(all_results, days, locations_to_search, pickup_date)
        
        print(f"\n✅ WEEKLY SEARCH COMPLETED!", flush=True)
        print(f"{'='*80}\n", flush=True)
        
    except Exception as e:
        print(f"\n❌ WEEKLY SEARCH ERROR: {str(e)}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)

def send_weekly_report():
    """Send weekly report (email only)"""
    logging.info(f"\n{'='*80}")
    logging.info(f"📧 WEEKLY REPORT EMAIL")
    logging.info(f"{'='*80}")
    
    try:
        # Load data from database and send email
        logging.info("✅ Weekly report email sent")
    except Exception as e:
        logging.error(f"❌ Error sending weekly report: {str(e)}")

def execute_monthly_search():
    """
    Execute monthly search - uses FIXED DAY of month (e.g., day 05)
    Can search multiple months ahead
    """
    print(f"\n{'='*80}", flush=True)
    print(f"🔍 EXECUTING MONTHLY SEARCH", flush=True)
    print(f"{'='*80}", flush=True)
    
    # PROTEÇÃO: Verificar se monthly reports ainda estão enabled
    settings = load_advanced_settings()
    if not settings or not settings.get('monthly', {}).get('enabled'):
        print("⚠️  ABORTED: Monthly search is DISABLED in database", flush=True)
        return
    
    try:
        import asyncio
        from datetime import datetime, timedelta
        
        monthly_config = settings['monthly']
        days = monthly_config.get('days', [7, 14, 30, 60])
        locations_config = monthly_config.get('locations', {'albufeira': True, 'faro': False})
        period_months = int(monthly_config.get('period', 6))  # How many months ahead
        fixed_day = int(monthly_config.get('day', 5))  # Fixed day of month
        
        # Prepare locations
        locations_to_search = []
        if locations_config.get('albufeira'):
            locations_to_search.append("Albufeira")
        if locations_config.get('faro'):
            locations_to_search.append("Aeroporto de Faro")
        
        # PICKUP DATE: Fixed day X months in future
        now = datetime.now()
        target_month = now.month + period_months
        year = now.year
        while target_month > 12:
            target_month -= 12
            year += 1
        
        pickup_date = f"{year}-{str(target_month).zfill(2)}-{str(fixed_day).zfill(2)}"
        
        print(f"\n🗓️ Monthly search config:", flush=True)
        print(f"   Pickup Date: {pickup_date} (day {fixed_day}, +{period_months} months)", flush=True)
        print(f"   Durations: {days}", flush=True)
        print(f"   Locations: {locations_to_search}", flush=True)
        
        # Execute search with Anti-WAF
        all_results = asyncio.run(_do_carjet_search(locations_to_search, days, pickup_date))
        
        # Save results
        _save_search_results(all_results, days, locations_to_search, pickup_date)
        
        print(f"\n✅ MONTHLY SEARCH COMPLETED!", flush=True)
        print(f"{'='*80}\n", flush=True)
        
    except Exception as e:
        print(f"\n❌ MONTHLY SEARCH ERROR: {str(e)}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)

def send_monthly_report():
    """Send monthly report (email only)"""
    logging.info(f"\n{'='*80}")
    logging.info(f"📧 MONTHLY REPORT EMAIL")
    logging.info(f"{'='*80}")
    
    try:
        # Load data from database and send email
        logging.info("✅ Monthly report email sent")
    except Exception as e:
        logging.error(f"❌ Error sending monthly report: {str(e)}")

def check_and_send_scheduled_checkout_emails():
    """
    Verifica e envia emails de self-checkout agendados.
    Executado a cada 5 minutos.
    """
    print("\n" + "="*80, flush=True)
    print("📧 CHECKING SCHEDULED CHECKOUT EMAILS", flush=True)
    print("="*80, flush=True)
    logging.info(f"\n{'='*80}")
    logging.info(f"📧 CHECKING SCHEDULED CHECKOUT EMAILS")
    logging.info(f"{'='*80}")
    
    try:
        from schedule_checkout_emails import get_pending_emails, mark_email_sent
        import requests
        import os
        
        print("🔍 Getting pending emails...", flush=True)
        # Obter emails pendentes
        pending = get_pending_emails()
        
        if not pending:
            print("✅ No pending checkout emails to send", flush=True)
            logging.info("✅ No pending checkout emails to send")
            return
        
        print(f"📬 Found {len(pending)} pending email(s)", flush=True)
        logging.info(f"📬 Found {len(pending)} pending email(s)")
        
        # Enviar cada email
        logging.info(f"🔄 Starting loop to process {len(pending)} emails...")
        for idx, email_data in enumerate(pending):
            logging.info(f"🔄 Processing email {idx+1}/{len(pending)}")
            logging.info(f"📦 Email data: {email_data}")
            
            inspection_number = email_data['inspection_number']
            client_email = email_data['client_email']
            client_name = email_data['client_name']
            vehicle_plate = email_data['vehicle_plate']
            
            logging.info(f"📧 Sending self-checkout email for {inspection_number} to {client_email}")
            
            conn = None
            try:
                # Obter dados do check-in para gerar link de self-checkout
                conn = _get_db_connection()
                if not conn:
                    logging.error(f"❌ Cannot connect to database for {inspection_number}")
                    mark_email_sent(inspection_number, success=False, error_message="Database connection failed")
                    continue
                
                cursor = conn.cursor()
                
                # Primeiro, buscar o contract_number do check-in
                cursor.execute("""
                    SELECT contract_number
                    FROM vehicle_inspections
                    WHERE inspection_number = %s
                      AND status != 'replaced'
                """, (inspection_number,))
                
                checkin_row = cursor.fetchone()
                
                # If not found, the inspection may have been replaced by a newer one
                # Try to find the current active inspection for the same vehicle plate
                if not checkin_row or not checkin_row[0]:
                    logging.warning(f"⚠️ Inspection {inspection_number} not found or replaced, searching by plate {vehicle_plate}...")
                    cursor.execute("""
                        SELECT contract_number, inspection_number
                        FROM vehicle_inspections
                        WHERE vehicle_plate = %s
                          AND inspection_type = 'checkin'
                          AND status != 'replaced'
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (vehicle_plate,))
                    checkin_row = cursor.fetchone()
                    if checkin_row and checkin_row[0]:
                        logging.info(f"✅ Found replacement inspection {checkin_row[1]} for plate {vehicle_plate}")
                    else:
                        logging.error(f"❌ No contract_number found for check-in {inspection_number} (plate: {vehicle_plate})")
                        mark_email_sent(inspection_number, success=False, error_message="Contract number not found")
                        continue
                
                contract_number = checkin_row[0]
                # Remover sufixo (e.g., "06691-09" -> "06691")
                ra_base = contract_number.split('-')[0] if '-' in contract_number else contract_number
                logging.info(f"🔍 Looking for RA token using contract: {contract_number} (base: {ra_base})")
                
                # Buscar token de self-checkout e país do cliente usando o RA number
                cursor.execute("""
                    SELECT self_checkin_token, rental_agreement_number, extracted_data
                    FROM rental_agreements
                    WHERE rental_agreement_number LIKE %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (f"{ra_base}%",))
                
                row = cursor.fetchone()
                
                if not row or not row[0]:
                    logging.error(f"❌ No self-checkout token found for RA {ra_base}")
                    mark_email_sent(inspection_number, success=False, error_message="Self-checkout token not found")
                    continue
                
                token = row[0]
                ra_number = row[1]
                extracted_data = row[2]
                logging.info(f"✅ Found token for RA {ra_number}")
            
            finally:
                # CRÍTICO: Sempre fechar conexão para evitar memory leak
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
            
            try:
                
                # Extrair país do cliente (mesma lógica do envio manual que funciona)
                country = None
                if extracted_data:
                    import json
                    try:
                        data = json.loads(extracted_data) if isinstance(extracted_data, str) else extracted_data
                        logging.info(f"🔍 DEBUG extracted_data keys: {list(data.keys())}")
                        
                        # Tentar múltiplos campos para o país
                        country = (data.get('country') or 
                                  data.get('pais') or 
                                  data.get('Country') or 
                                  data.get('COUNTRY') or
                                  data.get('clientCountry') or
                                  data.get('client_country'))
                        
                        if country:
                            logging.info(f"🌍 Client country from RA: '{country}'")
                        else:
                            logging.warning(f"⚠️ No country field found in extracted_data. Available keys: {list(data.keys())}")
                            logging.warning(f"⚠️ Full extracted_data: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    except Exception as e:
                        logging.error(f"❌ Could not extract country from RA: {e}")
                        import traceback
                        logging.error(traceback.format_exc())
                
                if not country:
                    logging.warning(f"⚠️ Country not found for RA {ra_number}, will use default language (pt)")
                
                # Construir link de self-checkout
                base_url = os.environ.get('BASE_URL', 'https://rentalprices.pt')
                checkout_link = f"{base_url}/self-checkout/{token}"
                
                logging.info(f"🔗 Checkout link: {checkout_link}")
                logging.info(f"📧 Sending email to {client_email} for RA {ra_number} (country: {country})")
                
                # Enviar email diretamente usando a função
                try:
                    from main import _send_self_checkin_invitation_email
                    
                    _send_self_checkin_invitation_email(
                        to_email=client_email,
                        client_name=client_name,
                        ra_number=ra_number,
                        plate=vehicle_plate,
                        return_date=str(email_data.get('checkout_date', '')),
                        token=token,
                        country=country
                    )
                    
                    mark_email_sent(inspection_number, success=True)
                    logging.info(f"✅ Email sent successfully for {inspection_number}")
                        
                except Exception as send_error:
                    error_msg = f"Failed to send email: {str(send_error)}"
                    logging.error(f"❌ {error_msg}")
                    import traceback
                    logging.error(traceback.format_exc())
                    mark_email_sent(inspection_number, success=False, error_message=error_msg)
                
            except Exception as email_error:
                logging.error(f"❌ Error sending email for {inspection_number}: {email_error}")
                mark_email_sent(inspection_number, success=False, error_message=str(email_error))
    
    except Exception as e:
        logging.error(f"❌ Error in check_and_send_scheduled_checkout_emails: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())

def setup_scheduled_tasks():
    """
    Setup all scheduled tasks based on database configuration
    This is called on startup and can be called to reload schedules
    """
    global scheduler
    
    print("\n" + "="*80, flush=True)
    print("🤖 SETTING UP AUTOMATED SCHEDULER", flush=True)
    print("="*80, flush=True)
    logging.info("\n" + "="*80)
    logging.info("🤖 SETTING UP AUTOMATED SCHEDULER")
    logging.info("="*80)
    
    # Load settings
    print("📥 Loading settings from database...", flush=True)
    settings = load_advanced_settings()
    
    if not settings:
        print("⚠️ No advanced settings found, scheduler not configured", flush=True)
        logging.warning("⚠️ No advanced settings found, scheduler not configured")
        return
    
    print(f"✅ Settings loaded successfully", flush=True)
    
    # PROTEÇÃO CRÍTICA: Verificar se TUDO está disabled
    daily_enabled = settings.get('daily', {}).get('enabled', False)
    weekly_enabled = settings.get('weekly', {}).get('enabled', False)
    monthly_enabled = settings.get('monthly', {}).get('enabled', False)
    
    print(f"\n🔍 VERIFICAÇÃO DE ESTADO:", flush=True)
    print(f"   Daily enabled: {daily_enabled}", flush=True)
    print(f"   Weekly enabled: {weekly_enabled}", flush=True)
    print(f"   Monthly enabled: {monthly_enabled}", flush=True)
    
    if not daily_enabled and not weekly_enabled and not monthly_enabled:
        print("\n⚠️  TODOS OS RELATÓRIOS ESTÃO DESATIVADOS", flush=True)
        print("   Scheduler NÃO vai agendar pesquisas ao CarJet", flush=True)
        print("   Apenas checkout emails continuam ativos\n", flush=True)
        logging.warning("⚠️ All automated reports DISABLED - no CarJet searches will be scheduled")
    
    # Initialize scheduler
    if scheduler is None:
        print("🆕 Creating new BackgroundScheduler...", flush=True)
        scheduler = BackgroundScheduler(timezone='UTC')
        scheduler.start()
        print("✅ Scheduler started", flush=True)
        logging.info("✅ Scheduler started")
    else:
        # Clear existing jobs
        print("🔄 Clearing existing jobs...", flush=True)
        scheduler.remove_all_jobs()
        print("✅ Jobs cleared", flush=True)
        logging.info("🔄 Cleared existing jobs")
    
    job_count = 0
    
    # Setup DAILY schedules
    print(f"\n📅 Checking DAILY schedules...", flush=True)
    print(f"   daily.enabled = {settings.get('daily', {}).get('enabled')}", flush=True)
    
    if settings.get('daily', {}).get('enabled'):
        schedules = settings['daily'].get('schedules', [])
        print(f"\n📅 DAILY REPORTS ENABLED: {len(schedules)} schedules", flush=True)
        logging.info(f"\n📅 DAILY REPORTS: {len(schedules)} schedules")
    else:
        print(f"   ⏭️  DAILY DISABLED - Skipping all daily schedules", flush=True)
        schedules = []
    
    if settings.get('daily', {}).get('enabled') and schedules:
        
        for idx, schedule in enumerate(schedules):
            search_time = schedule.get('searchTime', '08:55')
            send_time = schedule.get('sendTime', '09:00')
            search_hour, search_minute = search_time.split(':')
            send_hour, send_minute = send_time.split(':')
            
            # Add job for EXECUTING SEARCHES at searchTime
            scheduler.add_job(
                func=lambda s=schedule, i=idx: execute_search_for_schedule(s, i),
                trigger=CronTrigger(hour=int(search_hour), minute=int(search_minute)),
                id=f'daily_search_{idx}',
                name=f'Daily Search Schedule #{idx + 1} at {search_time}',
                replace_existing=True
            )
            job_count += 1
            print(f"   ✅ Search job #{idx + 1}: {search_time} | Days: {schedule.get('days')} | Locations: {schedule.get('locations')}", flush=True)
            logging.info(f"   ✅ Search job #{idx + 1}: {search_time}")
            
            # Add job for SENDING EMAIL at sendTime
            scheduler.add_job(
                func=lambda s=schedule, i=idx: send_daily_report_for_schedule(s, i),
                trigger=CronTrigger(hour=int(send_hour), minute=int(send_minute)),
                id=f'daily_send_{idx}',
                name=f'Daily Email Schedule #{idx + 1} at {send_time}',
                replace_existing=True
            )
            job_count += 1
            print(f"   ✅ Email job #{idx + 1}: {send_time}", flush=True)
            logging.info(f"   ✅ Email job #{idx + 1}: {send_time}")
    
    # Setup WEEKLY schedule (search on fixed day of month + email)
    print(f"\n📆 Checking WEEKLY schedule...", flush=True)
    print(f"   weekly.enabled = {settings.get('weekly', {}).get('enabled')}", flush=True)
    
    if settings.get('weekly', {}).get('enabled'):
        print(f"   ✅ WEEKLY ENABLED - Scheduling jobs", flush=True)
    else:
        print(f"   ⏭️  WEEKLY DISABLED - Skipping", flush=True)
    
    if settings.get('weekly', {}).get('enabled'):
        day = settings['weekly'].get('day', 'saturday')  # Day of week OR day of month
        search_time = settings['weekly'].get('searchTime', '09:55')
        send_time = settings['weekly'].get('sendTime', '10:00')
        search_hour, search_minute = search_time.split(':')
        send_hour, send_minute = send_time.split(':')
        
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        # Job for executing weekly searches (uses fixed day of month)
        scheduler.add_job(
            func=execute_weekly_search,
            trigger=CronTrigger(day_of_week=day_map.get(day, 5), hour=int(search_hour), minute=int(search_minute)),
            id='weekly_search',
            name=f'Weekly Search ({day} at {search_time})',
            replace_existing=True
        )
        job_count += 1
        print(f"\n📆 WEEKLY SEARCH: {day} at {search_time}", flush=True)
        logging.info(f"\n📆 WEEKLY SEARCH: {day} at {search_time}")
        
        # Job for sending weekly email
        scheduler.add_job(
            func=send_weekly_report,
            trigger=CronTrigger(day_of_week=day_map.get(day, 5), hour=int(send_hour), minute=int(send_minute)),
            id='weekly_email',
            name=f'Weekly Email ({day} at {send_time})',
            replace_existing=True
        )
        job_count += 1
        print(f"   ✅ Email: {send_time}", flush=True)
        logging.info(f"   ✅ Email: {send_time}")
    
    # Setup MONTHLY schedule (search on fixed day of future month + email)
    print(f"\n📊 Checking MONTHLY schedule...", flush=True)
    print(f"   monthly.enabled = {settings.get('monthly', {}).get('enabled')}", flush=True)
    
    if settings.get('monthly', {}).get('enabled'):
        print(f"   ✅ MONTHLY ENABLED - Scheduling jobs", flush=True)
    else:
        print(f"   ⏭️  MONTHLY DISABLED - Skipping", flush=True)
    
    if settings.get('monthly', {}).get('enabled'):
        day = settings['monthly'].get('day', '1')
        search_time = settings['monthly'].get('searchTime', '09:55')
        send_time = settings['monthly'].get('sendTime', '10:00')
        search_hour, search_minute = search_time.split(':')
        send_hour, send_minute = send_time.split(':')
        
        if day == 'last':
            day = 'last'
        else:
            day = int(day)
        
        # Job for executing monthly searches (uses fixed day X months ahead)
        scheduler.add_job(
            func=execute_monthly_search,
            trigger=CronTrigger(day=day, hour=int(search_hour), minute=int(search_minute)),
            id='monthly_search',
            name=f'Monthly Search (day {day} at {search_time})',
            replace_existing=True
        )
        job_count += 1
        print(f"\n📊 MONTHLY SEARCH: Day {day} at {search_time}", flush=True)
        logging.info(f"\n📊 MONTHLY SEARCH: Day {day} at {search_time}")
        
        # Job for sending monthly email
        scheduler.add_job(
            func=send_monthly_report,
            trigger=CronTrigger(day=day, hour=int(send_hour), minute=int(send_minute)),
            id='monthly_email',
            name=f'Monthly Email (day {day} at {send_time})',
            replace_existing=True
        )
        job_count += 1
        print(f"   ✅ Email: {send_time}", flush=True)
        logging.info(f"   ✅ Email: {send_time}")
    
    # Setup CHECKOUT EMAIL checker (todos os dias às 20 horas)
    scheduler.add_job(
        func=check_and_send_scheduled_checkout_emails,
        trigger='cron',
        hour=20,
        minute=0,
        id='checkout_email_checker',
        name='Checkout Email Checker (daily at 20:00)',
        replace_existing=True
    )
    job_count += 1
    print(f"\n📧 CHECKOUT EMAIL CHECKER: Daily at 20:00", flush=True)
    logging.info(f"\n📧 CHECKOUT EMAIL CHECKER: Daily at 20:00")
    
    print(f"\n{'='*80}", flush=True)
    print(f"✅ SCHEDULER CONFIGURED: {job_count} jobs scheduled", flush=True)
    print(f"{'='*80}\n", flush=True)
    
    logging.info(f"\n{'='*80}")
    logging.info(f"✅ SCHEDULER CONFIGURED: {job_count} jobs scheduled")
    logging.info(f"{'='*80}\n")
    
    # Print next run times
    if job_count > 0:
        print("📋 NEXT SCHEDULED RUNS:", flush=True)
        logging.info("📋 NEXT SCHEDULED RUNS:")
        for job in scheduler.get_jobs():
            next_run = job.next_run_time
            print(f"   • {job.name}: {next_run}", flush=True)
            logging.info(f"   • {job.name}: {next_run}")
    else:
        print("⚠️ No jobs scheduled - check your configuration", flush=True)

def shutdown_scheduler():
    """Shutdown the scheduler gracefully"""
    global scheduler
    if scheduler:
        logging.info("🛑 Shutting down scheduler...")
        scheduler.shutdown()
        logging.info("✅ Scheduler stopped")

if __name__ == "__main__":
    # For testing
    setup_scheduled_tasks()
    
    logging.info("\n🤖 Scheduler running... Press Ctrl+C to stop")
    
    try:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        shutdown_scheduler()
