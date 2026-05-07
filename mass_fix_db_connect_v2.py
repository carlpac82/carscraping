#!/usr/bin/env python3
"""
Versão 2: Corrige padrões onde conn = _db_connect() está dentro de um bloco
mas não tem try/finally explícito.
"""

import re
import sys
from pathlib import Path

def find_remaining_patterns(content: str):
    """Encontra padrões restantes de _db_connect()"""
    
    # Padrão: conn = _db_connect() sem try/finally
    # Dentro de um with _db_lock: ou outro bloco
    pattern = re.compile(
        r'^(\s+)(conn|con|migration_conn|temp_conn|verify_conn|conn2|conn_vehicle|connection|conn_verify|conn_check) = _db_connect\(\)\s*$',
        re.MULTILINE
    )
    
    matches = []
    for match in pattern.finditer(content):
        line_num = content[:match.start()].count('\n') + 1
        indent = match.group(1)
        var_name = match.group(2)
        matches.append((line_num, indent, var_name, match.start(), match.end()))
    
    return matches

def fix_pattern_v2(content: str, line_num: int, indent: str, var_name: str, start_pos: int, end_pos: int) -> str:
    """
    Corrige um padrão individual substituindo:
    
        conn = _db_connect()
        <código>
        conn.close()
    
    Por:
    
        with get_db_connection() as conn:
            if USE_POSTGRES:
                conn = PostgreSQLConnectionWrapper(conn)
            <código (sem conn.close())>
    """
    
    # Encontrar o bloco de código que usa esta conexão
    # Procurar até encontrar conn.close() ou fim do bloco
    
    lines_after = content[end_pos:].split('\n')
    block_lines = []
    found_close = False
    close_line_idx = -1
    
    for idx, line in enumerate(lines_after):
        if f'{var_name}.close()' in line:
            found_close = True
            close_line_idx = idx
            break
        block_lines.append(line)
    
    if not found_close:
        # Não encontrou .close() - não mexer
        return None
    
    # Reconstruir o bloco
    block_content = '\n'.join(block_lines)
    
    # Dedent o bloco (remove um nível de indentação)
    dedented_lines = []
    for line in block_content.split('\n'):
        if line.strip():
            if line.startswith(indent + '    '):
                dedented_lines.append(indent + line[len(indent + '    '):])
            else:
                dedented_lines.append(line)
        else:
            dedented_lines.append(line)
    
    dedented_block = '\n'.join(dedented_lines)
    
    # Construir novo código
    new_code = (
        f'{indent}with get_db_connection() as {var_name}:\n'
        f'{indent}    if USE_POSTGRES:\n'
        f'{indent}        {var_name} = PostgreSQLConnectionWrapper({var_name})\n'
        f'{dedented_block}'
    )
    
    # Calcular posição final (incluindo a linha do .close())
    end_of_close = end_pos + sum(len(l) + 1 for l in lines_after[:close_line_idx + 1])
    
    return (start_pos, end_of_close, new_code)


def main():
    input_file = Path('main.py')
    
    if not input_file.exists():
        print(f"❌ Erro: {input_file} não encontrado!")
        return 1
    
    print(f"📖 Lendo {input_file}...")
    content = input_file.read_text(encoding='utf-8')
    
    # Encontrar padrões restantes
    print(f"🔍 Procurando padrões restantes...")
    matches = find_remaining_patterns(content)
    
    print(f"   Encontrados {len(matches)} padrões restantes")
    
    # Mostrar primeiros 20
    print(f"\n📋 Primeiros 20 padrões:")
    for i, (line_num, indent, var_name, start, end) in enumerate(matches[:20]):
        print(f"   {i+1}. Linha {line_num}: {var_name} = _db_connect()")
    
    if len(matches) > 20:
        print(f"   ... e mais {len(matches) - 20}")
    
    print(f"\n⚠️  Estes padrões requerem análise manual para garantir correção segura")
    print(f"   Muitos podem estar em blocos complexos ou ter lógica especial")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
