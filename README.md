# 🤖 Sistema Agentico AI con LM Studio

Un sistema che permette a modelli AI locali di operare autonomamente sul computer, eseguendo task complessi attraverso azioni sequenziali sul file system.

## 📋 Caratteristiche

- ✅ **Autonomia completa**: L'AI analizza, pianifica ed esegue task senza intervento umano
- 🔄 **Gestione memoria intelligente**: Ottimizzazione automatica del contesto per conversazioni lunghe
- 🛠️ **13 comandi operativi**: Gestione completa di file, directory e shell
- 📝 **Logging dettagliato**: Tracciamento di tutte le operazioni eseguite
- 🔒 **Controllo iterazioni**: Limite massimo configurabile per evitare loop infiniti
- 🧠 **Ragionamento esplicito**: Ogni azione include il processo decisionale dell'AI

## 🚀 Prerequisiti

### Software Richiesto

1. **Python 3.7+**
2. **[LM Studio](https://lmstudio.ai/)** installato e configurato
3. Dipendenze Python:
   ```bash
   pip install requests
   ```

### Configurazione LM Studio

1. Scarica e installa LM Studio
2. Scarica un modello compatibile (es. Llama 3, Mistral, Phi-3)
3. Avvia il server locale:
   - Apri LM Studio
   - Vai su "Local Server"
   - Clicca "Start Server"
   - Verifica che sia in esecuzione su `http://localhost:1234`

## 📦 Installazione

```bash
# Clone del repository
git clone https://github.com/tuousername/ai-agent-lmstudio.git
cd ai-agent-lmstudio

# Installazione dipendenze
pip install -r requirements.txt

# Rendi eseguibile lo script (Linux/Mac)
chmod +x ai_agent.py
```

## 🎮 Utilizzo Rapido

### Avvio Base

```bash
python ai_agent.py
```

### Esempio di Sessione

```
📡 CONFIGURAZIONE LM STUDIO
URL LM Studio (default: http://localhost:1234/v1): [INVIO]
✓ Connesso a LM Studio
  Modello auto-selezionato: llama-3-8b-instruct

📁 CONFIGURAZIONE DIRECTORY
Directory di lavoro (vuoto per corrente): ./progetti

🎯 DEFINISCI IL TASK
Cosa vuoi che l'AI faccia?
> Crea un server web Flask con endpoint /health che ritorna {"status": "ok"}

🤖 ESECUZIONE AGENTICA
[L'AI procede autonomamente...]
```

## 📚 Comandi Disponibili

### Gestione File

| Comando | Descrizione | Esempio |
|---------|-------------|---------|
| `CREATE_FILE` | Crea un nuovo file | Scrivere codice, configurazioni |
| `READ_FILE` | Legge contenuto file | Analizzare codice esistente |
| `MODIFY_FILE` | Modifica file esistente | Aggiungere righe, sostituire contenuto |
| `DELETE_FILE` | Elimina file | Pulizia file temporanei |
| `MOVE_FILE` | Sposta file | Riorganizzare struttura |
| `COPY_FILE` | Copia file | Backup, duplicazione |
| `GET_INFO` | Info su file | Dimensione, data modifica |

### Gestione Directory

| Comando | Descrizione |
|---------|-------------|
| `CREATE_DIR` | Crea directory (ricorsivo) |
| `DELETE_DIR` | Elimina directory e contenuto |
| `LIST_FILES` | Elenca file (supporta pattern glob) |
| `SEARCH_FILES` | Cerca per nome o contenuto |

### Esecuzione Sistema

| Comando | Descrizione | Esempi |
|---------|-------------|--------|
| `EXECUTE_SHELL` | Esegue comandi shell | `git init`, `python test.py`, `npm install` |
| `DONE` | Segna task completato | Termina l'esecuzione |

## 💡 Esempi Pratici

### Esempio 1: Creare Applicazione Web

**Task**: "Crea un'applicazione Flask con homepage e API REST per gestire TODO"

L'AI eseguirà autonomamente:
1. Creazione struttura directory
2. File `app.py` con Flask
3. Template HTML
4. File `requirements.txt`
5. Test dell'applicazione
6. Verifica funzionamento

### Esempio 2: Setup Progetto Python

**Task**: "Inizializza un progetto Python con poetry, struttura src/tests e pre-commit"

L'AI gestirà:
1. Installazione Poetry
2. Creazione `pyproject.toml`
3. Struttura directory standard
4. Configurazione pre-commit
5. File README e .gitignore

### Esempio 3: Analisi e Refactoring

**Task**: "Trova tutti i file Python, analizza le funzioni duplicate e crea un modulo utils"

L'AI eseguirà:
1. Ricerca file `.py`
2. Lettura e analisi codice
3. Identificazione duplicati
4. Creazione `utils.py`
5. Refactoring file originali

## ⚙️ Configurazione Avanzata

### Modifica Parametri

Modifica direttamente nello script `ai_agent.py`:

```python
class AIAgent:
    def __init__(self, working_dir=None):
        self.max_iterations = 20  # Cambia qui il limite iterazioni

class LMStudioClient:
    def __init__(self, base_url="http://localhost:1234/v1", model=None):
        self.history_limit = 10  # Messaggi di storia mantenuti
```

### Temperature e Creatività

Nel metodo `chat()` di `LMStudioClient`:

```python
payload = {
    "temperature": 0.7,  # 0.0 = deterministico, 1.0 = creativo
    "max_tokens": -1,    # -1 = massimo disponibile
}
```

## 🔧 Risoluzione Problemi

### Errore: "LM Studio non raggiungibile"

**Causa**: Server LM Studio non attivo

**Soluzione**:
```bash
1. Apri LM Studio
2. Vai su "Local Server"
3. Clicca "Start Server"
4. Verifica porta 1234
```

### Errore 500: "Memoria piena"

**Causa**: Contesto del modello esaurito

**Soluzione**:
- Riduci `history_limit` in `LMStudioClient`
- Usa un modello con contesto maggiore (32k+ tokens)
- Riavvia lo script per conversazioni molto lunghe

### L'AI ripete comandi falliti

**Causa**: Modello non interpreta correttamente gli errori

**Soluzione**:
- Usa modelli più capaci (≥7B parametri)
- Aumenta la temperatura per risposte più creative
- Verifica che il system prompt sia caricato correttamente

### Comandi JSON non validi

**Causa**: Modello genera testo extra fuori dal JSON

**Soluzione**: La funzione `extract_json_from_response()` gestisce automaticamente questi casi

## 🤝 Contribuire

Contributi benvenuti! Per favore:

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/NuovaFunzionalita`)
3. Commit delle modifiche (`git commit -m 'Aggiunta NuovaFunzionalita'`)
4. Push al branch (`git push origin feature/NuovaFunzionalita`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## ⚠️ Avvertenze

- **Sicurezza**: L'AI ha accesso completo al file system nella directory configurata
- **Validazione**: Usa sempre una directory di test per sperimentare
- **Backup**: Fai backup prima di task su directory importanti
- **Supervisione**: Monitora le prime esecuzioni per verificare comportamento
- **Comandi Shell**: L'AI può eseguire qualsiasi comando shell - usa con cautela

## 🌟 Funzionalità Future

- [ ] Supporto per operazioni di rete (HTTP requests)
- [ ] Integrazione con Git (commit, push automatici)
- [ ] Modalità interattiva con approvazione manuale
- [ ] Plugin system per comandi custom
- [ ] Dashboard web per monitoraggio
- [ ] Supporto multi-modello (cambio dinamico)

## 📞 Supporto

Per bug, feature request o domande:
- Apri una [Issue](https://github.com/tuousername/ai-agent-lmstudio/issues)
- Discussioni su [GitHub Discussions](https://github.com/tuousername/ai-agent-lmstudio/discussions)

## 🙏 Ringraziamenti

- [LM Studio](https://lmstudio.ai/) per l'ottimo client locale
- Community open-source dei modelli LLM
- Tutti i contributori del progetto

---

**Creato con ❤️ per l'automazione intelligente**
