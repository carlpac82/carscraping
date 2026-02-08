"""
Teste visual: Limpeza do filtro de transmissão no CarJet mobile
Replica EXATAMENTE o fluxo do Railway (cookies, local, datas, submit)
Depois testa a limpeza do filtro e navegação por categorias.
"""
import time
import os
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

SCREENSHOTS_DIR = "screenshots_filtro"

def setup_driver():
    """Configurar Chrome EXATAMENTE como o Railway"""
    opts = Options()
    
    # NÃO headless (macOS) - igual ao Railway em macOS
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-extensions')
    opts.add_argument('--disable-setuid-sandbox')
    
    selected_device = {
        'name': 'iPhone 13 Pro',
        'ua': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'width': 390,
        'height': 844,
        'pixelRatio': 3.0
    }
    
    opts.add_argument(f'user-agent={selected_device["ua"]}')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument(f'--window-size={selected_device["width"]},{selected_device["height"]}')
    
    # EMULAÇÃO MOBILE COMPLETA
    mobile_emulation = {
        "deviceMetrics": { 
            "width": selected_device['width'], 
            "height": selected_device['height'], 
            "pixelRatio": selected_device['pixelRatio']
        },
        "userAgent": selected_device['ua']
    }
    opts.add_experimental_option("mobileEmulation", mobile_emulation)
    
    if os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        opts.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    driver = webdriver.Chrome(options=opts)
    
    # Stealth (igual ao Railway)
    stealth(driver,
        languages=["pt-PT", "pt", "en"],
        vendor="Apple Computer, Inc.",
        platform="iPhone",
        webgl_vendor="Apple Inc.",
        renderer="Apple GPU",
        fix_hairline=True,
    )
    
    # Esconder webdriver
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
    })
    
    driver.set_page_load_timeout(60)
    return driver


def reject_cookies(driver):
    """Rejeitar cookies - EXATAMENTE como o Railway"""
    try:
        result = driver.execute_script("""
            const buttons = document.querySelectorAll('button, a, [role="button"]');
            let found = false;
            for (let btn of buttons) {
                const text = btn.textContent.toLowerCase().trim();
                if (text.includes('rejeitar') || text.includes('recusar') || 
                    text.includes('reject') || text.includes('rechazar') ||
                    text.includes('não aceitar') || text.includes('decline')) {
                    btn.click();
                    found = true;
                    break;
                }
            }
            if (!found) {
                document.querySelectorAll('[id*=cookie], [class*=cookie], [id*=didomi], [class*=didomi], [id*=consent], [class*=consent]').forEach(el => {
                    el.remove();
                });
            }
            document.body.style.overflow = 'auto';
            return found;
        """)
        return result
    except:
        return False


def main():
    driver = setup_driver()
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    carjet_url = "https://www.carjet.com/aluguel-carros/index.htm"
    carjet_location = "Faro Aeroporto (FAO)"
    
    # Datas futuras (igual ao Railway)
    start_dt = datetime.now() + timedelta(days=30)
    end_dt = start_dt + timedelta(days=7)
    selected_hour = random.choice(['14:30', '15:00', '15:30', '16:00', '16:30', '17:00'])
    start_dt = start_dt.replace(hour=int(selected_hour.split(':')[0]), minute=int(selected_hour.split(':')[1]))
    end_dt = end_dt.replace(hour=int(selected_hour.split(':')[0]), minute=int(selected_hour.split(':')[1]))
    
    try:
        print("=" * 60)
        print("FLUXO EXATO DO RAILWAY - Selenium CarJet")
        print("=" * 60)
        print(f"URL: {carjet_url}")
        print(f"Local: {carjet_location}")
        print(f"Datas: {start_dt.strftime('%d/%m/%Y %H:%M')} - {end_dt.strftime('%d/%m/%Y %H:%M')}")
        
        # ========== PASSO 0: Limpar cache e cookies ==========
        print("\n[PASSO 0] Limpando cache e cookies...")
        driver.delete_all_cookies()
        try:
            driver.execute_cdp_cmd('Network.clearBrowserCache', {})
            driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
            print("   ✓ Cache e cookies limpos via CDP")
        except:
            pass
        
        # ========== PASSO 1: Abrir CarJet ==========
        print("\n[PASSO 1] Abrindo CarJet...")
        driver.get(carjet_url)
        
        # Rejeitar cookies (igual ao Railway)
        time.sleep(0.5)
        if reject_cookies(driver):
            print("   ✅ Cookies rejeitados")
        else:
            print("   ℹ️ Banner removido")
        time.sleep(0.5)
        
        driver.save_screenshot(f"{SCREENSHOTS_DIR}/01_homepage.png")
        print(f"   📸 Screenshot: 01_homepage.png")
        
        # ========== PASSO 2: Escrever local ==========
        print("\n[PASSO 2] Escrevendo local...")
        pickup_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pickup"))
        )
        pickup_input.clear()
        pickup_input.send_keys(carjet_location)
        print(f"   ✓ Local digitado: {carjet_location}")
        
        # Aguardar dropdown e clicar
        time.sleep(1.5)
        js_result = driver.execute_script("""
            try {
                const items = document.querySelectorAll('#recogida_lista li');
                if (items.length > 0) {
                    items[0].querySelector('a')?.click() || items[0].click();
                    return 'clicked:' + items.length;
                }
                return 'no_items';
            } catch(e) { return 'error:' + e.message; }
        """)
        print(f"   ✓ Dropdown: {js_result}")
        
        time.sleep(0.5)
        try:
            driver.find_element(By.CSS_SELECTOR, "h1, h2, .title, header").click()
        except:
            pass
        time.sleep(1)
        
        driver.save_screenshot(f"{SCREENSHOTS_DIR}/02_local_preenchido.png")
        print(f"   📸 Screenshot: 02_local_preenchido.png")
        
        # ========== PASSO 3: Preencher datas via campos hidden ==========
        print("\n[PASSO 3] Preenchendo datas via campos hidden...")
        fecha_recogida = start_dt.strftime("%d/%m/%Y")
        fecha_devolucion = end_dt.strftime("%d/%m/%Y")
        hour_pickup = start_dt.strftime("%H:%M")
        hour_dropoff = end_dt.strftime("%H:%M")
        
        driver.set_script_timeout(10)
        result = driver.execute_script("""
            const fechaRecogida = arguments[0];
            const fechaDevolucion = arguments[1];
            const hourPickup = arguments[2];
            const hourDropoff = arguments[3];
            let filled = {};
            const fechaRec = document.querySelector('#fechaRecogida');
            const fechaDev = document.querySelector('#fechaDevolucion');
            if (fechaRec) { fechaRec.value = fechaRecogida; filled.fechaRec = fechaRec.value; }
            if (fechaDev) { fechaDev.value = fechaDevolucion; filled.fechaDev = fechaDev.value; }
            const h1 = document.querySelector('#fechaRecogidaSelHour');
            if (h1) { h1.value = hourPickup; h1.dispatchEvent(new Event('change', {bubbles: true})); filled.h1 = h1.value; }
            const h2 = document.querySelector('#fechaDevolucionSelHour');
            if (h2) { h2.value = hourDropoff; h2.dispatchEvent(new Event('change', {bubbles: true})); filled.h2 = h2.value; }
            return filled;
        """, fecha_recogida, fecha_devolucion, hour_pickup, hour_dropoff)
        print(f"   ✓ Datas preenchidas: {result}")
        
        driver.save_screenshot(f"{SCREENSHOTS_DIR}/03_datas_preenchidas.png")
        print(f"   📸 Screenshot: 03_datas_preenchidas.png")
        
        # ========== PASSO 4: Submit ==========
        print("\n[PASSO 4] Submetendo formulário...")
        driver.set_script_timeout(5)
        try:
            driver.execute_script("window.scrollBy(0, 300);")
        except:
            pass
        time.sleep(0.3)
        try:
            driver.execute_script("window.scrollTo(0, 0);")
        except:
            pass
        time.sleep(0.3)
        
        submit_result = driver.execute_script("""
            const btn = document.querySelector('#btnBuscar');
            if (btn) { btn.click(); return 'OK_BTN'; }
            const form = document.querySelector('#frm_search_cars') || 
                         document.querySelector('form[name="menu_tarifas"]') ||
                         document.querySelector('form');
            if (form) { form.submit(); return 'OK_FORM'; }
            return 'NO_FORM';
        """)
        print(f"   ✓ Submit: {submit_result}")
        
        # ========== PASSO 5: Aguardar resultados ==========
        print("\n[PASSO 5] Aguardando resultados...")
        time.sleep(2)
        
        max_wait = 20
        waited = 0
        while waited < max_wait:
            current_url = driver.current_url
            if '/do/list/' in current_url and 's=' in current_url and 'b=' in current_url:
                print(f"   ✅ Resultados em {waited}s! URL: {current_url[:80]}...")
                break
            else:
                print(f"   Aguardando... ({waited}s)")
                time.sleep(2)
                waited += 2
        
        time.sleep(3)  # Esperar carregamento completo
        
        final_url = driver.current_url
        if 's=' not in final_url or 'b=' not in final_url:
            print(f"   ❌ Sem resultados! URL: {final_url}")
            driver.save_screenshot(f"{SCREENSHOTS_DIR}/erro_sem_resultados.png")
            return
        
        articles_homepage = driver.page_source.count('<article')
        driver.save_screenshot(f"{SCREENSHOTS_DIR}/04_resultados.png")
        print(f"   📸 Screenshot: 04_resultados.png")
        print(f"   Homepage: {articles_homepage} artigos")
        
        # ============================================================
        # AGORA: TESTAR LIMPEZA DO FILTRO E CATEGORIAS
        # ============================================================
        print("\n" + "=" * 60)
        print("TESTE: FILTRO DE TRANSMISSÃO")
        print("=" * 60)
        
        # Ver estado actual dos filtros
        filtro_info = driver.execute_script("""
            var r = {};
            var chk = document.getElementById('chkTransNone');
            r.chkTransNone = chk ? {exists: true, checked: chk.checked} : {exists: false};
            var radios = document.querySelectorAll('input[name="frmTrans"]');
            r.radios = [];
            radios.forEach(function(x) { r.radios.push({value: x.value, checked: x.checked, id: x.id}); });
            r.hasFilterAgrupVeh = typeof filterAgrupVeh === 'function';
            var fu = document.getElementById('filterUsed');
            r.filterUsed = fu ? fu.innerText.substring(0, 200) : 'N/A';
            return JSON.stringify(r, null, 2);
        """)
        print(f"   Estado filtros:\n{filtro_info}")
        
        # ============================================================
        # TESTE A: chkTransNone.click() + sleep(2) [MÉTODO ACTUAL]
        # ============================================================
        print("\n--- TESTE A: chkTransNone.click() + sleep(2) ---")
        t0 = time.time()
        r = driver.execute_script("""
            try {
                var chk = document.getElementById('chkTransNone');
                if (chk) { chk.click(); return 'clicked'; }
                return 'not found';
            } catch(e) { return 'erro: ' + e.message; }
        """)
        time.sleep(2)
        t1 = time.time()
        a_count = driver.page_source.count('<article')
        driver.save_screenshot(f"{SCREENSHOTS_DIR}/05_teste_A_chkTransNone.png")
        print(f"   {r} | {t1-t0:.1f}s | {a_count} artigos")
        
        # Reverter
        driver.execute_script("try { document.getElementById('chkTransNone').click(); } catch(e) {}")
        time.sleep(2)
        
        # ============================================================
        # TESTE B: frmTrans radio via JS (SEM sleep extra)
        # ============================================================
        print("\n--- TESTE B: frmTrans radio via JS (sem sleep) ---")
        t0 = time.time()
        r = driver.execute_script("""
            try {
                var radios = document.querySelectorAll('input[name="frmTrans"]');
                radios.forEach(function(x) { x.checked = false; });
                var none = document.querySelector('input[name="frmTrans"][value="none"]');
                if (none) { none.checked = true; return 'set none, ' + radios.length + ' radios'; }
                return 'none radio not found';
            } catch(e) { return 'erro: ' + e.message; }
        """)
        t1 = time.time()
        print(f"   {r} | {t1-t0:.3f}s (instantâneo!)")
        
        # ============================================================
        # TESTE C: Ver source do filterAgrupVeh
        # ============================================================
        print("\n--- TESTE C: filterAgrupVeh source ---")
        src = driver.execute_script("try { return filterAgrupVeh.toString().substring(0, 800); } catch(e) { return e.message; }")
        print(f"   {src}")
        
        # ============================================================
        # TESTE D: Categorias com polling rápido
        # ============================================================
        print("\n" + "=" * 60)
        print("CATEGORIAS: Polling rápido (100ms)")
        print("=" * 60)
        
        # Definir frmTrans=none via JS (instantâneo)
        driver.execute_script("""
            var radios = document.querySelectorAll('input[name="frmTrans"]');
            radios.forEach(function(x) { x.checked = false; });
            var none = document.querySelector('input[name="frmTrans"][value="none"]');
            if (none) none.checked = true;
        """)
        
        categories = ['MINI', 'COMP', 'FAMI', 'ESTA', 'SUVS', 'VANS', 'LUXU', 'AUTO']
        total_start = time.time()
        
        for cat in categories:
            t0 = time.time()
            driver.execute_script(f"filterAgrupVeh('{cat}')")
            
            # Polling rápido (100ms)
            ready = None
            for _ in range(30):  # Max 3s
                time.sleep(0.1)
                ready = driver.execute_script("""
                    var a = document.querySelectorAll('article');
                    if (a.length > 0) {
                        var p = document.querySelectorAll('.price.pr-euros');
                        return {articles: a.length, prices: p.length};
                    }
                    return null;
                """)
                if ready:
                    break
            
            t1 = time.time()
            jogger = 'jogger' in driver.page_source.lower()
            print(f"   {cat}: {ready} em {t1-t0:.2f}s {'🚗 JOGGER!' if jogger else ''}")
            driver.save_screenshot(f"{SCREENSHOTS_DIR}/06_cat_{cat}.png")
        
        total_time = time.time() - total_start
        print(f"\n   ⏱️ TEMPO TOTAL categorias: {total_time:.1f}s")
        
        print("\n" + "=" * 60)
        print("TESTE COMPLETO!")
        print(f"Screenshots em: {SCREENSHOTS_DIR}/")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot(f"{SCREENSHOTS_DIR}/erro.png")
    finally:
        input("\nPrime ENTER para fechar o browser...")
        driver.quit()

if __name__ == "__main__":
    main()
