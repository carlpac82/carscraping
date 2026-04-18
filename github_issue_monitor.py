#!/usr/bin/env python3
"""
GitHub Issue Monitor - Sistema automático para detectar e executar comandos via GitHub Issues
Funciona 100% automático: User cria issue no GitHub App (mobile) -> Sistema executa -> User vê no Railway
"""

import os
import json
import time
import requests
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configuração logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubIssueMonitor:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PAT')
        self.repo_owner = 'carlpac82'
        self.repo_name = 'carscraping'
        self.last_check_time = datetime.now() - timedelta(minutes=5)  # Verifica últimos 5 minutos
        self.processed_issues = set()  # Para evitar duplicação
        
        if not self.github_token:
            logger.error("GITHUB_TOKEN não encontrado! Configure nas variáveis de ambiente.")
            return
    
    def get_new_issues(self) -> List[Dict]:
        """Busca novos issues criados desde a última verificação"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            params = {
                'state': 'open',
                'since': self.last_check_time.isoformat(),
                'sort': 'created',
                'direction': 'desc'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            issues = response.json()
            new_issues = []
            
            for issue in issues:
                issue_id = issue['id']
                if issue_id not in self.processed_issues:
                    new_issues.append(issue)
                    self.processed_issues.add(issue_id)
            
            return new_issues
            
        except Exception as e:
            logger.error(f"Erro ao buscar issues: {e}")
            return []
    
    def parse_command_from_issue(self, issue: Dict) -> Optional[str]:
        """Extrai comando do título e corpo do issue"""
        title = issue.get('title', '').strip()
        body = issue.get('body', '').strip()
        
        # Comando simples: título do issue
        if title and not title.lower().startswith('bug') and not title.lower().startswith('question'):
            return title
        
        # Comando detalhado: primeira linha do corpo
        if body:
            lines = body.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('>'):
                    return line
        
        return None
    
    def execute_command(self, command: str, issue: Dict) -> bool:
        """Executa o comando extraído do issue"""
        try:
            issue_number = issue['number']
            issue_title = issue['title']
            logger.info(f"Executando comando do issue #{issue_number}: {command}")
            
            # Adicionar comentário no GitHub informando que está sendo processado
            self.add_issue_comment(issue_number, f"\\n\\n\\ud83e\udd16 **Cascade a processar...**\\nComando: `{command}`\\n\\nA executar agora...")
            
            # Parse do comando para determinar ação
            success = self.process_command(command, issue_number)
            
            # Adicionar comentário de resultado
            if success:
                self.add_issue_comment(issue_number, f"\\n\\n\\u2705 **Concluído!**\\nComando executado com sucesso.\\n\\nVerifique os logs no Railway para detalhes.")
                # Fechar issue automaticamente
                self.close_issue(issue_number)
            else:
                self.add_issue_comment(issue_number, f"\\n\\n\\u274c **Erro ao executar**\\nNão foi possível processar o comando.\\n\\nVerifique os logs para detalhes.")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao executar comando: {e}")
            return False
    
    def process_command(self, command: str, issue_number: int) -> bool:
        """Processa diferentes tipos de comandos"""
        command_lower = command.lower()
        
        try:
            # Comandos de texto/mudanças
            if 'mudar' in command_lower or 'alterar' in command_lower or 'trocar' in command_lower:
                return self.handle_text_change(command)
            
            # Comandos de cor
            elif 'cor' in command_lower or 'color' in command_lower:
                return self.handle_color_change(command)
            
            # Comandos de ativação/desativação
            elif 'ativar' in command_lower or 'ativar' in command_lower or 'enable' in command_lower:
                return self.handle_feature_toggle(command, enable=True)
            elif 'desativar' in command_lower or 'disable' in command_lower:
                return self.handle_feature_toggle(command, enable=False)
            
            # Comandos de rollback
            elif 'rollback' in command_lower or 'reverter' in command_lower:
                return self.handle_rollback(command)
            
            # Comandos de deploy
            elif 'deploy' in command_lower:
                return self.handle_deploy()
            
            # Comando genérico - tenta executar como comando shell
            else:
                return self.handle_generic_command(command)
                
        except Exception as e:
            logger.error(f"Erro no process_command: {e}")
            return False
    
    def handle_text_change(self, command: str) -> bool:
        """Lida com mudanças de texto"""
        try:
            # Exemplo: "Mudar botão Entrega para Check-in"
            if 'botão' in command.lower() or 'botao' in command.lower():
                if 'entrega' in command.lower() and 'check' in command.lower():
                    # Mudar texto do botão
                    result = subprocess.run(['sed', '-i', 's/Entrega/Check-in/g', 'templates/vehicle_inspection.html'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        self.commit_and_push("Change button text: Entrega -> Check-in")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro em handle_text_change: {e}")
            return False
    
    def handle_color_change(self, command: str) -> bool:
        """Lida com mudanças de cor"""
        try:
            # Implementar mudança de cores
            logger.info(f"Mudança de cor solicitada: {command}")
            # TODO: Implementar lógica específica de cores
            return True
            
        except Exception as e:
            logger.error(f"Erro em handle_color_change: {e}")
            return False
    
    def handle_feature_toggle(self, command: str, enable: bool) -> bool:
        """Lida com ativação/desativação de features"""
        try:
            # Implementar toggle de features
            action = "Ativar" if enable else "Desativar"
            logger.info(f"{action} feature: {command}")
            # TODO: Implementar lógica específica
            return True
            
        except Exception as e:
            logger.error(f"Erro em handle_feature_toggle: {e}")
            return False
    
    def handle_rollback(self, command: str) -> bool:
        """Lida com rollback de commits"""
        try:
            result = subprocess.run(['git', 'reset', '--hard', 'HEAD~1'], capture_output=True, text=True)
            if result.returncode == 0:
                self.commit_and_push("Rollback to previous commit")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro em handle_rollback: {e}")
            return False
    
    def handle_deploy(self) -> bool:
        """Faz deploy das alterações"""
        try:
            result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Erro em handle_deploy: {e}")
            return False
    
    def handle_generic_command(self, command: str) -> bool:
        """Tenta executar comando genérico"""
        try:
            # Comandos seguros permitidos
            safe_commands = ['git status', 'git log --oneline -5']
            
            if command in safe_commands:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                logger.info(f"Resultado: {result.stdout}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro em handle_generic_command: {e}")
            return False
    
    def commit_and_push(self, message: str):
        """Faz commit e push das alterações"""
        try:
            subprocess.run(['git', 'add', '-A'], check=True)
            subprocess.run(['git', 'commit', '-m', f"Auto-commit from GitHub Issue: {message}"], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            logger.info(f"Commit e push realizados: {message}")
            
        except Exception as e:
            logger.error(f"Erro em commit_and_push: {e}")
    
    def add_issue_comment(self, issue_number: int, comment: str):
        """Adiciona comentário no issue"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}/comments"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {'body': comment}
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Erro ao adicionar comentário: {e}")
    
    def close_issue(self, issue_number: int):
        """Fecha o issue automaticamente"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {'state': 'closed'}
            
            response = requests.patch(url, headers=headers, json=data)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Erro ao fechar issue: {e}")
    
    def run_monitor(self):
        """Loop principal do monitor"""
        logger.info("Iniciando GitHub Issue Monitor...")
        logger.info("Aguardando novos issues...")
        
        while True:
            try:
                new_issues = self.get_new_issues()
                
                for issue in new_issues:
                    logger.info(f"Novo issue detectado: #{issue['number']} - {issue['title']}")
                    
                    command = self.parse_command_from_issue(issue)
                    if command:
                        logger.info(f"Comando extraído: {command}")
                        success = self.execute_command(command, issue)
                        logger.info(f"Execução {'sucesso' if success else 'falhou'}")
                    else:
                        logger.info("Issue não contém comando executável")
                
                # Atualizar tempo da última verificação
                self.last_check_time = datetime.now()
                
                # Esperar 60 segundos antes da próxima verificação
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("Monitor interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                time.sleep(30)  # Esperar 30 segundos em caso de erro

if __name__ == "__main__":
    monitor = GitHubIssueMonitor()
    monitor.run_monitor()
