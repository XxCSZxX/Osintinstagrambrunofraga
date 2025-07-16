#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de OSINT para investigação de perfis do Instagram
Script criado para o Aulão Semanal #086 com foco em Investigação de Contas do Instagram.
Para acompanhar minhas aulas de investigação digital, haking e privacidade, acesse: https://aulao.brunofraga.com/

Autor: Bruno Fraga @brunofragax
Versão: I don't know - script rapido - criado com manus.ai em 15min - porém efetivo)
"""

import requests
import json
import csv
import argparse
import sys
import os
from urllib.parse import quote_plus
from datetime import datetime
import time

class Colors:
    """Cores para output no terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class InstagramInvestigatorCLI:
    def __init__(self):
        self.current_data = None
        
    def print_banner(self):
        """Exibe banner da aplicação"""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                      Instagram OSINT                         ║
║          Ferramenta criada para o Aulão com Bruno Fraga      ║
║                                                              ║
║           Para fins educacionais e investigativos.           ║
║                                                              ║
║                        @brunofragax                          ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
        print(banner)
        
    def print_tutorial(self):
        """Exibe tutorial para obter session ID"""
        tutorial = f"""
{Colors.OKCYAN}{Colors.BOLD}📋 Como obter o Session ID do Instagram:{Colors.ENDC}

{Colors.OKBLUE}1.{Colors.ENDC} Abra o Instagram no navegador e faça login
{Colors.OKBLUE}2.{Colors.ENDC} Pressione F12 para abrir as ferramentas de desenvolvedor
{Colors.OKBLUE}3.{Colors.ENDC} Vá na aba "Application" ou "Aplicação"
{Colors.OKBLUE}4.{Colors.ENDC} No menu lateral, clique em "Cookies" → "https://www.instagram.com"
{Colors.OKBLUE}5.{Colors.ENDC} Procure por "sessionid" e copie o valor

{Colors.WARNING}⚠️  IMPORTANTE: Mantenha seu session ID seguro e não compartilhe!{Colors.ENDC}
"""
        print(tutorial)
        
    def get_user_input(self):
        """Coleta dados do usuário via input interativo"""
        print(f"\n{Colors.BOLD}🔍 Dados para Investigação:{Colors.ENDC}")
        
        # Username
        while True:
            username = input(f"{Colors.OKGREEN}👤 Username do Instagram (sem @): {Colors.ENDC}").strip()
            if username:
                # Remove @ se presente
                if username.startswith('@'):
                    username = username[1:]
                    print(f"{Colors.WARNING}   @ removido automaticamente{Colors.ENDC}")
                
                # Validação básica
                if username.replace('_', '').replace('.', '').isalnum():
                    break
                else:
                    print(f"{Colors.FAIL}❌ Username inválido! Use apenas letras, números, pontos e underscores.{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}❌ Username é obrigatório!{Colors.ENDC}")
        
        # Session ID
        while True:
            session_id = input(f"{Colors.OKGREEN}🔑 Session ID do Instagram: {Colors.ENDC}").strip()
            if session_id:
                break
            else:
                print(f"{Colors.FAIL}❌ Session ID é obrigatório!{Colors.ENDC}")
                
        return username, session_id
        
    def show_progress(self, message):
        """Mostra progresso da operação"""
        print(f"{Colors.OKCYAN}⏳ {message}...{Colors.ENDC}")
        
    def show_success(self, message):
        """Mostra mensagem de sucesso"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
        
    def show_error(self, message):
        """Mostra mensagem de erro"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
        
    def show_warning(self, message):
        """Mostra mensagem de aviso"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
        
    def get_user_id(self, username, session_id):
        """Obtém ID do usuário a partir do username"""
        headers = {"User-Agent": "iphone_ua", "x-ig-app-id": "936619743392459"}
        url = f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}'
        
        try:
            response = requests.get(url, headers=headers, cookies={'sessionid': session_id}, timeout=30)
            
            if response.status_code == 404:
                return {"id": None, "error": "Usuário não encontrado"}
                
            data = response.json()
            user_id = data["data"]["user"]["id"]
            return {"id": user_id, "error": None}
            
        except requests.exceptions.RequestException as e:
            return {"id": None, "error": f"Erro de rede: {str(e)}"}
        except json.JSONDecodeError:
            return {"id": None, "error": "Rate limit atingido ou resposta inválida"}
        except KeyError:
            return {"id": None, "error": "Formato de resposta inválido"}
            
    def get_user_info(self, user_id, session_id):
        """Obtém informações detalhadas do usuário"""
        headers = {'User-Agent': 'Instagram 64.0.0.14.96'}
        url = f'https://i.instagram.com/api/v1/users/{user_id}/info/'
        
        try:
            response = requests.get(url, headers=headers, cookies={'sessionid': session_id}, timeout=30)
            
            if response.status_code == 429:
                return {"user": None, "error": "Rate limit atingido"}
                
            response.raise_for_status()
            data = response.json()
            
            user_info = data.get("user")
            if not user_info:
                return {"user": None, "error": "Usuário não encontrado"}
                
            user_info["userID"] = user_id
            return {"user": user_info, "error": None}
            
        except requests.exceptions.RequestException as e:
            return {"user": None, "error": f"Erro de rede: {str(e)}"}
        except json.JSONDecodeError:
            return {"user": None, "error": "Resposta inválida"}
            
    def advanced_lookup(self, username):
        """Realiza lookup avançado para informações ofuscadas"""
        data_payload = "signed_body=SIGNATURE." + quote_plus(json.dumps(
            {"q": username, "skip_recovery": "1"}, separators=(",", ":")
        ))
        
        headers = {
            "Accept-Language": "en-US",
            "User-Agent": "Instagram 101.0.0.15.120",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-IG-App-ID": "124024574287414",
            "Accept-Encoding": "gzip, deflate",
            "Host": "i.instagram.com",
            "Connection": "keep-alive",
            "Content-Length": str(len(data_payload))
        }
        
        try:
            response = requests.post('https://i.instagram.com/api/v1/users/lookup/',
                                   headers=headers, data=data_payload, timeout=30)
            
            data = response.json()
            return {"user": data, "error": None}
            
        except requests.exceptions.RequestException as e:
            return {"user": None, "error": f"Erro de rede: {str(e)}"}
        except json.JSONDecodeError:
            return {"user": None, "error": "Rate limit"}
            
    def investigate_profile(self, username, session_id):
        """Executa investigação completa do perfil"""
        try:
            # Passo 1: Obter ID do usuário
            self.show_progress("Obtendo ID do usuário")
            user_id_data = self.get_user_id(username, session_id)
            
            if user_id_data.get("error"):
                raise Exception(user_id_data["error"])
                
            user_id = user_id_data["id"]
            self.show_success(f"ID encontrado: {user_id}")
            
            # Pequeno delay para evitar rate limiting
            time.sleep(1)
            
            # Passo 2: Obter informações detalhadas
            self.show_progress("Coletando informações detalhadas")
            info_data = self.get_user_info(user_id, session_id)
            
            if info_data.get("error"):
                raise Exception(info_data["error"])
                
            user_info = info_data["user"]
            self.show_success("Informações básicas coletadas")
            
            # Pequeno delay para evitar rate limiting
            time.sleep(1)
            
            # Passo 3: Lookup avançado
            self.show_progress("Realizando lookup avançado")
            advanced_data = self.advanced_lookup(username)
            
            if not advanced_data.get("error"):
                self.show_success("Lookup avançado concluído")
            else:
                self.show_warning("Lookup avançado falhou (rate limit)")
            
            # Combina dados
            combined_data = {**user_info, **advanced_data.get("user", {})}
            self.current_data = combined_data
            
            return combined_data
            
        except Exception as e:
            raise Exception(f"Falha na investigação: {str(e)}")
            
    def display_results(self, data):
        """Exibe os resultados da investigação"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
        print(f"📊 RESULTADOS DA INVESTIGAÇÃO")
        print(f"{'='*70}{Colors.ENDC}")
        
        # Informações básicas
        print(f"\n{Colors.BOLD}👤 INFORMAÇÕES BÁSICAS:{Colors.ENDC}")
        print(f"   Username: {Colors.OKGREEN}{data.get('username', 'N/A')}{Colors.ENDC}")
        print(f"   User ID: {Colors.OKGREEN}{data.get('userID', 'N/A')}{Colors.ENDC}")
        print(f"   Nome Completo: {Colors.OKGREEN}{data.get('full_name', 'N/A')}{Colors.ENDC}")
        print(f"   Verificado: {Colors.OKGREEN if data.get('is_verified') else Colors.FAIL}{'Sim' if data.get('is_verified') else 'Não'}{Colors.ENDC}")
        print(f"   Conta Business: {Colors.OKGREEN if data.get('is_business') else Colors.FAIL}{'Sim' if data.get('is_business') else 'Não'}{Colors.ENDC}")
        print(f"   Conta Privada: {Colors.FAIL if data.get('is_private') else Colors.OKGREEN}{'Sim' if data.get('is_private') else 'Não'}{Colors.ENDC}")
        
        # Estatísticas
        print(f"\n{Colors.BOLD}📈 ESTATÍSTICAS:{Colors.ENDC}")
        print(f"   Seguidores: {Colors.OKCYAN}{data.get('follower_count', 'N/A'):,}{Colors.ENDC}")
        print(f"   Seguindo: {Colors.OKCYAN}{data.get('following_count', 'N/A'):,}{Colors.ENDC}")
        print(f"   Posts: {Colors.OKCYAN}{data.get('media_count', 'N/A'):,}{Colors.ENDC}")
        print(f"   Vídeos IGTV: {Colors.OKCYAN}{data.get('total_igtv_videos', 'N/A')}{Colors.ENDC}")
        
        # Informações de contato
        print(f"\n{Colors.BOLD}📞 INFORMAÇÕES DE CONTATO:{Colors.ENDC}")
        if data.get('public_email'):
            print(f"   Email Público: {Colors.OKGREEN}{data['public_email']}{Colors.ENDC}")
        if data.get('public_phone_number'):
            phone = f"+{data.get('public_phone_country_code', '')} {data['public_phone_number']}"
            print(f"   Telefone Público: {Colors.OKGREEN}{phone}{Colors.ENDC}")
        if data.get('obfuscated_email'):
            print(f"   Email Ofuscado: {Colors.WARNING}{data['obfuscated_email']}{Colors.ENDC}")
        if data.get('obfuscated_phone'):
            print(f"   Telefone Ofuscado: {Colors.WARNING}{data['obfuscated_phone']}{Colors.ENDC}")
        
        print(f"   WhatsApp Vinculado: {Colors.OKGREEN if data.get('is_whatsapp_linked') else Colors.FAIL}{'Sim' if data.get('is_whatsapp_linked') else 'Não'}{Colors.ENDC}")
        
        # Outras informações
        print(f"\n{Colors.BOLD}🔗 OUTRAS INFORMAÇÕES:{Colors.ENDC}")
        if data.get('external_url'):
            print(f"   URL Externa: {Colors.OKCYAN}{data['external_url']}{Colors.ENDC}")
        if data.get('biography'):
            bio = data['biography'][:100] + "..." if len(data.get('biography', '')) > 100 else data.get('biography', '')
            print(f"   Biografia: {Colors.OKCYAN}{bio}{Colors.ENDC}")
        if data.get('hd_profile_pic_url_info', {}).get('url'):
            print(f"   Foto de Perfil: {Colors.OKCYAN}{data['hd_profile_pic_url_info']['url']}{Colors.ENDC}")
            
        print(f"\n{Colors.HEADER}{'='*70}")
        print(f"⏰ Investigação concluída em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*70}{Colors.ENDC}")
        
    def export_data(self, data, format_type, filename=None):
        """Exporta dados em diferentes formatos"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            username = data.get('username', 'unknown')
            filename = f"instagram_{username}_{timestamp}"
            
        try:
            if format_type.lower() == 'json':
                filename += '.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
            elif format_type.lower() == 'csv':
                filename += '.csv'
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Campo', 'Valor'])
                    
                    for key, value in data.items():
                        if isinstance(value, dict):
                            continue
                        writer.writerow([key, str(value)])
                        
            self.show_success(f"Dados exportados para: {filename}")
            return filename
            
        except Exception as e:
            self.show_error(f"Erro ao exportar: {str(e)}")
            return None
            
    def interactive_mode(self):
        """Modo interativo da aplicação"""
        self.print_banner()
        
        while True:
            print(f"\n{Colors.BOLD}🔍 MENU PRINCIPAL:{Colors.ENDC}")
            print(f"{Colors.OKBLUE}1.{Colors.ENDC} Nova investigação")
            print(f"{Colors.OKBLUE}2.{Colors.ENDC} Ver tutorial (como obter Session ID)")
            print(f"{Colors.OKBLUE}3.{Colors.ENDC} Exportar última investigação")
            print(f"{Colors.OKBLUE}4.{Colors.ENDC} Sair")
            
            choice = input(f"\n{Colors.OKGREEN}Escolha uma opção (1-4): {Colors.ENDC}").strip()
            
            if choice == '1':
                try:
                    username, session_id = self.get_user_input()
                    print(f"\n{Colors.BOLD}🔍 Iniciando investigação de: @{username}{Colors.ENDC}")
                    
                    data = self.investigate_profile(username, session_id)
                    self.display_results(data)
                    
                    # Pergunta se quer exportar
                    export = input(f"\n{Colors.OKGREEN}Deseja exportar os dados? (s/N): {Colors.ENDC}").strip().lower()
                    if export in ['s', 'sim', 'y', 'yes']:
                        format_choice = input(f"{Colors.OKGREEN}Formato (json/csv): {Colors.ENDC}").strip().lower()
                        if format_choice in ['json', 'csv']:
                            self.export_data(data, format_choice)
                        
                except Exception as e:
                    self.show_error(str(e))
                    
            elif choice == '2':
                self.print_tutorial()
                
            elif choice == '3':
                if self.current_data:
                    format_choice = input(f"{Colors.OKGREEN}Formato (json/csv): {Colors.ENDC}").strip().lower()
                    if format_choice in ['json', 'csv']:
                        self.export_data(self.current_data, format_choice)
                    else:
                        self.show_error("Formato inválido! Use 'json' ou 'csv'")
                else:
                    self.show_warning("Nenhuma investigação realizada ainda!")
                    
            elif choice == '4':
                print(f"\n{Colors.OKGREEN}👋 Obrigado por usar o Instagram Investigator!{Colors.ENDC}")
                break
                
            else:
                self.show_error("Opção inválida! Escolha entre 1-4.")

def main():
    parser = argparse.ArgumentParser(description='Instagram Investigator - Ferramenta OSINT Simplificada')
    parser.add_argument('-u', '--username', help='Username do Instagram (sem @)')
    parser.add_argument('-s', '--sessionid', help='Session ID do Instagram')
    parser.add_argument('-o', '--output', help='Arquivo de saída (sem extensão)')
    parser.add_argument('-f', '--format', choices=['json', 'csv'], default='json', help='Formato de exportação')
    parser.add_argument('--tutorial', action='store_true', help='Mostra tutorial para obter Session ID')
    
    args = parser.parse_args()
    
    app = InstagramInvestigatorCLI()
    
    if args.tutorial:
        app.print_banner()
        app.print_tutorial()
        return
        
    if args.username and args.sessionid:
        # Modo linha de comando
        app.print_banner()
        
        try:
            username = args.username.lstrip('@')
            print(f"\n{Colors.BOLD}🔍 Investigando: @{username}{Colors.ENDC}")
            
            data = app.investigate_profile(username, args.sessionid)
            app.display_results(data)
            
            if args.output:
                app.export_data(data, args.format, args.output)
            else:
                # Pergunta se quer exportar
                export = input(f"\n{Colors.OKGREEN}Deseja exportar os dados? (s/N): {Colors.ENDC}").strip().lower()
                if export in ['s', 'sim', 'y', 'yes']:
                    app.export_data(data, args.format)
                    
        except Exception as e:
            app.show_error(str(e))
            sys.exit(1)
    else:
        # Modo interativo
        app.interactive_mode()

if __name__ == "__main__":
    main()

