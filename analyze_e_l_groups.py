#!/usr/bin/env python3
import json

with open('scraping_test_final.json', 'r') as f:
    data = json.load(f)

groups = {'E1': [], 'E2': [], 'L1': [], 'L2': []}

for item in data['all_items']:
    group = item.get('group', '')
    if group in groups:
        groups[group].append(item)

for group in ['E1', 'E2', 'L1', 'L2']:
    items = groups[group]
    print(f'\n{"=" * 80}')
    print(f'{group}: {len(items)} carros')
    print(f'{"=" * 80}')
    
    manual = sum(1 for item in items if item.get('transmission', '').lower() == 'manual')
    auto = sum(1 for item in items if item.get('transmission', '').lower() == 'automatic')
    
    print(f'Manual: {manual} | Automatic: {auto}')
    
    print(f'\nPrimeiros 10:')
    for i, item in enumerate(items[:10], 1):
        car = item.get('car', '')
        trans = item.get('transmission', '')
        cat = item.get('category', '')
        print(f'{i:2}. {car[:50]:50} | {trans:10} | {cat[:20]}')
    
    if len(items) > 10:
        print(f'... e mais {len(items) - 10}')
