"""
Teste visual de scraping CarJet - anti-detecção melhorada.
Compara versão ANTIGA vs NOVA para ver se reduz war=28.

Uso: python3 test_scrape_visual.py
"""
import sys
import time
import os
import random
import platform
from datetime import datetime, timedelta


def _human_delay(min_s=0.5, max_s=1.5):
    """Pausa aleatória que simula comportamento humano"""
    time.sleep(random.uniform(min_s, max_s))


def _type_human(element, text):
    """Digitar texto letra a letra com velocidade humana variável"""
    for i, char in enumerate(text):
        element.send_keys(char)
        # Velocidade variável: mais rápido no meio, mais lento no início/fim
        if i < 2 or i > len(text) - 2:
            time.sleep(random.uniform(0.18, 0.40))
        else:
            time.sleep(random.uniform(0.08, 0.22))


def _set_date_with_events(driver, field_id, value):
    """Preencher campo de data disparando eventos nativos (focus, input, change, blur)"""
    driver.execute_script("""
        const el = document.querySelector('#' + arguments[0]);
        if (!el) return;
        el.focus();
        el.dispatchEvent(new Event('focus', {bubbles:true}));
        
        // Simular setter nativo
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        nativeInputValueSetter.call(el, arguments[1]);
        
        el.dispatchEvent(new Event('input', {bubbles:true}));
        el.dispatchEvent(new Event('change', {bubbles:true}));
        el.dispatchEvent(new Event('blur', {bubbles:true}));
    """, field_id, value)


def _simulate_human_browsing(driver):
    """Simular comportamento humano: scroll, pausa, olhar a página"""
    # Scroll suave para baixo e para cima
    driver.execute_script("""
        window.scrollTo({top: 200, behavior: 'smooth'});
    """)
    time.sleep(random.uniform(0.8, 1.5))
    driver.execute_script("""
        window.scrollTo({top: 0, behavior: 'smooth'});
    """)
    time.sleep(random.uniform(0.5, 1.0))


def main():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        from selenium_stealth import stealth
        HAS_STEALTH = True
    except ImportError:
        HAS_STEALTH = False
        print("⚠️  selenium_stealth não instalado, continuando sem stealth")

    # UA actualizado: iOS 18.2 (2025)
    iphone_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1"

    chrome_options = Options()
    print(f"🖥️  Modo VISUAL ({platform.system()})")
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'user-agent={iphone_ua}')
    chrome_options.add_argument('--window-size=390,844')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Mobile emulation
    mobile_emulation = {
        "deviceMetrics": {"width": 390, "height": 844, "pixelRatio": 3.0},
        "userAgent": iphone_ua
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    if platform.system() == 'Darwin':
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            chrome_options.binary_location = chrome_path

    print("🚀 Iniciando Chrome...")
    driver = webdriver.Chrome(options=chrome_options)
    
    if HAS_STEALTH:
        stealth(driver,
            languages=["pt-PT", "pt", "en"],
            vendor="Apple Computer, Inc.",
            platform="iPhone",
            webgl_vendor="Apple Inc.",
            renderer="Apple GPU",
            fix_hairline=True,
        )
    
    # Esconder webdriver properties via JS
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
    
    driver.set_page_load_timeout(30)
    print("✅ Chrome iniciado!")
    
    try:
        # Datas: daqui a 2 meses, 3 dias de aluguer
        start_dt = datetime.now() + timedelta(days=60)
        end_dt = start_dt + timedelta(days=3)
        
        # 1. Homepage
        url = "https://www.carjet.com/aluguel-carros/index.htm"
        print(f"\n📄 Abrindo: {url}")
        driver.get(url)
        _human_delay(2.5, 4.0)
        
        print(f"   URL actual: {driver.current_url}")
        print(f"   Título: {driver.title}")
        
        # Rejeitar cookies
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
        _human_delay(1.0, 2.0)
        
        # Simular que o user olha a página antes de preencher
        print(f"\n👀 Simulando browsing humano...")
        _simulate_human_browsing(driver)
        
        # 2. Preencher local - digitação humana
        search_text = "Faro"
        print(f"\n📍 Escrevendo local: '{search_text}' (letra a letra)")
        try:
            pickup = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "pickup"))
            )
            pickup.click()
            _human_delay(0.3, 0.7)
            pickup.clear()
            _human_delay(0.2, 0.5)
            
            # Digitar letra a letra
            _type_human(pickup, search_text)
            
            print(f"   Texto digitado. Aguardando dropdown...")
            _human_delay(2.0, 3.0)
            
            # Verificar dropdown
            dropdown_count = driver.execute_script("""
                const items = document.querySelectorAll('#recogida_lista li');
                return items.length;
            """)
            print(f"   Dropdown items: {dropdown_count}")
            
            if dropdown_count > 0:
                options = driver.execute_script("""
                    const items = document.querySelectorAll('#recogida_lista li');
                    return Array.from(items).map(li => li.textContent.trim()).slice(0, 5);
                """)
                print(f"   Opções: {options}")
                
                _human_delay(0.5, 1.0)  # Pausa antes de clicar (humano lê as opções)
                
                clicked = driver.execute_script("""
                    const items = document.querySelectorAll('#recogida_lista li');
                    for (let li of items) {
                        const text = li.textContent.toLowerCase();
                        if (text.includes('faro') && text.includes('aeroporto')) {
                            const link = li.querySelector('a');
                            if (link) { link.click(); return 'clicked: ' + li.textContent.trim().substring(0,40); }
                            li.click();
                            return 'clicked: ' + li.textContent.trim().substring(0,40);
                        }
                    }
                    if (items.length > 0) {
                        const link = items[0].querySelector('a');
                        if (link) link.click(); else items[0].click();
                        return 'clicked_first: ' + items[0].textContent.trim().substring(0,40);
                    }
                    return 'no_items';
                """)
                print(f"   ✅ {clicked}")
            else:
                print(f"   ⚠️ Dropdown vazio!")
            
            _human_delay(0.8, 1.5)
            
            # Clicar fora
            try:
                driver.find_element(By.CSS_SELECTOR, "h1, h2, .title, header").click()
            except:
                pass
            _human_delay(0.5, 1.0)
            
        except Exception as e:
            print(f"   ❌ Erro no local: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Preencher datas com eventos nativos
        fecha_rec = start_dt.strftime("%d/%m/%Y")
        fecha_dev = end_dt.strftime("%d/%m/%Y")
        print(f"\n📅 Datas: {fecha_rec} → {fecha_dev}")
        
        _set_date_with_events(driver, 'fechaRecogida', fecha_rec)
        _human_delay(0.3, 0.6)
        _set_date_with_events(driver, 'fechaDevolucion', fecha_dev)
        _human_delay(0.3, 0.6)
        
        # Horas com eventos
        driver.execute_script("""
            const h1 = document.querySelector('#fechaRecogidaSelHour');
            const h2 = document.querySelector('#fechaDevolucionSelHour');
            if (h1) { 
                h1.focus();
                h1.value = '15:00'; 
                h1.dispatchEvent(new Event('input', {bubbles:true}));
                h1.dispatchEvent(new Event('change', {bubbles:true})); 
                h1.blur();
            }
            if (h2) { 
                h2.focus();
                h2.value = '15:00'; 
                h2.dispatchEvent(new Event('input', {bubbles:true}));
                h2.dispatchEvent(new Event('change', {bubbles:true})); 
                h2.blur();
            }
        """)
        _human_delay(0.8, 1.5)
        
        # Pequeno scroll antes de submeter (humano vê o botão)
        driver.execute_script("window.scrollTo({top: 100, behavior: 'smooth'});")
        _human_delay(0.5, 1.0)
        
        # 4. Submit com retry
        max_attempts = 5
        success = False
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n🔍 Clicando pesquisar (tentativa {attempt}/{max_attempts})...")
            
            driver.execute_script("""
                const btn = document.querySelector('#btnBuscar');
                if (btn) btn.click();
                else {
                    const form = document.querySelector('#frm_search_cars') || document.querySelector('form');
                    if (form) form.submit();
                }
            """)
            
            for i in range(15):
                time.sleep(2)
                url = driver.current_url
                
                if 'war=' in url:
                    wait = random.uniform(4, 8)
                    print(f"   ❌ war=28 após {i*2}s → pausa {wait:.1f}s e retry...")
                    time.sleep(wait)
                    break
                
                if '/do/list/' in url and 's=' in url and 'b=' in url:
                    print(f"   ✅ RESULTADOS PRONTOS após {i*2}s!")
                    time.sleep(3)
                    count = driver.execute_script("return document.querySelectorAll('article').length") or 0
                    print(f"   📊 Artigos encontrados: {count}")
                    
                    first_price = driver.execute_script("""
                        const el = document.querySelector('.price.pr-euros');
                        return el ? el.textContent.trim() : 'N/A';
                    """)
                    print(f"   💰 Primeiro preço: {first_price}")
                    success = True
                    break
            else:
                print(f"   ⏰ Timeout após 30s")
            
            if success:
                break
        
        if success:
            print(f"\n🎉 SUCESSO! Tentativa {attempt} de {max_attempts}")
        else:
            print(f"\n❌ Todas as {max_attempts} tentativas falharam.")
        
        print(f"\n👀 Chrome aberto para inspeção. Prima ENTER para fechar...")
        input()
        
    finally:
        driver.quit()
        print("🧹 Chrome fechado.")

if __name__ == "__main__":
    main()
