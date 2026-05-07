#!/usr/bin/env python3
"""
Script para substituir TODAS as ocorrências de _db_connect() de forma automática e segura.
Usa regex para identificar e substituir padrões try/finally.
"""

import re
import sys
from pathlib import Path

def fix_all_db_connect(content: str) -> tuple[str, int]:
    """
    Substitui todos os padrões de _db_connect() por get_db_connection() context manager.
    Retorna (conteúdo_corrigido, número_de_substituições)
    """
    
    fixes_count = 0
    
    # Padrão: variável = _db_connect() seguido de try: ... finally: variável.close()
    # Captura: indentação, nome da variável, corpo do try
    pattern = re.compile(
        r'^(\s+)(conn|con|migration_conn|temp_conn|verify_conn|conn2|conn_vehicle|connection) = _db_connect\(\)\s*\n'
        r'\1try:\s*\n'
        r'((?:(?!\1finally:).*\n)*?)'  # Captura tudo até o finally
        r'\1finally:\s*\n'
        r'\1\s+\2\.close\(\)',
        re.MULTILINE
    )
    
    def replacer(match):
        nonlocal fixes_count
        fixes_count += 1
        
        indent = match.group(1)
        var_name = match.group(2)
        try_body = match.group(3)
        
        # Dedent o corpo do try (remove 4 espaços)
        dedented_lines = []
        for line in try_body.split('\n'):
            if line.strip():  # Linha não vazia
                # Remove 4 espaços se a linha começar com indent + 4 espaços
                expected_indent = indent + '    '
                if line.startswith(expected_indent):
                    dedented_lines.append(indent + line[len(expected_indent):])
                else:
                    dedented_lines.append(line)
            else:
                dedented_lines.append(line)
        
        dedented_body = '\n'.join(dedented_lines)
        
        # Construir o novo código com context manager
        return (
            f'{indent}with get_db_connection() as {var_name}:\n'
            f'{indent}    if USE_POSTGRES:\n'
            f'{indent}        {var_name} = PostgreSQLConnectionWrapper({var_name})\n'
            f'{dedented_body}'
        )
    
    # Aplicar substituição
    new_content = pattern.sub(replacer, content)
    
    return new_content, fixes_count


def main():
    input_file = Path('main.py')
    backup_file = Path('main.py.backup_mass_fix')
    
    if not input_file.exists():
        print(f"❌ Erro: {input_file} não encontrado!")
        return 1
    
    print(f"📖 Lendo {input_file}...")
    content = input_file.read_text(encoding='utf-8')
    
    # Contar ocorrências originais
    original_count = len(re.findall(r'_db_connect\(\)', content))
    print(f"   Encontradas {original_count} ocorrências de _db_connect()")
    
    # Fazer backup
    print(f"💾 Criando backup em {backup_file}...")
    backup_file.write_text(content, encoding='utf-8')
    
    # Aplicar correções
    print(f"🔧 Aplicando correções...")
    fixed_content, fixes_count = fix_all_db_connect(content)
    
    # Contar ocorrências restantes
    remaining_count = len(re.findall(r'_db_connect\(\)', fixed_content))
    
    # Salvar
    print(f"💾 Salvando {input_file}...")
    input_file.write_text(fixed_content, encoding='utf-8')
    
    # Relatório
    print(f"\n✅ Concluído!")
    print(f"   Ocorrências originais: {original_count}")
    print(f"   Padrões corrigidos: {fixes_count}")
    print(f"   Ocorrências restantes: {remaining_count}")
    print(f"   Backup salvo em: {backup_file}")
    
    if remaining_count > 0:
        print(f"\n⚠️  ATENÇÃO: {remaining_count} ocorrências não foram corrigidas automaticamente")
        print(f"   Estas requerem correção manual (padrões não-standard)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
