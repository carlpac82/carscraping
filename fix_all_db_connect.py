#!/usr/bin/env python3
"""
Script para substituir TODAS as ocorrências de _db_connect() por get_db_connection()
de forma segura e automática.
"""

import re
import sys

def fix_db_connect_calls(content):
    """
    Substitui padrões de _db_connect() por get_db_connection() context manager
    """
    
    # Padrão 1: conn = _db_connect() seguido de try/finally com conn.close()
    pattern1 = r'(\s+)(conn|con|migration_conn|temp_conn|verify_conn|conn2|conn_vehicle) = _db_connect\(\)\s*\n(\s+)try:\s*\n((?:.*\n)*?)(\s+)finally:\s*\n\s+\2\.close\(\)'
    
    def replace1(match):
        indent = match.group(1)
        var_name = match.group(2)
        try_indent = match.group(3)
        try_body = match.group(4)
        
        # Remover um nível de indentação do try_body
        lines = try_body.split('\n')
        dedented_lines = []
        for line in lines:
            if line.strip():
                # Remove 4 espaços de indentação
                if line.startswith(try_indent + '    '):
                    dedented_lines.append(line[4:])
                else:
                    dedented_lines.append(line)
            else:
                dedented_lines.append(line)
        
        dedented_body = '\n'.join(dedented_lines)
        
        return f'''{indent}with get_db_connection() as {var_name}:
{indent}    if USE_POSTGRES:
{indent}        {var_name} = PostgreSQLConnectionWrapper({var_name})
{dedented_body}'''
    
    content = re.sub(pattern1, replace1, content, flags=re.MULTILINE)
    
    # Padrão 2: conn = _db_connect() SEM try/finally (mais perigoso)
    # Vamos apenas adicionar um comentário de warning
    pattern2 = r'(\s+)(conn|con) = _db_connect\(\)(?!\s*\n\s*try:)'
    
    def replace2(match):
        indent = match.group(1)
        var_name = match.group(2)
        return f'''{indent}# TODO: CRITICAL - Replace with context manager!
{indent}with get_db_connection() as {var_name}:
{indent}    if USE_POSTGRES:
{indent}        {var_name} = PostgreSQLConnectionWrapper({var_name})
{indent}    # IMPORTANT: Add proper indentation to code below'''
    
    # NÃO aplicar padrão 2 automaticamente - muito arriscado
    
    return content

def main():
    input_file = 'main.py'
    output_file = 'main.py.fixed'
    
    print(f"📖 Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"🔧 Applying fixes...")
    fixed_content = fix_db_connect_calls(content)
    
    print(f"💾 Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    # Count changes
    original_count = len(re.findall(r'_db_connect\(\)', content))
    fixed_count = len(re.findall(r'_db_connect\(\)', fixed_content))
    
    print(f"\n✅ Done!")
    print(f"   Original _db_connect() calls: {original_count}")
    print(f"   Remaining _db_connect() calls: {fixed_count}")
    print(f"   Fixed: {original_count - fixed_count}")
    print(f"\n⚠️  Review {output_file} before replacing {input_file}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
