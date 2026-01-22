#!/usr/bin/env python3
"""Script para testar extração do QR code do PDF"""

import os
from pdf2image import convert_from_bytes
from PIL import Image

# Criar diretório se não existir
os.makedirs("static/parking_qr_codes", exist_ok=True)

# Ler PDF
pdf_path = "QR-CODE.pdf"
print(f"📄 Lendo PDF: {pdf_path}")
with open(pdf_path, 'rb') as f:
    pdf_bytes = f.read()

# Converter PDF para imagem
print("🔄 Convertendo PDF para imagem...")
images = convert_from_bytes(pdf_bytes, dpi=300)

if images:
    print(f"✅ PDF convertido: {len(images)} página(s)")
    
    # Primeira página
    page_image = images[0]
    print(f"📐 Tamanho da página: {page_image.size}")
    
    # Salvar página inteira
    full_page_path = "static/parking_qr_codes/full_page.png"
    page_image.save(full_page_path, 'PNG')
    print(f"✅ Página inteira salva em: {full_page_path}")
    
    # Abrir para visualização
    print(f"\n🖼️  Abrindo imagem da página completa...")
    page_image.show()
    
    print("\n" + "="*60)
    print("NOTA: Esta é a página completa do PDF.")
    print("Agora vou implementar a extração do QR code no código principal.")
    print("="*60)
else:
    print("❌ Erro ao converter PDF")
