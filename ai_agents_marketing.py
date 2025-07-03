import streamlit as st
import openai
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
import re
import time
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import urllib.parse
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurazione Streamlit
st.set_page_config(
    page_title="🤖 AI Agents Marketing Research",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AIAgentsSystem:
    """Sistema di AI Agents specializzati per ricerca marketing"""
    
    def __init__(self, openai_api_key: str, semrush_api_key: str = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.semrush_api_key = semrush_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Inizializza gli agenti specializzati
        self.agents = {
            'financial_agent': self.create_financial_agent(),
            'digital_agent': self.create_digital_agent(), 
            'competitor_agent': self.create_competitor_agent(),
            'company_agent': self.create_company_agent(),
            'social_agent': self.create_social_agent()
        }
    
    def create_financial_agent(self) -> Dict:
        """Crea agente specializzato per dati finanziari"""
        return {
            'name': 'Financial Research Agent',
            'role': 'Specialista in ricerca dati finanziari aziendali',
            'instructions': '''
            Sei un esperto ricercatore finanziario. Il tuo compito è trovare dati finanziari REALI e verificati per le aziende italiane.
            
            FONTI PRIORITARIE:
            1. Registro Imprese (registroimprese.it)
            2. Camera di Commercio (infocamere.it)
            3. Ufficio Camerale (ufficiocamerale.it)
            4. Bilanci depositati ufficiali
            5. Comunicati stampa aziendali
            6. Relazioni annuali
            
            DATI DA CERCARE:
            - P.IVA e Codice Fiscale
            - Ragione sociale completa
            - Sede legale e operative
            - Forma giuridica
            - Codice ATECO
            - Capitale sociale
            - Fatturato (ultimo anno disponibile)
            - Numero dipendenti
            - Patrimonio netto
            - Trend crescita
            - Situazione finanziaria
            
            METODOLOGIA:
            1. Inizia sempre con ricerche su fonti ufficiali
            2. Verifica incrociando multiple fonti
            3. Indica sempre la fonte di ogni dato
            4. Non inventare mai dati se non li trovi
            5. Specifica il livello di affidabilità
            ''',
            'tools': ['web_search', 'web_scraping', 'data_extraction']
        }
    
    def create_digital_agent(self) -> Dict:
        """Crea agente specializzato per digital marketing"""
        return {
            'name': 'Digital Marketing Agent',
            'role': 'Specialista in analisi digital marketing e SEO',
            'instructions': '''
            Sei un esperto di digital marketing e SEO. Trova dati REALI sulle performance digitali delle aziende.
            
            FONTI E STRUMENTI:
            1. SEMRush API (se disponibile)
            2. Ahrefs data (tramite ricerca)
            3. SimilarWeb statistics
            4. Google Trends
            5. Analisi diretta siti web
            6. Social media analytics
            
            METRICHE DA RACCOGLIERE:
            - Traffico organico mensile
            - Keywords posizionate
            - Posizione media keywords
            - Backlinks totali
            - Domini referenti
            - Domain Authority/Rating
            - Traffico a pagamento
            - Principali competitor SEO
            - Trend di crescita
            - Tecnologie utilizzate
            
            METODOLOGIA:
            1. Usa SEMRush API se disponibile
            2. Analizza direttamente il sito web
            3. Cerca dati su tool di analisi pubblici
            4. Verifica con strumenti gratuiti
            5. Incrocia dati da multiple fonti
            ''',
            'tools': ['semrush_api', 'web_analysis', 'seo_tools']
        }
    
    def create_competitor_agent(self) -> Dict:
        """Crea agente specializzato per analisi competitor"""
        return {
            'name': 'Competitor Analysis Agent',
            'role': 'Specialista in analisi competitiva e market intelligence',
            'instructions': '''
            Sei un esperto di competitive intelligence. Identifica e analizza i competitor reali dell'azienda.
            
            METODOLOGIA RICERCA:
            1. Analisi settore e mercato di riferimento
            2. Ricerca competitor diretti e indiretti
            3. Analisi posizionamento competitivo
            4. Benchmark performance
            5. Trend di mercato
            
            DATI DA RACCOGLIERE:
            - Competitor diretti (5-10)
            - Competitor indiretti (3-5)
            - Quote di mercato stimate
            - Posizionamento competitivo
            - Punti di forza/debolezza relativi
            - Strategie competitive
            - Trend di mercato
            - Opportunità e minacce
            
            FONTI:
            1. Report di settore
            2. Analisi di mercato
            3. Comunicati stampa competitor
            4. Dati finanziari pubblici
            5. Presenza digitale competitor
            6. Social media analysis
            ''',
            'tools': ['market_research', 'competitor_analysis', 'industry_reports']
        }
    
    def create_company_agent(self) -> Dict:
        """Crea agente specializzato per profilo aziendale"""
        return {
            'name': 'Company Profile Agent',
            'role': 'Specialista in ricerca profili aziendali completi',
            'instructions': '''
            Sei un esperto ricercatore aziendale. Crea profili completi e accurati delle aziende.
            
            INFORMAZIONI DA RACCOGLIERE:
            - Storia e background aziendale
            - Missione e valori
            - Prodotti e servizi
            - Mercati di riferimento
            - Presenza geografica
            - Struttura organizzativa
            - Management team
            - Azionisti principali
            - Partnership strategiche
            - Innovazioni e brevetti
            
            FONTI:
            1. Sito web aziendale ufficiale
            2. LinkedIn company page
            3. Crunchbase profile
            4. Wikipedia
            5. Comunicati stampa
            6. Interviste management
            7. Case studies
            8. Award e riconoscimenti
            
            METODOLOGIA:
            1. Inizia dal sito web ufficiale
            2. Verifica su fonti multiple
            3. Cerca informazioni storiche
            4. Analizza comunicazione aziendale
            5. Identifica key differentiators
            ''',
            'tools': ['web_research', 'company_analysis', 'profile_building']
        }
    
    def create_social_agent(self) -> Dict:
        """Crea agente specializzato per social media"""
        return {
            'name': 'Social Media Agent',
            'role': 'Specialista in analisi social media e presenza digitale',
            'instructions': '''
            Sei un esperto di social media analytics. Analizza la presenza social delle aziende.
            
            PIATTAFORME DA ANALIZZARE:
            - Instagram (follower, engagement, contenuti)
            - Facebook (pagina, like, interazioni)
            - LinkedIn (company page, follower, engagement)
            - YouTube (canale, iscritti, visualizzazioni)
            - TikTok (se presente)
            - Twitter/X (se presente)
            
            METRICHE DA RACCOGLIERE:
            - Numero follower per piattaforma
            - Engagement rate medio
            - Frequenza posting
            - Tipologia contenuti
            - Interazioni medie
            - Crescita follower
            - Reach e impression (se disponibili)
            - Sentiment analysis
            
            METODOLOGIA:
            1. Identifica profili ufficiali
            2. Analizza metriche pubbliche
            3. Valuta qualità contenuti
            4. Calcola engagement rate
            5. Confronta con competitor
            ''',
            'tools': ['social_analysis', 'engagement_metrics', 'content_analysis']
        }
    
    def execute_agent_research(self, agent_name: str, company_name: str, company_url: str = None) -> Dict:
        """Esegue ricerca specializzata di un agente"""
        try:
            agent = self.agents[agent_name]
            
            # Crea prompt specializzato per l'agente
            prompt = f"""
            {agent['instructions']}
            
            COMPITO SPECIFICO:
            Analizza l'azienda "{company_name}" {f'(sito web: {company_url})' if company_url else ''}
            
            ISTRUZIONI:
            1. Conduci una ricerca approfondita usando le metodologie specificate
            2. Trova SOLO dati reali e verificabili
            3. Indica sempre la fonte di ogni informazione
            4. Non inventare mai dati se non li trovi
            5. Specifica il livello di affidabilità di ogni dato
            6. Fornisci un output strutturato e professionale
            
            RICHIESTA:
            Fornisci un report completo secondo la tua specializzazione per l'azienda "{company_name}".
            """
            
            # Esegui ricerca web specializzata
            search_results = self.specialized_web_search(agent_name, company_name, company_url)
            
            # Combina prompt con risultati di ricerca
            full_prompt = f"""
            {prompt}
            
            DATI DI RICERCA RACCOLTI:
            {json.dumps(search_results, indent=2, ensure_ascii=False)}
            
            Basandoti sui dati di ricerca raccolti, fornisci il tuo report specializzato.
            """
            
            # Chiamata a OpenAI con l'agente specializzato
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"Sei {agent['name']}. {agent['role']}."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=3000,
                temperature=0.1
            )
            
            agent_response = response.choices[0].message.content
            
            # Struttura la risposta dell'agente
            structured_response = self.structure_agent_response(agent_name, agent_response, search_results)
            
            return structured_response
            
        except Exception as e:
            st.error(f"Errore nell'esecuzione agente {agent_name}: {e}")
            return {"error": str(e)}
    
    def specialized_web_search(self, agent_name: str, company_name: str, company_url: str = None) -> Dict:
        """Ricerca web specializzata per tipo di agente"""
        try:
            search_results = {
                "agent": agent_name,
                "company": company_name,
                "searches_performed": [],
                "data_found": {}
            }
            
            # Query di ricerca specifiche per agente
            if agent_name == 'financial_agent':
                queries = [
                    f'"{company_name}" site:registroimprese.it',
                    f'"{company_name}" site:infocamere.it',
                    f'"{company_name}" p.iva partita iva',
                    f'"{company_name}" bilancio fatturato ricavi',
                    f'"{company_name}" camera commercio',
                    f'"{company_name}" sede legale indirizzo',
                    f'"{company_name}" dipendenti employees'
                ]
            elif agent_name == 'digital_agent':
                queries = [
                    f'"{company_name}" seo traffic statistics',
                    f'"{company_name}" website analysis',
                    f'"{company_name}" digital marketing performance',
                    f'"{company_name}" google rankings',
                    f'"{company_name}" backlinks domain authority'
                ]
            elif agent_name == 'competitor_agent':
                queries = [
                    f'"{company_name}" competitor analysis',
                    f'"{company_name}" market share competitors',
                    f'"{company_name}" industry rivals',
                    f'"{company_name}" competitive landscape',
                    f'"{company_name}" market positioning'
                ]
            elif agent_name == 'company_agent':
                queries = [
                    f'"{company_name}" company profile about',
                    f'"{company_name}" storia history founded',
                    f'"{company_name}" products services',
                    f'"{company_name}" management team',
                    f'"{company_name}" mission values'
                ]
            elif agent_name == 'social_agent':
                queries = [
                    f'"{company_name}" instagram profile',
                    f'"{company_name}" facebook page',
                    f'"{company_name}" linkedin company',
                    f'"{company_name}" youtube channel',
                    f'"{company_name}" social media presence'
                ]
            
            # Esegui ricerche
            for query in queries:
                try:
                    results = self.perform_web_search(query)
                    search_results["searches_performed"].append({
                        "query": query,
                        "results_count": len(results),
                        "results": results[:5]  # Limita a 5 risultati per query
                    })
                    
                    # Analizza risultati per estrarre dati
                    extracted_data = self.extract_data_from_results(results, agent_name)
                    if extracted_data:
                        search_results["data_found"].update(extracted_data)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    st.error(f"Errore nella ricerca '{query}': {e}")
                    continue
            
            return search_results
            
        except Exception as e:
            st.error(f"Errore nella ricerca specializzata: {e}")
            return {}
    
    def perform_web_search(self, query: str) -> List[Dict]:
        """Esegue ricerca web con DuckDuckGo"""
        try:
            # Usa DuckDuckGo HTML search
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Estrai risultati di ricerca
            for result_div in soup.find_all('div', class_='result')[:10]:
                try:
                    title_link = result_div.find('a', class_='result__a')
                    snippet_div = result_div.find('a', class_='result__snippet')
                    
                    if title_link:
                        title = title_link.get_text(strip=True)
                        url = title_link.get('href', '')
                        snippet = snippet_div.get_text(strip=True) if snippet_div else ''
                        
                        # Ottieni contenuto della pagina se rilevante
                        page_content = self.extract_page_content(url) if self.is_relevant_url(url, query) else ''
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'content': page_content[:1000] if page_content else ''
                        })
                
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            st.error(f"Errore nella ricerca web: {e}")
            return []
    
    def is_relevant_url(self, url: str, query: str) -> bool:
        """Verifica se l'URL è rilevante per la query"""
        if not url:
            return False
        
        # URL rilevanti per dati aziendali
        relevant_domains = [
            'registroimprese.it',
            'infocamere.it',
            'ufficiocamerale.it',
            'linkedin.com',
            'crunchbase.com',
            'wikipedia.org',
            'azienda.it'
        ]
        
        # Controlla se l'URL contiene domini rilevanti
        for domain in relevant_domains:
            if domain in url.lower():
                return True
        
        # Controlla se l'URL sembra essere il sito aziendale
        if any(word in url.lower() for word in ['company', 'azienda', 'about', 'chi-siamo']):
            return True
        
        return False
    
    def extract_page_content(self, url: str) -> str:
        """Estrae contenuto da una pagina web"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Rimuovi script e style
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Estrai testo principale
            text = soup.get_text()
            
            # Pulisci il testo
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            return ""
    
    def extract_data_from_results(self, results: List[Dict], agent_name: str) -> Dict:
        """Estrae dati specifici dai risultati di ricerca"""
        extracted_data = {}
        
        for result in results:
            content = f"{result.get('title', '')} {result.get('snippet', '')} {result.get('content', '')}"
            
            if agent_name == 'financial_agent':
                # Estrai dati finanziari
                if not extracted_data.get('piva'):
                    piva_match = re.search(r'P\.?\s*IVA[:\s]*(\d{11})', content, re.IGNORECASE)
                    if piva_match:
                        extracted_data['piva'] = piva_match.group(1)
                
                if not extracted_data.get('fatturato'):
                    fatturato_patterns = [
                        r'fatturato[:\s]*€?\s*([\d,]+(?:\.\d+)?)\s*(?:milioni?|mln|million)',
                        r'ricavi[:\s]*€?\s*([\d,]+(?:\.\d+)?)\s*(?:milioni?|mln|million)'
                    ]
                    for pattern in fatturato_patterns:
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            extracted_data['fatturato'] = match.group(1) + " milioni €"
                            break
                
                if not extracted_data.get('dipendenti'):
                    dipendenti_match = re.search(r'(\d+)\s*dipendenti', content, re.IGNORECASE)
                    if dipendenti_match:
                        extracted_data['dipendenti'] = dipendenti_match.group(1)
                
                if not extracted_data.get('sede'):
                    sede_match = re.search(r'sede[:\s]*([^,\n]+)', content, re.IGNORECASE)
                    if sede_match:
                        extracted_data['sede'] = sede_match.group(1).strip()
            
            elif agent_name == 'digital_agent':
                # Estrai dati digitali
                if not extracted_data.get('website'):
                    website_match = re.search(r'https?://[^\s]+', content)
                    if website_match:
                        extracted_data['website'] = website_match.group(0)
                
                # Cerca metriche SEO
                traffic_match = re.search(r'traffico[:\s]*(\d+[km]?)', content, re.IGNORECASE)
                if traffic_match:
                    extracted_data['traffic'] = traffic_match.group(1)
            
            elif agent_name == 'social_agent':
                # Estrai dati social
                if 'instagram' in content.lower():
                    follower_match = re.search(r'(\d+[km]?)\s*follower', content, re.IGNORECASE)
                    if follower_match:
                        extracted_data['instagram_followers'] = follower_match.group(1)
                
                if 'facebook' in content.lower():
                    like_match = re.search(r'(\d+[km]?)\s*like', content, re.IGNORECASE)
                    if like_match:
                        extracted_data['facebook_likes'] = like_match.group(1)
        
        return extracted_data
    
    def structure_agent_response(self, agent_name: str, response: str, search_data: Dict) -> Dict:
        """Struttura la risposta dell'agente"""
        return {
            'agent_name': agent_name,
            'agent_response': response,
            'search_data': search_data,
            'data_extracted': search_data.get('data_found', {}),
            'sources_count': len(search_data.get('searches_performed', [])),
            'confidence_score': self.calculate_confidence_score(search_data),
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_confidence_score(self, search_data: Dict) -> float:
        """Calcola score di confidenza basato sui dati trovati"""
        data_found = search_data.get('data_found', {})
        searches_performed = search_data.get('searches_performed', [])
        
        # Score basato su quantità di dati trovati
        data_score = min(len(data_found) * 0.2, 1.0)
        
        # Score basato su numero di ricerche con risultati
        searches_with_results = sum(1 for search in searches_performed if search.get('results_count', 0) > 0)
        search_score = min(searches_with_results * 0.1, 1.0)
        
        return round((data_score + search_score) / 2, 2)
    
    def orchestrate_full_analysis(self, company_name: str, company_url: str = None) -> Dict:
        """Orchestrazione completa di tutti gli agenti"""
        st.info("🤖 Avvio sistema AI Agents per ricerca completa...")
        
        analysis_results = {
            'company_name': company_name,
            'company_url': company_url,
            'analysis_date': datetime.now().isoformat(),
            'agents_results': {},
            'consolidated_data': {},
            'quality_metrics': {}
        }
        
        # Esegui agenti in parallelo per velocità
        agents_to_run = ['financial_agent', 'digital_agent', 'competitor_agent', 'company_agent', 'social_agent']
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Avvia tutti gli agenti
            future_to_agent = {
                executor.submit(self.execute_agent_research, agent_name, company_name, company_url): agent_name
                for agent_name in agents_to_run
            }
            
            # Raccogli risultati
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result()
                    analysis_results['agents_results'][agent_name] = result
                    st.success(f"✅ {agent_name} completato")
                except Exception as e:
                    st.error(f"❌ Errore in {agent_name}: {e}")
                    analysis_results['agents_results'][agent_name] = {"error": str(e)}
        
        # Consolida i dati da tutti gli agenti
        analysis_results['consolidated_data'] = self.consolidate_agents_data(analysis_results['agents_results'])
        
        # Calcola metriche di qualità
        analysis_results['quality_metrics'] = self.calculate_quality_metrics(analysis_results)
        
        return analysis_results
    
    def consolidate_agents_data(self, agents_results: Dict) -> Dict:
        """Consolida i dati da tutti gli agenti"""
        consolidated = {
            'company_profile': {},
            'financial_data': {},
            'digital_data': {},
            'social_data': {},
            'competitor_data': {},
            'all_sources': []
        }
        
        for agent_name, result in agents_results.items():
            if 'error' in result:
                continue
            
            # Aggiungi dati estratti
            data_extracted = result.get('data_extracted', {})
            
            if agent_name == 'financial_agent':
                consolidated['financial_data'].update(data_extracted)
            elif agent_name == 'digital_agent':
                consolidated['digital_data'].update(data_extracted)
            elif agent_name == 'social_agent':
                consolidated['social_data'].update(data_extracted)
            elif agent_name == 'competitor_agent':
                consolidated['competitor_data'].update(data_extracted)
            elif agent_name == 'company_agent':
                consolidated['company_profile'].update(data_extracted)
            
            # Aggiungi fonti
            search_data = result.get('search_data', {})
            searches = search_data.get('searches_performed', [])
            for search in searches:
                consolidated['all_sources'].extend(search.get('results', []))
        
        return consolidated
    
    def calculate_quality_metrics(self, analysis_results: Dict) -> Dict:
        """Calcola metriche di qualità dell'analisi"""
        agents_results = analysis_results.get('agents_results', {})
        
        # Calcola score per agente
        agent_scores = {}
        for agent_name, result in agents_results.items():
            if 'error' not in result:
                agent_scores[agent_name] = result.get('confidence_score', 0)
        
        # Score complessivo
        overall_score = sum(agent_scores.values()) / len(agent_scores) if agent_scores else 0
        
        # Conta dati trovati
        consolidated = analysis_results.get('consolidated_data', {})
        total_data_points = sum(len(data) for data in consolidated.values() if isinstance(data, dict))
        
        return {
            'overall_score': round(overall_score, 2),
            'agent_scores': agent_scores,
            'total_data_points': total_data_points,
            'agents_succeeded': len([r for r in agents_results.values() if 'error' not in r]),
            'agents_failed': len([r for r in agents_results.values() if 'error' in r]),
            'quality_level': 'Eccellente' if overall_score >= 0.8 else 'Buona' if overall_score >= 0.6 else 'Sufficiente' if overall_score >= 0.4 else 'Limitata'
        }

def display_agents_results(analysis_results: Dict):
    """Visualizza i risultati dell'analisi degli agenti"""
    
    st.markdown("---")
    st.markdown(f"# 🤖 Analisi AI Agents: {analysis_results['company_name']}")
    
    # Metriche di qualità
    quality_metrics = analysis_results.get('quality_metrics', {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Score Complessivo", f"{quality_metrics.get('overall_score', 0):.2f}")
    with col2:
        st.metric("Dati Raccolti", quality_metrics.get('total_data_points', 0))
    with col3:
        st.metric("Agenti Riusciti", quality_metrics.get('agents_succeeded', 0))
    with col4:
        st.metric("Qualità", quality_metrics.get('quality_level', 'Sconosciuta'))
    
    # Risultati per agente
    agents_results = analysis_results.get('agents_results', {})
    
    for agent_name, result in agents_results.items():
        if 'error' in result:
            st.error(f"❌ {agent_name}: {result['error']}")
            continue
        
        agent_title = {
            'financial_agent': '💰 Agente Finanziario',
            'digital_agent': '🔍 Agente Digital',
            'competitor_agent': '🎯 Agente Competitor',
            'company_agent': '🏢 Agente Aziendale',
            'social_agent': '📱 Agente Social'
        }.get(agent_name, agent_name)
        
        with st.expander(f"{agent_title} - Score: {result.get('confidence_score', 0):.2f}"):
            
            # Dati estratti
            data_extracted = result.get('data_extracted', {})
            if data_extracted:
                st.markdown("**📊 Dati Estratti:**")
                for key, value in data_extracted.items():
                    st.markdown(f"- **{key}:** {value}")
            
            # Ricerche effettuate
            search_data = result.get('search_data', {})
            searches = search_data.get('searches_performed', [])
            
            if searches:
                st.markdown("**🔍
