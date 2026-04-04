import base64

# Converter logo para base64
with open('static/ap-heather.png', 'rb') as f:
    logo_base64 = base64.b64encode(f.read()).decode('utf-8')
    print("Logo base64:")
    print(logo_base64[:100] + "...")
    print("\nLogo HTML:")
    print(f'<img src="data:image/png;base64,{logo_base64}" alt="AutoPrudente" class="logo">')

print("\n" + "="*50 + "\n")

# Converter QR code para base64
with open('static/check-in.png', 'rb') as f:
    qr_base64 = base64.b64encode(f.read()).decode('utf-8')
    print("QR Code base64:")
    print(qr_base64[:100] + "...")
    print("\nQR Code HTML:")
    print(f'<img src="data:image/png;base64,{qr_base64}" alt="Check-in Online" style="width: 60px; height: 60px; display: block;">')
