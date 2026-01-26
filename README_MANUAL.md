# 📚 Manual de Inspeções - Auto Prudente

## 📄 Sobre o Manual

Manual completo e profissional do Sistema de Inspeções de Veículos da Auto Prudente, incluindo:

- ✅ Instruções detalhadas de Check-in (Entrega)
- ✅ Instruções detalhadas de Check-out (Recolha)
- ✅ Guia de Self-Checkout
- ✅ Gestão de Rental Agreements
- ✅ Resolução de problemas
- ✅ Boas práticas
- ✅ Design profissional com header azul e logo Auto Prudente

---

## 🎨 Design

- **Header:** Gradiente azul (#009cb6 → #007a94)
- **Logo:** Auto Prudente (ap-heather.png) no canto superior esquerdo
- **Tipografia:** Segoe UI, profissional e clean
- **Cores:** Azul corporativo com alertas coloridos (warning, info, success)
- **Layout:** Otimizado para impressão A4

---

## 📥 Como Converter para PDF

### **Método 1: Browser (Recomendado)**

1. **Abrir o ficheiro HTML:**
   ```bash
   open MANUAL_INSPECOES.html
   ```
   Ou duplo-clique no ficheiro `MANUAL_INSPECOES.html`

2. **Imprimir para PDF:**
   - **Mac:** `Cmd + P` → Selecionar "Save as PDF"
   - **Windows:** `Ctrl + P` → Selecionar "Save as PDF"
   - **Linux:** `Ctrl + P` → Selecionar "Print to File (PDF)"

3. **Configurações de Impressão:**
   - Tamanho: **A4**
   - Margens: **Nenhuma** (já configuradas no CSS)
   - Orientação: **Retrato**
   - Escala: **100%**
   - Fundo gráfico: **Ativado** (para ver o header azul)

4. **Guardar:**
   - Nome: `Manual_Inspecoes_AutoPrudente.pdf`
   - Local: Onde preferir

---

### **Método 2: Linha de Comando (macOS/Linux)**

Se tiver `wkhtmltopdf` instalado:

```bash
# Instalar wkhtmltopdf (macOS)
brew install wkhtmltopdf

# Converter para PDF
wkhtmltopdf MANUAL_INSPECOES.html Manual_Inspecoes_AutoPrudente.pdf
```

---

### **Método 3: Python (se WeasyPrint funcionar)**

```bash
# Instalar dependências (macOS)
brew install pango gdk-pixbuf libffi

# Instalar WeasyPrint
pip3 install weasyprint

# Executar script
python3 generate_manual.py
```

**Nota:** WeasyPrint pode ter problemas com dependências do sistema. Método 1 (Browser) é mais confiável.

---

## 📋 Conteúdo do Manual

### **Capítulos:**

1. **Introdução ao Sistema**
   - Visão geral
   - Funcionalidades
   - Acesso ao sistema

2. **Terminologia**
   - Check-in vs Check-out
   - Self-checkout
   - Rental Agreement (RA)

3. **Check-in (Entrega de Viatura)**
   - Passo-a-passo completo
   - Upload de RA
   - Captura de fotos (9 obrigatórias)
   - Preenchimento de dados
   - Marcação de danos
   - Finalização

4. **Check-out (Recolha de Viatura)**
   - Diferenças vs check-in
   - Validação de combustível
   - Identificação de danos novos
   - Alertas de incidentes
   - Email ao cliente

5. **Self-Checkout**
   - Geração de link
   - Interface do cliente
   - Validação pelo colaborador

6. **Gestão de Rental Agreements**
   - Upload e extração automática
   - Múltiplos contratos
   - Estados do contrato

7. **Resolução de Problemas**
   - Matrícula não encontrada
   - RA não encontrado
   - Contrato bloqueado
   - Fotos não carregam
   - Email não enviado
   - Sistema lento

8. **Boas Práticas**
   - Antes da inspeção
   - Durante a inspeção
   - Após a inspeção
   - Dicas profissionais

9. **Segurança e Backup**
   - Proteção de dados
   - Backup automático
   - Conformidade RGPD

---

## 🎯 Uso do Manual

### **Para Formação:**
- Imprimir PDF e distribuir aos colaboradores
- Usar como material de onboarding
- Referência rápida durante inspeções

### **Para Clientes:**
- Secção de Self-Checkout pode ser extraída
- Enviar por email como guia

### **Para Documentação:**
- Anexar a propostas comerciais
- Incluir em apresentações
- Arquivo de procedimentos internos

---

## 📁 Ficheiros Relacionados

- `MANUAL_INSPECOES.html` - Manual em HTML (abrir no browser)
- `criar_manual.py` - Script Python que gera o HTML
- `generate_manual.py` - Script alternativo com WeasyPrint
- `static/ap-heather.png` - Logo Auto Prudente (usado no header)

---

## ✅ Checklist de Qualidade

- [x] Header azul com gradiente
- [x] Logo Auto Prudente no canto esquerdo
- [x] Todas as seções completas
- [x] Tabelas formatadas
- [x] Alertas coloridos (warning, info, success)
- [x] Passos numerados com círculos azuis
- [x] Otimizado para impressão A4
- [x] Footer com informações de contacto
- [x] Instruções de conversão para PDF

---

## 📞 Suporte

Para questões sobre o manual ou sistema de inspeções:
- **Email:** suporte@autoprudente.pt
- **Sistema:** https://rentalprices.pt

---

**Versão:** 1.0  
**Data:** Janeiro 2026  
**Autor:** Auto Prudente - Sistema de Gestão de Frotas
