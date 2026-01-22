#!/usr/bin/env python3
"""
Script para testar envio de email diretamente
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_email():
    """Testar envio de email simples"""
    
    # Configurações de email
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL', smtp_user)
    
    print("="*60)
    print("  TESTE DE ENVIO DE EMAIL")
    print("="*60)
    print(f"\n📧 Configurações:")
    print(f"   SMTP Server: {smtp_server}")
    print(f"   SMTP Port: {smtp_port}")
    print(f"   SMTP User: {smtp_user}")
    print(f"   From Email: {from_email}")
    print(f"   To Email: carlpac82@hotmail.com")
    
    if not smtp_user or not smtp_password:
        print("\n❌ ERRO: SMTP_USER ou SMTP_PASSWORD não configurados no .env")
        return False
    
    try:
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Teste de Email - Auto Prudente'
        msg['From'] = from_email
        msg['To'] = 'carlpac82@hotmail.com'
        
        # Corpo do email
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #009cb6;">Teste de Email - Auto Prudente</h2>
            <p>Este é um email de teste para verificar se o sistema de envio está a funcionar corretamente.</p>
            <p>Se recebeu este email, significa que o sistema de envio está operacional.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Auto Prudente - Sistema de Inspeções</p>
        </body>
        </html>
        """
        
        part = MIMEText(html, 'html')
        msg.attach(part)
        
        # Enviar email
        print(f"\n📤 Enviando email...")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Email enviado com sucesso!")
        print(f"\n💡 Verifique a caixa de entrada (e spam) de: carlpac82@hotmail.com")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao enviar email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_email()
    print("\n" + "="*60)
