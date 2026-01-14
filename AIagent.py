#!/usr/bin/env python3
"""
Sistema Agentico AI con integrazione LM Studio
Permette a un modello AI locale di operare autonomamente sul computer
"""

import os
import sys
import json
import subprocess
import shutil
import requests
from pathlib import Path
from datetime import datetime
import time

class AIAgent:
    def __init__(self, working_dir=None):
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.history = []
        self.max_iterations = 20
        
    def log_action(self, action, result, success=True):
        """Registra le azioni eseguite"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "success": success
        }
        self.history.append(log_entry)
        print(f"{'✓' if success else '✗'} {action}: {result}")
        
    def execute_command(self, command_data):
        """Esegue un comando basato sulla keyword"""
        keyword = command_data.get("keyword", "").upper()
        
        handlers = {
            "CREATE_FILE": self.create_file,
            "READ_FILE": self.read_file,
            "MODIFY_FILE": self.modify_file,
            "DELETE_FILE": self.delete_file,
            "LIST_FILES": self.list_files,
            "CREATE_DIR": self.create_directory,
            "DELETE_DIR": self.delete_directory,
            "EXECUTE_SHELL": self.execute_shell,
            "SEARCH_FILES": self.search_files,
            "MOVE_FILE": self.move_file,
            "COPY_FILE": self.copy_file,
            "GET_INFO": self.get_file_info,
            "DONE": self.mark_done
        }
        
        handler = handlers.get(keyword)
        if handler:
            return handler(command_data)
        else:
            return {"success": False, "error": f"Keyword sconosciuta: {keyword}"}
    
    def create_file(self, data):
        """CREATE_FILE - Crea un nuovo file"""
        try:
            filepath = self.working_dir / data["path"]
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data.get("content", ""))
            
            result = f"File creato: {filepath}"
            self.log_action("CREATE_FILE", result)
            return {"success": True, "message": result, "path": str(filepath)}
        except Exception as e:
            error = f"Errore creazione file: {str(e)}"
            self.log_action("CREATE_FILE", error, False)
            return {"success": False, "error": error}
    
    def read_file(self, data):
        """READ_FILE - Legge il contenuto di un file"""
        try:
            filepath = self.working_dir / data["path"]
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = f"File letto: {filepath} ({len(content)} caratteri)"
            self.log_action("READ_FILE", result)
            return {"success": True, "content": content, "path": str(filepath)}
        except Exception as e:
            error = f"Errore lettura file: {str(e)}"
            self.log_action("READ_FILE", error, False)
            return {"success": False, "error": error}
    
    def modify_file(self, data):
        """MODIFY_FILE - Modifica un file esistente"""
        try:
            filepath = self.working_dir / data["path"]
            mode = data.get("mode", "replace")
            
            if mode == "replace":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(data["content"])
            elif mode == "append":
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(data["content"])
            elif mode == "prepend":
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing = f.read()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(data["content"] + existing)
            
            result = f"File modificato ({mode}): {filepath}"
            self.log_action("MODIFY_FILE", result)
            return {"success": True, "message": result}
        except Exception as e:
            error = f"Errore modifica file: {str(e)}"
            self.log_action("MODIFY_FILE", error, False)
            return {"success": False, "error": error}
    
    def delete_file(self, data):
        """DELETE_FILE - Elimina un file"""
        try:
            filepath = self.working_dir / data["path"]
            filepath.unlink()
            
            result = f"File eliminato: {filepath}"
            self.log_action("DELETE_FILE", result)
            return {"success": True, "message": result}
        except Exception as e:
            error = f"Errore eliminazione file: {str(e)}"
            self.log_action("DELETE_FILE", error, False)
            return {"success": False, "error": error}
    
    def list_files(self, data):
        """LIST_FILES - Lista i file in una directory"""
        try:
            dirpath = self.working_dir / data.get("path", ".")
            pattern = data.get("pattern", "*")
            
            files = []
            for item in dirpath.glob(pattern):
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.working_dir)),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else 0
                })
            
            result = f"Trovati {len(files)} elementi in {dirpath}"
            self.log_action("LIST_FILES", result)
            return {"success": True, "files": files, "count": len(files)}
        except Exception as e:
            error = f"Errore lista file: {str(e)}"
            self.log_action("LIST_FILES", error, False)
            return {"success": False, "error": error}
    
    def create_directory(self, data):
        """CREATE_DIR - Crea una nuova directory"""
        try:
            dirpath = self.working_dir / data["path"]
            dirpath.mkdir(parents=True, exist_ok=True)
            
            result = f"Directory creata: {dirpath}"
            self.log_action("CREATE_DIR", result)
            return {"success": True, "message": result}
        except Exception as e:
            error = f"Errore creazione directory: {str(e)}"
            self.log_action("CREATE_DIR", error, False)
            return {"success": False, "error": error}
    
    def delete_directory(self, data):
        """DELETE_DIR - Elimina una directory"""
        try:
            dirpath = self.working_dir / data["path"]
            shutil.rmtree(dirpath)
            
            result = f"Directory eliminata: {dirpath}"
            self.log_action("DELETE_DIR", result)
            return {"success": True, "message": result}
        except Exception as e:
            error = f"Errore eliminazione directory: {str(e)}"
            self.log_action("DELETE_DIR", error, False)
            return {"success": False, "error": error}
    
    def execute_shell(self, data):
        """EXECUTE_SHELL - Esegue un comando shell"""
        try:
            command = data["command"]
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.working_dir,
                timeout=30
            )
            
            output = result.stdout + result.stderr
            self.log_action("EXECUTE_SHELL", f"Comando: {command}")
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            error = f"Errore esecuzione comando: {str(e)}"
            self.log_action("EXECUTE_SHELL", error, False)
            return {"success": False, "error": error}
    
    def search_files(self, data):
        """SEARCH_FILES - Cerca file per nome o contenuto"""
        try:
            search_term = data["term"]
            search_type = data.get("type", "name")
            
            results = []
            for filepath in self.working_dir.rglob("*"):
                if filepath.is_file():
                    if search_type == "name" and search_term.lower() in filepath.name.lower():
                        results.append(str(filepath.relative_to(self.working_dir)))
                    elif search_type == "content":
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                if search_term in f.read():
                                    results.append(str(filepath.relative_to(self.working_dir)))
                        except:
                            pass
            
            result = f"Trovati {len(results)} file"
            self.log_action("SEARCH_FILES", result)
            return {"success": True, "results": results, "count": len(results)}
        except Exception as e:
            error = f"Errore ricerca file: {str(e)}"
            self.log_action("SEARCH_FILES", error, False)
            return {"success": False, "error": error}
    
    def move_file(self, data):
        """MOVE_FILE - Sposta un file"""
        try:
            src = self.working_dir / data["source"]
            dst = self.working_dir / data["destination"]
            shutil.move(str(src), str(dst))
            
            result = f"File spostato: {src} -> {dst}"
            self.log_action("MOVE_FILE", result)
            return {"success": True, "message": result}
        except Exception as e:
            error = f"Errore spostamento file: {str(e)}"
            self.log_action("MOVE_FILE", error, False)
            return {"success": False, "error": error}
    
    def copy_file(self, data):
        """COPY_FILE - Copia un file"""
        try:
            src = self.working_dir / data["source"]
            dst = self.working_dir / data["destination"]
            shutil.copy2(str(src), str(dst))
            
            result = f"File copiato: {src} -> {dst}"
            self.log_action("COPY_FILE", result)
            return {"success": True, "message": result}
        except Exception as e:
            error = f"Errore copia file: {str(e)}"
            self.log_action("COPY_FILE", error, False)
            return {"success": False, "error": error}
    
    def get_file_info(self, data):
        """GET_INFO - Ottiene informazioni su un file"""
        try:
            filepath = self.working_dir / data["path"]
            stat = filepath.stat()
            
            info = {
                "path": str(filepath),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": filepath.is_file(),
                "is_dir": filepath.is_dir()
            }
            
            self.log_action("GET_INFO", f"Info: {filepath}")
            return {"success": True, "info": info}
        except Exception as e:
            error = f"Errore info file: {str(e)}"
            self.log_action("GET_INFO", error, False)
            return {"success": False, "error": error}
    
    def mark_done(self, data):
        """DONE - Indica che il task è completato"""
        message = data.get("message", "Task completato")
        self.log_action("DONE", message)
        return {"success": True, "message": message, "done": True}


class LMStudioClient:
    def __init__(self, base_url="http://localhost:1234/v1", model=None):
        self.base_url = base_url
        self.model = model
        self.conversation_history = []
        # Mantieni solo gli ultimi 10 scambi (20 messaggi) + il task originale
        self.history_limit = 10 
        
    def test_connection(self):
        """Verifica la connessione a LM Studio"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                print(f"✓ Connesso a LM Studio")
                # Se l'utente non ha definito un modello, prendi il primo disponibile
                if not self.model and models.get("data"):
                    self.model = models['data'][0]['id']
                    print(f"  Modello auto-selezionato: {self.model}")
                return True
            return False
        except Exception as e:
            print(f"✗ Errore connessione LM Studio: {e}")
            return False
    
    def _manage_memory(self):
        """Mantiene la memoria pulita rimuovendo i messaggi vecchi centrali"""
        # Se la storia supera il limite (moltiplicato x2 perché ogni scambio è User+Assistant)
        if len(self.conversation_history) > (self.history_limit * 2):
            # Manteniamo sempre il primo messaggio (il Task dell'utente)
            first_message = self.conversation_history[0]
            
            # Tagliamo la parte vecchia, mantenendo gli ultimi N messaggi
            # Esempio: tieni l'ultimo 60% della conversazione
            keep_count = int(self.history_limit * 2)
            recent_history = self.conversation_history[-keep_count:]
            
            # Ricostruiamo la storia: Task Originale + Storia Recente
            self.conversation_history = [first_message] + recent_history
            
            print(f"\n🧹 [SISTEMA] Memoria ottimizzata: rimossi messaggi vecchi per liberare contesto.")

    def chat(self, user_message, system_prompt=None):
        """Invia un messaggio al modello con gestione errori e memoria"""
        try:
            # 1. Gestione Memoria prima di aggiungere nuovi dati
            self._manage_memory()
            
            # 2. Aggiungi messaggio utente
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # 3. Costruisci il payload completo
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.extend(self.conversation_history)
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": -1, # -1 usa il massimo disponibile in LM Studio
                "stream": False
            }
            
            # 4. Chiamata API
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=120 # Timeout aumentato per ragionamenti lunghi
            )
            
            # 5. Gestione Risposta
            if response.status_code == 200:
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"]
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                return assistant_message
            
            # Gestione specifica Errore 500 (Context Full)
            elif response.status_code == 500:
                print("\n⚠️  Errore 500 da LM Studio (Probabile memoria piena). Tento pulizia aggressiva...")
                # Rimuovi metà della memoria e riprova (ultimo tentativo non implementato qui per semplicità, ma evitiamo crash)
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-4:]
                return '{"reasoning": "Errore memoria piena. Devo riassumere e continuare.", "keyword": "DONE", "message": "Memoria piena, riprovare il comando."}'
            
            else:
                error_msg = f"Errore API: {response.status_code} - {response.text}"
                print(f"\n❌ {error_msg}")
                # Restituisci un JSON di errore fake per non rompere il parser del main
                return '{"reasoning": "Errore di connessione API.", "keyword": "DONE", "message": "Errore API rilevato."}'
                
        except Exception as e:
            return f'{{"reasoning": "Eccezione Python critica.", "keyword": "DONE", "message": "Errore: {str(e)}"}}'
    
    def reset_conversation(self):
        self.conversation_history = []

def get_system_prompt():
    """Restituisce il system prompt ottimizzato per l'AI Agent"""
    return """Sei un Agente Operativo AI autonomo collegato a un terminale locale.
Il tuo obiettivo è completare task complessi eseguendo azioni sequenziali sul file system.

RAGIONAMENTO OBBLIGATORIO:
Ogni tua risposta DEVE contenere un campo "reasoning" dove spieghi brevemente:
1. Cosa hai fatto prima (se applicabile).
2. Cosa stai per fare e perché.
3. Cosa ti aspetti che succeda.

FORMATO RISPOSTA:
Rispondi RIGOROSAMENTE solo con un singolo oggetto JSON valido.
Non scrivere mai testo introduttivo o conclusivo fuori dal blocco JSON.

SCHEMA JSON GENERALE:
{
    "reasoning": "Analisi della situazione e piano d'azione...",
    "keyword": "COMANDO",
    ... parametri specifici ...
}

LISTA COMANDI DISPONIBILI:

1. CREATE_FILE
   Crea un file scrivendo il contenuto. Sovrascrive se esiste.
   {"reasoning": "...", "keyword": "CREATE_FILE", "path": "dir/file.txt", "content": "testo"}

2. READ_FILE
   Legge tutto il contenuto di un file. Utile per analizzare codice o testo.
   {"reasoning": "...", "keyword": "READ_FILE", "path": "dir/file.txt"}

3. MODIFY_FILE
   Modifica file esistenti.
   - mode "replace": sovrascrive tutto.
   - mode "append": aggiunge alla fine.
   - mode "prepend": aggiunge all'inizio.
   {"reasoning": "...", "keyword": "MODIFY_FILE", "path": "file.txt", "content": "nuova riga", "mode": "append"}

4. DELETE_FILE
   Rimuove definitivamente un file.
   {"reasoning": "...", "keyword": "DELETE_FILE", "path": "file.txt"}

5. LIST_FILES
   Elenca file nella directory. Usa pattern glob (es. "*.py").
   {"reasoning": "...", "keyword": "LIST_FILES", "path": ".", "pattern": "*"}

6. CREATE_DIR
   Crea una cartella (e le parent se mancano).
   {"reasoning": "...", "keyword": "CREATE_DIR", "path": "nuova/cartella"}

7. DELETE_DIR
   Rimuove una cartella e tutto il suo contenuto (ricorsivo).
   {"reasoning": "...", "keyword": "DELETE_DIR", "path": "vecchia/cartella"}

8. EXECUTE_SHELL
   Esegue comandi di sistema (ls, git, python, pip, etc).
   ATTENZIONE: Non usare comandi interattivi (come nano, vim, python senza argomenti) che bloccano il processo.
   {"reasoning": "...", "keyword": "EXECUTE_SHELL", "command": "python script.py"}

9. SEARCH_FILES
   Cerca file per nome o contenuto testuale.
   {"reasoning": "...", "keyword": "SEARCH_FILES", "term": "TODO", "type": "content"}

10. MOVE_FILE / COPY_FILE
    Sposta o Copia file.
    {"reasoning": "...", "keyword": "MOVE_FILE", "source": "src.txt", "destination": "dest.txt"}

11. GET_INFO
    Ottiene metadati (dimensione, data modifica).
    {"reasoning": "...", "keyword": "GET_INFO", "path": "file.txt"}

12. DONE
    Usa QUESTO comando SOLO quando hai verificato che il task è completato al 100%.
    {"reasoning": "Ho verificato i file creati e il risultato è corretto.", "keyword": "DONE", "message": "Task completato con successo."}

LINEE GUIDA OPERATIVE:
1. **Verifica sempre**: Dopo aver creato o modificato un file importante, leggilo o esegui il codice per assicurarti che funzioni.
2. **Gestione Errori**: Se un comando fallisce (campo "success": false), LEGGI l'errore nel log, ragiona su cosa è andato storto e prova un approccio alternativo. Non ripetere lo stesso comando identico.
3. **Persistenza**: Ricorda che non puoi chiedere input all'utente. Devi risolvere i problemi autonomamente.
4. **Iterazione**: Procedi un passo alla volta. Non cercare di fare tutto in un solo comando (tranne script shell complessi).

ESEMPIO DI FLUSSO DI PENSIERO:
Task: "Crea uno script python che stampa ciao"
Risposta:
{
  "reasoning": "L'utente vuole uno script python. Devo creare il file main.py con il codice richiesto.",
  "keyword": "CREATE_FILE",
  "path": "main.py",
  "content": "print('Ciao')"
}
"""
def extract_json_from_response(response):
    """Estrae JSON dalla risposta dell'AI"""
    # Cerca blocchi JSON
    response = response.strip()
    
    # Rimuovi blocchi markdown se presenti
    if "```json" in response:
        start = response.find("```json") + 7
        end = response.find("```", start)
        response = response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        response = response[start:end].strip()
    
    # Cerca pattern JSON
    if "{" in response:
        start = response.find("{")
        # Trova la fine del JSON
        brace_count = 0
        for i, char in enumerate(response[start:], start):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    response = response[start:i+1]
                    break
    
    return response


def main():
    print("=" * 60)
    print("  SISTEMA AGENTICO AI CON LM STUDIO")
    print("=" * 60)
    
    # Configurazione LM Studio
    print("\n📡 CONFIGURAZIONE LM STUDIO")
    lm_url = input("URL LM Studio (default: http://localhost:1234/v1): ").strip()
    if not lm_url:
        lm_url = "http://localhost:1234/v1"
    
    client = LMStudioClient(lm_url)
    
    # Test connessione
    print("\nTest connessione...")
    if not client.test_connection():
        print("\n⚠️  LM Studio non raggiungibile!")
        print("Assicurati che LM Studio sia avviato e un modello sia caricato.")
        return
    
    # Selezione modello
    model_name = input("\nNome modello (lascia vuoto per auto): ").strip()
    if model_name:
        client.model = model_name
    
    # Directory di lavoro
    print("\n📁 CONFIGURAZIONE DIRECTORY")
    working_dir = input("Directory di lavoro (vuoto per corrente): ").strip()
    if not working_dir:
        working_dir = os.getcwd()
    
    agent = AIAgent(working_dir)
    print(f"✓ Directory di lavoro: {agent.working_dir}")
    
    # Task dell'utente
    print("\n" + "=" * 60)
    print("🎯 DEFINISCI IL TASK")
    print("=" * 60)
    task = input("\nCosa vuoi che l'AI faccia?\n> ").strip()
    
    if not task:
        print("Nessun task specificato!")
        return
    
    # Esecuzione agentica
    print("\n" + "=" * 60)
    print("🤖 ESECUZIONE AGENTICA")
    print("=" * 60)
    
    system_prompt = get_system_prompt()
    initial_message = f"Task da completare: {task}\n\nAnalizza il task e inizia con il primo comando JSON necessario."
    
    iteration = 0
    task_completed = False
    
    while iteration < agent.max_iterations and not task_completed:
        iteration += 1
        print(f"\n{'─' * 60}")
        print(f"ITERAZIONE {iteration}/{agent.max_iterations}")
        print('─' * 60)
        
        # Ottieni risposta dal modello
        if iteration == 1:
            print("🤔 AI sta analizzando il task...")
            ai_response = client.chat(initial_message, system_prompt)
        else:
            print("🤔 AI sta pianificando il prossimo passo...")
            ai_response = client.chat(
                "Operazione completata. Continua con il prossimo comando JSON o usa DONE se hai finito.",
                system_prompt
            )
        
        print(f"\n📝 Risposta AI:\n{ai_response}")
        
        # Estrai JSON
        try:
            json_str = extract_json_from_response(ai_response)
            command = json.loads(json_str)
            
            print(f"\n⚙️  Comando estratto: {command.get('keyword', 'UNKNOWN')}")
            
            # Esegui comando
            result = agent.execute_command(command)
            
            # Mostra risultato
            print(f"\n📊 Risultato:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Check completamento
            if result.get("done"):
                task_completed = True
                print("\n" + "=" * 60)
                print("✅ TASK COMPLETATO!")
                print("=" * 60)
                break
            
            # Feedback all'AI sul risultato
            if not result.get("success"):
                print("\n⚠️  Operazione fallita, l'AI proverà un approccio diverso...")
            
            time.sleep(0.5)  # Breve pausa
            
        except json.JSONDecodeError as e:
            print(f"\n❌ Errore parsing JSON: {e}")
            print("L'AI non ha generato un JSON valido. Riprovo...")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏸️  Interrotto dall'utente")
            break
        except Exception as e:
            print(f"\n❌ Errore: {e}")
            break
    
    if iteration >= agent.max_iterations and not task_completed:
        print("\n⚠️  Raggiunto limite massimo di iterazioni!")
    
    # Storico finale
    print("\n" + "=" * 60)
    print("📜 STORICO OPERAZIONI")
    print("=" * 60)
    for i, entry in enumerate(agent.history, 1):
        status = "✓" if entry["success"] else "✗"
        print(f"{i}. {status} [{entry['timestamp']}] {entry['action']}: {entry['result']}")
    
    print("\n" + "=" * 60)
    print("FINE ESECUZIONE")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Errore fatale: {e}")
        import traceback
        traceback.print_exc()