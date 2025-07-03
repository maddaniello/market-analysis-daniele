# 🚀 Analizzatore Marketing AI

Un'applicazione Python completa per l'analisi automatica di aziende e competitor nel mercato italiano, utilizzando OpenAI GPT-4 e tecniche di web scraping avanzate.

## 📋 Caratteristiche Principali

### 🏢 Analisi Aziendale Completa
- **Dati Camera di Commercio**: P.IVA, sede legale, settore ATECO, forma giuridica
- **Analisi Finanziaria**: Fatturato, trend di crescita, patrimonio netto, dipendenti
- **Performance SEO**: Keywords organiche, traffico, backlinks, domain authority
- **Social Media Analytics**: Follower, engagement rate, performance su tutte le piattaforme
- **Struttura Societaria**: Soci, organi sociali, quote di partecipazione

### 🎯 Analisi Competitor
- **Identificazione Automatica**: Trova i principali competitor nel settore
- **Benchmark Completo**: Confronto su metriche SEO, social, financial
- **Posizionamento Competitivo**: Analisi punti di forza/debolezza relativi
- **Raccomandazioni Strategiche**: Suggerimenti specifici per migliorare la competitività

### 📊 Report e Visualizzazioni
- **Dashboard Interattivo**: Grafici e metriche in tempo reale
- **Report Downloadabili**: Formato JSON e Markdown
- **Analisi SWOT**: Punti di forza, debolezze, opportunità, minacce
- **Trend Analysis**: Visualizzazione dell'evoluzione temporale

## 🛠️ Installazione

### Prerequisiti
- Python 3.8 o superiore
- OpenAI API Key
- SEMRush API Key (opzionale, per dati SEO reali)

### Setup Locale

1. **Clona il repository**:
```bash
git clone https://github.com/tuousername/marketing-analyzer-ai.git
cd marketing-analyzer-ai
```

2. **Installa le dipendenze**:
```bash
pip install -r requirements.txt
```

3. **Configura le variabili d'ambiente**:
```bash
cp .env.example .env
# Modifica .env con le tue API keys
```

4. **Avvia l'applicazione**:
```bash
streamlit run app.py
```

### Deploy su Streamlit Cloud

1. **Fork il repository** su GitHub
2. **Connetti a Streamlit Cloud**:
   - Vai su [streamlit.io](https://streamlit.io)
   - Clicca "New App"
   - Seleziona il tuo repository
   - Imposta file principale: `app.py`
3. **Configura i secrets**:
   - In Streamlit Cloud, vai su Settings → Secrets
   - Aggiungi le tue API keys:
```toml
OPENAI_API_KEY = "sk-your-openai-key"
SEMRUSH_API_KEY = "your-semrush-key"
```

## 🔑 Configurazione API Keys

### OpenAI API Key (Obbligatoria)
1. Registrati su [OpenAI](https://platform.openai.com/)
2. Genera una nuova API key
3. Aggiungi credito al tuo account (minimo $5)
4. Inserisci la key nell'applicazione

### SEMRush API Key (Opzionale)
1. Registrati su [SEMRush](https://www.semrush.com/)
2. Sottoscrivi un piano API
3. Genera la tua API key
4. Inserisci la key per dati SEO reali

*Nota: Senza SEMRush, l'app userà dati SEO simulati ma realistici*

## 🚀 Utilizzo

### Analisi Base
1. **Inserisci nome azienda** o URL del sito web
2. **Clicca "Avvia Analisi"**
3. **Attendi il completamento** (2-3 minuti)
4. **Esplora i risultati** nelle diverse sezioni

### Funzionalità Avanzate

#### 📈 Analisi Finanziaria
- Visualizza trend di fatturato degli ultimi 5 anni
- Confronta crescita anno su anno
- Analizza struttura patrimoniale

#### 🔍 SEO Performance
- Monitora posizionamento organico
- Analizza profilo backlinks
- Stima valore del traffico

#### 📱 Social Media
- Traccia crescita follower
- Misura engagement rate
- Confronta performance multi-piattaforma

#### 🎯 Competitive Analysis
- Identifica competitor principali
- Confronta metriche chiave
- Ricevi raccomandazioni strategiche

## 📊 Esempi di Output

### Report Aziendale
```
📊 VENEZIANICO SRL
P.IVA: 04427770278
Fatturato 2023: €7.489.581 (+140%)
SEO Keywords: 6.223
Instagram Followers: 117.587
```

### Analisi SWOT
```
💪 PUNTI DI FORZA:
- Heritage veneziano unico
- Crescita finanziaria esponenziale
- Community social consolidata
- Design distintivo riconoscibile

⚠️ PUNTI DI DEBOLEZZA:
- Struttura aziendale snella
- Dipendenza dai fondatori
- Limitata diversificazione prodotti

🌟 OPPORTUNITÀ:
- Espansione mercati internazionali
- Diversificazione gamma prodotti
- Sviluppo esperienze fisiche

🚨 MINACCE:
- Concorrenza crescente microbrand
- Volatilità mercato lusso
- Rischio contraffazione
```

## 🏗️ Architettura del Progetto

```
marketing-analyzer-ai/
├── app.py                    # Applicazione Streamlit principale
├── config.py                 # Configurazioni e costanti
├── camera_commercio_scraper.py # Scraper Camera di Commercio
├── competitor_analyzer.py    # Analizzatore competitor
├── requirements.txt          # Dipendenze Python
├── README.md                # Documentazione
├── .env.example             # Template variabili ambiente
└── utils/
    ├── __init__.py
    ├── data_processors.py   # Processori dati
    ├── visualization.py     # Grafici e visualizzazioni
    └── export_utils.py      # Utility per export
```

## 🔧 Componenti Principali

### MarketingAnalyzer
Classe principale che orchestra tutte le analisi:
- Ricerca informazioni aziendali
- Analisi SEO e social media
- Generazione report completi
- Integrazione con OpenAI GPT-4

### CameraCommercioScraper
Estrazione dati ufficiali:
- Informazioni registrate alla Camera di Commercio
- Dati finanziari e bilanci
- Struttura societaria
- Codici ATECO e classificazioni

### CompetitorAnalyzer
Analisi competitiva avanzata:
- Identificazione automatica competitor
- Benchmark multi-dimensionale
- Analisi posizionamento
- Raccomandazioni strategiche

## 📈 Metriche Analizzate

### 🏢 Dati Aziendali
- **Anagrafici**: P.IVA, Codice Fiscale, Sede Legale
- **Societari**: Forma giuridica, Capitale sociale, Soci
- **Settoriali**: Codice ATECO, Descrizione attività
- **Temporali**: Data costituzione, Stato attuale

### 💰 Finanziari
- **Fatturato**: Trend pluriennale, Crescita YoY
- **Patrimonio**: Netto, Attivo totale, Passivo
- **Personale**: Dipendenti, Costo del lavoro
- **Redditività**: Margini, ROI, ROE

### 🔍 SEO & Digital
- **Organico**: Keywords, Traffico, Posizioni
- **Backlinks**: Profilo, Qualità, Autorità
- **Tecnico**: Velocità, Mobile-friendly, Core Web Vitals
- **Competitor**: Gap analysis, Opportunità

### 📱 Social Media
- **Reach**: Follower, Crescita, Distribuzione
- **Engagement**: Rate, Interazioni, Commenti
- **Content**: Frequenza, Qualità, Tipologia
- **Performance**: Impression, Click, Conversioni

## 🎯 Casi d'Uso

### 🏪 Analisi Pre-Acquisizione
- Due diligence finanziaria
- Valutazione posizionamento mercato
- Identificazione rischi e opportunità
- Stima potenziale crescita

### 📊 Benchmark Competitivo
- Confronto performance settoriali
- Analisi gap competitivi
- Identificazione best practices
- Pianificazione strategica

### 🚀 Pianificazione Marketing
- Audit presenza digitale
- Ottimizzazione SEO
- Strategia social media
- Budget allocation

### 💼 Consulenza Aziendale
- Report clienti professionali
- Analisi settoriali
- Raccomandazioni strategiche
- Monitoraggio competitor

## 🔒 Privacy e Sicurezza

### Gestione Dati
- **Nessun salvataggio locale** di dati sensibili
- **Crittografia** delle API keys
- **Anonimizzazione** dei dati processati
- **Conformità GDPR** italiana

### Rate Limiting
- **Throttling automatico** per evitare ban
- **Retry logic** per richieste fallite
- **Caching intelligente** per ridurre chiamate API
- **Monitoring utilizzo** API keys

## 🐛 Troubleshooting

### Problemi Comuni

#### ❌ "OpenAI API Key non valida"
```bash
# Verifica formato key
echo $OPENAI_API_KEY
# Deve iniziare con "sk-"
```

#### ❌ "Errore connessione"
```bash
# Controlla connessione internet
ping google.com
# Verifica proxy/firewall
```

#### ❌ "Timeout richieste"
```bash
# Aumenta timeout in config.py
TIMEOUT = 60  # secondi
```

#### ❌ "Quota API superata"
- Controlla utilizzo su OpenAI Dashboard
- Aggiungi credito all'account
- Riduci frequenza richieste

### Debug Mode
```python
# Attiva logging dettagliato
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Roadmap Sviluppo

### V1.1 (Prossimo Release)
- [ ] Integrazione Google Analytics
- [ ] Export PDF professionale
- [ ] Scheduling analisi automatiche
- [ ] API REST per integrazioni

### V1.2 (Futuro)
- [ ] Database persistente
- [ ] Analisi sentiment brand
- [ ] Predizioni machine learning
- [ ] Dashboard multi-cliente

### V2.0 (Visione)
- [ ] Analisi video/immagini
- [ ] Integrazione CRM
- [ ] Reportistica white-label
- [ ] Marketplace competitor intelligence

## 🤝 Contribuire

### Come Contribuire
1. **Fork** il repository
2. **Crea branch** per feature: `git checkout -b feature/nuova-funzione`
3. **Commit** modifiche: `git commit -m 'Aggiungi nuova funzione'`
4. **Push** branch: `git push origin feature/nuova-funzione`
5. **Apri Pull Request**

### Linee Guida
- Segui PEP 8 per stile Python
- Aggiungi test per nuove funzioni
- Documenta modifiche nel README
- Mantieni compatibilità backward

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi file `LICENSE` per dettagli.

## 📞 Supporto

### Contatti
- **GitHub Issues**: Per bug report e feature request
- **Email**: support@marketing-analyzer.com
- **Discord**: [Server Community](https://discord.gg/marketing-analyzer)

### FAQ

**Q: Posso usare l'app senza OpenAI API?**
A: No, OpenAI è necessario per analisi AI. Considera costi ~$0.50 per analisi completa.

**Q: I dati sono accurati al 100%?**
A: I dati sono stime basate su AI e scraping. Per dati certificati, consulta fonti ufficiali.

**Q: Posso analizzare aziende estere?**
A: Sì, ma l'app è ottimizzata per il mercato italiano. Risultati migliori con aziende italiane.

**Q: Quanto tempo richiede un'analisi?**
A: 2-5 minuti per analisi completa, dipende da dimensioni azienda e competitor.

**Q: Posso automatizzare le analisi?**
A: Sì, usando l'API mode (feature in sviluppo) o scheduling script personalizzati.

---

## 🌟 Powered by

- **OpenAI GPT-4** - Analisi intelligente
- **Streamlit** - Interface utente
- **Python** - Backend robusto
- **BeautifulSoup** - Web scraping
- **Plotly** - Visualizzazioni interattive

---

*Realizzato con ❤️ per il marketing digitale italiano*
