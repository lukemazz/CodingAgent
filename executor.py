"""Parser ed esecutore dei comandi dell'agente"""

import re
from typing import Optional, Tuple, Dict, Any
from tools import FileTools, SystemTools, ToolResult

class CommandParser:
    """Parser per i comandi dell'agente"""
    
    # Modifica: Usa \s* invece di \n per tollerare spazi o a capo dopo i tag
    # Modifica: Usa re.DOTALL implicito nella compilazione o nel search
    COMMANDS = {
        'CREATE_FILE': r'\[CREATE_FILE\]\s*path:\s*(.+?)\s+content:\s*(.*?)\[/CREATE_FILE\]',
        'READ_FILE': r'\[READ_FILE\]\s*path:\s*(.+?)\s*\[/READ_FILE\]',
        'EDIT_FILE': r'\[EDIT_FILE\]\s*path:\s*(.+?)\s+old_content:\s*(.*?)\s+new_content:\s*(.*?)\[/EDIT_FILE\]',
        'DELETE_FILE': r'\[DELETE_FILE\]\s*path:\s*(.+?)\s*\[/DELETE_FILE\]',
        'APPEND_FILE': r'\[APPEND_FILE\]\s*path:\s*(.+?)\s+content:\s*(.*?)\[/APPEND_FILE\]',
        'CREATE_DIR': r'\[CREATE_DIR\]\s*path:\s*(.+?)\s*\[/CREATE_DIR\]',
        'LIST_DIR': r'\[LIST_DIR\]\s*path:\s*(.+?)\s*\[/LIST_DIR\]',
        'DELETE_DIR': r'\[DELETE_DIR\]\s*path:\s*(.+?)\s*\[/DELETE_DIR\]',
        'EXECUTE': r'\[EXECUTE\]\s*command:\s*(.+?)\s*\[/EXECUTE\]',
        'SEARCH': r'\[SEARCH\]\s*pattern:\s*(.+?)(?:\s+path:\s*(.+?))?\s*\[/SEARCH\]',
        'TREE': r'\[TREE\](?:\s*path:\s*(.+?))?(?:\s+depth:\s*(\d+))?\s*\[/TREE\]',
        'RESPOND': r'\[RESPOND\]\s*(.*?)\[/RESPOND\]',
        'DONE': r'\[DONE\]\s*(.*?)\[/DONE\]',
    }
    
    @classmethod
    def parse(cls, response: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Parsa la risposta dell'AI e estrae il comando"""
        
        # Pulizia base: a volte i modelli locali mettono spazi prima del tag
        response = response.strip()

        for cmd_name, pattern in cls.COMMANDS.items():
            # re.DOTALL permette al punto (.) di matchare anche i newlines
            # re.IGNORECASE rende i tag case-insensitive
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                groups = match.groups()
                
                try:
                    if cmd_name == 'CREATE_FILE':
                        return cmd_name, {'path': groups[0].strip(), 'content': groups[1].strip()}
                    elif cmd_name == 'READ_FILE':
                        return cmd_name, {'path': groups[0].strip()}
                    elif cmd_name == 'EDIT_FILE':
                        return cmd_name, {
                            'path': groups[0].strip(),
                            'old_content': groups[1].strip(), # Rimuove spazi extra inizio/fine
                            'new_content': groups[2].strip()
                        }
                    elif cmd_name == 'DELETE_FILE':
                        return cmd_name, {'path': groups[0].strip()}
                    elif cmd_name == 'APPEND_FILE':
                        return cmd_name, {'path': groups[0].strip(), 'content': groups[1]}
                    elif cmd_name == 'CREATE_DIR':
                        return cmd_name, {'path': groups[0].strip()}
                    elif cmd_name == 'LIST_DIR':
                        return cmd_name, {'path': groups[0].strip()}
                    elif cmd_name == 'DELETE_DIR':
                        return cmd_name, {'path': groups[0].strip()}
                    elif cmd_name == 'EXECUTE':
                        return cmd_name, {'command': groups[0].strip()}
                    elif cmd_name == 'SEARCH':
                        return cmd_name, {
                            'pattern': groups[0].strip(),
                            'path': groups[1].strip() if groups[1] else '.'
                        }
                    elif cmd_name == 'TREE':
                        return cmd_name, {
                            'path': groups[0].strip() if groups[0] else '.',
                            'depth': int(groups[1]) if groups[1] else 3
                        }
                    elif cmd_name == 'RESPOND':
                        return cmd_name, {'message': groups[0].strip()}
                    elif cmd_name == 'DONE':
                        return cmd_name, {'summary': groups[0].strip()}
                except Exception as e:
                    print(f"Errore durante il parsing dei gruppi per {cmd_name}: {e}")
                    continue
        
        return None


class CommandExecutor:
    """Esegue i comandi parsati"""
    
    def __init__(self, workspace: str, safe_mode: bool = True):
        self.file_tools = FileTools(workspace, safe_mode)
        self.system_tools = SystemTools(workspace, safe_mode)
        self.safe_mode = safe_mode
    
    def execute(self, command: str, params: Dict[str, Any]) -> Tuple[ToolResult, bool]:
        """
        Esegue un comando e ritorna (risultato, is_done)
        """
        
        if command == 'CREATE_FILE':
            return self.file_tools.create_file(params['path'], params['content']), False
        
        elif command == 'READ_FILE':
            return self.file_tools.read_file(params['path']), False
        
        elif command == 'EDIT_FILE':
            return self.file_tools.edit_file(
                params['path'], params['old_content'], params['new_content']
            ), False
        
        elif command == 'DELETE_FILE':
            if self.safe_mode:
                if not self._confirm(f"Eliminare il file {params['path']}?"):
                    return ToolResult(False, "❌ Operazione annullata dall'utente"), False
            return self.file_tools.delete_file(params['path']), False
        
        elif command == 'APPEND_FILE':
            return self.file_tools.append_file(params['path'], params['content']), False
        
        elif command == 'CREATE_DIR':
            return self.file_tools.create_dir(params['path']), False
        
        elif command == 'LIST_DIR':
            return self.file_tools.list_dir(params['path']), False
        
        elif command == 'DELETE_DIR':
            if self.safe_mode:
                if not self._confirm(f"Eliminare la directory {params['path']} e tutto il suo contenuto?"):
                    return ToolResult(False, "❌ Operazione annullata dall'utente"), False
            return self.file_tools.delete_dir(params['path']), False
        
        elif command == 'EXECUTE':
            cmd = params['command']
            if self.safe_mode and self.system_tools.is_dangerous(cmd):
                if not self._confirm(f"Eseguire comando potenzialmente pericoloso?\n{cmd}"):
                    return ToolResult(False, "❌ Operazione annullata dall'utente"), False
            return self.system_tools.execute(cmd), False
        
        elif command == 'SEARCH':
            return self.file_tools.search(params['pattern'], params['path']), False
        
        elif command == 'TREE':
            return self.file_tools.tree(params['path'], params['depth']), False
        
        elif command == 'RESPOND':
            return ToolResult(True, params['message']), False
        
        elif command == 'DONE':
            return ToolResult(True, f"✅ Task completato!\n{params['summary']}"), True
        
        return ToolResult(False, "", f"Comando sconosciuto: {command}"), False
    
    def _confirm(self, message: str) -> bool:
        """Chiede conferma all'utente"""
        print(f"\n⚠️  {message}")
        response = input("Confermi? (s/n): ").strip().lower()
        return response in ('s', 'si', 'sì', 'y', 'yes')