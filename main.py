#!/usr/bin/env python3
"""
AI Agent Terminal - Sistema agentico per AI
"""

import os
import sys
import argparse
from config import Config
from agent import Agent

# Colori ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════╗
║                                                      ║
║              🤖 AI AGENT TERMINAL v1.0               ║
║           System Interface & Task Executor           ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)
    print(f"{Colors.YELLOW}Type 'exit', 'quit' or 'esci' to stop.{Colors.END}\n")

def main():
    parser = argparse.ArgumentParser(description="AI Agent Terminal")
    parser.add_argument("--provider", type=str, help="AI Provider (ollama, openai, lmstudio, etc)")
    parser.add_argument("--model", type=str, help="Model name")
    parser.add_argument("--safe-mode", action="store_true", help="Enable safe mode")
    
    args = parser.parse_args()
    
    # Carica configurazione
    config = Config()
    
    # Override da argomenti
    if args.provider:
        config.provider = args.provider
    if args.model:
        config.model = args.model
    if args.safe_mode:
        config.safe_mode = True
        
    print_banner()
    print(f"🔧 Provider:  {Colors.BOLD}{config.provider}{Colors.END}")
    print(f"🧠 Model:     {Colors.BOLD}{config.model}{Colors.END}")
    print(f"📂 Workspace: {Colors.BOLD}{config.workspace}{Colors.END}")
    
    if config.provider == "lmstudio":
        print(f"📡 URL:       {Colors.BOLD}{config.lmstudio_base_url}{Colors.END}")
        
    print("-" * 60)
    
    try:
        agent = Agent(config)
        
        while True:
            try:
                user_input = input(f"\n{Colors.GREEN}You ➤ {Colors.END}")
                
                if user_input.lower() in ['exit', 'quit', 'esci']:
                    print(f"\n{Colors.BLUE}Goodbye! 👋{Colors.END}")
                    break
                
                if not user_input.strip():
                    continue
                    
                print(f"\n{Colors.CYAN}Thinking...{Colors.END}")
                
                for output in agent.run(user_input):
                    # Stampa output colorato in base al contenuto
                    if "❌" in output:
                        print(f"{Colors.RED}{output}{Colors.END}")
                    elif "⚙️" in output:
                        print(f"{Colors.YELLOW}{output}{Colors.END}")
                    elif "🤖" in output:
                        print(f"{Colors.BLUE}{output}{Colors.END}")
                    else:
                        print(output)
                        
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}\nOperazione annullata.{Colors.END}")
                continue
                
    except Exception as e:
        print(f"\n{Colors.RED}Fatal Error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()