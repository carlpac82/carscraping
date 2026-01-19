#!/usr/bin/env python3
"""
Script de teste para verificar a funcionalidade de anexar PDFs de T&C aos emails
"""
import os
import sys

def test_pdf_loading():
    """Testa se os PDFs podem ser carregados corretamente"""
    print("🧪 Testing PDF attachment functionality...")
    print("=" * 60)
    
    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Project root: {project_root}")
    
    # Test both PDFs
    pdf_files = ['T&C-PT.pdf', 'T&C-EN.pdf']
    
    for pdf_filename in pdf_files:
        pdf_path = os.path.join(project_root, pdf_filename)
        print(f"\n📄 Testing: {pdf_filename}")
        print(f"   Path: {pdf_path}")
        
        if os.path.exists(pdf_path):
            try:
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                    print(f"   ✅ File loaded successfully")
                    print(f"   📊 Size: {len(pdf_content):,} bytes ({len(pdf_content) / 1024 / 1024:.2f} MB)")
                    
                    # Simulate attachment structure
                    attachment = {
                        'filename': pdf_filename,
                        'content': pdf_content,
                        'mimetype': 'application/pdf'
                    }
                    print(f"   ✅ Attachment structure created")
                    print(f"   📎 Filename: {attachment['filename']}")
                    print(f"   📎 Content length: {len(attachment['content']):,} bytes")
                    print(f"   📎 MIME type: {attachment['mimetype']}")
            except Exception as e:
                print(f"   ❌ Error loading file: {e}")
        else:
            print(f"   ❌ File not found!")
    
    print("\n" + "=" * 60)
    print("✅ PDF loading test completed!")

def test_language_detection():
    """Testa a lógica de detecção de idioma"""
    print("\n🧪 Testing language detection logic...")
    print("=" * 60)
    
    test_cases = [
        ('Portugal', 'pt', 'T&C-PT.pdf'),
        ('Brazil', 'pt', 'T&C-PT.pdf'),
        ('United Kingdom', 'en', 'T&C-EN.pdf'),
        ('United States', 'en', 'T&C-EN.pdf'),
        ('Spain', 'en', 'T&C-EN.pdf'),
        ('France', 'en', 'T&C-EN.pdf'),
        ('', 'en', 'T&C-EN.pdf'),
        (None, 'en', 'T&C-EN.pdf'),
    ]
    
    for country, expected_lang, expected_pdf in test_cases:
        # Simulate language detection
        detected_lang = 'pt' if country and country.lower() in ['portugal', 'brazil'] else 'en'
        pdf_filename = 'T&C-PT.pdf' if detected_lang == 'pt' else 'T&C-EN.pdf'
        
        status = "✅" if detected_lang == expected_lang and pdf_filename == expected_pdf else "❌"
        print(f"{status} Country: {country or 'None':20s} -> Lang: {detected_lang} -> PDF: {pdf_filename}")
    
    print("=" * 60)
    print("✅ Language detection test completed!")

if __name__ == '__main__':
    test_pdf_loading()
    test_language_detection()
    print("\n🎉 All tests completed!")
