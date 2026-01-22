
📋 LISTA DE FUNCIONALIDADES EM FALTA:

1. BACKEND - Endpoint de Advertência
   ✅ POST /api/self-checkin/warn - IMPLEMENTADO
   - Recebe inspection_number e notes (opcional)
   - Envia email usando templates email_selfcheckout_warning_*.html
   - Marca inspeção com status 'warned'
   - Não fecha o contrato

2. FRONTEND - Botão de Advertir no Histórico
   ❌ Botão "Advertir" (laranja/amarelo)
   - Aparece junto com "Validar" e "Invalidar"
   - Chama endpoint /api/self-checkin/warn
   - Mostra confirmação antes de enviar

3. UI - Indicadores Visuais de Status
   ❌ Badge de status na card do contrato
   - "Pendente" (amarelo)
   - "Validado" (verde)
   - "Com Divergências" (laranja)
   - "Invalidado" (vermelho)

4. UI - Badge Self-Checkout
   ❌ Tag "SELF-CHECKOUT" na card
   - Distinguir de inspeções manuais
   - Cor diferenciada (roxo/azul)

5. UI - Filtros e Pesquisa
   ❌ Filtro "Apenas Self-Checkouts"
   ❌ Filtro por status (Pendente/Validado/etc)
   ❌ Contador de pendentes no topo

6. EMAILS - Função de Envio de Advertência
   ❌ Função _send_self_checkout_warning_email()
   - Similar a _send_self_checkin_confirmation_email
   - Usa templates email_selfcheckout_warning_*.html
   - Suporta PT/EN/FR

7. DATABASE - Campo de Status
   ❌ Adicionar campo 'warning_sent' em vehicle_inspections
   ❌ Adicionar campo 'discrepancy_notes' para observações

8. HISTÓRICO - Ícones Monocromáticos
   ⚠️  Atualmente os ícones de carro são COLORIDOS
   - Verde para Check-in (Entrega)
   - Vermelho para Check-out (Recolha)
   ❓ Confirmar se devem ser monocromáticos

9. NOTIFICAÇÕES
   ❌ Notificação quando self-checkout é submetido
   ❌ Notificação quando self-checkout precisa validação
   ❌ Dashboard com métricas de self-checkout

10. LOGS E AUDITORIA
    ❌ Log de quem validou/invalidou/advertiu
    ❌ Timestamp de cada ação
    ❌ Histórico de emails enviados
