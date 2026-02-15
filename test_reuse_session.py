#!/usr/bin/env python3
"""
Teste visual: Reutilizar mesma sessão Chrome para múltiplos dias.
Em vez de fechar e abrir Chrome para cada dia, muda as datas na página
de resultados, clica Atualizar, e navega pelas categorias.

Fluxo:
1. Abrir Chrome → Homepage → Pesquisar Dia 1
2. Navegar categorias do Dia 1
3. Modificar datas para Dia 2 (sem fechar Chrome)
4. Navegar categorias do Dia 2
5. Repetir para Dia 3
"""
import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

CATEGORIES = ['MINI', 'COMP', 'FAMI', 'ESTA', 'SUVS', 'VANS', 'LUXU', 'AUTO']

def reject_cookies(driver):
    """Rejeitar cookies se aparecerem"""
    try:
        driver.execute_script("""
            const buttons = document.querySelectorAll('button, a, [role="button"]');
            for (let btn of buttons) {
                const text = btn.textContent.toLowerCase().trim();
                if (text.includes('rejeitar') || text.includes('reject')) {
                    btn.click(); return true;
                }
            }
            return false;
        """)
    except:
        pass

def wait_for_results(driver, max_wait=30):
    """Aguardar até URL ter s= e b= (resultados prontos)"""
    waited = 0
    while waited < max_wait:
        url = driver.current_url
        if 'war=' in url:
            print(f"       ❌ war= detectado após {waited}s!")
            return False
        if '/do/list/' in url and 's=' in url and 'b=' in url:
            print(f"       ✅ Resultados prontos após {waited}s")
            return True
        time.sleep(2)
        waited += 2
    print(f"       ⏰ Timeout após {max_wait}s")
    return False

def wait_for_articles(driver, min_articles=5, max_wait=15):
    """Aguardar até artigos aparecerem na página"""
    waited = 0
    while waited < max_wait:
        count = driver.execute_script("return document.querySelectorAll('article').length") or 0
        if count >= min_articles:
            return count
        time.sleep(1)
        waited += 1
    return driver.execute_script("return document.querySelectorAll('article').length") or 0

def do_first_search(driver, location, start_dt, end_dt):
    """Primeira pesquisa: preencher tudo desde a homepage"""
    url = "https://www.carjet.com/aluguel-carros/index.htm"
    print(f"\n   [HOMEPAGE] Abrindo: {url}")
    driver.get(url)
    time.sleep(3)
    
    reject_cookies(driver)
    time.sleep(1)
    
    # Preencher local
    print(f"   [LOCAL] Escrevendo: {location}")
    pickup = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "pickup"))
    )
    pickup.clear()
    pickup.send_keys(location)
    time.sleep(1.5)
    
    # Clicar dropdown
    driver.execute_script("""
        const items = document.querySelectorAll('#recogida_lista li');
        if (items.length > 0) items[0].querySelector('a')?.click() || items[0].click();
    """)
    time.sleep(0.5)
    try:
        driver.find_element(By.CSS_SELECTOR, "h1, h2, .title, header").click()
    except:
        pass
    time.sleep(1)
    
    # Preencher datas
    fill_dates(driver, start_dt, end_dt)
    
    # Submit
    print(f"   [SUBMIT] Pesquisando...")
    driver.execute_script("""
        const btn = document.querySelector('#btnBuscar');
        if (btn) btn.click();
        else {
            const form = document.querySelector('#frm_search_cars') || document.querySelector('form');
            if (form) form.submit();
        }
    """)
    time.sleep(2)
    
    return wait_for_results(driver)

def fill_dates(driver, start_dt, end_dt):
    """Preencher campos de data e hora via JS"""
    fecha_rec = start_dt.strftime("%d/%m/%Y")
    fecha_dev = end_dt.strftime("%d/%m/%Y")
    hour = start_dt.strftime("%H:%M")
    
    print(f"   [DATAS] {fecha_rec} → {fecha_dev} às {hour}")
    driver.execute_script("""
        const fr = document.querySelector('#fechaRecogida');
        const fd = document.querySelector('#fechaDevolucion');
        if (fr) fr.value = arguments[0];
        if (fd) fd.value = arguments[1];
        const h1 = document.querySelector('#fechaRecogidaSelHour');
        const h2 = document.querySelector('#fechaDevolucionSelHour');
        if (h1) { h1.value = arguments[2]; h1.dispatchEvent(new Event('change', {bubbles:true})); }
        if (h2) { h2.value = arguments[2]; h2.dispatchEvent(new Event('change', {bubbles:true})); }
    """, fecha_rec, fecha_dev, hour)

def update_search(driver, start_dt, end_dt):
    """Atualizar pesquisa na página de resultados (sem voltar à homepage).
    
    Tenta múltiplas abordagens:
    1. Abrir painel de modificação de pesquisa na página de resultados
    2. Alterar datas nos campos hidden
    3. Clicar no botão de atualizar/modificar
    4. Fallback: re-submeter formulário
    """
    print(f"\n   [UPDATE] Modificando datas na página de resultados...")
    
    # Tentar abrir painel de edição de pesquisa (se existir)
    panel_opened = driver.execute_script("""
        // Tentar clicar no botão "Modificar pesquisa" ou similar
        const modifyBtns = document.querySelectorAll(
            '.modify-search, .edit-search, [data-action="modify"], ' +
            '.btn-modify, .search-modify, .change-search, ' +
            'a[href*="modify"], button[class*="modif"], ' +
            '.cl--header-search, .search-bar, .search-summary'
        );
        for (let btn of modifyBtns) {
            if (btn.offsetParent !== null) {  // visível
                btn.click();
                return 'clicked_modify: ' + btn.className;
            }
        }
        
        // Tentar clicar em qualquer elemento que contenha texto de modificar
        const allClickable = document.querySelectorAll('a, button, div[onclick], span[onclick]');
        for (let el of allClickable) {
            const text = el.textContent.toLowerCase().trim();
            if ((text.includes('modificar') || text.includes('alterar') || 
                 text.includes('editar') || text.includes('modify') ||
                 text.includes('change') || text.includes('edit')) &&
                text.length < 50 && el.offsetParent !== null) {
                el.click();
                return 'clicked_text: ' + text.substring(0, 30);
            }
        }
        
        return 'no_modify_button';
    """)
    print(f"   [UPDATE] Painel: {panel_opened}")
    time.sleep(1.5)
    
    # Preencher novas datas
    fill_dates(driver, start_dt, end_dt)
    time.sleep(0.5)
    
    # Tentar submeter a atualização
    submit_result = driver.execute_script("""
        // 1. Botão "Pesquisar" / "Buscar" / "Atualizar" na página de resultados
        const searchBtns = document.querySelectorAll(
            '#btnBuscar, .btn-search, .search-btn, ' +
            'button[type="submit"], input[type="submit"], ' +
            '.btn-primary, .btn-update'
        );
        for (let btn of searchBtns) {
            if (btn.offsetParent !== null) {
                btn.click();
                return 'clicked_btn: ' + (btn.id || btn.className || btn.textContent.substring(0,20));
            }
        }
        
        // 2. Tentar botão por texto
        const allBtns = document.querySelectorAll('button, a.btn, input[type="submit"]');
        for (let btn of allBtns) {
            const text = (btn.textContent || btn.value || '').toLowerCase().trim();
            if ((text.includes('pesquisar') || text.includes('buscar') || 
                 text.includes('search') || text.includes('atualizar') ||
                 text.includes('actualizar') || text.includes('update')) &&
                btn.offsetParent !== null) {
                btn.click();
                return 'clicked_text_btn: ' + text.substring(0, 30);
            }
        }
        
        // 3. Fallback: submeter formulário
        const form = document.querySelector('#frm_search_cars') || 
                     document.querySelector('form[action*="list"]') ||
                     document.querySelector('form');
        if (form) {
            form.submit();
            return 'form_submit';
        }
        
        // 4. Último recurso: searchCars() se existir
        if (typeof searchCars === 'function') {
            searchCars();
            return 'searchCars()';
        }
        
        return 'no_submit_found';
    """)
    print(f"   [UPDATE] Submit: {submit_result}")
    time.sleep(2)
    
    return wait_for_results(driver)

def navigate_categories(driver, day_label):
    """Navegar por todas as categorias e contar artigos"""
    print(f"\n   [CATEGORIAS] Navegando categorias para {day_label}...")
    
    # Esperar artigos iniciais
    initial = wait_for_articles(driver, min_articles=3, max_wait=10)
    print(f"   [CATEGORIAS] Artigos iniciais: {initial}")
    
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
    
    total_articles = 0
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
                    window.scrollTo(0, document.body.scrollHeight);
                """)
                time.sleep(0.5)
            except:
                pass
            
            articles = driver.execute_script("return document.querySelectorAll('article').length") or 0
            total_articles += articles
            
            # Verificar war=
            if 'war=' in driver.current_url:
                print(f"       ❌ {cat}: war= detectado!")
                return -1
            
            print(f"       {cat}: {articles} artigos")
            
        except Exception as e:
            print(f"       {cat}: erro - {e}")
    
    print(f"   [CATEGORIAS] Total (com duplicados): {total_articles}")
    return total_articles

def main():
    # Gerar 3 dias de pesquisa (como automated prices faria)
    base = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=2)
    days_to_search = []
    for d in range(3):
        start = base + timedelta(days=d)
        end = start + timedelta(days=3)
        days_to_search.append((start, end))
    
    print("=" * 70)
    print("TESTE: Reutilizar sessão Chrome para múltiplos dias")
    print("=" * 70)
    for i, (s, e) in enumerate(days_to_search):
        print(f"  Dia {i+1}: {s.strftime('%d/%m/%Y')} → {e.strftime('%d/%m/%Y')}")
    print("=" * 70)
    
    # Configurar Chrome (UMA VEZ)
    iphone_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-agent={iphone_ua}")
    options.add_argument("--window-size=390,844")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    mobile_emulation = {
        "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
        "userAgent": iphone_ua
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    driver = webdriver.Chrome(options=options)
    
    stealth(driver,
        languages=["pt-PT", "pt", "en"],
        vendor="Apple Computer, Inc.",
        platform="iPhone",
        webgl_vendor="Apple Inc.",
        renderer="Apple GPU",
        fix_hairline=True,
    )
    
    driver.set_page_load_timeout(30)
    
    results = {}
    
    try:
        for day_idx, (start_dt, end_dt) in enumerate(days_to_search):
            day_label = f"Dia {day_idx + 1} ({start_dt.strftime('%d/%m')} → {end_dt.strftime('%d/%m')})"
            print(f"\n{'━' * 70}")
            print(f"📅 {day_label}")
            print(f"{'━' * 70}")
            
            if day_idx == 0:
                # Primeira pesquisa: homepage completa
                ok = do_first_search(driver, "Faro Aeroporto (FAO)", start_dt, end_dt)
            else:
                # Pesquisas seguintes: reutilizar sessão, só mudar datas
                ok = update_search(driver, start_dt, end_dt)
            
            if ok:
                # Esperar conteúdo carregar
                time.sleep(3)
                total = navigate_categories(driver, day_label)
                results[day_label] = total
                print(f"\n   ✅ {day_label}: {total} artigos totais")
            else:
                results[day_label] = -1
                print(f"\n   ❌ {day_label}: falhou (war= ou timeout)")
                
                # Se falhou, tentar voltar à homepage e refazer
                print(f"   [RECOVERY] Tentando voltar à homepage...")
                ok2 = do_first_search(driver, "Faro Aeroporto (FAO)", start_dt, end_dt)
                if ok2:
                    time.sleep(3)
                    total = navigate_categories(driver, day_label)
                    results[day_label] = total
                    print(f"\n   ✅ {day_label} (recovery): {total} artigos totais")
            
            # Pausa entre dias (simular comportamento humano)
            if day_idx < len(days_to_search) - 1:
                pause = random.uniform(3, 5)
                print(f"\n   ⏸️  Pausa de {pause:.1f}s antes do próximo dia...")
                time.sleep(pause)
        
        # Resumo final
        print(f"\n{'=' * 70}")
        print(f"📊 RESUMO FINAL")
        print(f"{'=' * 70}")
        for day, total in results.items():
            status = "✅" if total > 0 else "❌"
            print(f"  {status} {day}: {total} artigos")
        print(f"{'=' * 70}")
        
        print(f"\nMantendo browser aberto 20s para inspeção...")
        time.sleep(20)
        
    finally:
        driver.quit()
        print("Chrome fechado.")

if __name__ == '__main__':
    main()
