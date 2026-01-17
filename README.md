Ecco il file `README.md` riscritto esattamente con lo stile, la struttura e la formattazione professionale dell'esempio che hai fornito, adattato però alle reali funzionalità e comandi del tuo codice.

---

# 🤖 AI Agent Terminal

Un sistema agentico avanzato da terminale che permette a modelli AI (sia locali che cloud) di operare autonomamente sul computer, eseguendo task complessi attraverso azioni sequenziali sul file system.

## 📋 Caratteristiche

* ✅ **Agnostico al Modello**: Supporta LM Studio, Ollama, OpenAI, Anthropic e Groq
* 🛡️ **Safe Mode Integrata**: Protezione attiva contro comandi distruttivi con richiesta di conferma
* 🔄 **Loop Autonomo**: L'AI analizza, pianifica, esegue e corregge i propri errori
* 📂 **Workspace Isolato**: Tutte le operazioni avvengono in una sandbox sicura
* 🎨 **Interfaccia CLI**: Output colorato e strutturato per una facile lettura
* 🛠️ **13 Tool Nativi**: Set completo di strumenti per manipolazione file e sistema

## 🚀 Prerequisiti

### Software Richiesto

1. **Python 3.8+**
2. **[LM Studio](https://lmstudio.ai/)** o **[Ollama](https://ollama.com/)** (opzionali per uso locale)
3. API Keys (opzionali per uso Cloud: OpenAI, Anthropic, Groq)

### Configurazione Dipendenze

```bash
pip install -r requirements.txt

```

## 📦 Installazione

```bash
# Clone del repository
git clone https://github.com/tuousername/ai-agent-terminal.git
cd ai-agent-terminal

# Installazione dipendenze
pip install -r requirements.txt

# Rendi eseguibile lo script (Linux/Mac)
chmod +x main.py

```

## 🎮 Utilizzo Rapido

### Avvio Base (LM Studio)

Assicurati che LM Studio sia attivo su `localhost:1234`.

```bash
python main.py

```

### Avvio con Parametri Specifici

```bash
# Usa Ollama con Llama 3
python main.py --provider ollama --model llama3

# Usa Groq per velocità estrema
python main.py --provider groq --model llama3-70b-8192 --safe-mode

```

### Esempio di Sessione

```text
🔧 Provider:  lmstudio
🧠 Model:     local-model
📂 Workspace: ./workspace
------------------------------------------------------------

You ➤ Crea un file python che calcola i numeri di Fibonacci

Thinking...

⚙️ Comando: [CREATE_FILE] path: fib.py
✅ File creato: fib.py

🤖 AI: Ho creato lo script. Vuoi che lo esegua per testarlo?

You ➤ Procedi

⚙️ Comando: [EXECUTE] command: python fib.py
📤 Output: 0, 1, 1, 2, 3, 5...

```

## 📚 Comandi Disponibili

L'agente utilizza un sistema di tag specifici per interagire con il sistema.

### Gestione File

| Comando | Descrizione | Esempio |
| --- | --- | --- |
| `[CREATE_FILE]` | Crea un nuovo file | Scrivere script, note, config |
| `[READ_FILE]` | Legge contenuto file | Analizzare codice esistente |
| `[EDIT_FILE]` | Modifica file (Search & Replace) | Refactoring, bugfix |
| `[DELETE_FILE]` | Elimina file | Pulizia (richiede conferma in Safe Mode) |
| `[APPEND_FILE]` | Aggiunge contenuto in coda | Log, liste, aggiunte rapide |

### Gestione Directory

| Comando | Descrizione |
| --- | --- |
| `[CREATE_DIR]` | Crea una nuova directory |
| `[DELETE_DIR]` | Elimina directory ricorsivamente |
| `[LIST_DIR]` | Elenca contenuto cartella (ls) |
| `[TREE]` | Visualizza struttura ad albero |

### Esecuzione Sistema

| Comando | Descrizione | Esempi |
| --- | --- | --- |
| `[EXECUTE]` | Esegue comandi shell | `python app.py`, `pip install`, `git status` |
| `[SEARCH]` | Cerca file con pattern (Regex) | Trovare tutti i `.py` o file specifici |
| `[DONE]` | Segna task completato | Termina l'esecuzione e riassume |
| `[RESPOND]` | Risponde all'utente | Chiedere chiarimenti o conversare |

## 💡 Esempi Pratici

### Esempio 1: Creazione Progetto Web

**Task**: "Crea un sito web base con HTML, CSS e un file JS nella cartella 'sito'"

L'AI eseguirà autonomamente:

1. `[CREATE_DIR]` path: sito
2. `[CREATE_FILE]` path: sito/index.html
3. `[CREATE_FILE]` path: sito/style.css
4. `[CREATE_FILE]` path: sito/app.js
5. `[DONE]` Riepilogo creazione sito.

### Esempio 2: Refactoring Codice

**Task**: "Leggi il file main.py e cambia il colore dei messaggi di errore in ROSSO"

L'AI gestirà:

1. `[READ_FILE]` path: main.py
2. Analisi del codice
3. `[EDIT_FILE]` Sostituzione codici colore ANSI
4. `[EXECUTE]` Test del file (se richiesto)

### Esempio 3: Esplorazione e Pulizia

**Task**: "Mostrami la struttura della cartella corrente ed elimina i file .log"

L'AI eseguirà:

1. `[TREE]` path: . depth: 2
2. `[SEARCH]` pattern: .log
3. `[DELETE_FILE]` per ogni file trovato (con conferma utente)

## ⚙️ Configurazione Avanzata

### Variabili d'Ambiente

Per i provider Cloud, imposta le chiavi prima dell'avvio:

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GROQ_API_KEY="gsk-..."

# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."

```

### Configurazione `config.py`

Puoi modificare i parametri di default direttamente nel file:

```python
@dataclass
class Config:
    provider: str = "lmstudio"      # Provider predefinito
    safe_mode: bool = True          # Attiva conferme per azioni pericolose
    workspace: str = "./workspace"  # Sandbox operativa
    max_file_size_mb: int = 10      # Limite lettura file

```

## 🔧 Risoluzione Problemi

### Errore: "Comando sconosciuto / Risposta non valida"

**Causa**: Il modello LLM non ha rispettato il formato dei tag `[COMANDO]`.

**Soluzione**:

* Usa un modello più capace (es. Llama 3 8B invece di modelli < 7B).
* Abbassa la temperatura nel provider in `agent.py`.
* L'agente proverà automaticamente a correggersi al prossimo turno.

### Errore: "Accesso negato / Fuori dalla workspace"

**Causa**: L'AI ha tentato di accedere a file di sistema (es. `/etc/passwd`).

**Soluzione**:

* Il sistema di sicurezza impedisce l'uscita dalla cartella `./workspace` tramite i file tools.
* Usa `[EXECUTE]` con percorsi assoluti se strettamente necessario (e se Safe Mode lo permette).

### LM Studio non risponde

**Causa**: Server locale non avviato o porta errata.

**Soluzione**:

1. Apri LM Studio -> Local Server.
2. Verifica che l'URL sia `http://localhost:1234/v1`.
3. Assicurati di aver caricato un modello in memoria.

## 🤝 Contribuire

Contributi benvenuti! Per favore:

1. Fork del repository
2. Crea un branch (`git checkout -b feature/NuovaFunzionalita`)
3. Apri una Pull Request

## ⚠️ Avvertenze

* **Backup**: Anche se opera in una workspace, l'uso di `[EXECUTE]` (shell) è potente. Non eseguire su dati sensibili senza backup.
* **Costi API**: Se usi OpenAI/Anthropic, monitora il consumo dei token.
* **Safe Mode**: Si consiglia di tenerla sempre attiva (`True`) per evitare cancellazioni accidentali.

---

**Creato con ❤️ per l'automazione intelligente**
