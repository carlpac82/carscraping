# RESUMO DO PROBLEMA - C3, C4, C5 NÃO APARECEM NO EXCEL

## PROBLEMA
Quando fazes download de Brokers ou Website na homepage, as colunas C3, C4, C5 aparecem com valores 0.

## CAUSA RAIZ IDENTIFICADA
1. O download lê os preços **diretamente dos cards HTML** visíveis na página
2. Os cards de C3, C4, C5 **não são renderizados** na homepage
3. Os cards não são renderizados porque o backend **não retorna C3, C4, C5** no objeto `prices`

## SOLUÇÃO IMPLEMENTADA
Adicionei código ao `load_prices_from_db()` (linhas 85-125) para:
1. Carregar preços de C3, C4, C5 da tabela `vans_pricing`
2. Adicionar ao objeto `prices_data` antes de retornar ao frontend
3. Frontend renderiza cards com esses preços
4. Download lê dos cards e gera Excel com valores corretos

## CÓDIGO ADICIONADO
```python
# Linha 86-125 em current_prices_module.py
logging.info(f"[VANS] Location: '{location}', Check: {location != 'Faro Airport' and 'Faro' not in location}")
if location != 'Faro Airport' and 'Faro' not in location:
    logging.info("[VANS] ✅ Adding vans pricing...")
    # ... código para carregar de vans_pricing e adicionar a prices_data
```

## PROBLEMA ATUAL
**Os logs `[VANS]` NUNCA aparecem nos logs do Railway**, o que significa:
- OU o Railway não fez deploy da versão mais recente (cache)
- OU o loop `for row in rows:` nunca executa (rows vazio)
- OU há uma exceção silenciosa

## PRÓXIMO PASSO
Aguardar deploy do Railway completar (commit b621b6d) e verificar se logs `[VANS]` aparecem quando recarregas a homepage.

## TESTES PARA FAZER
1. Recarregar homepage com CTRL+SHIFT+R
2. Verificar logs do Railway para:
   - `Loading all periods for Albufeira`
   - `Found X rows for Albufeira`
   - `[DEBUG] About to loop through X rows`
   - `[DEBUG] Processing row 1/X`
   - `[VANS] Location: 'Albufeira'`
3. Se logs aparecem mas C3, C4, C5 não são adicionados → problema no código
4. Se logs NÃO aparecem → problema de deploy/cache

## FICHEIROS MODIFICADOS
- `current_prices_module.py` (linhas 85-125) - adiciona C3, C4, C5 aos períodos
- `templates/index.html` (linha 1129) - suporta estrutura {net, commission}
- `generate_brokers_excel()` e `generate_website_excel()` - também têm código para C3, C4, C5
