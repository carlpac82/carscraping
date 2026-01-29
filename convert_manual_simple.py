#!/usr/bin/env python3
"""
Converte o Manual de Inspeções HTML para PDF usando método simples
"""

import subprocess
import sys
import os

def convert_with_browser():
    """Usa o browser do sistema para converter HTML em PDF"""
    html_path = os.path.abspath('MANUAL_INSPECOES.html')
    pdf_path = os.path.abspath('MANUAL_INSPECOES.pdf')
    
    print("=" * 60)
    print("🔄 CONVERSÃO HTML → PDF (A4)")
    print("=" * 60)
    print(f"📄 HTML: {html_path}")
    print(f"📄 PDF: {pdf_path}")
    print()
    
    # Tentar usar Chrome/Chromium headless
    chrome_commands = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        'google-chrome',
        'chromium',
        'chromium-browser'
    ]
    
    for chrome_cmd in chrome_commands:
        if os.path.exists(chrome_cmd) or subprocess.run(['which', chrome_cmd.split('/')[-1]], 
                                                         capture_output=True).returncode == 0:
            print(f"🌐 Usando: {chrome_cmd}")
            try:
                cmd = [
                    chrome_cmd,
                    '--headless',
                    '--disable-gpu',
                    '--print-to-pdf=' + pdf_path,
                    '--print-to-pdf-no-header',
                    '--no-margins',
                    html_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if os.path.exists(pdf_path):
                    size_kb = os.path.getsize(pdf_path) / 1024
                    print(f"\n✅ PDF criado com sucesso!")
                    print(f"📊 Tamanho: {size_kb:.1f} KB")
                    print(f"📍 Local: {pdf_path}")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Erro com {chrome_cmd}: {e}")
                continue
    
    print("\n❌ Não foi possível converter automaticamente.")
    print("\n💡 INSTRUÇÕES MANUAIS:")
    print("=" * 60)
    print("1. Abrir o ficheiro no browser:")
    print(f"   open {html_path}")
    print()
    print("2. Pressionar Cmd+P (ou Ctrl+P)")
    print()
    print("3. Nas opções de impressão:")
    print("   - Destino: 'Guardar como PDF'")
    print("   - Tamanho: A4")
    print("   - Margens: Nenhuma")
    print("   - Gráficos de fundo: Ativado")
    print()
    print("4. Guardar como: MANUAL_INSPECOES.pdf")
    print("=" * 60)
    
    # Tentar abrir o HTML no browser
    try:
        subprocess.run(['open', html_path])
        print("\n✅ Ficheiro HTML aberto no browser")
        print("   Siga as instruções acima para guardar como PDF")
    except:
        pass
    
    return False

if __name__ == "__main__":
    convert_with_browser()
