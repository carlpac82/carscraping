# Sistema de Email com QR Code de Parque do Aeroporto

## 📋 Resumo da Funcionalidade

Sistema completo para enviar emails com códigos QR de acesso aos parques do Aeroporto de Faro. Inclui:

- ✅ Templates de email em 3 idiomas (PT/EN/FR)
- ✅ Botão de avião no histórico de RAs
- ✅ Modal para seleção do parque (1-4)
- ✅ Backend endpoint `/api/send-parking-qr`
- ✅ Detecção automática de idioma do cliente
- ✅ Embed de QR code como imagem inline
- ✅ Localizações Google Maps dos parques
- ✅ Informações do veículo e data/hora de recolha

## 🗂️ Ficheiros Criados/Modificados

### Templates de Email
- `templates/email_parking_qr_pt.html` - Template português
- `templates/email_parking_qr_en.html` - Template inglês
- `templates/email_parking_qr_fr.html` - Template francês

### UI
- `templates/inspection_history.html` - Adicionado botão de avião e modal

### Backend
- `main.py` - Endpoint `/api/send-parking-qr` (linhas 31366-31565)

### Documentação
- `preview_parking_email.html` - Preview do email
- `static/parking_qr_codes/README.md` - Instruções para QR codes

## 🎯 Como Usar

### 1. Adicionar QR Codes

Coloque os ficheiros PNG dos QR codes em:
```
static/parking_qr_codes/
├── parking_1.png
├── parking_2.png
├── parking_3.png
└── parking_4.png
```

**Formato recomendado:** PNG, 500x500px ou superior, fundo branco

### 2. Enviar Email via UI

1. Aceda ao histórico de RAs
2. Clique no botão do avião (✈️) ao lado do email
3. Selecione o número do parque (1-4)
4. Confirme o envio

### 3. Enviar Email via API

```bash
curl -X POST http://localhost:8000/api/send-parking-qr \
  -H "Content-Type: application/json" \
  -d '{
    "ra_number": "06727-09",
    "parking_number": 4
  }'
```

## 📧 Variáveis do Template

Os templates suportam as seguintes variáveis:

- `{{CLIENT_NAME}}` - Nome do cliente
- `{{RA_NUMBER}}` - Número do RA
- `{{PARKING_NUMBER}}` - Número do parque (1-4)
- `{{LICENSE_PLATE}}` - Matrícula do veículo
- `{{VEHICLE_BRAND}}` - Marca do veículo
- `{{VEHICLE_MODEL}}` - Modelo do veículo
- `{{PICKUP_DATE}}` - Data de recolha (formato DD/MM/YYYY)
- `{{PICKUP_TIME}}` - Hora de recolha (formato HH:MM)
- `{{PARKING_LOCATION_NAME}}` - Nome do parque
- `{{PARKING_GOOGLE_MAPS_LINK}}` - Link Google Maps

## 🌍 Localizações dos Parques

| Parque | Coordenadas | Google Maps |
|--------|-------------|-------------|
| Parque 1 | 37.0194, -7.9658 | [Ver no mapa](https://maps.google.com/?q=37.0194,-7.9658) |
| Parque 2 | 37.0189, -7.9665 | [Ver no mapa](https://maps.google.com/?q=37.0189,-7.9665) |
| Parque 3 | 37.0185, -7.9672 | [Ver no mapa](https://maps.google.com/?q=37.0185,-7.9672) |
| Parque 4 | 37.0181, -7.9679 | [Ver no mapa](https://maps.google.com/?q=37.0181,-7.9679) |

## 🔧 Detecção de Idioma

O sistema deteta automaticamente o idioma baseado no país do cliente:

- **Portugal** → Português
- **United Kingdom, Ireland, USA, Canada, Australia** → Inglês
- **France, Belgium, Switzerland, Luxembourg, Monaco** → Francês
- **Default** → Português

## 📝 Conteúdo do Email

### Secções Incluídas

1. **Header** - Logo Auto Prudente + Número RA
2. **Saudação** - Personalizada com nome do cliente
3. **Detalhes do Veículo** - Matrícula, marca/modelo, data/hora recolha
4. **QR Code** - Imagem embutida com link Google Maps
5. **Instruções de Utilização** - 3 passos claros
   - Entrada no parque
   - Ticket de estacionamento
   - Entrega da chave
6. **Notas Importantes** - Avisos sobre uso único e confirmação
7. **Contactos Úteis** - Escritório, assistência, email
8. **Footer** - Informações legais da empresa

## 🔐 Configuração SMTP

Certifique-se de que as seguintes variáveis estão configuradas no `main.py`:

```python
SMTP_SERVER = "seu-servidor-smtp.com"
SMTP_PORT = 587
SMTP_USERNAME = "seu-email@dominio.com"
SMTP_PASSWORD = "sua-senha"
SMTP_FROM_EMAIL = "noreply@auto-prudente.com"
```

## 📊 Logs e Debugging

O sistema gera logs detalhados:

```
✅ QR code image attached from static/parking_qr_codes/parking_4.png
✅ Parking QR email sent to cliente@email.com for RA 06727-09, Parking #4
⚠️ QR code image not found at static/parking_qr_codes/parking_4.png
```

## 🧪 Testar o Sistema

1. **Preview do Email:**
   - Abra `preview_parking_email.html` no browser

2. **Teste Local:**
   ```bash
   # Certifique-se de que o servidor está a correr
   python main.py
   
   # Envie um email de teste
   curl -X POST http://localhost:8000/api/send-parking-qr \
     -H "Content-Type: application/json" \
     -d '{"ra_number": "06727-09", "parking_number": 1}'
   ```

## ⚠️ Notas Importantes

- Se o QR code não existir, o email é enviado na mesma mas sem a imagem
- O sistema valida que o número do parque está entre 1-4
- O email do cliente é extraído dos dados do RA
- A data/hora de recolha vem do campo `data_recolha` do RA
- Os templates usam inline CSS para compatibilidade com clientes de email

## 🚀 Próximos Passos (Opcional)

- [ ] Implementar upload de QR codes via interface admin
- [ ] Adicionar histórico de emails enviados
- [ ] Criar relatório de QR codes utilizados
- [ ] Integrar com sistema de geração automática de QR codes
- [ ] Adicionar notificações de confirmação de leitura

---

**Desenvolvido para Auto Prudente Rent a Car**  
Sistema completo e pronto para produção ✅
