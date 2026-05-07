#!/usr/bin/env python3
"""
Versão 4: Corrige padrões onde conn = _db_connect() é seguido de conn.close()
mas SEM try/finally explícito.
"""

import re
import sys
from pathlib import Path

def fix_simple_close_pattern(content: str) -> tuple[str, int]:
    """
    Substitui padrões simples:
    
        conn = _db_connect()
        is_postgres = _is_postgresql_connection(conn)
        <código>
        conn.close()
    
    Por:
    
        with get_db_connection() as conn:
            if USE_POSTGRES:
                conn = PostgreSQLConnectionWrapper(conn)
            is_postgres = _is_postgresql_connection(conn)
            <código (sem conn.close())>
    """
    
    fixes_count = 0
    
    # Padrão: conn = _db_connect() ... conn.close() (sem try/finally)
    # Usa lookahead negativo para garantir que não há 'try:' logo após
    pattern = re.compile(
        r'^(\s+)(conn|con) = _db_connect\(\)\s*\n'
        r'(\1is_postgres = _is_postgresql_connection\(\2\)\s*\n)?'  # Linha opcional
        r'(?!\1try:)'  # Lookahead negativo: não deve ter 'try:' logo após
        r'((?:(?!^\1\2\.close\(\)).*\n)*?)'  # Captura até conn.close()
        r'^\1\2\.close\(\)',
        re.MULTILINE
    )
    
    def replacer(match):
        nonlocal fixes_count
        fixes_count += 1
        
        indent = match.group(1)
        var_name = match.group(2)
        is_postgres_line = match.group(3) or ''
        body = match.group(4)
        
        # Dedent o corpo
        dedented_lines = []
        for line in body.split('\n'):
            if line.strip():
                expected_indent = indent
                if line.startswith(expected_indent):
                    # Adicionar 4 espaços de indentação
                    dedented_lines.append(indent + '    ' + line[len(expected_indent):])
                else:
                    dedented_lines.append(line)
            else:
                dedented_lines.append(line)
        
        dedented_body = '\n'.join(dedented_lines)
        
        # Construir novo código
        result = f'{indent}with get_db_connection() as {var_name}:\n'
        result += f'{indent}    if USE_POSTGRES:\n'
        result += f'{indent}        {var_name} = PostgreSQLConnectionWrapper({var_name})\n'
        
        if is_postgres_line:
            result += f'{indent}    is_postgres = _is_postgresql_connection({var_name})\n'
        
        result += dedented_body
        
        return result
    
    new_content = pattern.sub(replacer, content)
    
    return new_content, fixes_count


def main():
    input_file = Path('main.py')
    backup_file = Path('main.py.backup_v4')
    
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
    print(f"🔧 Aplicando correções v4 (padrões simples sem try/finally)...")
    fixed_content, fixes_count = fix_simple_close_pattern(content)
    
    # Contar restantes
    remaining_count = len(re.findall(r'_db_connect\(\)', fixed_content))
    
    # Salvar
    print(f"💾 Salvando {input_file}...")
    input_file.write_text(fixed_content, encoding='utf-8')
    
    # Relatório
    print(f"\n✅ Concluído!")
    print(f"   Ocorrências originais: {original_count}")
    print(f"   Padrões corrigidos (v4): {fixes_count}")
    print(f"   Ocorrências restantes: {remaining_count}")
    print(f"   Backup salvo em: {backup_file}")
    
    if remaining_count > 0:
        print(f"\n⚠️  {remaining_count} ocorrências ainda restantes")
        print(f"   Estas podem ser padrões muito complexos ou especiais")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
