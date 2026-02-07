#!/usr/bin/env python3
"""
Teste visual CarJet - Comparar Homepage vs Categorias
Conta carros por supplier na homepage e em cada categoria.
Verifica se todos os carros da homepage aparecem nas categorias.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os
from collections import defaultdict

# Categorias (sem CARG - carrinhas comerciais)
CATEGORIES = {
    'MINI': 'Pequeno',
    'COMP': 'Médio',
    'FAMI': 'Grande',
    'ESTA': 'Station Wagon',
    'SUVS': 'SUVs',
    'VANS': 'Minivans',
    'LUXU': 'Premium',
    'AUTO': 'Automático',
}


def setup_chrome():
    opts = Options()
    opts.add_argument('--start-maximized')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    return opts


def wait_for_cars(driver, max_wait=8):
    """Polling rápido até carros aparecerem"""
    for _ in range(max_wait):
        time.sleep(1)
        articles = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
        visible = [a for a in articles if a.is_displayed()]
        if len(visible) > 0:
            return len(visible)
    return 0


def extract_cars(driver):
    """Extrai (nome, supplier) de cada carro visível"""
    cars = []
    articles = driver.find_elements(By.CSS_SELECTOR, 'section.newcarlist article')
    for art in articles:
        try:
            if not art.is_displayed():
                continue
            name_el = art.find_elements(By.CSS_SELECTOR, 'h2, h3, .cl--title')
            name = name_el[0].text.strip() if name_el else ''
            supplier = art.get_attribute('data-prv') or '?'
            if name:
                cars.append((name.lower().strip(), supplier.strip()))
        except:
            continue
    return cars


def count_by_supplier(cars):
    """Conta carros por supplier"""
    counts = defaultdict(int)
    for _, supplier in cars:
        counts[supplier] += 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def print_supplier_table(title, supplier_counts, total):
    print(f"\n   {title} ({total} carros):")
    for sup, cnt in supplier_counts.items():
        bar = '█' * min(cnt, 40)
        print(f"      {sup:12s}: {cnt:3d} {bar}")


def test_homepage_vs_categories():
    ss_dir = 'screenshots_categories'
    os.makedirs(ss_dir, exist_ok=True)

    print("=" * 70)
    print("🚗 TESTE: HOMEPAGE vs CATEGORIAS (por supplier)")
    print("=" * 70)

    opts = setup_chrome()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        url = "https://www.carjet.com/do/list/pt?s=acc2519f-b521-4f31-b31e-3577274fd60a&b=15362c64-66d7-4cb3-84bf-9661ce12feaa"
        print(f"\n📌 Abrindo homepage de resultados...")
        driver.get(url)
        print("⏳ Aguardando carregamento...")
        time.sleep(10)
        driver.save_screenshot(f"{ss_dir}/00_homepage.png")

        # ── HOMEPAGE ──
        homepage_cars = extract_cars(driver)
        homepage_set = set(homepage_cars)  # set de (nome, supplier)
        homepage_by_supplier = count_by_supplier(homepage_cars)

        print("\n" + "=" * 70)
        print("📋 HOMEPAGE")
        print("=" * 70)
        print_supplier_table("Homepage", homepage_by_supplier, len(homepage_cars))

        # ── CATEGORIAS ──
        all_category_cars = []  # lista de (nome, supplier)
        category_data = {}     # cat_code -> lista de (nome, supplier)

        print("\n" + "=" * 70)
        print("📂 CATEGORIAS")
        print("=" * 70)

        for cat_code, cat_name in CATEGORIES.items():
            print(f"\n   🔍 {cat_name} ({cat_code})...", end=" ", flush=True)
            try:
                driver.execute_script(f"filterAgrupVeh('{cat_code}')")
                wait_for_cars(driver, max_wait=8)
                driver.save_screenshot(f"{ss_dir}/cat_{cat_code}.png")

                cars = extract_cars(driver)
                category_data[cat_code] = cars
                all_category_cars.extend(cars)

                by_sup = count_by_supplier(cars)
                suppliers_str = ", ".join(f"{s}:{c}" for s, c in list(by_sup.items())[:5])
                print(f"{len(cars)} carros ({suppliers_str})")
            except Exception as e:
                print(f"❌ {e}")
                category_data[cat_code] = []

        # ── DEDUPLICAÇÃO DAS CATEGORIAS ──
        all_cat_set = set(all_category_cars)

        # ── ANÁLISE: Homepage vs Categorias ──
        print("\n" + "=" * 70)
        print("🔍 ANÁLISE: HOMEPAGE vs CATEGORIAS")
        print("=" * 70)

        # Carros da homepage que NÃO aparecem nas categorias
        only_homepage = homepage_set - all_cat_set
        # Carros das categorias que NÃO aparecem na homepage
        only_categories = all_cat_set - homepage_set
        # Carros em ambos
        in_both = homepage_set & all_cat_set

        print(f"\n   Homepage total:     {len(homepage_set)} carros únicos")
        print(f"   Categorias total:   {len(all_cat_set)} carros únicos")
        print(f"   Em ambos:           {len(in_both)}")
        print(f"   SÓ na homepage:     {len(only_homepage)}")
        print(f"   SÓ nas categorias:  {len(only_categories)}")

        if only_homepage:
            print(f"\n   ⚠️  Carros que SÓ existem na homepage ({len(only_homepage)}):")
            for name, sup in sorted(only_homepage):
                print(f"      - {name} | {sup}")
        else:
            print(f"\n   ✅ TODOS os carros da homepage aparecem nas categorias!")
            print(f"      → Não é necessário recolher da homepage, basta as categorias.")

        if only_categories:
            print(f"\n   📦 Carros EXTRA nas categorias ({len(only_categories)}):")
            for name, sup in sorted(list(only_categories)[:20]):
                print(f"      + {name} | {sup}")
            if len(only_categories) > 20:
                print(f"      ... e mais {len(only_categories) - 20}")

        # ── RESUMO POR SUPPLIER ──
        print("\n" + "=" * 70)
        print("📊 RESUMO POR SUPPLIER")
        print("=" * 70)

        all_combined = homepage_set | all_cat_set
        combined_by_supplier = count_by_supplier(list(all_combined))
        homepage_by_sup = count_by_supplier(list(homepage_set))
        cat_by_sup = count_by_supplier(list(all_cat_set))

        print(f"\n   {'Supplier':12s} | {'Homepage':>8s} | {'Categorias':>10s} | {'Combinado':>9s} | {'Extra cat':>9s}")
        print(f"   {'─'*12} | {'─'*8} | {'─'*10} | {'─'*9} | {'─'*9}")

        all_suppliers = sorted(set(list(homepage_by_sup.keys()) + list(cat_by_sup.keys())))
        for sup in all_suppliers:
            h = homepage_by_sup.get(sup, 0)
            c = cat_by_sup.get(sup, 0)
            t = combined_by_supplier.get(sup, 0)
            extra = c - h if c > h else 0
            marker = f"+{extra}" if extra > 0 else ""
            print(f"   {sup:12s} | {h:8d} | {c:10d} | {t:9d} | {marker:>9s}")

        print(f"   {'─'*12} | {'─'*8} | {'─'*10} | {'─'*9} | {'─'*9}")
        print(f"   {'TOTAL':12s} | {len(homepage_set):8d} | {len(all_cat_set):10d} | {len(all_combined):9d} | +{len(only_categories)}")

        # ── CONCLUSÃO ──
        print("\n" + "=" * 70)
        print("� CONCLUSÃO")
        print("=" * 70)
        if len(only_homepage) == 0:
            print("   ✅ As categorias contêm TODOS os carros da homepage.")
            print("   → Podemos usar SÓ as categorias e ignorar a homepage.")
            print(f"   → Isto dá {len(only_categories)} carros EXTRA que a homepage não mostra!")
        else:
            print(f"   ⚠️  {len(only_homepage)} carros SÓ existem na homepage.")
            print("   → Precisamos da homepage + categorias para ter tudo.")

        print(f"\n   Screenshots em: {ss_dir}/")

        print("\n" + "=" * 70)
        input("👀 Pressione ENTER para fechar o navegador...")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione ENTER para fechar...")
    finally:
        driver.quit()
        print("🔒 Navegador fechado")


if __name__ == '__main__':
    test_homepage_vs_categories()
