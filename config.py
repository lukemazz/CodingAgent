"""Configurazione dell'agente"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # Provider AI supportati: openai, anthropic, ollama, groq, lmstudio
    provider: str = "lmstudio"
    model: str = "local-model"  # Nome generico per LM Studio
    
    # API Keys (da environment variables)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # LM Studio (Nuova aggiunta)
    lmstudio_base_url: str = "http://localhost:1234/v1"
    
    # Sicurezza
    safe_mode: bool = True  # Chiede conferma per operazioni pericolose
    allowed_directories: list = None  # None = tutte
    max_file_size_mb: int = 10
    
    # Working directory
    workspace: str = "./workspace"
    
    def __post_init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if self.allowed_directories is None:
            self.allowed_directories = [os.path.abspath(self.workspace)]
        
        # Crea workspace se non esiste
        os.makedirs(self.workspace, exist_ok=True)