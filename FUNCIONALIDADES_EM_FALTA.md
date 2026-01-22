# 📋 FUNCIONALIDADES EM FALTA - SELF-CHECKOUT

## Contrato de Teste
- **Matrícula**: AS-46-EO
- **RA**: 06716
- **Email de Teste**: carlpac82@hotmail.com

---

## 1. ❌ BACKEND - Endpoint de Advertência

### Endpoint: `POST /api/self-checkin/warn`
**Status**: NÃO IMPLEMENTADO

**Funcionalidade**:
- Recebe `inspection_number` no body
- Envia email usando templates `email_selfcheckout_warning_*.html`
- Marca inspeção com status 'warned' ou 'with_discrepancies'
- **NÃO** fecha o contrato (fica pendente para análise)
- Envia email ao cliente explicando que há divergências

**Implementação necessária**:
```python
@app.post("/api/self-checkin/warn")
async def warn_self_checkin(request: Request):
    # Buscar dados da inspeção
    # Enviar email de advertência
    # Atualizar status para 'warned'
    # Retornar sucesso
```

---

## 2. ❌ BACKEND - Função de Envio de Email de Advertência

### Função: `_send_self_checkout_warning_email()`
**Status**: NÃO IMPLEMENTADO

**Funcionalidade**:
- Similar a `_send_self_checkin_confirmation_email()`
- Usa templates `email_selfcheckout_warning_*.html`
- Suporta PT/EN/FR baseado no país do cliente
- Preenche placeholders com dados do contrato e inspeção

**Parâmetros necessários**:
- `to_email`: Email do cliente
- `ra_data`: Dados do rental agreement
- `inspection_data`: Dados da inspeção
- `photos_list`: Lista de fotos (opcional, pois não aparecem no email de advertência)
- `language`: 'pt', 'en' ou 'fr'

---

## 3. ❌ FRONTEND - Botão de Advertir no Histórico

### Localização: `templates/inspection_history.html`
**Status**: NÃO IMPLEMENTADO

**Funcionalidade**:
- Botão "Advertir" ou "Divergências" (cor laranja/amarelo)
- Aparece junto com botões "Validar" e "Invalidar"
- Apenas visível para self-checkouts com status 'pending'
- Ao clicar, mostra modal de confirmação
- Chama endpoint `/api/self-checkin/warn`

**Design sugerido**:
```html
<button onclick="warnSelfCheckin('${inspection_number}')" 
        class="flex items-center gap-2 px-3 py-2 bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors" 
        title="Advertir Cliente sobre Divergências">
    <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
    </svg>
    <span class="hidden sm:inline text-sm font-medium text-orange-600">Advertir</span>
</button>
```

---

## 4. ❌ UI - Indicadores Visuais de Status

### Localização: Cards de contrato no histórico
**Status**: NÃO IMPLEMENTADO

**Funcionalidade**:
- Badge de status visível na card do contrato
- Cores diferentes por status:
  - 🟡 **Pendente** (amarelo) - `status = 'pending'`
  - 🟢 **Validado** (verde) - `status = 'validated'`
  - 🟠 **Com Divergências** (laranja) - `status = 'warned'`
  - 🔴 **Invalidado** (vermelho) - `status = 'rejected'`

**Design sugerido**:
```html
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
    ⏳ Pendente Validação
</span>
```

---

## 5. ❌ UI - Badge Self-Checkout

### Localização: Cards de contrato no histórico
**Status**: NÃO IMPLEMENTADO

**Funcionalidade**:
- Tag "SELF-CHECKOUT" visível na card
- Distinguir de inspeções manuais
- Cor diferenciada (roxo/azul claro)

**Design sugerido**:
```html
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
    📱 SELF-CHECKOUT
</span>
```

---

## 6. ❌ UI - Filtros e Pesquisa

### Localização: Topo da página de histórico
**Status**: NÃO IMPLEMENTADO

**Funcionalidades necessárias**:
1. **Filtro "Apenas Self-Checkouts"**
   - Checkbox ou toggle
   - Mostra apenas inspeções com `is_self_checkin = true`

2. **Filtro por Status**
   - Dropdown com opções:
     - Todos
     - Pendente
     - Validado
     - Com Divergências
     - Invalidado

3. **Contador de Pendentes**
   - Badge no topo mostrando: "X self-checkouts pendentes de validação"
   - Cor laranja/amarela para chamar atenção

---

## 7. ❌ DATABASE - Campos Adicionais

### Tabela: `vehicle_inspections`
**Status**: CAMPOS EM FALTA

**Campos a adicionar**:
```sql
ALTER TABLE vehicle_inspections 
ADD COLUMN warning_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN discrepancy_notes TEXT,
ADD COLUMN warned_at TIMESTAMP,
ADD COLUMN warned_by VARCHAR(100);
```

**Descrição**:
- `warning_sent`: Se email de advertência foi enviado
- `discrepancy_notes`: Notas sobre as divergências detectadas
- `warned_at`: Timestamp de quando foi advertido
- `warned_by`: Usuário que enviou a advertência

---

## 8. ⚠️ UI - Ícones Monocromáticos vs Coloridos

### Localização: Botões de inspeção no histórico
**Status**: ATUALMENTE COLORIDOS

**Situação atual**:
- ✅ Ícone de carro **VERDE** para Check-in (Entrega)
- ✅ Ícone de carro **VERMELHO** para Check-out (Recolha)

**Questão**:
- Os ícones devem ser **monocromáticos** (cinza/preto) ou manter as cores?
- Atualmente estão coloridos e funcionais
- **DECISÃO PENDENTE DO UTILIZADOR**

---

## 9. ❌ NOTIFICAÇÕES

### Sistema de Notificações
**Status**: NÃO IMPLEMENTADO

**Funcionalidades necessárias**:
1. **Notificação quando self-checkout é submetido**
   - Toast/banner no dashboard
   - Som opcional
   - Link direto para validar

2. **Notificação quando self-checkout precisa validação**
   - Badge de contador no menu
   - Lista de pendentes

3. **Dashboard com métricas**
   - Total de self-checkouts hoje/semana/mês
   - Taxa de validação
   - Tempo médio de validação
   - Self-checkouts com divergências

---

## 10. ❌ LOGS E AUDITORIA

### Sistema de Auditoria
**Status**: NÃO IMPLEMENTADO

**Funcionalidades necessárias**:
1. **Log de ações**
   - Quem validou/invalidou/advertiu
   - Timestamp de cada ação
   - IP do utilizador

2. **Histórico de emails enviados**
   - Tabela `email_logs`
   - Campos: tipo_email, destinatario, enviado_em, status

3. **Rastreabilidade completa**
   - Cada alteração de status registada
   - Possibilidade de reverter ações

---

## 📊 RESUMO DE PRIORIDADES

### 🔴 ALTA PRIORIDADE (Funcionalidades Core)
1. ✅ Templates de email de advertência (CONCLUÍDO)
2. ❌ Endpoint `/api/self-checkin/warn`
3. ❌ Função `_send_self_checkout_warning_email()`
4. ❌ Botão "Advertir" no histórico
5. ❌ Badge de status nas cards

### 🟡 MÉDIA PRIORIDADE (UX/UI)
6. ❌ Badge "SELF-CHECKOUT"
7. ❌ Filtros e pesquisa
8. ❌ Contador de pendentes
9. ⚠️ Decisão sobre ícones monocromáticos

### 🟢 BAIXA PRIORIDADE (Nice to Have)
10. ❌ Sistema de notificações
11. ❌ Dashboard com métricas
12. ❌ Logs e auditoria completa

---

## 🧪 TESTES NECESSÁRIOS

### Fluxo Completo de Teste
1. ✅ Gerar link de self-checkout
2. ✅ Submeter self-checkout (email de submissão)
3. ✅ Validar self-checkout (email de validação)
4. ❌ Advertir self-checkout (email de advertência) - **FALTA IMPLEMENTAR**
5. ❌ Verificar histórico com badges e status
6. ❌ Testar filtros e pesquisa

### Contrato de Teste
- **RA**: 06716
- **Matrícula**: AS-46-EO
- **Email**: carlpac82@hotmail.com

---

## 📝 NOTAS ADICIONAIS

- Os templates de email de advertência já estão criados e prontos:
  - `email_selfcheckout_warning_pt.html`
  - `email_selfcheckout_warning_en.html`
  - `email_selfcheckout_warning_fr.html`
  - `preview_email_selfcheckout_warning.html`

- Terminologia correta já aplicada: "Divergências" (não "Discrepâncias")

- Cores definidas para advertência: `#f59e0b` (laranja/amarelo)

---

**Última atualização**: 22 de Janeiro de 2026
**Criado por**: Cascade AI Assistant
