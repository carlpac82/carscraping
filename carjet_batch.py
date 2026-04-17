"""
CarJet Batch Scraping - Reutiliza mesma sessão Chrome para múltiplos dias.

Em vez de abrir/fechar Chrome para cada dia de pesquisa:
1. Abre Chrome UMA VEZ → Homepage → Pesquisa Dia 1
2. Navega categorias do Dia 1
3. Modifica datas para Dia 2 (clica "Alterar" + "Pesquisar")
4. Navega categorias do Dia 2
5. Repete para todos os dias
6. Fecha Chrome UMA VEZ no final

Benefícios:
- Menos suspeito (comportamento mais humano)
- Mais rápido (não carrega homepage para cada dia)
- Menos recursos (1 instância Chrome para todos os dias)
- Menos deteção WAF (war=28)
"""
import sys
import time
import random
import os
import platform
import signal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple


CATEGORIES = ['MINI', 'COMP', 'FAMI', 'ESTA', 'SUVS', 'VANS', 'LUXU', 'AUTO']

# Progresso global do batch (partilhado com endpoint de progresso)
# Estrutura: { batch_id: { 'total': N, 'completed': M, 'status': 'running'|'done', 'results': {days: items}, 'cancelled': bool } }
import threading
_batch_progress = {}
_batch_progress_lock = threading.Lock()

def get_batch_progress(batch_id: str) -> dict:
    """Obter progresso atual de um batch"""
    with _batch_progress_lock:
        return _batch_progress.get(batch_id, {}).copy()

def clear_batch_progress(batch_id: str):
    """Limpar progresso de um batch terminado"""
    with _batch_progress_lock:
        _batch_progress.pop(batch_id, None)

def cancel_batch(batch_id: str) -> bool:
    """Cancelar um batch em execução"""
    with _batch_progress_lock:
        prog = _batch_progress.get(batch_id)
        if prog and prog.get('status') == 'running':
            prog['cancelled'] = True
            prog['status'] = 'cancelled'
            return True
        return False

def is_batch_cancelled(batch_id: str) -> bool:
    """Verificar se batch foi cancelado (thread-safe)"""
    if not batch_id:
        return False
    with _batch_progress_lock:
        prog = _batch_progress.get(batch_id)
        return prog and prog.get('cancelled', False)


def _setup_chrome_driver():
    """Configurar e iniciar Chrome driver com anti-deteção (igual ao main.py)"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium_stealth import stealth

    iphone_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1"

    chrome_options = Options()
    system = platform.system()

    # Headless apenas em Linux (Railway/Docker)
    if system == 'Linux':
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        print(f"[BATCH] Modo headless (Linux)", file=sys.stderr, flush=True)
    else:
        print(f"[BATCH] Modo visual ({system})", file=sys.stderr, flush=True)

    # Flags essenciais
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument(f'user-agent={iphone_ua}')

    # Flags de estabilidade
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--disable-site-isolation-trials')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-hang-monitor')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-prompt-on-repost')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--safebrowsing-disable-auto-update')
    chrome_options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
    chrome_options.add_argument('--force-color-profile=srgb')
    # chrome_options.add_argument('--single-process')  # Removido: flag conhecida por denunciar headless
    chrome_options.add_argument('--disable-crash-reporter')
    chrome_options.add_argument('--disable-in-process-stack-traces')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-breakpad')
    chrome_options.add_argument('--disable-component-update')
    chrome_options.add_argument('--disable-domain-reliability')
    chrome_options.add_argument('--disable-client-side-phishing-detection')
    chrome_options.add_argument('--js-flags=--max-old-space-size=256')

    # Window size mobile
    chrome_options.add_argument('--window-size=390,844')

    # Emulação mobile
    mobile_emulation = {
        "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
        "userAgent": iphone_ua
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Anti-deteção
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Caminho do Chrome
    if system == 'Darwin':
        if os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
            chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif system == 'Linux':
        for path in ['/usr/bin/google-chrome-stable', '/usr/bin/google-chrome', '/usr/bin/chromium-browser', '/usr/bin/chromium']:
            if os.path.exists(path):
                chrome_options.binary_location = path
                break

    # Iniciar driver
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e1:
        print(f"[BATCH] Chrome tentativa 1 falhou: {e1}", file=sys.stderr, flush=True)
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
        except Exception as e2:
            print(f"[BATCH] Chrome tentativa 2 falhou: {e2}", file=sys.stderr, flush=True)
            raise

    # Aplicar stealth
    stealth(driver,
        languages=["pt-PT", "pt", "en"],
        vendor="Apple Computer, Inc.",
        platform="iPhone",
        webgl_vendor="Apple Inc.",
        renderer="Apple GPU",
        fix_hairline=True,
    )

    # Esconder webdriver properties via CDP
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['pt-PT', 'pt', 'en-US', 'en']});
                window.chrome = {runtime: {}};
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                );
            '''
        })
    except Exception:
        pass

    driver.set_page_load_timeout(30)
    print(f"[BATCH] ✅ Chrome iniciado com stealth + CDP", file=sys.stderr, flush=True)
    return driver


def _reject_cookies(driver):
    """Rejeitar cookies se aparecerem"""
    try:
        driver.execute_script("""
            const buttons = document.querySelectorAll('button, a, [role="button"]');
            for (let btn of buttons) {
                const text = btn.textContent.toLowerCase().trim();
                if (text.includes('rejeitar') || text.includes('reject') ||
                    text.includes('recusar') || text.includes('decline')) {
                    btn.click(); return true;
                }
            }
            return false;
        """)
    except:
        pass


def _click_search(driver):
    """Clicar no botão pesquisar"""
    driver.execute_script("""
        const btn = document.querySelector('#btnBuscar');
        if (btn) btn.click();
        else {
            const form = document.querySelector('#frm_search_cars') || document.querySelector('form');
            if (form) form.submit();
        }
    """)


def _wait_for_results(driver, max_wait=30, batch_id=None):
    """Aguardar até URL ter s= e b= (resultados prontos).
    Se war=28, clicar pesquisar outra vez (até 4 retries com pausa)."""
    max_war_retries = 4
    war_count = 0
    
    while war_count <= max_war_retries:
        waited = 0
        while waited < max_wait:
            # Verificar cancelamento
            if is_batch_cancelled(batch_id):
                print(f"[BATCH] 🛑 Cancelado durante wait_for_results", file=sys.stderr, flush=True)
                return False
            
            url = driver.current_url
            if 'war=' in url:
                war_count += 1
                if war_count > max_war_retries:
                    print(f"[BATCH] ❌ war= detectado {war_count}x - desistindo", file=sys.stderr, flush=True)
                    return False
                pause = random.uniform(4, 8)
                print(f"[BATCH] ⚠️ war= detectado ({war_count}/{max_war_retries}) → pausa {pause:.1f}s e retry...", file=sys.stderr, flush=True)
                time.sleep(pause)
                _click_search(driver)
                time.sleep(2)
                break  # Reiniciar o wait loop
            if '/do/list/' in url and 's=' in url and 'b=' in url:
                print(f"[BATCH] ✅ Resultados prontos após {waited}s (war retries: {war_count})", file=sys.stderr, flush=True)
                return True
            time.sleep(2)
            waited += 2
        else:
            # Timeout sem war= nem resultados
            print(f"[BATCH] ⏰ Timeout após {max_wait}s", file=sys.stderr, flush=True)
            return False
    
    return False


def _human_delay(min_s=0.5, max_s=1.5):
    """Pausa aleatória que simula comportamento humano"""
    time.sleep(random.uniform(min_s, max_s))


def _type_human(element, text):
    """Digitar texto letra a letra com velocidade humana variável"""
    for i, char in enumerate(text):
        element.send_keys(char)
        if i < 2 or i > len(text) - 2:
            time.sleep(random.uniform(0.18, 0.40))
        else:
            time.sleep(random.uniform(0.08, 0.22))


def _set_field_with_events(driver, field_id, value):
    """Preencher campo disparando eventos nativos (focus, input, change, blur)"""
    driver.execute_script("""
        const el = document.querySelector('#' + arguments[0]);
        if (!el) return;
        el.focus();
        el.dispatchEvent(new Event('focus', {bubbles:true}));
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        nativeInputValueSetter.call(el, arguments[1]);
        el.dispatchEvent(new Event('input', {bubbles:true}));
        el.dispatchEvent(new Event('change', {bubbles:true}));
        el.dispatchEvent(new Event('blur', {bubbles:true}));
    """, field_id, value)


def _fill_dates(driver, start_dt, end_dt):
    """Preencher campos de data e hora via JS com eventos nativos"""
    fecha_rec = start_dt.strftime("%d/%m/%Y")
    fecha_dev = end_dt.strftime("%d/%m/%Y")
    hour = start_dt.strftime("%H:%M")

    _set_field_with_events(driver, 'fechaRecogida', fecha_rec)
    _human_delay(0.3, 0.6)
    _set_field_with_events(driver, 'fechaDevolucion', fecha_dev)
    _human_delay(0.3, 0.6)

    driver.execute_script("""
        const h1 = document.querySelector('#fechaRecogidaSelHour');
        const h2 = document.querySelector('#fechaDevolucionSelHour');
        if (h1) { 
            h1.focus();
            h1.value = arguments[0]; 
            h1.dispatchEvent(new Event('input', {bubbles:true}));
            h1.dispatchEvent(new Event('change', {bubbles:true})); 
            h1.blur();
        }
        if (h2) { 
            h2.focus();
            h2.value = arguments[0]; 
            h2.dispatchEvent(new Event('input', {bubbles:true}));
            h2.dispatchEvent(new Event('change', {bubbles:true})); 
            h2.blur();
        }
    """, hour)


def _do_first_search(driver, carjet_location, start_dt, end_dt, batch_id=None):
    """Primeira pesquisa: homepage completa com comportamento humano"""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    url = "https://www.carjet.com/aluguel-carros/index.htm"
    print(f"[BATCH] Abrindo homepage: {url}", file=sys.stderr, flush=True)
    driver.get(url)
    _human_delay(2.5, 4.0)

    _reject_cookies(driver)
    _human_delay(1.0, 2.0)

    # Simular browsing humano (scroll antes de preencher)
    try:
        driver.execute_script("window.scrollTo({top: 200, behavior: 'smooth'});")
        _human_delay(0.8, 1.5)
        driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        _human_delay(0.5, 1.0)
    except:
        pass

    # Preencher local - apenas "Faro" ou "Albufeira" (curto, para dropdown)
    search_text = carjet_location.split()[0]  # "Faro" ou "Albufeira"
    print(f"[BATCH] Escrevendo local: {search_text} (letra a letra)", file=sys.stderr, flush=True)
    pickup = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "pickup"))
    )
    pickup.click()
    _human_delay(0.3, 0.7)
    pickup.clear()
    _human_delay(0.2, 0.5)

    # Digitar letra a letra
    _type_human(pickup, search_text)
    _human_delay(2.0, 3.0)

    # Clicar dropdown - procurar opção correcta
    target_lower = carjet_location.lower()
    driver.execute_script("""
        const items = document.querySelectorAll('#recogida_lista li');
        const target = arguments[0];
        for (let li of items) {
            const text = li.textContent.toLowerCase();
            if (text.includes(target.split(' ')[0]) && (target.includes('aeroporto') ? text.includes('aeroporto') || text.includes('fao') : true)) {
                const link = li.querySelector('a');
                if (link) { link.click(); return; }
                li.click(); return;
            }
        }
        if (items.length > 0) {
            const link = items[0].querySelector('a');
            if (link) link.click(); else items[0].click();
        }
    """, target_lower)
    _human_delay(0.8, 1.5)

    try:
        driver.find_element(By.CSS_SELECTOR, "h1, h2, .title, header").click()
    except:
        pass
    _human_delay(0.5, 1.0)

    # Preencher datas com eventos nativos
    _fill_dates(driver, start_dt, end_dt)
    _human_delay(0.8, 1.5)

    # Scroll antes de submeter
    try:
        driver.execute_script("window.scrollTo({top: 100, behavior: 'smooth'});")
        _human_delay(0.5, 1.0)
    except:
        pass

    # Submit
    print(f"[BATCH] Submetendo pesquisa...", file=sys.stderr, flush=True)
    _click_search(driver)
    time.sleep(2)

    return _wait_for_results(driver, batch_id=batch_id)


def _update_search(driver, start_dt, end_dt, batch_id=None):
    """Atualizar pesquisa na página de resultados (sem voltar à homepage)"""
    print(f"[BATCH] Modificando datas: {start_dt.strftime('%d/%m/%Y')} → {end_dt.strftime('%d/%m/%Y')}", file=sys.stderr, flush=True)

    # Tentar abrir painel de edição
    panel_result = driver.execute_script("""
        // Clicar em "Alterar" / "Modificar pesquisa"
        const allClickable = document.querySelectorAll('a, button, div[onclick], span[onclick]');
        for (let el of allClickable) {
            const text = el.textContent.toLowerCase().trim();
            if ((text.includes('modificar') || text.includes('alterar') ||
                 text.includes('editar') || text.includes('modify') ||
                 text.includes('change') || text.includes('edit')) &&
                text.length < 50 && el.offsetParent !== null) {
                el.click();
                return 'clicked: ' + text.substring(0, 30);
            }
        }
        // Fallback: clicar em elementos de pesquisa
        const modifyBtns = document.querySelectorAll(
            '.modify-search, .edit-search, .cl--header-search, .search-bar, .search-summary'
        );
        for (let btn of modifyBtns) {
            if (btn.offsetParent !== null) {
                btn.click();
                return 'clicked_class: ' + btn.className;
            }
        }
        return 'no_modify_button';
    """)
    print(f"[BATCH] Painel: {panel_result}", file=sys.stderr, flush=True)
    time.sleep(1.5)

    # Preencher novas datas
    _fill_dates(driver, start_dt, end_dt)
    time.sleep(0.5)

    # Submeter atualização
    submit_result = driver.execute_script("""
        // Botão Pesquisar/Buscar
        const searchBtns = document.querySelectorAll(
            '#btnBuscar, .btn-search, .search-btn, button[type="submit"], input[type="submit"]'
        );
        for (let btn of searchBtns) {
            if (btn.offsetParent !== null) {
                btn.click();
                return 'clicked_btn: ' + (btn.id || btn.className || btn.textContent.substring(0,20));
            }
        }
        // Botão por texto
        const allBtns = document.querySelectorAll('button, a.btn, input[type="submit"]');
        for (let btn of allBtns) {
            const text = (btn.textContent || btn.value || '').toLowerCase().trim();
            if ((text.includes('pesquisar') || text.includes('buscar') ||
                 text.includes('search') || text.includes('atualizar') ||
                 text.includes('actualizar') || text.includes('update')) &&
                btn.offsetParent !== null) {
                btn.click();
                return 'clicked_text: ' + text.substring(0, 30);
            }
        }
        // Fallback: submeter formulário
        const form = document.querySelector('#frm_search_cars') ||
                     document.querySelector('form[action*="list"]') ||
                     document.querySelector('form');
        if (form) { form.submit(); return 'form_submit'; }
        if (typeof searchCars === 'function') { searchCars(); return 'searchCars()'; }
        return 'no_submit_found';
    """)
    print(f"[BATCH] Submit: {submit_result}", file=sys.stderr, flush=True)
    time.sleep(2)

    return _wait_for_results(driver, batch_id=batch_id)


def _navigate_categories(driver, batch_id=None):
    """Navegar por todas as categorias e recolher HTML de cada uma"""
    print(f"[BATCH] Navegando categorias...", file=sys.stderr, flush=True)

    # Esperar artigos iniciais
    for _ in range(10):
        # Verificar cancelamento
        if is_batch_cancelled(batch_id):
            print(f"[BATCH] 🛑 Cancelado durante navigate_categories", file=sys.stderr, flush=True)
            return []
        
        count = driver.execute_script("return document.querySelectorAll('article').length") or 0
        if count >= 3:
            break
        time.sleep(1)

    # Garantir frmTrans=none
    try:
        driver.execute_script("""
            var radios = document.querySelectorAll('input[name="frmTrans"]');
            radios.forEach(function(x) { x.checked = false; });
            var none = document.querySelector('input[name="frmTrans"][value="none"]');
            if (none) none.checked = true;
        """)
    except:
        pass

    all_html_parts = []
    for i, cat in enumerate(CATEGORIES):
        try:
            if i > 0:
                delay = random.uniform(1.5, 3.0)
                time.sleep(delay)

            driver.execute_script(f"filterAgrupVeh('{cat}')")

            # Polling: esperar artigos estabilizarem
            stable = 0
            last_count = -1
            for _ in range(50):
                time.sleep(0.1)
                count = driver.execute_script("return document.querySelectorAll('article').length") or 0
                if count > 0 and count == last_count:
                    stable += 1
                    if stable >= 3:
                        break
                else:
                    stable = 0
                last_count = count

            # Scroll para lazy-load
            try:
                driver.execute_script("""
                    var container = document.querySelector('.results-list, .cl--list, [class*="results"]') || document.documentElement;
                    container.scrollTop = container.scrollHeight;
                    window.scrollTo(0, document.body.scrollHeight);
                """)
                time.sleep(0.5)
            except:
                pass

            cat_html = driver.page_source
            cat_articles = cat_html.count('<article')
            all_html_parts.append(cat_html)

            # Verificar war=
            if 'war=' in driver.current_url:
                print(f"[BATCH] ❌ {cat}: war= detectado!", file=sys.stderr, flush=True)
                return all_html_parts

            print(f"[BATCH]    {cat}: {cat_articles} artigos", file=sys.stderr, flush=True)

        except Exception as e:
            print(f"[BATCH]    {cat}: erro - {e}", file=sys.stderr, flush=True)

    return all_html_parts


def _parse_and_process_categories(all_html_parts, final_url, parse_prices_fn, convert_fn, adjust_fn, normalize_fn, filter_fn):
    """Parse HTML de todas as categorias, deduplicar, e processar"""
    all_items_raw = []
    for i, cat_html in enumerate(all_html_parts):
        cat_items = parse_prices_fn(cat_html, final_url)
        if cat_items:
            all_items_raw.extend(cat_items)
            cat_name = CATEGORIES[i] if i < len(CATEGORIES) else f"CAT{i}"
            print(f"[BATCH]    {cat_name}: +{len(cat_items)} carros", file=sys.stderr, flush=True)

    # Deduplicar por (car_name, supplier, price)
    seen = set()
    unique_items = []
    for item in all_items_raw:
        key = (
            (item.get('car') or item.get('car_name') or '').strip().lower(),
            (item.get('supplier') or '').strip().lower(),
            str(item.get('price_num') or item.get('price') or '').strip().lower()
        )
        if key not in seen and key[0]:
            seen.add(key)
            unique_items.append(item)

    print(f"[BATCH] Dedup: {len(all_items_raw)} → {len(unique_items)} únicos", file=sys.stderr, flush=True)

    # Processar
    items = convert_fn(unique_items)
    items = adjust_fn(items, final_url)

    if items:
        items = normalize_fn(items, supplier_priority=None)
        items = filter_fn(items)

    return items


def scrape_carjet_batch(
    location: str,
    searches: List[Dict[str, Any]],
    parse_prices_fn,
    convert_fn,
    adjust_fn,
    normalize_fn,
    filter_fn,
    lang: str = "pt",
    currency: str = "EUR",
    **kwargs,
) -> Dict[int, List[Dict[str, Any]]]:
    """
    Scraping batch do CarJet - reutiliza mesma sessão Chrome para múltiplos dias.

    Args:
        location: "Faro" ou "Albufeira"
        searches: Lista de dicts com {days, start_dt, end_dt}
        parse_prices_fn: Função parse_prices do main.py
        convert_fn: Função convert_items_gbp_to_eur
        adjust_fn: Função apply_price_adjustments
        normalize_fn: Função normalize_and_sort
        filter_fn: Função filter_automatic_only
        lang: Idioma (default "pt")
        currency: Moeda (default "EUR")

    Returns:
        Dict mapeando days → lista de items
    """
    # Mapear location para formato CarJet
    carjet_location = location
    if 'faro' in location.lower():
        carjet_location = 'Faro Aeroporto (FAO)'
    elif 'albufeira' in location.lower():
        carjet_location = 'Albufeira Cidade'

    print(f"\n{'='*70}", file=sys.stderr, flush=True)
    print(f"[BATCH] 🚀 Scraping batch: {location} ({len(searches)} pesquisas)", file=sys.stderr, flush=True)
    print(f"[BATCH] Local CarJet: {carjet_location}", file=sys.stderr, flush=True)
    for s in searches:
        print(f"[BATCH]   {s['days']} dias: {s['start_dt'].strftime('%d/%m/%Y')} → {s['end_dt'].strftime('%d/%m/%Y')}", file=sys.stderr, flush=True)
    print(f"{'='*70}", file=sys.stderr, flush=True)

    results = {}
    driver = None

    # Inicializar progresso se batch_id fornecido
    batch_id = kwargs.get('batch_id')
    if batch_id:
        with _batch_progress_lock:
            _batch_progress[batch_id] = {
                'total': len(searches),
                'completed': 0,
                'status': 'starting',
                'results': {},
                'current_day': None,
            }

    def _update_progress(day_key=None, items=None, status=None):
        if not batch_id:
            return
        with _batch_progress_lock:
            prog = _batch_progress.get(batch_id)
            if not prog:
                return
            if status:
                prog['status'] = status
            if day_key is not None and items is not None:
                prog['results'][str(day_key)] = items
                prog['completed'] = len(prog['results'])
            if day_key is not None and items is None:
                prog['current_day'] = day_key

    try:
        _update_progress(status='starting_chrome')
        driver = _setup_chrome_driver()

        # Timeout global (5 min por pesquisa + margem)
        total_timeout = len(searches) * 300 + 60
        try:
            def _timeout_handler(signum, frame):
                raise TimeoutError(f"Batch timeout após {total_timeout}s")
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(total_timeout)
        except:
            pass

        _update_progress(status='running')

        for idx, search in enumerate(searches):
            # Verificar se foi cancelado
            if batch_id:
                with _batch_progress_lock:
                    prog = _batch_progress.get(batch_id)
                    if prog and prog.get('cancelled'):
                        print(f"[BATCH] 🛑 Batch cancelado pelo utilizador", file=sys.stderr, flush=True)
                        break
            
            days = search['days']
            start_dt = search['start_dt']
            end_dt = search['end_dt']

            print(f"\n{'━'*70}", file=sys.stderr, flush=True)
            print(f"[BATCH] 📅 Pesquisa {idx+1}/{len(searches)}: {days} dias ({start_dt.strftime('%d/%m')} → {end_dt.strftime('%d/%m')})", file=sys.stderr, flush=True)
            print(f"{'━'*70}", file=sys.stderr, flush=True)
            _update_progress(day_key=days, status='running')

            try:
                if idx == 0:
                    # Primeira pesquisa: homepage completa
                    ok = _do_first_search(driver, carjet_location, start_dt, end_dt, batch_id=batch_id)
                else:
                    # Pesquisas seguintes: reutilizar sessão
                    ok = _update_search(driver, start_dt, end_dt, batch_id=batch_id)

                if not ok:
                    # Recovery: tentar homepage apenas como último recurso
                    print(f"[BATCH] 🔄 Recovery: tentando homepage...", file=sys.stderr, flush=True)
                    time.sleep(random.uniform(5, 10))
                    ok = _do_first_search(driver, carjet_location, start_dt, end_dt, batch_id=batch_id)

                if ok:
                    time.sleep(3)  # Esperar conteúdo carregar
                    final_url = driver.current_url

                    # Navegar categorias
                    all_html_parts = _navigate_categories(driver, batch_id=batch_id)

                    if all_html_parts:
                        items = _parse_and_process_categories(
                            all_html_parts, final_url,
                            parse_prices_fn, convert_fn, adjust_fn,
                            normalize_fn, filter_fn
                        )
                        results[days] = items
                        _update_progress(day_key=days, items=items)
                        print(f"[BATCH] ✅ {days} dias: {len(items)} carros", file=sys.stderr, flush=True)
                    else:
                        results[days] = []
                        _update_progress(day_key=days, items=[])
                        print(f"[BATCH] ⚠️ {days} dias: sem HTML das categorias", file=sys.stderr, flush=True)
                else:
                    results[days] = []
                    _update_progress(day_key=days, items=[])
                    print(f"[BATCH] ❌ {days} dias: falhou (war= ou timeout)", file=sys.stderr, flush=True)

            except Exception as e:
                print(f"[BATCH] ❌ {days} dias: erro - {e}", file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)
                results[days] = []
                _update_progress(day_key=days, items=[])

            # Pausa entre pesquisas (simular comportamento humano)
            if idx < len(searches) - 1:
                pause = random.uniform(3, 6)
                print(f"[BATCH] ⏸️  Pausa de {pause:.1f}s...", file=sys.stderr, flush=True)
                time.sleep(pause)

    except TimeoutError as e:
        print(f"[BATCH] ⏰ {e}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[BATCH] ❌ Erro geral: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
    finally:
        # Cancelar alarm
        try:
            signal.alarm(0)
        except:
            pass
        # Fechar Chrome
        if driver:
            try:
                driver.quit()
                print(f"[BATCH] 🧹 Chrome fechado", file=sys.stderr, flush=True)
            except:
                pass

    # Resumo
    print(f"\n{'='*70}", file=sys.stderr, flush=True)
    print(f"[BATCH] 📊 RESUMO:", file=sys.stderr, flush=True)
    for days, items in sorted(results.items()):
        status = "✅" if items else "❌"
        print(f"[BATCH]   {status} {days} dias: {len(items)} carros", file=sys.stderr, flush=True)
    print(f"{'='*70}", file=sys.stderr, flush=True)

    _update_progress(status='done')
    return results
