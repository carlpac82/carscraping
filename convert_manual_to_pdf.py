#!/usr/bin/env python3
"""
Converte o Manual de Inspeções HTML para PDF em formato A4
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bs4 import BeautifulSoup
import subprocess
import sys

def convert_html_to_pdf_weasyprint():
    """Converte HTML para PDF usando WeasyPrint (melhor qualidade)"""
    try:
        import weasyprint
        
        html_path = 'MANUAL_INSPECOES.html'
        pdf_path = 'MANUAL_INSPECOES.pdf'
        
        print(f"📄 Convertendo {html_path} para PDF...")
        
        # Ler HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Converter para PDF
        weasyprint.HTML(string=html_content, base_url='.').write_pdf(
            pdf_path,
            stylesheets=None,
            presentational_hints=True
        )
        
        print(f"✅ PDF criado com sucesso: {pdf_path}")
        print(f"📊 Tamanho: {os.path.getsize(pdf_path) / 1024:.1f} KB")
        
        return True
        
    except ImportError:
        print("⚠️ WeasyPrint não instalado. A instalar...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
        return convert_html_to_pdf_weasyprint()
    except Exception as e:
        print(f"❌ Erro ao converter com WeasyPrint: {e}")
        return False

def convert_html_to_pdf_pdfkit():
    """Converte HTML para PDF usando pdfkit (alternativa)"""
    try:
        import pdfkit
        
        html_path = 'MANUAL_INSPECOES.html'
        pdf_path = 'MANUAL_INSPECOES.pdf'
        
        print(f"📄 Convertendo {html_path} para PDF com pdfkit...")
        
        options = {
            'page-size': 'A4',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        pdfkit.from_file(html_path, pdf_path, options=options)
        
        print(f"✅ PDF criado com sucesso: {pdf_path}")
        print(f"📊 Tamanho: {os.path.getsize(pdf_path) / 1024:.1f} KB")
        
        return True
        
    except ImportError:
        print("⚠️ pdfkit não instalado. A instalar...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfkit"])
        return convert_html_to_pdf_pdfkit()
    except Exception as e:
        print(f"❌ Erro ao converter com pdfkit: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🔄 CONVERSÃO HTML → PDF (A4)")
    print("=" * 60)
    
    # Tentar WeasyPrint primeiro (melhor qualidade)
    if convert_html_to_pdf_weasyprint():
        return
    
    # Fallback para pdfkit
    print("\n🔄 Tentando método alternativo...")
    if convert_html_to_pdf_pdfkit():
        return
    
    print("\n❌ Não foi possível converter o PDF automaticamente.")
    print("💡 Solução manual:")
    print("   1. Abrir MANUAL_INSPECOES.html no browser")
    print("   2. Ctrl+P (Imprimir)")
    print("   3. Selecionar 'Guardar como PDF'")
    print("   4. Guardar como MANUAL_INSPECOES.pdf")

if __name__ == "__main__":
    main()
