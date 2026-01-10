"""
AI Learning System - Analisa histórico de preços editados e gera sugestões inteligentes
Considera sazonalidade mensal e períodos especiais
"""
import json
import statistics
from collections import defaultdict
from datetime import datetime, timedelta

def get_year_month_from_pickup_date(pickup_date):
    """Extrai ano e mês da data de pickup"""
    try:
        if isinstance(pickup_date, str):
            date_obj = datetime.strptime(pickup_date, '%Y-%m-%d')
        else:
            date_obj = pickup_date
        return date_obj.year, date_obj.month
    except:
        return None, None

def get_period_type(pickup_date):
    """
    Identifica tipo de período baseado na data
    - high_season: Julho, Agosto (época alta)
    - shoulder: Maio, Junho, Setembro (meia época)
    - low_season: Outubro-Abril (época baixa)
    - christmas: 20 Dez - 5 Jan
    - easter: Semana Santa (variável)
    """
    try:
        if isinstance(pickup_date, str):
            date_obj = datetime.strptime(pickup_date, '%Y-%m-%d')
        else:
            date_obj = pickup_date
        
        month = date_obj.month
        day = date_obj.day
        
        # Natal/Ano Novo
        if (month == 12 and day >= 20) or (month == 1 and day <= 5):
            return 'christmas'
        
        # Época alta (Verão)
        if month in [7, 8]:
            return 'high_season'
        
        # Meia época
        if month in [5, 6, 9]:
            return 'shoulder'
        
        # Época baixa
        return 'low_season'
    except:
        return 'unknown'

def analyze_pricing_patterns(conn, location, min_samples=2):
    """
    Analisa padrões de preços editados pelo user para uma localização
    Agrupa por ANO+MÊS e PERÍODO para capturar sazonalidade
    
    Returns:
        dict: Padrões identificados por ano/mês/grupo/dia com:
            - position: Posição média vs mercado (1º, 2º, etc)
            - diff_pct: Diferença percentual média vs preço mais baixo
            - min_price: Preço mínimo usado pelo user
            - max_price: Preço máximo usado pelo user
            - samples: Número de amostras analisadas
            - year: Ano (2025, 2026, etc)
            - month: Mês do ano (1-12)
            - period_type: Tipo de período (high_season, low_season, etc)
    """
    
    # Pegar TODAS as pesquisas editadas (current) com supplier_data - SEM LIMITE
    cursor = conn.execute("""
        SELECT id, pickup_date, prices_data, supplier_data
        FROM automated_search_history
        WHERE location ILIKE ?
          AND search_type = 'current'
          AND supplier_data IS NOT NULL
        ORDER BY search_date DESC
    """, (f'%{location}%',))
    
    rows = cursor.fetchall()
    
    # Estrutura para armazenar análises: {year_month: {grupo: {dia: [amostras]}}}
    # Agrupado por ANO+MÊS para capturar sazonalidade (2025-01 ≠ 2026-01)
    yearly_monthly_analysis = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for row in rows:
        search_id, pickup_date, prices_data, supplier_data = row
        
        # Parse JSON
        if isinstance(prices_data, str):
            prices_data = json.loads(prices_data)
        if isinstance(supplier_data, str):
            supplier_data = json.loads(supplier_data)
        
        # Identificar ano, mês e período
        year, month = get_year_month_from_pickup_date(pickup_date)
        period_type = get_period_type(pickup_date)
        
        if not year or not month:
            continue
        
        # Criar chave única: "2025-01", "2026-08", etc
        year_month_key = f"{year}-{str(month).zfill(2)}"
        
        # Analisar cada grupo
        for grupo in ['B1', 'B2', 'C', 'D', 'E1', 'E2', 'F']:
            if grupo in prices_data and grupo in supplier_data:
                for day, user_price in prices_data[grupo].items():
                    # Pegar preços do mercado para este dia
                    if day in supplier_data[grupo]:
                        cars = supplier_data[grupo][day]
                        market_prices = sorted([
                            c.get('price_num', 0) 
                            for c in cars 
                            if c.get('price_num', 0) > 0
                        ])
                        
                        if market_prices:
                            market_low = market_prices[0]
                            
                            # Descobrir em que posição o user se colocou
                            position = 1
                            for i, price in enumerate(market_prices, 1):
                                if user_price <= price:
                                    position = i
                                    break
                            else:
                                position = len(market_prices) + 1
                            
                            diff_vs_low = user_price - market_low
                            diff_pct = (diff_vs_low / market_low * 100) if market_low > 0 else 0
                            
                            # Guardar análise agrupada por ANO+MÊS
                            yearly_monthly_analysis[year_month_key][grupo][day].append({
                                'user_price': user_price,
                                'market_low': market_low,
                                'market_prices': market_prices[:5],
                                'position': position,
                                'diff_vs_low': diff_vs_low,
                                'diff_pct': diff_pct,
                                'pickup_date': pickup_date,
                                'period_type': period_type,
                                'year': year,
                                'month': month
                            })
    
    # Calcular padrões agregados POR ANO+MÊS
    # Estrutura: {year_month: {grupo: {day: pattern}}}
    patterns = {}
    
    for year_month_key, grupos_data in yearly_monthly_analysis.items():
        patterns[year_month_key] = {}
        
        for grupo, days_data in grupos_data.items():
            patterns[year_month_key][grupo] = {}
            
            for day, entries in days_data.items():
                if len(entries) >= min_samples:
                    # Identificar período predominante
                    period_types = [e['period_type'] for e in entries]
                    most_common_period = max(set(period_types), key=period_types.count)
                    
                    # Extrair ano e mês do primeiro entry
                    year = entries[0]['year']
                    month = entries[0]['month']
                    
                    patterns[year_month_key][grupo][day] = {
                        'position': statistics.mean([e['position'] for e in entries]),
                        'diff_pct': statistics.mean([e['diff_pct'] for e in entries]),
                        'diff_euros': statistics.mean([e['diff_vs_low'] for e in entries]),
                        'min_price': min([e['user_price'] for e in entries]),
                        'max_price': max([e['user_price'] for e in entries]),
                        'samples': len(entries),
                        'recent_price': entries[0]['user_price'],  # Mais recente
                        'recent_market_low': entries[0]['market_low'],
                        'period_type': most_common_period,
                        'year': year,
                        'month': month,
                        'year_month': year_month_key
                    }
    
    return patterns


def generate_smart_suggestions(patterns, location):
    """
    Gera sugestões de estratégias baseadas nos padrões identificados
    Considera sazonalidade mensal e períodos especiais
    
    Returns:
        list: Lista de sugestões com estratégias recomendadas, agrupadas por mês
    """
    suggestions = []
    
    month_names = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    # Iterar por ano+mês, grupo e dia
    for year_month_key, grupos_data in patterns.items():
        # Extrair ano e mês da chave "2025-01"
        try:
            year_str, month_str = year_month_key.split('-')
            year = int(year_str)
            month = int(month_str)
            month_name = month_names.get(month, f'Mês {month}')
            year_month_display = f"{month_name} {year}"
        except:
            year_month_display = year_month_key
        
        for grupo, days_data in grupos_data.items():
            for day, pattern in days_data.items():
                # Determinar tipo de estratégia baseado no padrão
                position = pattern['position']
                diff_pct = pattern['diff_pct']
                period_type = pattern.get('period_type', 'unknown')
                
                # Estratégia: Follow Lowest com ajuste percentual
                if position <= 1.5:  # Posiciona-se em 1º lugar
                    strategy_type = 'follow_lowest'
                    target_position = 1
                    
                    if diff_pct < -0.5:
                        # User fica abaixo do mais baixo
                        suggestion_text = f"{year_month_display}: {abs(diff_pct):.1f}% ABAIXO do mais baixo"
                        diff_operation = 'subtract'
                        diff_value = abs(diff_pct)
                    elif diff_pct > 0.5:
                        # User fica acima do mais baixo
                        suggestion_text = f"{year_month_display}: {diff_pct:.1f}% ACIMA do mais baixo"
                        diff_operation = 'add'
                        diff_value = diff_pct
                    else:
                        # User fica igual ao mais baixo
                        suggestion_text = f"{year_month_display}: Iguala o preço mais baixo"
                        diff_operation = 'subtract'
                        diff_value = 0
                        
                elif position <= 2.5:  # Posiciona-se em 2º lugar
                    strategy_type = 'follow_lowest'
                    target_position = 2
                    suggestion_text = f"{year_month_display}: 2º lugar ({diff_pct:+.1f}% vs mais baixo)"
                    diff_operation = 'add' if diff_pct > 0 else 'subtract'
                    diff_value = abs(diff_pct)
                    
                else:  # Posiciona-se em 3º+ lugar
                    strategy_type = 'follow_lowest'
                    target_position = int(position)
                    suggestion_text = f"{year_month_display}: {target_position}º lugar ({diff_pct:+.1f}% vs mais baixo)"
                    diff_operation = 'add' if diff_pct > 0 else 'subtract'
                    diff_value = abs(diff_pct)
                
                suggestions.append({
                    'location': location,
                    'grupo': grupo,
                    'day': int(day),
                    'year': pattern.get('year'),
                    'month': pattern.get('month'),
                    'yearMonth': year_month_key,
                    'yearMonthDisplay': year_month_display,
                    'periodType': period_type,
                    'strategy': {
                        'type': strategy_type,
                        'targetPosition': target_position,
                        'diffType': 'percentage',
                        'diffValue': round(diff_value, 2),
                        'diffOperation': diff_operation
                    },
                    'minPrice': round(pattern['min_price'], 2),
                    'pattern': {
                        'avgPosition': round(pattern['position'], 1),
                        'avgDiffPct': round(pattern['diff_pct'], 1),
                        'samples': pattern['samples'],
                        'periodType': period_type
                    },
                    'description': suggestion_text,
                    'confidence': min(95, 50 + (pattern['samples'] * 10))
                })
    
    return suggestions
