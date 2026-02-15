#!/usr/bin/env python3
"""
Teste visual para diagnosticar war=28 no CarJet.
Faz pesquisa simples SEM navegação por categorias para isolar o problema.
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

def main():
    start = datetime.now().replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=2)
    end = start + timedelta(days=3)
    
    print("=" * 70)
    print("TESTE: Selenium SEM categorias (isolar war=28)")
    print(f"Datas: {start.strftime('%d/%m/%Y')} → {end.strftime('%d/%m/%Y')}")
    print("=" * 70)
    
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
    
    try:
        # PASSO 1: Abrir homepage
        url = "https://www.carjet.com/aluguel-carros/index.htm"
        print(f"\n[1] Abrindo homepage: {url}")
        driver.get(url)
        time.sleep(3)
        print(f"    URL: {driver.current_url}")
        
        # Rejeitar cookies
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
        time.sleep(1)
        
        # PASSO 2: Preencher local
        print(f"\n[2] Preenchendo local: Faro Aeroporto (FAO)")
        pickup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pickup"))
        )
        pickup.clear()
        pickup.send_keys("Faro Aeroporto (FAO)")
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
        
        # PASSO 3: Preencher datas
        fecha_rec = start.strftime("%d/%m/%Y")
        fecha_dev = end.strftime("%d/%m/%Y")
        hour = "15:00"
        
        print(f"\n[3] Preenchendo datas: {fecha_rec} → {fecha_dev} às {hour}")
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
        time.sleep(0.5)
        
        # PASSO 4: Submit
        print(f"\n[4] Submetendo pesquisa...")
        driver.execute_script("""
            const btn = document.querySelector('#btnBuscar');
            if (btn) btn.click();
            else {
                const form = document.querySelector('#frm_search_cars') || document.querySelector('form');
                if (form) form.submit();
            }
        """)
        
        # PASSO 5: Aguardar resultados
        print(f"\n[5] Aguardando resultados...")
        time.sleep(2)
        
        max_wait = 30
        waited = 0
        while waited < max_wait:
            current_url = driver.current_url
            if 'war=' in current_url:
                print(f"    ❌ war= DETECTADO após {waited}s!")
                print(f"    URL: {current_url}")
                break
            if '/do/list/' in current_url and 's=' in current_url and 'b=' in current_url:
                print(f"    ✅ Resultados carregados após {waited}s!")
                print(f"    URL: {current_url[:100]}...")
                break
            print(f"    Aguardando... ({waited}s) URL: {current_url[:80]}...")
            time.sleep(2)
            waited += 2
        
        if waited >= max_wait:
            print(f"    ⏰ Timeout após {max_wait}s")
            print(f"    URL final: {driver.current_url}")
        
        # PASSO 6: Verificar resultados (sem navegar categorias)
        final_url = driver.current_url
        if 's=' in final_url and 'b=' in final_url and 'war=' not in final_url:
            time.sleep(5)  # Esperar carros carregarem
            html = driver.page_source
            articles = html.count('<article')
            print(f"\n[6] RESULTADOS SEM CATEGORIAS:")
            print(f"    Artigos: {articles}")
            print(f"    HTML: {len(html)} bytes")
            print(f"    war= na URL: {'war=' in final_url}")
            
            # Agora testar navegar UMA categoria
            print(f"\n[7] Testando UMA categoria (MINI)...")
            try:
                driver.execute_script("filterAgrupVeh('MINI')")
                time.sleep(3)
                html2 = driver.page_source
                articles2 = html2.count('<article')
                url2 = driver.current_url
                print(f"    Artigos MINI: {articles2}")
                print(f"    war= na URL: {'war=' in url2}")
            except Exception as e:
                print(f"    Erro: {e}")
            
            # Testar segunda categoria
            time.sleep(2)
            print(f"\n[8] Testando segunda categoria (COMP)...")
            try:
                driver.execute_script("filterAgrupVeh('COMP')")
                time.sleep(3)
                html3 = driver.page_source
                articles3 = html3.count('<article')
                url3 = driver.current_url
                print(f"    Artigos COMP: {articles3}")
                print(f"    war= na URL: {'war=' in url3}")
            except Exception as e:
                print(f"    Erro: {e}")
        
        print(f"\n{'=' * 70}")
        print(f"TESTE CONCLUÍDO")
        print(f"Mantendo browser aberto 30s para inspeção visual...")
        print(f"{'=' * 70}")
        time.sleep(30)
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
