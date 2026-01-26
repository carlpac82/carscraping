#!/usr/bin/env python3
"""
Gerador de Manual PDF - Sistema de Inspeções Auto Prudente
"""

from weasyprint import HTML, CSS
from pathlib import Path

# HTML do manual
html_content = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>Manual de Inspeções - Auto Prudente</title>
    <style>
        @page {
            size: A4;
            margin: 0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #009cb6 0%, #007a94 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
        }
        
        .header img {
            position: absolute;
            left: 40px;
            top: 50%;
            transform: translateY(-50%);
            height: 60px;
        }
        
        .header h1 {
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 18px;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
            page-break-inside: avoid;
        }
        
        h2 {
            color: #009cb6;
            font-size: 28px;
            margin-bottom: 20px;
            border-bottom: 3px solid #009cb6;
            padding-bottom: 10px;
        }
        
        h3 {
            color: #007a94;
            font-size: 22px;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        
        h4 {
            color: #555;
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        
        p {
            margin-bottom: 15px;
            text-align: justify;
        }
        
        ul, ol {
            margin-left: 30px;
            margin-bottom: 20px;
        }
        
        li {
            margin-bottom: 10px;
        }
        
        .step {
            background: #f8f9fa;
            border-left: 4px solid #009cb6;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 0 8px 8px 0;
        }
        
        .step-number {
            display: inline-block;
            background: #009cb6;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        
        .info {
            background: #d1ecf1;
            border-left: 4px solid #0dcaf0;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        
        .success {
            background: #d1e7dd;
            border-left: 4px solid #198754;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background: #009cb6;
            color: white;
            font-weight: 600;
        }
        
        tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 40px;
        }
        
        .page-break {
            page-break-after: always;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="static/ap-heather.png" alt="Auto Prudente">
        <h1>Manual de Inspeções de Veículos</h1>
        <p>Sistema Completo de Check-in e Check-out</p>
    </div>
    
    <div class="content">
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
            </ol>
        </div>
        
        <div class="page-break"></div>
        
        <div class="section">
            <h2>1. Introdução ao Sistema</h2>
            
            <p>O Sistema de Inspeções da Auto Prudente permite realizar inspeções completas de veículos durante a entrega e recolha, garantindo:</p>
            
            <ul>
                <li>✅ Registo fotográfico completo do veículo</li>
                <li>✅ Documentação de danos e incidentes</li>
                <li>✅ Validação de combustível e quilometragem</li>
                <li>✅ Envio automático de relatórios por email</li>
                <li>✅ Integração com Rental Agreements</li>
                <li>✅ Histórico completo de inspeções</li>
            </ul>
            
            <div class="info">
                <strong>💡 Nota Importante:</strong> Todas as inspeções são guardadas permanentemente na base de dados e nunca serão perdidas. O sistema faz backup automático diário.
            </div>
        </div>
        
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
                    <td>Quando o cliente recebe o veículo</td>
                </tr>
                <tr>
                    <td><strong>CHECK-OUT</strong></td>
                    <td>Recolha da viatura do cliente</td>
                    <td>Quando o cliente devolve o veículo</td>
                </tr>
                <tr>
                    <td><strong>SELF-CHECKOUT</strong></td>
                    <td>Cliente faz inspeção sozinho</td>
                    <td>Via link enviado por email</td>
                </tr>
                <tr>
                    <td><strong>RA</strong></td>
                    <td>Rental Agreement (Contrato)</td>
                    <td>Número do contrato de aluguer</td>
                </tr>
            </table>
            
            <div class="warning">
                <strong>⚠️ Atenção:</strong> A terminologia CHECK-IN/CHECK-OUT é oposta à terminologia antiga. CHECK-IN = ENTREGA (delivery), CHECK-OUT = RECOLHA (pickup).
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <div class="section">
            <h2>3. Check-in (Entrega de Viatura)</h2>
            
            <p>O Check-in é realizado quando o cliente <strong>recebe</strong> o veículo. Este processo documenta o estado do veículo no início do aluguer.</p>
            
            <h3>3.1. Aceder à Página de Inspeções</h3>
            
            <div class="step">
                <span class="step-number">1</span>
                <strong>Fazer login no sistema</strong><br>
                Aceder a <code>https://rentalprices.pt/login</code> com as suas credenciais.
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                <strong>Navegar para Inspeções</strong><br>
                No menu principal, clicar em "Check-out - Inspeção de Veículo" (apesar do nome, esta página serve para ambos os tipos de inspeção).
            </div>
            
            <h3>3.2. Preencher Dados Iniciais</h3>
            
            <div class="step">
                <span class="step-number">3</span>
                <strong>Inserir Matrícula</strong><br>
                Digite a matrícula do veículo (ex: 30-XQ-17). O sistema irá:
                <ul>
                    <li>Validar se a matrícula existe no Gestor de Frota</li>
                    <li>Buscar automaticamente o Rental Agreement mais recente</li>
                    <li>Preencher o campo RA automaticamente</li>
                    <li>Preencher o email do cliente (se disponível)</li>
                </ul>
            </div>
            
            <div class="info">
                <strong>💡 Dica:</strong> Se tiver vários contratos para a mesma matrícula, o sistema mostra automaticamente o mais recente (por data de check-in). Para buscar um contrato mais antigo, insira manualmente o número do RA.
            </div>
            
            <div class="step">
                <span class="step-number">4</span>
                <strong>Verificar Estado do Contrato</strong><br>
                O sistema verifica automaticamente:
                <ul>
                    <li><strong>Sem RA:</strong> Pop-up a avisar que precisa fazer upload do RA primeiro</li>
                    <li><strong>Contrato Ativo:</strong> Pop-up a avisar que o contrato ainda não foi encerrado (bloqueia inspeção)</li>
                    <li><strong>Contrato Encerrado:</strong> Permite iniciar novo check-in</li>
                    <li><strong>Sem Inspeções:</strong> Permite fazer check-in</li>
                </ul>
            </div>
            
            <h3>3.3. Upload do Rental Agreement (PDF)</h3>
            
            <div class="step">
                <span class="step-number">5</span>
                <strong>Fazer Upload do PDF</strong><br>
                Se ainda não tiver feito upload do RA:
                <ol>
                    <li>Clicar em "Upload Rental Agreement PDF"</li>
                    <li>Selecionar o ficheiro PDF do contrato</li>
                    <li>Aguardar processamento automático</li>
                    <li>Sistema extrai automaticamente: matrícula, RA, email, datas, etc.</li>
                </ol>
            </div>
            
            <div class="success">
                <strong>✅ Sucesso:</strong> Após upload, todos os campos são preenchidos automaticamente com os dados extraídos do PDF.
            </div>
            
            <h3>3.4. Iniciar Check-in</h3>
            
            <div class="step">
                <span class="step-number">6</span>
                <strong>Clicar em "CHECK-IN (ENTREGA)"</strong><br>
                Botão vermelho no lado esquerdo. Isto inicia o processo de inspeção de entrega.
            </div>
            
            <h3>3.5. Capturar Fotos do Veículo</h3>
            
            <p>O sistema solicita 9 fotos obrigatórias:</p>
            
            <table>
                <tr>
                    <th>Foto</th>
                    <th>Descrição</th>
                </tr>
                <tr>
                    <td>Frente</td>
                    <td>Vista frontal completa do veículo</td>
                </tr>
                <tr>
                    <td>Frente Esquerda</td>
                    <td>Ângulo frontal esquerdo (45°)</td>
                </tr>
                <tr>
                    <td>Esquerda</td>
                    <td>Lateral esquerda completa</td>
                </tr>
                <tr>
                    <td>Traseira Esquerda</td>
                    <td>Ângulo traseiro esquerdo (45°)</td>
                </tr>
                <tr>
                    <td>Traseira</td>
                    <td>Vista traseira completa</td>
                </tr>
                <tr>
                    <td>Traseira Direita</td>
                    <td>Ângulo traseiro direito (45°)</td>
                </tr>
                <tr>
                    <td>Direita</td>
                    <td>Lateral direita completa</td>
                </tr>
                <tr>
                    <td>Frente Direita</td>
                    <td>Ângulo frontal direito (45°)</td>
                </tr>
                <tr>
                    <td>Odómetro</td>
                    <td>Foto clara do painel com quilometragem</td>
                </tr>
            </table>
            
            <div class="warning">
                <strong>⚠️ Importante:</strong> Todas as 9 fotos são obrigatórias. O sistema não permite avançar sem todas as fotos.
            </div>
            
            <h3>3.6. Preencher Dados da Inspeção</h3>
            
            <div class="step">
                <span class="step-number">7</span>
                <strong>Inserir Quilometragem</strong><br>
                Digite a quilometragem atual do veículo (deve corresponder à foto do odómetro).
            </div>
            
            <div class="step">
                <span class="step-number">8</span>
                <strong>Selecionar Nível de Combustível</strong><br>
                Escolher entre: Vazio (E), 1/4, 1/2, 3/4, Cheio (F)
            </div>
            
            <div class="step">
                <span class="step-number">9</span>
                <strong>Adicionar Observações (Opcional)</strong><br>
                Campo de texto livre para notas adicionais sobre o veículo.
            </div>
            
            <h3>3.7. Marcar Danos (Se Existirem)</h3>
            
            <div class="step">
                <span class="step-number">10</span>
                <strong>Usar o Croqui Interativo</strong><br>
                <ol>
                    <li>Clicar na imagem do veículo onde existe o dano</li>
                    <li>Selecionar tipo de dano (risco, amolgadela, etc.)</li>
                    <li>Adicionar descrição do dano</li>
                    <li>Repetir para todos os danos</li>
                </ol>
            </div>
            
            <div class="info">
                <strong>💡 Nota:</strong> No check-in (entrega), normalmente não há danos a reportar, pois o veículo está em bom estado. Os danos são mais comuns no check-out (recolha).
            </div>
            
            <h3>3.8. Finalizar Check-in</h3>
            
            <div class="step">
                <span class="step-number">11</span>
                <strong>Clicar em "Finalizar Inspeção"</strong><br>
                O sistema irá:
                <ul>
                    <li>Guardar todas as fotos e dados na base de dados</li>
                    <li>Gerar relatório PDF</li>
                    <li>Enviar email ao cliente com o relatório</li>
                    <li>Atualizar estado do contrato</li>
                </ul>
            </div>
            
            <div class="success">
                <strong>✅ Check-in Concluído!</strong> O cliente recebeu o veículo e o relatório foi enviado por email.
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <div class="section">
            <h2>4. Check-out (Recolha de Viatura)</h2>
            
            <p>O Check-out é realizado quando o cliente <strong>devolve</strong> o veículo. Este processo documenta o estado do veículo no fim do aluguer e valida incidentes.</p>
            
            <h3>4.1. Diferenças entre Check-in e Check-out</h3>
            
            <table>
                <tr>
                    <th>Aspeto</th>
                    <th>Check-in (Entrega)</th>
                    <th>Check-out (Recolha)</th>
                </tr>
                <tr>
                    <td>Quando</td>
                    <td>Cliente recebe veículo</td>
                    <td>Cliente devolve veículo</td>
                </tr>
                <tr>
                    <td>Danos</td>
                    <td>Normalmente nenhum</td>
                    <td>Possíveis danos a reportar</td>
                </tr>
                <tr>
                    <td>Combustível</td>
                    <td>Geralmente cheio</td>
                    <td>Validar se está cheio</td>
                </tr>
                <tr>
                    <td>Email</td>
                    <td>Sem alertas</td>
                    <td>Com alertas de incidentes</td>
                </tr>
                <tr>
                    <td>Botão</td>
                    <td>Vermelho (esquerda)</td>
                    <td>Azul (direita)</td>
                </tr>
            </table>
            
            <h3>4.2. Processo de Check-out</h3>
            
            <p>O processo é semelhante ao check-in, mas com validações adicionais:</p>
            
            <div class="step">
                <span class="step-number">1</span>
                <strong>Inserir Matrícula e RA</strong><br>
                Igual ao check-in. Sistema valida se já existe check-in para este contrato.
            </div>
            
            <div class="warning">
                <strong>⚠️ Regra Importante:</strong> Não é possível fazer check-out sem ter feito check-in primeiro. O sistema bloqueia automaticamente.
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                <strong>Clicar em "CHECK-OUT (RECOLHA)"</strong><br>
                Botão azul no lado direito. Só fica ativo se já existir check-in.
            </div>
            
            <div class="step">
                <span class="step-number">3</span>
                <strong>Capturar as 9 Fotos</strong><br>
                Mesmas fotos que no check-in (frente, laterais, traseira, odómetro).
            </div>
            
            <div class="step">
                <span class="step-number">4</span>
                <strong>Validar Combustível</strong><br>
                <ul>
                    <li>Se combustível não estiver cheio → <strong>INCIDENTE</strong></li>
                    <li>Sistema calcula automaticamente o custo de reabastecimento</li>
                    <li>Alerta incluído no email ao cliente</li>
                </ul>
            </div>
            
            <div class="step">
                <span class="step-number">5</span>
                <strong>Marcar Danos Novos</strong><br>
                <ul>
                    <li>Usar croqui interativo para marcar danos</li>
                    <li>Sistema compara com check-in para identificar danos novos</li>
                    <li>Danos novos → <strong>INCIDENTE</strong></li>
                </ul>
            </div>
            
            <div class="step">
                <span class="step-number">6</span>
                <strong>Finalizar Check-out</strong><br>
                Sistema envia email com:
                <ul>
                    <li>Relatório completo de recolha</li>
                    <li>Alertas de incidentes (se existirem)</li>
                    <li>Comparação com check-in</li>
                    <li>Custos adicionais (se aplicável)</li>
                </ul>
            </div>
            
            <div class="success">
                <strong>✅ Check-out Concluído!</strong> O contrato está encerrado e o veículo foi devolvido.
            </div>
        </div>
        
        <div class="page-break"></div>
        
        <div class="section">
            <h2>5. Self-Checkout</h2>
            
            <p>O Self-Checkout permite que o cliente faça a inspeção de recolha sozinho, sem necessidade de um colaborador presente.</p>
            
            <h3>5.1. Como Funciona</h3>
            
            <div class="step">
                <span class="step-number">1</span>
                <strong>Gerar Link de Self-Checkout</strong><br>
                <ol>
                    <li>Aceder à página de inspeções</li>
                    <li>Inserir matrícula e RA</li>
                    <li>Clicar em "Gerar Link Self-Checkout"</li>
                    <li>Sistema envia email ao cliente com link único</li>
                </ol>
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                <strong>Cliente Acede ao Link</strong><br>
                <ul>
                    <li>Link é único e só pode ser usado uma vez</li>
                    <li>Válido por 7 dias</li>
                    <li>Interface simplificada e mobile-friendly</li>
                    <li>Disponível em PT, EN, FR</li>
                </ul>
            </div>
            
            <div class="step">
                <span class="step-number">3</span>
                <strong>Cliente Completa Inspeção</strong><br>
                <ol>
                    <li>Tira as 9 fotos do veículo</li>
                    <li>Insere quilometragem</li>
                    <li>Seleciona nível de combustível</li>
                    <li>Marca danos (se existirem)</li>
                    <li>Submete inspeção</li>
                </ol>
            </div>
            
            <div class="step">
                <span class="step-number">4</span>
                <strong>Validação pelo Colaborador</strong><br>
                <ul>
                    <li>Self-checkout fica com status "Pendente"</li>
                    <li>Colaborador revê fotos e dados</li>
                    <li>Aprova ou rejeita inspeção</li>
                    <li>Após aprovação, contrato é encerrado</li>
                </ul>
            </div>
            
            <div class="info">
                <strong>💡 Vantagem:</strong> Self-checkout permite devoluções fora do horário de expediente e reduz tempo de espera do cliente.
            </div>
        </div>
        
        <div class="section">
            <h2>6. Gestão de Rental Agreements</h2>
            
            <h3>6.1. Upload de RA</h3>
            
            <p>O sistema extrai automaticamente dados do PDF do Rental Agreement:</p>
            
            <ul>
                <li>✅ Número do RA</li>
                <li>✅ Matrícula do veículo</li>
                <li>✅ Nome do cliente</li>
                <li>✅ Email do cliente</li>
                <li>✅ Telefone</li>
                <li>✅ Data de check-in (pickup_date)</li>
                <li>✅ Data de check-out (return_date)</li>
                <li>✅ Local de entrega</li>
                <li>✅ Local de devolução</li>
                <li>✅ Marca e modelo do veículo</li>
            </ul>
            
            <h3>6.2. Múltiplos Contratos para a Mesma Matrícula</h3>
            
            <p>Uma matrícula pode ter vários contratos ao longo do tempo:</p>
            
            <div class="step">
                <strong>Sistema Inteligente</strong><br>
                <ul>
                    <li>Ao inserir matrícula, sistema busca RA mais recente (por pickup_date)</li>
                    <li>Para buscar RA mais antigo, inserir manualmente o número do RA</li>
                    <li>Sistema valida estado de cada contrato individualmente</li>
                </ul>
            </div>
            
            <h3>6.3. Estados do Contrato</h3>
            
            <table>
                <tr>
                    <th>Estado</th>
                    <th>Descrição</th>
                    <th>Ações Permitidas</th>
                </tr>
                <tr>
                    <td>Sem Inspeções</td>
                    <td>RA existe mas sem check-in nem check-out</td>
                    <td>✅ Pode fazer check-in</td>
                </tr>
                <tr>
                    <td>Contrato Ativo</td>
                    <td>Tem check-in mas não tem check-out</td>
                    <td>❌ Bloqueado (cliente tem veículo)</td>
                </tr>
                <tr>
                    <td>Contrato Encerrado</td>
                    <td>Tem check-in E check-out</td>
                    <td>✅ Pode fazer novo check-in (novo contrato)</td>
                </tr>
            </table>
        </div>
        
        <div class="page-break"></div>
        
        <div class="section">
            <h2>7. Resolução de Problemas</h2>
            
            <h3>7.1. Matrícula Não Encontrada</h3>
            
            <div class="warning">
                <strong>Problema:</strong> Pop-up "Matrícula inválida ou inexistente"
            </div>
            
            <p><strong>Solução:</strong></p>
            <ol>
                <li>Verificar se matrícula está correta (ex: 30-XQ-17)</li>
                <li>Verificar se veículo existe no Admin Settings → Gestão de Frota</li>
                <li>Se não existir, adicionar veículo primeiro</li>
            </ol>
            
            <h3>7.2. RA Não Encontrado</h3>
            
            <div class="warning">
                <strong>Problema:</strong> Pop-up "Sem Rental Agreement"
            </div>
            
            <p><strong>Solução:</strong></p>
            <ol>
                <li>Fazer upload do PDF do Rental Agreement</li>
                <li>Aguardar processamento automático</li>
                <li>Verificar se dados foram extraídos corretamente</li>
            </ol>
            
            <h3>7.3. Contrato Ativo Bloqueado</h3>
            
            <div class="warning">
                <strong>Problema:</strong> Pop-up "Contrato Ativo" - ambos botões desativados
            </div>
            
            <p><strong>Solução:</strong></p>
            <ol>
                <li>Verificar se cliente já devolveu o veículo</li>
                <li>Se sim, fazer check-out primeiro</li>
                <li>Após check-out, contrato fica encerrado</li>
                <li>Pode então fazer novo check-in para novo contrato</li>
            </ol>
            
            <h3>7.4. Botão Check-out Desativado</h3>
            
            <div class="warning">
                <strong>Problema:</strong> Botão CHECK-OUT (RECOLHA) está cinzento
            </div>
            
            <p><strong>Solução:</strong></p>
            <ol>
                <li>Verificar se já foi feito check-in para este contrato</li>
                <li>Não é possível fazer check-out sem check-in primeiro</li>
                <li>Fazer check-in primeiro, depois check-out</li>
            </ol>
            
            <h3>7.5. Fotos Não Carregam</h3>
            
            <div class="warning">
                <strong>Problema:</strong> Fotos não aparecem após captura
            </div>
            
            <p><strong>Solução:</strong></p>
            <ol>
                <li>Verificar permissões da câmara no browser</li>
                <li>Tentar usar outro browser (Chrome recomendado)</li>
                <li>Verificar conexão à internet</li>
                <li>Limpar cache do browser</li>
            </ol>
            
            <h3>7.6. Email Não Enviado</h3>
            
            <div class="warning">
                <strong>Problema:</strong> Cliente não recebeu email com relatório
            </div>
            
            <p><strong>Solução:</strong></p>
            <ol>
                <li>Verificar se email está correto no RA</li>
                <li>Pedir ao cliente para verificar spam/lixo</li>
                <li>Verificar logs do sistema (Admin → System Logs)</li>
                <li>Reenviar email manualmente se necessário</li>
            </ol>
        </div>
        
        <div class="section">
            <h2>8. Boas Práticas</h2>
            
            <div class="success">
                <strong>✅ Recomendações:</strong>
                <ul>
                    <li>Sempre fazer upload do RA antes de iniciar inspeção</li>
                    <li>Tirar fotos com boa iluminação</li>
                    <li>Verificar que todas as 9 fotos estão nítidas</li>
                    <li>Marcar todos os danos visíveis no croqui</li>
                    <li>Adicionar observações detalhadas quando necessário</li>
                    <li>Confirmar email do cliente antes de finalizar</li>
                    <li>Verificar que relatório foi enviado com sucesso</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Auto Prudente</strong> - Sistema de Gestão de Frotas e Inspeções</p>
            <p>Manual gerado automaticamente - Versão 1.0 - Janeiro 2026</p>
            <p>Para suporte técnico, contactar: suporte@autoprudente.pt</p>
        </div>
    </div>
</body>
</html>
"""

# Gerar PDF
def generate_pdf():
    output_path = Path(__file__).parent / "MANUAL_INSPECOES.pdf"
    HTML(string=html_content, base_url=str(Path(__file__).parent)).write_pdf(output_path)
    print(f"✅ Manual PDF gerado: {output_path}")

if __name__ == '__main__':
    generate_pdf()
