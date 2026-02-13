#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de OSINT para investigação de perfis do Instagram
Script original de Bruno Fraga @brunofragax
Restaurado e Corrigido por Manus AI (Otimizado para Kali Linux)
"""

import requests
import json
import csv
import argparse
import sys
import os
import re
from urllib.parse import quote_plus
from datetime import datetime
import time
import random

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
        self.session = requests.Session()
        # User-Agent de alta fidelidade para evitar bloqueios no Kali
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        
    def print_banner(self):
        """Exibe banner da aplicação original"""
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
        """Exibe tutorial original para obter session ID"""
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
        
        while True:
            username = input(f"{Colors.OKGREEN}👤 Username do Instagram (sem @): {Colors.ENDC}").strip()
            if username:
                if username.startswith('@'):
                    username = username[1:]
                    print(f"{Colors.WARNING}   @ removido automaticamente{Colors.ENDC}")
                if username.replace('_', '').replace('.', '').isalnum():
                    break
                else:
                    print(f"{Colors.FAIL}❌ Username inválido!{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}❌ Username é obrigatório!{Colors.ENDC}")
        
        while True:
            session_id = input(f"{Colors.OKGREEN}🔑 Session ID do Instagram: {Colors.ENDC}").strip()
            if session_id:
                break
            else:
                print(f"{Colors.FAIL}❌ Session ID é obrigatório!{Colors.ENDC}")
                
        return username, session_id
        
    def show_progress(self, message):
        print(f"{Colors.OKCYAN}⏳ {message}...{Colors.ENDC}")
        
    def show_success(self, message):
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
        
    def show_error(self, message):
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
        
    def show_warning(self, message):
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

    def get_user_id(self, username, session_id):
        """Obtém ID do usuário com headers avançados e fallbacks"""
        # Headers de alta fidelidade para Kali Linux
        headers = {
            "authority": "www.instagram.com",
            "accept": "*/*",
            "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "referer": f"https://www.instagram.com/{username}/",
            "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self.user_agent,
            "x-asbd-id": "129477",
            "x-ig-app-id": "936619743392459",
            "x-ig-www-claim": "0",
            "x-requested-with": "XMLHttpRequest"
        }
        url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}'
        
        try:
            response = self.session.get(url, headers=headers, cookies={'sessionid': session_id}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                user_id = data["data"]["user"]["id"]
                return {"id": user_id, "error": None, "web_info": data["data"]["user"]}
        except:
            pass

        # Fallback HTML Scraping robusto
        try:
            url_html = f'https://www.instagram.com/{username}/'
            resp_html = self.session.get(url_html, headers={"User-Agent": self.user_agent}, cookies={'sessionid': session_id}, timeout=30)
            for pattern in [r'"profilePage_([0-9]+)"', r'"user_id":"([0-9]+)"', r'"id":"([0-9]+)"']:
                match = re.search(pattern, resp_html.text)
                if match: return {"id": match.group(1), "error": None}
        except:
            pass

        return {"id": None, "error": "Não foi possível obter o ID do usuário."}

    def get_user_info(self, user_id, session_id):
        """Obtém informações detalhadas via API interna"""
        headers = {
            'User-Agent': 'Instagram 64.0.0.14.96',
            'X-IG-App-ID': '936619743392459',
            'Cookie': f'sessionid={session_id}'
        }
        url = f'https://i.instagram.com/api/v1/users/{user_id}/info/'
        try:
            response = self.session.get(url, headers=headers, timeout=30)
            data = response.json()
            user_info = data.get("user")
            if user_info:
                user_info["userID"] = user_id
                return {"user": user_info, "error": None}
        except:
            pass
        return {"user": None, "error": "Falha ao obter informações detalhadas."}

    def advanced_lookup(self, username):
        """Lookup avançado original"""
        data_payload = "signed_body=SIGNATURE." + quote_plus(json.dumps(
            {"q": username, "skip_recovery": "1"}, separators=(",", ":")
        ))
        headers = {
            "User-Agent": "Instagram 101.0.0.15.120",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-IG-App-ID": "124024574287414",
        }
        try:
            response = self.session.post('https://i.instagram.com/api/v1/users/lookup/', headers=headers, data=data_payload, timeout=30)
            return {"user": response.json(), "error": None}
        except:
            return {"user": {}, "error": "Lookup avançado falhou"}

    def investigate_profile(self, username, session_id):
        """Executa investigação completa com estrutura original"""
        try:
            self.show_progress("Obtendo ID do usuário")
            id_data = self.get_user_id(username, session_id)
            if id_data.get("error"): raise Exception(id_data["error"])
            user_id = id_data["id"]
            self.show_success(f"ID encontrado: {user_id}")
            
            time.sleep(2) # Delay humano
            self.show_progress("Coletando informações detalhadas")
            info_data = self.get_user_info(user_id, session_id)
            user_info = info_data.get("user", {})
            
            time.sleep(1)
            self.show_progress("Realizando lookup avançado")
            advanced = self.advanced_lookup(username)
            advanced_info = advanced.get("user", {})
            
            combined = {**(id_data.get("web_info", {})), **user_info, **advanced_info}
            self.current_data = combined
            return combined
        except Exception as e:
            raise Exception(f"Falha na investigação: {str(e)}")

    def display_results(self, data):
        """Exibe resultados com layout original"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
        print(f"📊 RESULTADOS DA INVESTIGAÇÃO")
        print(f"{'='*70}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}👤 INFORMAÇÕES BÁSICAS:{Colors.ENDC}")
        print(f"   Username: {Colors.OKGREEN}{data.get('username', 'N/A')}{Colors.ENDC}")
        print(f"   User ID: {Colors.OKGREEN}{data.get('userID', data.get('pk', 'N/A'))}{Colors.ENDC}")
        print(f"   Nome Completo: {Colors.OKGREEN}{data.get('full_name', 'N/A')}{Colors.ENDC}")
        print(f"   Verificado: {Colors.OKGREEN if data.get('is_verified') else Colors.FAIL}{'Sim' if data.get('is_verified') else 'Não'}{Colors.ENDC}")
        print(f"   Conta Business: {Colors.OKGREEN if data.get('is_business') else Colors.FAIL}{'Sim' if data.get('is_business') else 'Não'}{Colors.ENDC}")
        print(f"   Conta Privada: {Colors.FAIL if data.get('is_private') else Colors.OKGREEN}{'Sim' if data.get('is_private') else 'Não'}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}📈 ESTATÍSTICAS:{Colors.ENDC}")
        print(f"   Seguidores: {Colors.OKCYAN}{data.get('follower_count', 'N/A')}{Colors.ENDC}")
        print(f"   Seguindo: {Colors.OKCYAN}{data.get('following_count', 'N/A')}{Colors.ENDC}")
        print(f"   Posts: {Colors.OKCYAN}{data.get('media_count', 'N/A')}{Colors.ENDC}")
        
        if data.get('public_email'):
            print(f"   Email Público: {Colors.OKGREEN}{data['public_email']}{Colors.ENDC}")
        if data.get('obfuscated_email'):
            print(f"   Email Ofuscado: {Colors.WARNING}{data['obfuscated_email']}{Colors.ENDC}")
        
        print(f"\n{Colors.HEADER}{'='*70}")
        print(f"⏰ Investigação concluída em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*70}{Colors.ENDC}")

    def export_data(self, data, format_type, filename=None):
        """Função de exportação original completa"""
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
                        if not isinstance(value, (dict, list)):
                            writer.writerow([key, str(value)])
            self.show_success(f"Dados exportados para: {filename}")
            return filename
        except Exception as e:
            self.show_error(f"Erro ao exportar: {str(e)}")
            return None

    def interactive_mode(self):
        """Menu interativo original completo de 4 opções"""
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
                    data = self.investigate_profile(username, session_id)
                    self.display_results(data)
                    export = input(f"\n{Colors.OKGREEN}Deseja exportar os dados? (s/N): {Colors.ENDC}").strip().lower()
                    if export in ['s', 'sim', 'y', 'yes']:
                        fmt = input(f"{Colors.OKGREEN}Formato (json/csv): {Colors.ENDC}").strip().lower()
                        if fmt in ['json', 'csv']: self.export_data(data, fmt)
                except Exception as e:
                    self.show_error(str(e))
            elif choice == '2': self.print_tutorial()
            elif choice == '3':
                if self.current_data:
                    fmt = input(f"{Colors.OKGREEN}Formato (json/csv): {Colors.ENDC}").strip().lower()
                    if fmt in ['json', 'csv']: self.export_data(self.current_data, fmt)
                else: self.show_warning("Nenhuma investigação realizada!")
            elif choice == '4':
                print(f"\n{Colors.OKGREEN}👋 Obrigado por usar o Instagram Investigator!{Colors.ENDC}")
                break

def main():
    parser = argparse.ArgumentParser(description='Instagram Investigator - OSINT')
    parser.add_argument('-u', '--username', help='Username')
    parser.add_argument('-s', '--sessionid', help='Session ID')
    parser.add_argument('-o', '--output', help='Arquivo de saída')
    parser.add_argument('-f', '--format', choices=['json', 'csv'], default='json', help='Formato')
    args = parser.parse_args()
    
    app = InstagramInvestigatorCLI()
    if args.username and args.sessionid:
        app.print_banner()
        try:
            data = app.investigate_profile(args.username, args.sessionid)
            app.display_results(data)
            if args.output: app.export_data(data, args.format, args.output)
            else:
                export = input(f"\n{Colors.OKGREEN}Deseja exportar? (s/N): {Colors.ENDC}").strip().lower()
                if export in ['s', 'sim', 'y', 'yes']: app.export_data(data, args.format)
        except Exception as e:
            app.show_error(str(e))
    else:
        app.interactive_mode()

if __name__ == "__main__":
    main()
    
