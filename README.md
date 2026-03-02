<h1 align="center">🛡️ Appunti di <strong>Crimini Informatici e Sicurezza delle Reti</strong></h1>

<p align="center">
  <em>Un viaggio tra vulnerabilità, risk management e hacking, alla scoperta di come difendere i sistemi digitali.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Stato-In%20sviluppo-blue?style=for-the-badge" alt="Stato: In sviluppo"/>
  <img src="https://img.shields.io/badge/Linguaggio-LaTeX-green?style=for-the-badge" alt="Linguaggio: LaTeX"/>
  <img src="https://img.shields.io/badge/Focus-Cybersecurity%20%26%20Risk%20Management-orange?style=for-the-badge" alt="Focus: Cybersecurity & Risk Management"/>
</p>

---

### 🧠 Descrizione

Questo repository raccoglie i miei **appunti strutturati e approfondimenti** per il corso universitario di **Crimini informatici e sicurezza dei computer e delle reti**.  

Il progetto nasce da un metodo di studio meticoloso e ibrido:  
> **L'ascolto attivo in aula**, unito a registrazioni elaborate tramite **modelli di intelligenza artificiale (Transformers)** per ottenere trascrizioni fedeli.  
> **L'integrazione accademica**, fondendo il testo sbobinato con le slide ufficiali del corso, i testi di riferimento e le spiegazioni tecniche, il tutto impaginato in **LaTeX** per la massima qualità tipografica.

Dalla triade CIA (Riservatezza, Integrità, Disponibilità) e l'analisi del rischio (ISO/NIST), fino allo studio pratico delle vulnerabilità web (OWASP Top 10, SQL Injection, XSS), questo percorso esplora come difendere le infrastrutture tenendo sempre a mente una regola d'oro: **il fattore umano è l'anello più debole della catena**.

---

### 🎯 Obiettivi del progetto

- Creare una risorsa accademica organica, professionale e altamente visiva (con schemi e diagrammi) sullo studio della **Cybersecurity**.  
- Approfondire i framework di **Risk Management** e l'evoluzione delle minacce informatiche, dagli attacchi opportunistici alle Advanced Persistent Threats (APT).  
- Analizzare nel dettaglio i protocolli di rete, i meccanismi di crittografia e le vulnerabilità *by design* e *by misconfiguration*.  
- Fornire una solida base teorica e pratica per chiunque voglia comprendere le dinamiche del **Data Leak**, dell'hacking delle applicazioni web e delle contromisure di difesa.

---

```bash
├── 📁 dataset
│   └── 🐍 dataset.py
│
├── 📁 images
│   ├── 🖼️ flusso_minaccia.png
│   ├── 🖼️ iceberg_web.png
│   ├── 🖼️ owasp_top10.png
│   ├── 🖼️ risk_management.png
│   ├── 🖼️ sensitive_data_exposure.png
│   ├── 🖼️ sql_injection.png
│   └── 🖼️ xss_attack.png
│
├── 📁 model
│   └── 🐍 model.py
│
├── 📁 sezioni
│   ├── 📄 Intro.tex
│   └── 📄 index.tex
│
├── 📁 slide
│
├── 📁 transcriptions
│   ├── 📄 Sicurezza lez 1.txt
│   ├── 📄 Sicurezza lez 2.txt
│   └── 📄 Sicurezza lez 3.txt
│
├── ⚙️ .gitignore
├── 📝 README.md
│
├── 📄 appunti.tex
│
├── 🐍 config.py
├── ⚙️ config.yaml
├── ⚙️ environment.yaml
│
├── 🐍 download_data.py
├── 🐍 upload_data.py
│
├── 🐍 inference.py
│
├── 📄 prepare.sh
└── 📄 requirements.txt
```

---

## 🎙️ Pipeline di Trascrizione Audio (Inference Engine)

Il core di questo repository è un framework di inferenza modulare e *production-ready*, progettato per scaricare, pulire e trascrivere lezioni universitarie sfruttando modelli AI State-of-the-Art (Whisper). 

L'architettura è basata sul principio della **Separazione delle Responsabilità (SoC)** e garantisce un'esecuzione robusta, *fail-fast* (grazie alla validazione rigorosa dei parametri) e facilmente monitorabile.

[Image of audio processing and speech-to-text pipeline architecture]

### ⚙️ Architettura e Moduli Principali

Il processo di trascrizione è orchestrato da una serie di moduli disaccoppiati che comunicano attraverso una configurazione centralizzata:

* **`config.yaml` & `config.py` (Single Source of Truth):**
  Tutti i parametri operativi (modello AI, impostazioni audio, device, parametri VAD) sono definiti in `config.yaml`. Il file `config.py` utilizza **Pydantic** per caricare, tipizzare e validare questi dati a runtime, bloccando l'esecuzione immediatamente in caso di configurazioni errate.
* **`download_data.py` (Kaggle Downloader):**
  Interroga le API di Kaggle per scaricare in modo selettivo o massivo i file audio (`.m4a` / `.mp4`) delle lezioni in un ambiente locale. Estrae dal pacchetto `.zip` solo i file necessari per ottimizzare l'uso della memoria.
* **`dataset/dataset.py` (Audio Preprocessing):**
  Si occupa dell'ingegneria del dato audio. Estrae la traccia dal contenitore video tramite `ffmpeg` (forzando il campionamento a 16kHz mono, il formato ottimale per Whisper) ed esegue opzionalmente algoritmi di *Noise Reduction* per abbattere il rumore di fondo delle aule.
* **`model/model.py` (AI Inference):**
  Gestisce il ciclo di vita del modello `faster-whisper`. Implementa filtri VAD (*Voice Activity Detection*) per ignorare i silenzi e prevenire allucinazioni del modello. Fornisce inoltre una barra di avanzamento real-time basata sui timestamp audio per monitorare l'elaborazione.
* **`inference.py` (Orchestrator):**
  È l'entry-point della pipeline. Non contiene logica di business diretta, ma coordina i moduli: individua i file da processare, salta quelli già trascritti (caching), avvia il pre-processing, chiama l'inferenza e gestisce il salvataggio dei file `.txt` finali, oltre alla pulizia dei file temporanei.

---

### 🚀 Guida all'Uso

Per avviare l'intero processo di acquisizione e trascrizione, segui questi passaggi:

**1. Preparazione dell'Ambiente**
Assicurati di avere le dipendenze installate e i tool di sistema (come `ffmpeg`) configurati. 
```bash
bash prepare.sh
```

**2. Setup delle Credenziali Kaggle**
Assicurati che il file `kaggle.json` (contenente le tue chiavi API) sia presente nella root del progetto. Il sistema lo rileverà automaticamente per autenticarsi.

**3. Download del Dataset**
Avvia lo script di download. Ti verrà presentata una CLI interattiva per selezionare quali lezioni scaricare dalla repository remota:
```bash
python download_data.py
```
I file verranno salvati nella directory definita in `config.yaml` (default: `data/`).

**4. Esecuzione dell'Inferenza (Batch Processing)**
Una volta che i file audio sono in locale, avvia l'orchestratore. Il sistema elaborerà automaticamente tutti i file non ancora trascritti:
```bash
python inference.py
```
Durante l'esecuzione, il terminale mostrerà un log dettagliato delle operazioni e una **progress bar** che stima il tempo residuo (ETA) per ogni singola lezione.

**5. Risultati**
A processo concluso, le trascrizioni testuali grezze saranno disponibili e pronte all'uso nella cartella di output:
`📁 transcriptions/`

> [!IMPORTANT]
> 
> È consigliato l'utilizzo di un ambiente conda.

--- 

<!--───────────────────────────────────────────────-->
<!--                   AUTORE                     -->
<!--───────────────────────────────────────────────-->

<h2 align="center">✨ Autore ✨</h2>

<p align="center">
  <strong>Giovanni Giuseppe Iacuzzo</strong><br>
  <em>Studente di Ingegneria Dell'IA e della CyberSecurity · Università degli Studi Kore di Enna</em>
</p>

<p align="center">
  <a href="https://github.com/giovanniIacuzzo" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-%40giovanniIacuzzo-181717?style=for-the-badge&logo=github" alt="GitHub"/>
  </a>
  <a href="mailto:giovanni.iacuzzo@unikore.it">
    <img src="https://img.shields.io/badge/Email-Contattami-blue?style=for-the-badge&logo=gmail" alt="Email"/>
  </a>
</p>

---
