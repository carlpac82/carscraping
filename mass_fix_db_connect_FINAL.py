#!/usr/bin/env python3
"""
Versão FINAL: Captura TODOS os padrões restantes de _db_connect()
incluindo variações com is_postgres = os.environ...
"""

import re
import sys
from pathlib import Path

def fix_all_remaining_patterns(content: str) -> tuple[str, int]:
    """Corrige todos os padrões restantes"""
    
    fixes_count = 0
    
    # Padrão 1: com is_postgres = os.environ.get(...)
    pattern1 = re.compile(
        r'^(\s+)(conn|con|migration_conn|temp_conn|verify_conn|conn2|conn_vehicle|connection|conn_verify|conn_check|conn_temp|conn_user) = _db_connect\(\)\s*\n'
        r'\1is_postgres = os\.environ\.get\([^)]+\)\.startswith\([^)]+\)\s*\n'
        r'\1try:\s*\n'
        r'((?:(?!^\1finally:).*\n)*?)'
        r'^\1finally:\s*\n'
        r'\1\s+\2\.close\(\)',
        re.MULTILINE
    )
    
    def replacer1(match):
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
            f'{indent}    is_postgres = os.environ.get(\'DATABASE_URL\', \'\').startswith(\'postgresql\')\n'
            f'{dedented_body}'
        )
    
    content = pattern1.sub(replacer1, content)
    
    # Padrão 2: Conexões aninhadas dentro de blocos (sem try/finally próprio)
    # Exemplo: dentro de um if/else, apenas conn = _db_connect() ... conn.close()
    pattern2 = re.compile(
        r'^(\s+)(conn|con|migration_conn|temp_conn|verify_conn|conn2|conn_vehicle|connection|conn_verify|conn_check|conn_temp|conn_user) = _db_connect\(\)\s*\n'
        r'(?!\1try:)(?!\1is_postgres)'  # Não tem try: ou is_postgres logo após
        r'((?:(?!^\1\2\.close\(\)).*\n)*?)'
        r'^\1\2\.close\(\)',
        re.MULTILINE
    )
    
    def replacer2(match):
        nonlocal fixes_count
        fixes_count += 1
        
        indent = match.group(1)
        var_name = match.group(2)
        body = match.group(3)
        
        # Indent o corpo (adicionar 4 espaços)
        indented_lines = []
        for line in body.split('\n'):
            if line.strip():
                indented_lines.append(indent + '    ' + line[len(indent):] if line.startswith(indent) else line)
            else:
                indented_lines.append(line)
        
        indented_body = '\n'.join(indented_lines)
        
        return (
            f'{indent}with get_db_connection() as {var_name}:\n'
            f'{indent}    if USE_POSTGRES:\n'
            f'{indent}        {var_name} = PostgreSQLConnectionWrapper({var_name})\n'
            f'{indented_body}'
        )
    
    content = pattern2.sub(replacer2, content)
    
    return content, fixes_count


def main():
    input_file = Path('main.py')
    backup_file = Path('main.py.backup_FINAL')
    
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
    print(f"🔧 Aplicando correções FINAIS...")
    fixed_content, fixes_count = fix_all_remaining_patterns(content)
    
    # Contar restantes
    remaining_count = len(re.findall(r'_db_connect\(\)', fixed_content))
    
    # Salvar
    print(f"💾 Salvando {input_file}...")
    input_file.write_text(fixed_content, encoding='utf-8')
    
    # Relatório
    print(f"\n✅ Concluído!")
    print(f"   Ocorrências originais: {original_count}")
    print(f"   Padrões corrigidos (FINAL): {fixes_count}")
    print(f"   Ocorrências restantes: {remaining_count}")
    print(f"   Backup salvo em: {backup_file}")
    
    if remaining_count > 0:
        print(f"\n⚠️  {remaining_count} ocorrências ainda restantes")
        print(f"   Estas são provavelmente:")
        print(f"   - Comentários")
        print(f"   - Docstrings")
        print(f"   - Definição da função _db_connect() em si")
    else:
        print(f"\n🎉 TODAS as ocorrências foram corrigidas!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
