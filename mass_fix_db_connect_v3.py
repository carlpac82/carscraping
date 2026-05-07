#!/usr/bin/env python3
"""
Versão 3: Regex melhorado para capturar blocos try/finally maiores e mais complexos
"""

import re
import sys
from pathlib import Path

def fix_all_db_connect_v3(content: str) -> tuple[str, int]:
    """
    Substitui padrões de _db_connect() por get_db_connection().
    Usa regex não-greedy para capturar blocos try/finally complexos.
    """
    
    fixes_count = 0
    
    # Padrão melhorado: captura blocos try/finally de qualquer tamanho
    # (?:(?!finally:).)*? = non-greedy match que não inclui 'finally:'
    pattern = re.compile(
        r'^(\s+)(conn|con|migration_conn|temp_conn|verify_conn|conn2|conn_vehicle|connection|conn_verify|conn_check) = _db_connect\(\)\s*\n'
        r'(\s+)is_postgres = _is_postgresql_connection\(\2\)\s*\n'  # Linha opcional
        r'\s*\n?'  # Linha em branco opcional
        r'\1try:\s*\n'
        r'((?:(?!^\1finally:).*\n)*?)'  # Captura tudo até finally (non-greedy)
        r'^\1finally:\s*\n'
        r'\1\s+\2\.close\(\)',
        re.MULTILINE
    )
    
    def replacer(match):
        nonlocal fixes_count
        fixes_count += 1
        
        indent = match.group(1)
        var_name = match.group(2)
        try_body = match.group(4)
        
        # Dedent o corpo do try
        dedented_lines = []
        for line in try_body.split('\n'):
            if line.strip():
                expected_indent = indent + '    '
                if line.startswith(expected_indent):
                    dedented_lines.append(indent + line[len(expected_indent):])
                else:
                    dedented_lines.append(line)
            else:
                dedented_lines.append(line)
        
        dedented_body = '\n'.join(dedented_lines)
        
        # Construir novo código
        return (
            f'{indent}with get_db_connection() as {var_name}:\n'
            f'{indent}    if USE_POSTGRES:\n'
            f'{indent}        {var_name} = PostgreSQLConnectionWrapper({var_name})\n'
            f'{indent}    is_postgres = _is_postgresql_connection({var_name})\n'
            f'\n'
            f'{dedented_body}'
        )
    
    new_content = pattern.sub(replacer, content)
    fixes_count_v1 = fixes_count
    
    # Padrão 2: SEM a linha is_postgres
    pattern2 = re.compile(
        r'^(\s+)(conn|con|migration_conn|temp_conn|verify_conn|conn2|conn_vehicle|connection|conn_verify|conn_check) = _db_connect\(\)\s*\n'
        r'\s*\n?'  # Linha em branco opcional
        r'\1try:\s*\n'
        r'((?:(?!^\1finally:).*\n)*?)'  # Captura tudo até finally
        r'^\1finally:\s*\n'
        r'\1\s+\2\.close\(\)',
        re.MULTILINE
    )
    
    def replacer2(match):
        nonlocal fixes_count
        fixes_count += 1
        
        indent = match.group(1)
        var_name = match.group(2)
        try_body = match.group(3)
        
        # Dedent
        dedented_lines = []
        for line in try_body.split('\n'):
            if line.strip():
                expected_indent = indent + '    '
                if line.startswith(expected_indent):
                    dedented_lines.append(indent + line[len(expected_indent):])
                else:
                    dedented_lines.append(line)
            else:
                dedented_lines.append(line)
        
        dedented_body = '\n'.join(dedented_lines)
        
        return (
            f'{indent}with get_db_connection() as {var_name}:\n'
            f'{indent}    if USE_POSTGRES:\n'
            f'{indent}        {var_name} = PostgreSQLConnectionWrapper({var_name})\n'
            f'{dedented_body}'
        )
    
    new_content = pattern2.sub(replacer2, new_content)
    
    return new_content, fixes_count


def main():
    input_file = Path('main.py')
    backup_file = Path('main.py.backup_v3')
    
    if not input_file.exists():
        print(f"❌ Erro: {input_file} não encontrado!")
        return 1
    
    print(f"📖 Lendo {input_file}...")
    content = input_file.read_text(encoding='utf-8')
    
    # Contar originais
    original_count = len(re.findall(r'_db_connect\(\)', content))
    print(f"   Encontradas {original_count} ocorrências de _db_connect()")
    
    # Backup
    print(f"💾 Criando backup em {backup_file}...")
    backup_file.write_text(content, encoding='utf-8')
    
    # Aplicar correções
    print(f"🔧 Aplicando correções v3...")
    fixed_content, fixes_count = fix_all_db_connect_v3(content)
    
    # Contar restantes
    remaining_count = len(re.findall(r'_db_connect\(\)', fixed_content))
    
    # Salvar
    print(f"💾 Salvando {input_file}...")
    input_file.write_text(fixed_content, encoding='utf-8')
    
    # Relatório
    print(f"\n✅ Concluído!")
    print(f"   Ocorrências originais: {original_count}")
    print(f"   Padrões corrigidos (v3): {fixes_count}")
    print(f"   Ocorrências restantes: {remaining_count}")
    print(f"   Backup salvo em: {backup_file}")
    
    if remaining_count > 0:
        print(f"\n⚠️  {remaining_count} ocorrências ainda restantes")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
