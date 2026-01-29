#!/usr/bin/env python3
"""
Converte o Manual de Inspeções HTML para PDF usando Playwright
"""

import asyncio
from playwright.async_api import async_playwright
import os

async def convert_html_to_pdf():
    """Converte HTML para PDF usando Playwright"""
    html_path = os.path.abspath('MANUAL_INSPECOES.html')
    pdf_path = os.path.abspath('MANUAL_INSPECOES.pdf')
    
    print("=" * 60)
    print("🔄 CONVERSÃO HTML → PDF (A4) usando Playwright")
    print("=" * 60)
    print(f"📄 Arquivo HTML: {html_path}")
    print(f"📄 Arquivo PDF: {pdf_path}")
    
    async with async_playwright() as p:
        # Lançar browser
        print("\n🌐 Iniciando browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Carregar HTML
        print("📖 Carregando HTML...")
        await page.goto(f'file://{html_path}')
        
        # Aguardar carregamento completo
        await page.wait_for_load_state('networkidle')
        
        # Converter para PDF com configurações A4
        print("🖨️  Gerando PDF em formato A4...")
        await page.pdf(
            path=pdf_path,
            format='A4',
            print_background=True,
            margin={
                'top': '0mm',
                'right': '0mm',
                'bottom': '0mm',
                'left': '0mm'
            },
            prefer_css_page_size=True
        )
        
        await browser.close()
        
        # Verificar se PDF foi criado
        if os.path.exists(pdf_path):
            size_kb = os.path.getsize(pdf_path) / 1024
            print(f"\n✅ PDF criado com sucesso!")
            print(f"📊 Tamanho: {size_kb:.1f} KB")
            print(f"📍 Local: {pdf_path}")
            return True
        else:
            print("\n❌ Erro: PDF não foi criado")
            return False

def main():
    """Função principal"""
    try:
        result = asyncio.run(convert_html_to_pdf())
        if result:
            print("\n🎉 Conversão concluída com sucesso!")
        else:
            print("\n❌ Falha na conversão")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
