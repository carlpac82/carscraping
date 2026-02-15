#!/usr/bin/env python3
"""Teste visual: pesquisa CarJet + navegação por categorias (igual ao scraping real)"""

import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

def test_carjet_categories():
    print("🚀 Teste CarJet: Pesquisa + Categorias (Chrome visível)")
    
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
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        
        stealth(driver,
            languages=["pt-PT", "pt", "en"],
            vendor="Apple Computer, Inc.",
            platform="iPhone",
            webgl_vendor="Apple Inc.",
            renderer="Apple GPU",
            fix_hairline=True,
        )
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        })
        
        driver.set_page_load_timeout(60)
        driver.delete_all_cookies()
        try:
            driver.execute_cdp_cmd('Network.clearBrowserCache', {})
            driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        except:
            pass
        
        # Abrir CarJet
        url = "https://www.carjet.com/aluguel-carros/index.htm"
        print(f"📍 Abrindo: {url}")
        driver.get(url)
        print(f"✅ Página: {driver.title}")
        
        # Rejeitar cookies
        time.sleep(0.5)
        driver.execute_script("""
            const buttons = document.querySelectorAll('button, a, [role="button"]');
            for (let btn of buttons) {
                const text = btn.textContent.toLowerCase().trim();
                if (text.includes('rejeitar') || text.includes('recusar') || text.includes('reject')) {
                    btn.click(); break;
                }
            }
            document.querySelectorAll('[id*=cookie],[class*=cookie],[id*=consent],[class*=consent]').forEach(el => el.remove());
            document.body.style.overflow = 'auto';
        """)
        print("🍪 Cookies tratados")
        time.sleep(0.5)
        
        if 'war=' in driver.current_url:
            print("❌ BLOQUEADO na homepage!")
            input("Enter para fechar...")
            return
        
        # Datas de teste
        start_dt = datetime(2026, 2, 11, 15, 0)
        end_dt = datetime(2026, 2, 12, 15, 0)
        selected_hour = random.choice(['14:30', '15:00', '15:30', '16:00'])
        
        # PASSO 1: Local
        print("\n📍 PASSO 1: Preenchendo localização...")
        pickup_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pickup"))
        )
        pickup_input.click()
        time.sleep(0.3)
        pickup_input.clear()
        pickup_input.send_keys("albufeira")
        print("   ✅ Local digitado: Albufeira")
        time.sleep(2)
        
        # PASSO 2: Dropdown
        print("📍 PASSO 2: Clicando no dropdown...")
        clicked = driver.execute_script("""
            const list = document.querySelector('#recogida_lista');
            if (!list) return 'no list';
            const items = list.querySelectorAll('li a');
            for (const a of items) {
                if (a.textContent.includes('Albufeira')) {
                    a.click();
                    return 'clicked: ' + a.textContent.substring(0, 40);
                }
            }
            const lis = list.querySelectorAll('li');
            if (lis.length > 0) { lis[0].click(); return 'clicked li[0]'; }
            return 'nothing';
        """)
        print(f"   ✅ {clicked}")
        
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, "h1, h2, .title, header").click()
        print("   ✅ Local confirmado")
        
        # PASSO 3: Datas
        fecha_rec = start_dt.strftime("%d/%m/%Y")
        fecha_dev = end_dt.strftime("%d/%m/%Y")
        print(f"\n📅 PASSO 3: Datas: {fecha_rec} → {fecha_dev}, Hora: {selected_hour}")
        
        result = driver.execute_script("""
            const fechaRec = arguments[0], fechaDev = arguments[1], hour = arguments[2];
            let filled = {};
            const fr = document.querySelector('#fechaRecogida');
            const fd = document.querySelector('#fechaDevolucion');
            if (fr) { fr.value = fechaRec; filled.fechaRec = fr.value; }
            if (fd) { fd.value = fechaDev; filled.fechaDev = fd.value; }
            const h1 = document.querySelector('#fechaRecogidaSelHour');
            if (h1) { h1.value = hour; h1.dispatchEvent(new Event('change', {bubbles:true})); filled.h1 = h1.value; }
            const h2 = document.querySelector('#fechaDevolucionSelHour');
            if (h2) { h2.value = hour; h2.dispatchEvent(new Event('change', {bubbles:true})); filled.h2 = h2.value; }
            return filled;
        """, fecha_rec, fecha_dev, selected_hour)
        print(f"   ✅ {result}")
        
        # PASSO 4: Submit
        print("\n🔍 PASSO 4: Submetendo...")
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(0.3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.3)
        
        driver.execute_script("""
            const btn = document.querySelector('#btnBuscar');
            if (btn) btn.click();
            else {
                const form = document.querySelector('#frm_search_cars') || document.querySelector('form');
                if (form) form.submit();
            }
        """)
        
        # Aguardar resultados
        print("⏳ Aguardando resultados...")
        time.sleep(2)
        for i in range(15):
            time.sleep(2)
            cur = driver.current_url
            if '/do/list/' in cur and 's=' in cur and 'b=' in cur:
                print(f"   ✅ Resultados carregados após {i*2+2}s")
                break
            if 'war=' in cur:
                print(f"   ❌ WAR detectado: {cur}")
                input("Enter para fechar...")
                return
            print(f"   ⏳ {i*2+2}s: {cur[:70]}...")
        
        time.sleep(3)
        final_url = driver.current_url
        print(f"\n🔗 URL: {final_url[:80]}...")
        
        if 's=' not in final_url or 'b=' not in final_url:
            print("❌ Sem URL s/b válida!")
            input("Enter para fechar...")
            return
        
        # ═══════════════════════════════════════════════════════════
        # NAVEGAR POR CATEGORIAS (igual ao scraping real)
        # ═══════════════════════════════════════════════════════════
        print("\n" + "="*60)
        print("📂 NAVEGANDO POR CATEGORIAS (igual ao scraping real)")
        print("="*60)
        
        # Garantir frmTrans=none
        driver.execute_script("""
            var radios = document.querySelectorAll('input[name="frmTrans"]');
            radios.forEach(function(x) { x.checked = false; });
            var none = document.querySelector('input[name="frmTrans"][value="none"]');
            if (none) none.checked = true;
        """)
        print("🧹 frmTrans=none definido")
        
        CATEGORIES = ['MINI', 'COMP', 'FAMI', 'ESTA', 'SUVS', 'VANS', 'LUXU', 'AUTO']
        total_articles = 0
        
        for cat in CATEGORIES:
            try:
                before = driver.execute_script("return document.querySelectorAll('article').length") or 0
                driver.execute_script(f"filterAgrupVeh('{cat}')")
                
                # Aguardar estabilização
                stable = 0
                last_count = -1
                for poll in range(50):
                    time.sleep(0.1)
                    count = driver.execute_script("return document.querySelectorAll('article').length") or 0
                    if count > 0 and count == last_count:
                        stable += 1
                        if stable >= 3:
                            break
                    else:
                        stable = 0
                    last_count = count
                
                # Scroll para lazy loading
                try:
                    driver.execute_script("""
                        var container = document.querySelector('.results-list, .cl--list, [class*="results"]') || document.documentElement;
                        container.scrollTop = container.scrollHeight;
                        window.scrollTo(0, document.body.scrollHeight);
                    """)
                    time.sleep(0.5)
                except:
                    pass
                
                articles = driver.execute_script("return document.querySelectorAll('article').length") or 0
                total_articles += articles
                print(f"   📂 {cat}: {articles} artigos (before={before})")
                
            except Exception as e:
                print(f"   ❌ {cat}: erro - {e}")
        
        print(f"\n📊 TOTAL: {total_articles} artigos em {len(CATEGORIES)} categorias")
        print("\n✅ Teste completo! Chrome fica aberto para inspeção visual.")
        input("\n⏳ Pressione Enter para fechar o Chrome...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        input("Enter para fechar...")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_carjet_categories()
