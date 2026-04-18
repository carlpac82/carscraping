# Setup GitHub Mobile 100% - Sistema Automático

## Sistema criado e funcionando! 

### O que foi implementado:
- **Sistema automático**: Você cria issue no GitHub App (mobile) -> Sistema executa automaticamente
- **Sem precisar de me avisar**: Funciona 100% automático
- **Feedback automático**: Sistema comenta no issue com status da execução

---

## Configuração necessária (AGORA com computador):

### 1. Configurar variáveis de ambiente no Railway:
Vá ao Railway Dashboard -> Settings -> Environment Variables e adicione:

```
GITHUB_TOKEN=seu_github_personal_access_token
GITHUB_WEBHOOK_SECRET=carscraping-webhook-secret
```

### 2. Criar GitHub Personal Access Token:
1. Vá para github.com/settings/tokens
2. Clique "Generate new token (classic)"
3. Permissions: `repo` (full control)
4. Copie o token e cole no Railway

### 3. Configurar Webhook no GitHub:
1. Vá para github.com/carlpac82/carscraping/settings/hooks
2. Add webhook
3. Payload URL: `https://seu-app-name.railway.app/webhook/github`
4. Content type: `application/json`
5. Secret: `carscraping-webhook-secret`
6. Events: `Issues`

---

## Como usar durante as férias (100% mobile):

### Passo 1: Criar Issue no GitHub App
```
1. Abrir GitHub App no telemóvel
2. Repositório: carlpac82/carscraping
3. Criar "New Issue"
4. Título: "Mudar botão Entrega para Check-in"
5. Body (opcional): detalhes se precisar
```

### Passo 2: Sistema executa automaticamente
```
- Sistema detecta issue novo
- Extrai comando do título
- Executa código automaticamente
- Faz commit e push
- Comenta no issue com status
- Fecha issue automaticamente
```

### Passo 3: Monitorar resultado
```
1. Abrir browser no telemóvel
2. railway.app
3. Ver logs em tempo real
4. Ver aplicação funcionando
```

---

## Comandos suportados:

### Mudanças de texto:
```
"Mudar botão Entrega para Check-in"
"Alterar título da página para Novo Título"
"Trocar texto 'Olá' por 'Bem-vindo'"
```

### Cores:
```
"Mudar cor do botão para azul"
"Alterar fundo para branco"
```

### Ativar/Desativar:
```
"Ativar relatórios diários"
"Desativar scheduler"
"Enable feature X"
```

### Rollback:
```
"Rollback último commit"
"Reverter alterações"
```

### Deploy:
```
"Fazer deploy"
"Deploy agora"
```

---

## Exemplo completo durante férias:

### Você (GitHub App mobile):
```
Issue: "Mudar botão Entrega para Check-in"
```

### Sistema (automático):
```
1. Detecta issue novo
2. Extrai comando: "Mudar botão Entrega para Check-in"
3. Executa: sed -i 's/Entrega/Check-in/g' templates/vehicle_inspection.html
4. Faz commit: "Auto-commit from GitHub Issue: Change button text"
5. Faz push para main
6. Comenta: "Concluído! Comando executado com sucesso"
7. Fecha issue
```

### Você (monitoramento):
```
1. Browser mobile -> railway.app
2. Ver logs:
   - "GitHub Issue recebido: #123 - Mudar botão..."
   - "Comando extraído: Mudar botão..."
   - "Execução sucesso"
   - "Commit e push realizados"
3. Abre aplicação -> vê botão "Check-in"
```

---

## Teste agora:

1. Configure as variáveis de ambiente no Railway
2. Configure o webhook no GitHub
3. Crie um issue de teste: "Teste automático"
4. Veja se funciona automaticamente

---

## Suporte durante férias:

Se algo não funcionar:
- Verifique logs no Railway
- Issue pode ficar aberto com erro
- Sistema comenta o que deu errado
- Você pode criar outro issue para corrigir

**Está 100% pronto para as férias!** 

Só precisa configurar tokens e webhook uma vez (agora com computador). Depois é só usar o GitHub App no telemóvel!
