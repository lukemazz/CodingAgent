"""Core dell'agente AI"""

import os
from typing import Generator, Optional
from config import Config
from prompts import SYSTEM_PROMPT, CONTINUE_PROMPT
from executor import CommandParser, CommandExecutor

class AIProvider:
    """Provider base per i modelli AI"""
    
    def chat(self, messages: list) -> str:
        raise NotImplementedError


class OllamaProvider(AIProvider):
    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url
    
    def chat(self, messages: list) -> str:
        import requests
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def chat(self, messages: list) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content


class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def chat(self, messages: list) -> str:
        # Anthropic usa formato diverso
        system = ""
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=chat_messages
        )
        return response.content[0].text


class GroqProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        from groq import Groq
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def chat(self, messages: list) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

# --- CLASSE AGGIUNTA PER LM STUDIO ---
class LMStudioProvider(AIProvider):
    def __init__(self, base_url: str, model: str):
        # LM Studio simula le API di OpenAI
        from openai import OpenAI
        self.client = OpenAI(
            base_url=base_url,
            api_key="lm-studio"  # Chiave dummy necessaria per la libreria
        )
        self.model = model
    
    def chat(self, messages: list) -> str:
        # Temperature leggermente ridotta per comandi più precisi
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7 
        )
        return response.choices[0].message.content
# -------------------------------------

class Agent:
    """Agente AI principale"""
    
    def __init__(self, config: Config):
        self.config = config
        self.provider = self._create_provider()
        self.executor = CommandExecutor(config.workspace, config.safe_mode)
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.max_iterations = 20  # Sicurezza anti-loop
    
    def _create_provider(self) -> AIProvider:
        """Crea il provider AI appropriato"""
        if self.config.provider == "ollama":
            return OllamaProvider(self.config.model, self.config.ollama_base_url)
        elif self.config.provider == "openai":
            if not self.config.openai_api_key:
                raise ValueError("OPENAI_API_KEY non configurata")
            return OpenAIProvider(self.config.openai_api_key, self.config.model)
        elif self.config.provider == "anthropic":
            if not self.config.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY non configurata")
            return AnthropicProvider(self.config.anthropic_api_key, self.config.model)
        elif self.config.provider == "groq":
            if not self.config.groq_api_key:
                raise ValueError("GROQ_API_KEY non configurata")
            return GroqProvider(self.config.groq_api_key, self.config.model)
        
        # --- BLOCCO AGGIUNTO PER LM STUDIO ---
        elif self.config.provider == "lmstudio":
             return LMStudioProvider(self.config.lmstudio_base_url, self.config.model)
        # -------------------------------------
        
        else:
            raise ValueError(f"Provider sconosciuto: {self.config.provider}")
    
    def run(self, user_input: str) -> Generator[str, None, None]:
        """Esegue un task e yield i risultati intermedi"""
        
        self.messages.append({"role": "user", "content": user_input})
        
        for iteration in range(self.max_iterations):
            # Ottieni risposta dall'AI
            try:
                response = self.provider.chat(self.messages)
            except Exception as e:
                yield f"❌ Errore comunicazione AI: {e}"
                return
            
            yield f"\n🤖 AI:\n{response}\n"
            
            # Parsa il comando
            parsed = CommandParser.parse(response)
            
            if not parsed:
                yield "⚠️ Risposta non valida, nessun comando riconosciuto"
                self.messages.append({"role": "assistant", "content": response})
                self.messages.append({
                    "role": "user", 
                    "content": "Non ho capito. Usa il formato corretto con le keyword tra parentesi quadre."
                })
                continue
            
            command, params = parsed
            yield f"⚙️ Comando: {command}"
            
            # Esegui il comando
            result, is_done = self.executor.execute(command, params)
            
            if result.error:
                yield f"❌ Errore: {result.error}"
                feedback = f"Errore nell'esecuzione: {result.error}"
            else:
                yield f"{result.output}"
                feedback = result.output
            
            # Aggiorna la conversazione
            self.messages.append({"role": "assistant", "content": response})
            
            if is_done:
                return
            
            # Continua con il feedback
            self.messages.append({
                "role": "user",
                "content": CONTINUE_PROMPT.format(result=feedback)
            })
        
        yield "⚠️ Raggiunto limite massimo iterazioni"
    
    def reset(self):
        """Resetta la conversazione"""
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]