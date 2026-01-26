#!/usr/bin/env python3
"""Script para criar manual HTML de inspeções"""

html = open('MANUAL_INSPECOES.html', 'w', encoding='utf-8')

# Parte 1: Header e CSS
html.write("""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manual de Inspeções - Auto Prudente</title>
    <style>
        @page { size: A4; margin: 0; }
        @media print {
            .page-break { page-break-after: always; }
            body { margin: 0; }
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #009cb6 0%, #007a94 100%);
            color: white;
            padding: 50px 40px;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .header img {
            position: absolute;
            left: 40px;
            height: 70px;
        }
        .header-content { text-align: center; }
        .header h1 { font-size: 42px; font-weight: 700; margin-bottom: 10px; }
        .header p { font-size: 20px; opacity: 0.95; }
        .content { padding: 40px; max-width: 1200px; margin: 0 auto; }
        .section { margin-bottom: 40px; }
        h2 {
            color: #009cb6;
            font-size: 32px;
            margin-bottom: 25px;
            border-bottom: 4px solid #009cb6;
            padding-bottom: 12px;
        }
        h3 { color: #007a94; font-size: 24px; margin-top: 30px; margin-bottom: 15px; }
        h4 { color: #555; font-size: 20px; margin-top: 20px; margin-bottom: 10px; }
        p { margin-bottom: 15px; text-align: justify; font-size: 16px; }
        ul, ol { margin-left: 30px; margin-bottom: 20px; }
        li { margin-bottom: 10px; font-size: 16px; }
        .step {
            background: #f8f9fa;
            border-left: 5px solid #009cb6;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 0 8px 8px 0;
        }
        .step-number {
            display: inline-block;
            background: #009cb6;
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            text-align: center;
            line-height: 35px;
            font-weight: bold;
            margin-right: 12px;
            font-size: 18px;
        }
        .warning {
            background: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 18px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        .info {
            background: #d1ecf1;
            border-left: 5px solid #0dcaf0;
            padding: 18px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        .success {
            background: #d1e7dd;
            border-left: 5px solid #198754;
            padding: 18px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 16px;
        }
        th, td { border: 1px solid #ddd; padding: 14px; text-align: left; }
        th { background: #009cb6; color: white; font-weight: 600; }
        tr:nth-child(even) { background: #f8f9fa; }
        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 15px;
            margin-top: 50px;
            border-top: 3px solid #009cb6;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="static/ap-heather.png" alt="Auto Prudente">
        <div class="header-content">
            <h1>Manual de Inspeções de Veículos</h1>
            <p>Sistema Completo de Check-in e Check-out</p>
        </div>
    </div>
    
    <div class="content">
""")

# Índice
html.write("""
        <div class="section">
            <h2>📋 Índice</h2>
            <ol>
                <li>Introdução ao Sistema</li>
                <li>Terminologia</li>
                <li>Check-in (Entrega de Viatura)</li>
                <li>Check-out (Recolha de Viatura)</li>
                <li>Self-Checkout</li>
                <li>Gestão de Rental Agreements</li>
                <li>Resolução de Problemas</li>
                <li>Boas Práticas</li>
            </ol>
        </div>
        
        <div class="page-break"></div>
""")

# Seção 1: Introdução
html.write("""
        <div class="section">
            <h2>1. Introdução ao Sistema</h2>
            
            <p>O Sistema de Inspeções da Auto Prudente permite realizar inspeções completas de veículos durante a entrega e recolha, garantindo:</p>
            
            <ul>
                <li>✅ Registo fotográfico completo do veículo (9 fotos obrigatórias)</li>
                <li>✅ Documentação de danos e incidentes com croqui interativo</li>
                <li>✅ Validação de combustível e quilometragem</li>
                <li>✅ Envio automático de relatórios por email ao cliente</li>
                <li>✅ Integração automática com Rental Agreements</li>
                <li>✅ Histórico completo de inspeções permanente</li>
            </ul>
            
            <div class="info">
                <strong>💡 Nota Importante:</strong> Todas as inspeções são guardadas permanentemente na base de dados PostgreSQL com backup automático diário. Os dados NUNCA serão perdidos.
            </div>
            
            <h3>1.1. Acesso ao Sistema</h3>
            <p>Para aceder ao sistema de inspeções:</p>
            <ol>
                <li>Abrir browser e ir para <code>https://rentalprices.pt/login</code></li>
                <li>Inserir credenciais de utilizador</li>
                <li>No menu principal, clicar em "Check-out - Inspeção de Veículo"</li>
            </ol>
        </div>
""")

# Seção 2: Terminologia
html.write("""
        <div class="section">
            <h2>2. Terminologia</h2>
            
            <table>
                <tr>
                    <th>Termo</th>
                    <th>Significado</th>
                    <th>Quando Usar</th>
                </tr>
                <tr>
                    <td><strong>CHECK-IN</strong></td>
                    <td>Entrega da viatura ao cliente</td>
                    <td>Quando o cliente <strong>recebe</strong> o veículo</td>
                </tr>
                <tr>
                    <td><strong>CHECK-OUT</strong></td>
                    <td>Recolha da viatura do cliente</td>
                    <td>Quando o cliente <strong>devolve</strong> o veículo</td>
                </tr>
                <tr>
                    <td><strong>SELF-CHECKOUT</strong></td>
                    <td>Cliente faz inspeção sozinho</td>
                    <td>Via link único enviado por email</td>
                </tr>
                <tr>
                    <td><strong>RA</strong></td>
                    <td>Rental Agreement (Contrato de Aluguer)</td>
                    <td>Número do contrato (ex: 06700)</td>
                </tr>
            </table>
            
            <div class="warning">
                <strong>⚠️ Atenção:</strong> A terminologia CHECK-IN/CHECK-OUT foi invertida após desenvolvimento inicial. CHECK-IN = ENTREGA (delivery antigo), CHECK-OUT = RECOLHA (pickup antigo).
            </div>
        </div>
        
        <div class="page-break"></div>
""")

# Seção 3: Check-in
html.write("""
        <div class="section">
            <h2>3. Check-in (Entrega de Viatura)</h2>
            
            <p>O Check-in é realizado quando o cliente <strong>recebe</strong> o veículo. Este processo documenta o estado do veículo no início do aluguer.</p>
            
            <h3>3.1. Preencher Dados Iniciais</h3>
            
            <div class="step">
                <span class="step-number">1</span>
                <strong>Inserir Matrícula</strong><br>
                Digite a matrícula do veículo (ex: 30-XQ-17, AX-90-XG). O sistema irá automaticamente:
                <ul style="margin-top: 10px;">
                    <li>Validar se a matrícula existe no Gestor de Frota</li>
                    <li>Buscar o Rental Agreement mais recente (por data de check-in)</li>
                    <li>Preencher o campo RA automaticamente</li>
                    <li>Preencher o email do cliente (se disponível)</li>
                </ul>
            </div>
            
            <div class="info">
                <strong>💡 Dica:</strong> Se tiver vários contratos para a mesma matrícula, o sistema mostra automaticamente o mais recente. Para buscar um contrato mais antigo, insira manualmente o número do RA no campo correspondente.
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                <strong>Verificar Estado do Contrato</strong><br>
                O sistema verifica automaticamente e mostra pop-ups conforme o estado:
                <ul style="margin-top: 10px;">
                    <li><strong>Matrícula não existe:</strong> Pop-up "Matrícula inválida" → Adicionar veículo no Gestor de Frota primeiro</li>
                    <li><strong>Sem RA:</strong> Pop-up "Sem Rental Agreement" → Fazer upload do PDF do RA</li>
                    <li><strong>Contrato Ativo:</strong> Pop-up "Contrato Ativo" → Cliente ainda tem o veículo (bloqueia nova inspeção)</li>
                    <li><strong>Contrato Encerrado:</strong> Permite iniciar novo check-in para novo contrato</li>
                    <li><strong>Sem Inspeções:</strong> Permite fazer check-in normalmente</li>
                </ul>
            </div>
            
            <h3>3.2. Upload do Rental Agreement (PDF)</h3>
            
            <div class="step">
                <span class="step-number">3</span>
                <strong>Fazer Upload do PDF (se necessário)</strong><br>
                Se ainda não tiver feito upload do RA:
                <ol style="margin-top: 10px;">
                    <li>Clicar em "Upload Rental Agreement PDF"</li>
                    <li>Selecionar o ficheiro PDF do contrato</li>
                    <li>Aguardar processamento automático (5-10 segundos)</li>
                    <li>Sistema extrai automaticamente: matrícula, RA, email, datas, nome cliente, etc.</li>
                </ol>
            </div>
            
            <div class="success">
                <strong>✅ Sucesso:</strong> Após upload, todos os campos são preenchidos automaticamente com os dados extraídos do PDF usando OCR e AI.
            </div>
            
            <h3>3.3. Iniciar Check-in</h3>
            
            <div class="step">
                <span class="step-number">4</span>
                <strong>Clicar em "CHECK-IN (ENTREGA)"</strong><br>
                Botão <strong>vermelho</strong> no lado esquerdo. Isto inicia o processo de inspeção de entrega.
            </div>
            
            <h3>3.4. Capturar Fotos do Veículo</h3>
            
            <p>O sistema solicita <strong>9 fotos obrigatórias</strong> do veículo:</p>
            
            <table>
                <tr>
                    <th>Nº</th>
                    <th>Foto</th>
                    <th>Descrição</th>
                </tr>
                <tr>
                    <td>1</td>
                    <td>Frente</td>
                    <td>Vista frontal completa do veículo</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Frente Esquerda</td>
                    <td>Ângulo frontal esquerdo (45°)</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Esquerda</td>
                    <td>Lateral esquerda completa</td>
                </tr>
                <tr>
                    <td>4</td>
                    <td>Traseira Esquerda</td>
                    <td>Ângulo traseiro esquerdo (45°)</td>
                </tr>
                <tr>
                    <td>5</td>
                    <td>Traseira</td>
                    <td>Vista traseira completa</td>
                </tr>
                <tr>
                    <td>6</td>
                    <td>Traseira Direita</td>
                    <td>Ângulo traseiro direito (45°)</td>
                </tr>
                <tr>
                    <td>7</td>
                    <td>Direita</td>
                    <td>Lateral direita completa</td>
                </tr>
                <tr>
                    <td>8</td>
                    <td>Frente Direita</td>
                    <td>Ângulo frontal direito (45°)</td>
                </tr>
                <tr>
                    <td>9</td>
                    <td>Odómetro</td>
                    <td>Foto clara do painel com quilometragem visível</td>
                </tr>
            </table>
            
            <div class="warning">
                <strong>⚠️ Importante:</strong> Todas as 9 fotos são obrigatórias. O sistema não permite avançar sem todas as fotos. Certifique-se que as fotos estão nítidas e bem iluminadas.
            </div>
""")

print("✅ Manual HTML criado com sucesso!")
html.close()
