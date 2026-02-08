#!/usr/bin/env python3
"""
Teste: Selenium - clicar em Minivans SEM filtro Automático
1. Abrir CarJet
2. Limpar filtro Automático se existir
3. Clicar em Minivans
4. Contar todos os carros (manuais + automáticos)
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

SESSION_URL = "https://www.carjet.com/do/list/pt?s=ab62cb74-e360-4119-8236-dc822802cb23&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"

def main():
    opts = Options()
    opts.add_argument('--start-maximized')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("📌 Abrindo CarJet...")
        driver.get(SESSION_URL)
        time.sleep(10)
        
        # 1. Ver filtros activos
        print("\n🔍 Verificando filtros activos...")
        html = driver.page_source
        
        # Procurar "Limpar tudo" ou filtros activos
        filter_els = driver.find_elements(By.CSS_SELECTOR, '.filtros-activos, .filter-active, [class*="filter"]')
        for f in filter_els[:5]:
            print(f"   Filtro: {f.text[:100]}")
        
        # 2. Verificar se filtro Automático está activo
        auto_filter = driver.find_elements(By.XPATH, "//*[contains(text(), 'Automático')]")
        print(f"\n   Elementos com 'Automático': {len(auto_filter)}")
        for af in auto_filter[:5]:
            print(f"      {af.tag_name}: {af.text[:80]}")
        
        # 3. Tentar limpar filtros - clicar "Limpar tudo"
        print("\n🧹 Tentando limpar filtros...")
        try:
            limpar = driver.find_elements(By.XPATH, "//a[contains(text(), 'Limpar tudo')] | //span[contains(text(), 'Limpar tudo')] | //button[contains(text(), 'Limpar')]")
            if limpar:
                print(f"   Encontrado 'Limpar tudo' - clicando...")
                limpar[0].click()
                time.sleep(5)
            else:
                # Tentar via JavaScript
                print("   Tentando limpar via JS...")
                driver.execute_script("""
                    // Limpar filtro de transmissão
                    if (typeof filterTransmision === 'function') {
                        filterTransmision('');
                    }
                    // Limpar campo frmTrans se existir
                    var frmTrans = document.getElementById('frmTrans');
                    if (frmTrans) frmTrans.value = '';
                    var frmTransmision = document.getElementById('frmTransmision');
                    if (frmTransmision) frmTransmision.value = '';
                """)
                time.sleep(3)
        except Exception as e:
            print(f"   Erro ao limpar: {e}")
        
        # 4. Contar carros na homepage (sem filtros)
        articles = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
        visible = [a for a in articles if a.is_displayed()]
        print(f"\n📋 Homepage (após limpar filtros): {len(visible)} carros visíveis")
        
        # 5. Agora clicar em Minivans
        print("\n🚐 Clicando em Minivans...")
        driver.execute_script("filterAgrupVeh('VANS')")
        time.sleep(5)
        
        articles_vans = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
        visible_vans = [a for a in articles_vans if a.is_displayed()]
        print(f"   Minivans: {len(visible_vans)} carros visíveis")
        
        # 6. Listar todos os carros
        print(f"\n   Todos os carros nas Minivans:")
        for art in visible_vans:
            try:
                name_el = art.find_elements(By.CSS_SELECTOR, 'h2, h3, .cl--title')
                name = name_el[0].text.strip() if name_el else '?'
                supplier = art.get_attribute('data-prv') or '?'
                
                # Transmissão
                trans_els = art.find_elements(By.XPATH, ".//li[contains(text(), 'Automático') or contains(text(), 'Manual')]")
                trans = trans_els[0].text.strip() if trans_els else '?'
                
                price_els = art.find_elements(By.CSS_SELECTOR, '.price.pr-euros')
                price = '?'
                for p in price_els:
                    txt = p.text.strip()
                    if txt and '€' in txt:
                        price = txt
                        break
                
                print(f"      {name:40s} | {supplier:8s} | {price:>12s} | {trans}")
            except:
                continue
        
        # 7. Verificar formulário - que campos existem
        print(f"\n🔧 Campos do formulário CarJet:")
        form_fields = driver.execute_script("""
            var fields = {};
            var inputs = document.querySelectorAll('input[type="hidden"], select');
            for (var i = 0; i < inputs.length; i++) {
                var name = inputs[i].name || inputs[i].id;
                if (name && name.startsWith('frm')) {
                    fields[name] = inputs[i].value;
                }
            }
            return fields;
        """)
        for name, value in sorted(form_fields.items()):
            if value:
                print(f"      {name:30s} = {value}")
            else:
                print(f"      {name:30s} = (vazio)")
        
        input("\n👀 Pressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
