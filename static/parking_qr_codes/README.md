# QR Codes de Acesso aos Parques do Aeroporto

Esta pasta contém os códigos QR para acesso aos parques do Aeroporto de Faro.

## Estrutura de Ficheiros

Coloque os ficheiros PNG dos QR codes nesta pasta com os seguintes nomes:

- `parking_1.png` - QR code para o Parque 1
- `parking_2.png` - QR code para o Parque 2
- `parking_3.png` - QR code para o Parque 3
- `parking_4.png` - QR code para o Parque 4

## Formato dos Ficheiros

- **Formato:** PNG
- **Tamanho recomendado:** 500x500 pixels ou superior
- **Fundo:** Branco ou transparente
- **Qualidade:** Alta resolução para garantir leitura correta

## Como Extrair QR Codes de PDFs

Se tiver os QR codes em formato PDF, pode extraí-los usando uma das seguintes ferramentas:

### Opção 1: Adobe Acrobat / Preview (Mac)
1. Abra o PDF
2. Selecione a ferramenta de captura/screenshot
3. Capture apenas a área do QR code
4. Guarde como PNG

### Opção 2: Ferramentas Online
- [PDF to Image Converter](https://www.ilovepdf.com/pdf_to_jpg)
- [Smallpdf](https://smallpdf.com/pdf-to-jpg)

### Opção 3: Python (Automático)
```python
from pdf2image import convert_from_path
from PIL import Image

# Converter PDF para imagem
images = convert_from_path('parking_qr.pdf', dpi=300)

# Guardar primeira página como PNG
images[0].save('parking_1.png', 'PNG')
```

## Localizações dos Parques

- **Parque 1:** 37.0194, -7.9658
- **Parque 2:** 37.0189, -7.9665
- **Parque 3:** 37.0185, -7.9672
- **Parque 4:** 37.0181, -7.9679

## Notas

- Os QR codes são embedidos nos emails como imagens inline (Content-ID)
- Se um QR code não existir, o email será enviado na mesma mas sem a imagem
- Verifique os logs do servidor para confirmar se os QR codes foram anexados corretamente
