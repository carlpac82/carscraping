// Verificar conteúdo específico da página de comissões
console.log('🔍 Verificação do conteúdo de comissões');

// Procurar elementos específicos da página de comissões
const commissionsElements = {
    'Título de comissões': document.querySelector('h1, h2, h3'),
    'Tabelas de comissões': document.querySelectorAll('table'),
    'Cards de resumo': document.querySelectorAll('[class*="card"], [class*="summary"]'),
    'Botões de ação': document.querySelectorAll('button'),
    'Filtros': document.querySelectorAll('select, input[type="text"]'),
    'Gráficos': document.querySelectorAll('[class*="chart"], canvas'),
    'Listas de comissões': document.querySelectorAll('[class*="commission"], [class*="booking"]')
};

console.log('📊 Elementos encontrados:');
Object.entries(commissionsElements).forEach(([name, elements]) => {
    console.log(`${name}: ${elements.length}`);
    if (elements.length > 0 && elements.length <= 3) {
        elements.forEach((el, i) => {
            console.log(`  ${i + 1}: ${el.textContent?.substring(0, 50)}...`);
        });
    }
});

// Verificar o título da página
console.log('📄 Título da página:', document.title);

// Verificar se há algum erro ou mensagem
const messages = document.querySelectorAll('[class*="error"], [class*="warning"], [class*="info"]');
console.log('📨 Mensagens:', Array.from(messages).map(m => m.textContent));

// Verificar o conteúdo principal
const mainContent = document.querySelector('main') || document.querySelector('.container') || document.body;
if (mainContent) {
    const textContent = mainContent.textContent.substring(0, 200);
    console.log('📝 Conteúdo principal (primeiros 200 chars):', textContent);
}

// Verificar se há abas ou tabs
const tabs = document.querySelectorAll('[class*="tab"], [role="tab"]');
console.log('📑 Abas encontradas:', tabs.length);

// Verificar se há dados sendo carregados via JavaScript
setTimeout(() => {
    const loadingElements = document.querySelectorAll('[class*="loading"], [class*="spinner"]');
    console.log('⏳ Elementos de loading:', loadingElements.length);
}, 2000);
