"""Strumenti disponibili per l'agente"""

import os
import re
import subprocess
import shutil
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class ToolResult:
    success: bool
    output: str
    error: Optional[str] = None

class FileTools:
    def __init__(self, workspace: str, safe_mode: bool = True, max_size_mb: int = 10):
        self.workspace = os.path.abspath(workspace)
        self.safe_mode = safe_mode
        self.max_size_mb = max_size_mb
    
    def _resolve_path(self, path: str) -> str:
        """Risolve il path relativo alla workspace"""
        if os.path.isabs(path):
            resolved = path
        else:
            resolved = os.path.abspath(os.path.join(self.workspace, path))
        
        # Sicurezza: verifica che sia dentro la workspace
        if not resolved.startswith(self.workspace):
            raise PermissionError(f"Accesso negato: {path} è fuori dalla workspace")
        
        return resolved
    
    def create_file(self, path: str, content: str) -> ToolResult:
        """Crea un nuovo file"""
        try:
            full_path = self._resolve_path(path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return ToolResult(True, f"✅ File creato: {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def read_file(self, path: str) -> ToolResult:
        """Legge un file"""
        try:
            full_path = self._resolve_path(path)
            
            # Check dimensione
            size_mb = os.path.getsize(full_path) / (1024 * 1024)
            if size_mb > self.max_size_mb:
                return ToolResult(False, "", f"File troppo grande: {size_mb:.2f}MB")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return ToolResult(True, f"📄 Contenuto di {path}:\n```\n{content}\n```")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def edit_file(self, path: str, old_content: str, new_content: str) -> ToolResult:
        """Modifica un file sostituendo contenuto"""
        try:
            full_path = self._resolve_path(path)
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_content not in content:
                return ToolResult(False, "", "Contenuto da sostituire non trovato nel file")
            
            new_file_content = content.replace(old_content, new_content, 1)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_file_content)
            
            return ToolResult(True, f"✏️ File modificato: {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def append_file(self, path: str, content: str) -> ToolResult:
        """Aggiunge contenuto a un file"""
        try:
            full_path = self._resolve_path(path)
            
            with open(full_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return ToolResult(True, f"➕ Contenuto aggiunto a: {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def delete_file(self, path: str) -> ToolResult:
        """Elimina un file"""
        try:
            full_path = self._resolve_path(path)
            os.remove(full_path)
            return ToolResult(True, f"🗑️ File eliminato: {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def create_dir(self, path: str) -> ToolResult:
        """Crea una directory"""
        try:
            full_path = self._resolve_path(path)
            os.makedirs(full_path, exist_ok=True)
            return ToolResult(True, f"📁 Directory creata: {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def list_dir(self, path: str = ".") -> ToolResult:
        """Lista contenuto directory"""
        try:
            full_path = self._resolve_path(path)
            items = os.listdir(full_path)
            
            output = f"📂 Contenuto di {path}:\n"
            for item in sorted(items):
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    output += f"  📁 {item}/\n"
                else:
                    size = os.path.getsize(item_path)
                    output += f"  📄 {item} ({size} bytes)\n"
            
            if not items:
                output += "  (vuota)\n"
            
            return ToolResult(True, output)
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def delete_dir(self, path: str) -> ToolResult:
        """Elimina una directory"""
        try:
            full_path = self._resolve_path(path)
            shutil.rmtree(full_path)
            return ToolResult(True, f"🗑️ Directory eliminata: {path}")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def tree(self, path: str = ".", depth: int = 3) -> ToolResult:
        """Mostra albero directory"""
        try:
            full_path = self._resolve_path(path)
            output = self._tree_recursive(full_path, "", depth)
            return ToolResult(True, f"🌳 Struttura di {path}:\n{output}")
        except Exception as e:
            return ToolResult(False, "", str(e))
    
    def _tree_recursive(self, path: str, prefix: str, depth: int) -> str:
        if depth < 0:
            return ""
        
        output = ""
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return prefix + "  [Permission Denied]\n"
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            item_path = os.path.join(path, item)
            
            if os.path.isdir(item_path):
                output += f"{prefix}{current_prefix}📁 {item}/\n"
                next_prefix = prefix + ("    " if is_last else "│   ")
                output += self._tree_recursive(item_path, next_prefix, depth - 1)
            else:
                output += f"{prefix}{current_prefix}📄 {item}\n"
        
        return output
    
    def search(self, pattern: str, path: str = ".") -> ToolResult:
        """Cerca file per pattern"""
        try:
            full_path = self._resolve_path(path)
            matches = []
            
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    if re.search(pattern, file, re.IGNORECASE):
                        rel_path = os.path.relpath(os.path.join(root, file), full_path)
                        matches.append(rel_path)
            
            if matches:
                output = f"🔍 File trovati per '{pattern}':\n"
                for m in matches:
                    output += f"  📄 {m}\n"
            else:
                output = f"🔍 Nessun file trovato per '{pattern}'"
            
            return ToolResult(True, output)
        except Exception as e:
            return ToolResult(False, "", str(e))


class SystemTools:
    def __init__(self, workspace: str, safe_mode: bool = True):
        self.workspace = os.path.abspath(workspace)
        self.safe_mode = safe_mode
        
        # Comandi pericolosi che richiedono conferma
        self.dangerous_patterns = [
            r'\brm\b.*-rf',
            r'\bsudo\b',
            r'\bdd\b',
            r'\bmkfs\b',
            r'\bformat\b',
            r'>\s*/dev/',
            r'\bshutdown\b',
            r'\breboot\b',
        ]
    
    def is_dangerous(self, command: str) -> bool:
        """Verifica se un comando è pericoloso"""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False
    
    def execute(self, command: str, timeout: int = 30) -> ToolResult:
        """Esegue un comando shell"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = ""
            if result.stdout:
                output += f"📤 Output:\n{result.stdout}\n"
            if result.stderr:
                output += f"⚠️ Stderr:\n{result.stderr}\n"
            if result.returncode != 0:
                output += f"❌ Exit code: {result.returncode}"
            else:
                output += f"✅ Comando completato"
            
            return ToolResult(result.returncode == 0, output)
        except subprocess.TimeoutExpired:
            return ToolResult(False, "", f"Timeout dopo {timeout} secondi")
        except Exception as e:
            return ToolResult(False, "", str(e))