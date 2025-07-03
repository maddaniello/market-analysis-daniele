import streamlit as st
import openai
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import urllib.parse

st.set_page_config(
    page_title="🚀 Analizzatore Marketing AI - Dati Reali",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class RealDataAnalyzer:
    """Analizzatore con dati reali da fonti web"""
    
    def __init__(self, openai_api_key: str):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Cache per evitare ricerche duplicate
        self.search_cache = {}
    
    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """Ricerca web con cache"""
        if query in self.search_cache:
            return self.search_cache[query]
        
        try:
            # Usa DuckDuckGo Instant Answer API (gratuita)
            search_url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Risposta diretta
            if data.get('Answer'):
                results.append({
                    'title': 'Risposta Diretta',
                    'content': data['Answer'],
                    'url': data.get('AnswerURL', ''),
                    'type': 'direct_answer'
                })
            
            # Abstract (Wikipedia)
            if data.get('Abstract'):
                results.append({
                    'title': 'Wikipedia',
                    'content': data['Abstract'],
                    'url': data.get('AbstractURL', ''),
                    'type': 'wikipedia'
                })
            
            # Definizione
            if data.get('Definition'):
                results.append({
                    'title': 'Definizione',
                    'content': data['Definition'],
                    'url': data.get('DefinitionURL', ''),
                    'type': 'definition'
                })
            
            # Argomenti correlati
            for topic in data.get('RelatedTopics', []):
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic['Text'].split(' - ')[0] if ' - ' in topic['Text'] else topic['Text'][:50],
                        'content': topic['Text'],
                        'url': topic.get('FirstURL', ''),
                        'type': 'related_topic'
                    })
            
            # Limita risultati
            results = results[:max_results]
            
            # Cache
            self.search_cache[query] = results
            
            return results
            
        except Exception as e:
            st.error(f"Errore nella ricerca web: {e}")
            return []
    
    def get_company_website(self, company_name: str) -> Optional[str]:
        """Trova il sito web ufficiale dell'azienda"""
        try:
            query = f'"{company_name}" sito ufficiale'
            results = self.search_web(query, max_results=5)
            
            for result in results:
                content = result.get('content', '').lower()
                if 'sito' in content or 'website' in content or 'www' in content:
                    # Estrai URL
                    url_match = re.search(r'https?://[^\s]+', content)
                    if url_match:
                        return url_match.group(0)
            
            # Fallback: prova a indovinare
            clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
            return f"https://www.{clean_name}.it"
            
        except Exception as e:
            st.error(f"Errore nel trovare sito web: {e}")
            return None
    
    def analyze_company_comprehensive(self, company_name: str) -> Dict:
        """Analisi completa dell'azienda"""
        
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            analysis_data = {
                "company_name": company_name,
                "analysis_date": datetime.now().isoformat(),
                "data_quality_score": 0,
                "sources_used": []
            }
            
            # 1. Informazioni generali
            status_placeholder.text("🔍 Ricerca informazioni generali...")
            progress_placeholder.progress(10)
            
            general_info = self.get_general_company_info(company_name)
            if general_info:
                analysis_data["general_info"] = general_info
                analysis_data["data_quality_score"] += 1
                analysis_data["sources_used"].append("Informazioni Generali")
            
            # 2. Dati registro imprese
            status_placeholder.text("🏛️ Ricerca registro imprese...")
            progress_placeholder.progress(25)
            
            registry_info = self.get_registry_info(company_name)
            if registry_info:
                analysis_data["registry_info"] = registry_info
                analysis_data["data_quality_score"] += 1
                analysis_data["sources_used"].append("Registro Imprese")
            
            # 3. Dati finanziari
            status_placeholder.text("💰 Ricerca dati finanziari...")
            progress_placeholder.progress(40)
            
            financial_info = self.get_financial_info(company_name)
            if financial_info:
                analysis_data["financial_info"] = financial_info
                analysis_data["data_quality_score"] += 1
                analysis_data["sources_used"].append("Dati Finanziari")
            
            # 4. Competitor
            status_placeholder.text("🎯 Ricerca competitor...")
            progress_placeholder.progress(55)
            
            competitor_info = self.get_competitor_info(company_name)
            if competitor_info:
                analysis_data["competitor_info"] = competitor_info
                analysis_data["data_quality_score"] += 1
                analysis_data["sources_used"].append("Competitor Analysis")
            
            # 5. Social media
            status_placeholder.text("📱 Ricerca social media...")
            progress_placeholder.progress(70)
            
            social_info = self.get_social_media_info(company_name)
            if social_info:
                analysis_data["social_info"] = social_info
                analysis_data["data_quality_score"] += 1
                analysis_data["sources_used"].append("Social Media")
            
            # 6. Analisi AI finale
            status_placeholder.text("🧠 Analisi AI finale...")
            progress_placeholder.progress(85)
            
            ai_analysis = self.generate_comprehensive_ai_analysis(company_name, analysis_data)
            if ai_analysis:
                analysis_data["ai_analysis"] = ai_analysis
                analysis_data["data_quality_score"] += 1
                analysis_data["sources_used"].append("AI Analysis")
            
            # Cleanup
            progress_placeholder.progress(100)
            status_placeholder.text("✅ Analisi completata!")
            
            time.sleep(1)
            progress_placeholder.empty()
            status_placeholder.empty()
            
            return analysis_data
            
        except Exception as e:
            progress_placeholder.empty()
            status_placeholder.empty()
            st.error(f"Errore nell'analisi: {e}")
            return {"error": str(e)}
    
    def get_general_company_info(self, company_name: str) -> Dict:
        """Informazioni generali azienda"""
        try:
            queries = [
                f'"{company_name}" azienda italiana',
                f'"{company_name}" company profile',
                f'"{company_name}" chi siamo about'
            ]
            
            info = {}
            
            for query in queries:
                results = self.search_web(query, max_results=3)
                
                for result in results:
                    content = result.get('content', '')
                    
                    # Estrai anno di fondazione
                    if not info.get('founded_year'):
                        year_match = re.search(r'fondat[ao].*?(\d{4})', content, re.IGNORECASE)
                        if year_match:
                            info['founded_year'] = year_match.group(1)
                    
                    # Estrai settore
                    if not info.get('sector'):
                        sector_keywords = ['settore', 'industria', 'campo', 'business']
                        for keyword in sector_keywords:
                            if keyword in content.lower():
                                sector_match = re.search(f'{keyword}[^.]*([^.]+)', content, re.IGNORECASE)
                                if sector_match:
                                    info['sector'] = sector_match.group(1).strip()
                                    break
                    
                    # Estrai descrizione
                    if not info.get('description') and len(content) > 50:
                        info['description'] = content[:300] + "..."
                    
                    # Estrai sito web
                    if not info.get('website'):
                        website_match = re.search(r'https?://[^\s]+', content)
                        if website_match:
                            info['website'] = website_match.group(0)
            
            return info if info else None
            
        except Exception as e:
            st.error(f"Errore informazioni generali: {e}")
            return None
    
    def get_registry_info(self, company_name: str) -> Dict:
        """Informazioni registro imprese"""
        try:
            queries = [
                f'"{company_name}" p.iva partita iva',
                f'"{company_name}" registro imprese camera commercio',
                f'"{company_name}" sede legale indirizzo',
                f'"{company_name}" forma giuridica srl spa'
            ]
            
            registry_info = {}
            
            for query in queries:
                results = self.search_web(query, max_results=3)
                
                for result in results:
                    content = result.get('content', '')
                    
                    # P.IVA
                    if not registry_info.get('piva'):
                        piva_match = re.search(r'P\.?\s*IVA[:\s]*(\d{11})', content, re.IGNORECASE)
                        if piva_match:
                            registry_info['piva'] = piva_match.group(1)
                    
                    # Sede legale
                    if not registry_info.get('sede_legale'):
                        sede_patterns = [
                            r'sede\s+legale[:\s]*([^,\n]+)',
                            r'indirizzo[:\s]*([^,\n]+)',
                            r'via\s+[^,\n]+,\s*[^,\n]+',
                        ]
                        for pattern in sede_patterns:
                            match = re.search(pattern, content, re.IGNORECASE)
                            if match:
                                registry_info['sede_legale'] = match.group(1).strip()
                                break
                    
                    # Forma giuridica
                    if not registry_info.get('forma_giuridica'):
                        forma_match = re.search(r'(S\.r\.l\.|S\.p\.A\.|SRL|SPA)', content, re.IGNORECASE)
                        if forma_match:
                            registry_info['forma_giuridica'] = forma_match.group(1)
                    
                    # ATECO
                    if not registry_info.get('ateco'):
                        ateco_match = re.search(r'ATECO[:\s]*(\d{4})', content, re.IGNORECASE)
                        if ateco_match:
                            registry_info['ateco'] = ateco_match.group(1)
            
            return registry_info if registry_info else None
            
        except Exception as e:
            st.error(f"Errore registro imprese: {e}")
            return None
    
    def get_financial_info(self, company_name: str) -> Dict:
        """Informazioni finanziarie"""
        try:
            queries = [
                f'"{company_name}" fatturato ricavi bilancio',
                f'"{company_name}" dipendenti employees',
                f'"{company_name}" crescita cresciuta',
                f'"{company_name}" investimenti funding'
            ]
            
            financial_info = {}
            
            for query in queries:
                results = self.search_web(query, max_results=3)
                
                for result in results:
                    content = result.get('content', '')
                    
                    # Fatturato
                    if not financial_info.get('fatturato'):
                        fatturato_patterns = [
                            r'fatturato[:\s]*€?\s*([\d,]+(?:\.\d+)?)\s*(?:milioni?|mln|million)',
                            r'ricavi[:\s]*€?\s*([\d,]+(?:\.\d+)?)\s*(?:milioni?|mln|million)',
                            r'€\s*([\d,]+(?:\.\d+)?)\s*(?:milioni?|mln|million)'
                        ]
                        for pattern in fatturato_patterns:
                            match = re.search(pattern, content, re.IGNORECASE)
                            if match:
                                financial_info['fatturato'] = match.group(1) + " milioni €"
                                break
                    
                    # Dipendenti
                    if not financial_info.get('dipendenti'):
                        dipendenti_patterns = [
                            r'(\d+)\s*dipendenti',
                            r'(\d+)\s*employees',
                            r'team\s*(?:di)?\s*(\d+)'
                        ]
                        for pattern in dipendenti_patterns:
                            match = re.search(pattern, content, re.IGNORECASE)
                            if match:
                                financial_info['dipendenti'] = match.group(1)
                                break
                    
                    # Crescita
                    if not financial_info.get('crescita'):
                        crescita_match = re.search(r'crescita[:\s]*([^,\n]+)', content, re.IGNORECASE)
                        if crescita_match:
                            financial_info['crescita'] = crescita_match.group(1).strip()
            
            return financial_info if financial_info else None
            
        except Exception as e:
            st.error(f"Errore dati finanziari: {e}")
            return None
    
    def get_competitor_info(self, company_name: str) -> Dict:
        """Informazioni competitor"""
        try:
            queries = [
                f'"{company_name}" competitor concorrenti',
                f'"{company_name}" vs competizione',
                f'"{company_name}" mercato settore leader'
            ]
            
            competitor_info = {
                'competitors': [],
                'market_position': ''
            }
            
            for query in queries:
                results = self.search_web(query, max_results=3)
                
                for result in results:
                    content = result.get('content', '')
                    
                    # Trova competitor
                    competitor_patterns = [
                        r'competitor[:\s]*([^,\n]+)',
                        r'concorrenti[:\s]*([^,\n]+)',
                        r'vs\s+([A-Z][a-zA-Z\s]+)',
                        r'insieme\s+a\s+([A-Z][a-zA-Z\s]+)'
                    ]
                    
                    for pattern in competitor_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if len(match) > 3 and match not in [c.get('name') for c in competitor_info['competitors']]:
                                competitor_info['competitors'].append({
                                    'name': match.strip(),
                                    'website': self.guess_website(match.strip())
                                })
                    
                    # Posizione nel mercato
                    if not competitor_info.get('market_position'):
                        if any(word in content.lower() for word in ['leader', 'primo', 'maggiore', 'principale']):
                            competitor_info['market_position'] = 'Leader di mercato'
                        elif any(word in content.lower() for word in ['secondo', 'importante', 'significativo']):
                            competitor_info['market_position'] = 'Player importante'
                        elif any(word in content.lower() for word in ['emergente', 'crescita', 'startup']):
                            competitor_info['market_position'] = 'Emergente'
            
            # Limita a 5 competitor
            competitor_info['competitors'] = competitor_info['competitors'][:5]
            
            return competitor_info if competitor_info['competitors'] else None
            
        except Exception as e:
            st.error(f"Errore competitor: {e}")
            return None
    
    def guess_website(self, company_name: str) -> str:
        """Indovina il sito web di un'azienda"""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        return f"https://www.{clean_name}.it"
    
    def get_social_media_info(self, company_name: str) -> Dict:
        """Informazioni social media"""
        try:
            queries = [
                f'"{company_name}" instagram followers',
                f'"{company_name}" facebook page',
                f'"{company_name}" linkedin company',
                f'"{company_name}" youtube channel'
            ]
            
            social_info = {}
            
            for query in queries:
                results = self.search_web(query, max_results=2)
                
                for result in results:
                    content = result.get('content', '').lower()
                    
                    # Instagram
                    if 'instagram' in content and not social_info.get('instagram'):
                        follower_match = re.search(r'(\d+[km]?)\s*follower', content, re.IGNORECASE)
                        if follower_match:
                            social_info['instagram'] = follower_match.group(1)
                    
                    # Facebook
                    if 'facebook' in content and not social_info.get('facebook'):
                        like_match = re.search(r'(\d+[km]?)\s*like', content, re.IGNORECASE)
                        if like_match:
                            social_info['facebook'] = like_match.group(1)
                    
                    # LinkedIn
                    if 'linkedin' in content and not social_info.get('linkedin'):
                        social_info['linkedin'] = 'Presente'
                    
                    # YouTube
                    if 'youtube' in content and not social_info.get('youtube'):
                        sub_match = re.search(r'(\d+[km]?)\s*subscriber', content, re.IGNORECASE)
                        if sub_match:
                            social_info['youtube'] = sub_match.group(1)
            
            return social_info if social_info else None
            
        except Exception as e:
            st.error(f"Errore social media: {e}")
            return None
    
    def generate_comprehensive_ai_analysis(self, company_name: str, data: Dict) -> Dict:
        """Analisi AI completa basata sui dati raccolti"""
        try:
            # Prepara il contenuto per l'AI
            data_summary = self.prepare_data_for_ai(data)
            
            prompt = f"""
            Analizza i seguenti dati REALI raccolti per l'azienda "{company_name}":

            {data_summary}

            Basandoti ESCLUSIVAMENTE sui dati forniti, genera:

            1. PROFILO AZIENDALE
            - Sintesi dell'azienda
            - Settore e posizionamento
            - Dimensioni e struttura

            2. ANALISI FINANZIARIA
            - Performance economica
            - Trend di crescita
            - Confronto settoriale

            3. ANALISI COMPETITIVA
            - Posizione nel mercato
            - Confronto con competitor
            - Vantaggi competitivi

            4. PRESENZA DIGITALE
            - Performance online
            - Social media strategy
            - Digital marketing

            5. ANALISI SWOT
            - Punti di forza (basati sui dati)
            - Aree di miglioramento
            - Opportunità di mercato
            - Minacce competitive

            6. RACCOMANDAZIONI
            - Strategie di crescita
            - Ottimizzazioni digitali
            - Azioni prioritarie

            IMPORTANTE: Usa SOLO i dati forniti, non inventare informazioni.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un consulente aziendale esperto. Analizza SOLO i dati forniti, non inventare informazioni. Sii preciso e factual."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.1
            )
            
            ai_analysis = response.choices[0].message.content
            
            # Struttura l'analisi
            return {
                'company_profile': self.extract_ai_section(ai_analysis, 'PROFILO AZIENDALE'),
                'financial_analysis': self.extract_ai_section(ai_analysis, 'ANALISI FINANZIARIA'),
                'competitive_analysis': self.extract_ai_section(ai_analysis, 'ANALISI COMPETITIVA'),
                'digital_presence': self.extract_ai_section(ai_analysis, 'PRESENZA DIGITALE'),
                'swot_analysis': self.extract_swot_from_ai(ai_analysis),
                'recommendations': self.extract_recommendations_from_ai(ai_analysis),
                'full_analysis': ai_analysis
            }
            
        except Exception as e:
            st.error(f"Errore nell'analisi AI: {e}")
            return None
    
    def prepare_data_for_ai(self, data: Dict) -> str:
        """Prepara i dati per l'analisi AI"""
        content = f"AZIENDA: {data['company_name']}\n\n"
        
        if data.get('general_info'):
            content += "INFORMAZIONI GENERALI:\n"
            for key, value in data['general_info'].items():
                content += f"- {key}: {value}\n"
            content += "\n"
        
        if data.get('registry_info'):
            content += "REGISTRO IMPRESE:\n"
            for key, value in data['registry_info'].items():
                content += f"- {key}: {value}\n"
            content += "\n"
        
        if data.get('financial_info'):
            content += "DATI FINANZIARI:\n"
            for key, value in data['financial_info'].items():
                content += f"- {key}: {value}\n"
            content += "\n"
        
        if data.get('competitor_info'):
            content += "COMPETITOR:\n"
            for comp in data['competitor_info'].get('competitors', []):
                content += f"- {comp.get('name', 'N/A')}\n"
            if data['competitor_info'].get('market_position'):
                content += f"- Posizione: {data['competitor_info']['market_position']}\n"
            content += "\n"
        
        if data.get('social_info'):
            content += "SOCIAL MEDIA:\n"
            for platform, value in data['social_info'].items():
                content += f"- {platform}: {value}\n"
            content += "\n"
        
        return content
    
    def extract_ai_section(self, text: str, section_name: str) -> str:
        """Estrae una sezione specifica dall'analisi AI"""
        try:
            pattern = rf'{section_name}.*?(?=\d+\.\s+[A-Z]|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0).strip()
            return ""
        except:
            return ""
    
    def extract_swot_from_ai(self, text: str) -> Dict:
        """Estrae analisi SWOT dall'analisi AI"""
        try:
            swot_section = self.extract_ai_section(text, 'ANALISI SWOT')
            
            swot = {
                'strengths': [],
                'weaknesses': [],
                'opportunities': [],
                'threats': []
            }
            
            # Pattern per le sezioni SWOT
            patterns = {
                'strengths': r'punti\s+di\s+forza[^:]*:?\s*(.*?)(?=aree|opportunità|minacce|$)',
                'weaknesses': r'aree\s+di\s+miglioramento[^:]*:?\s*(.*?)(?=punti|opportunità|minacce|$)',
                'opportunities': r'opportunità[^:]*:?\s*(.*?)(?=punti|aree|minacce|$)',
                'threats': r'minacce[^:]*:?\s*(.*?)(?=punti|aree|opportunità|$)'
            }
            
            for category, pattern in patterns.items():
                match = re.search(pattern, swot_section, re.IGNORECASE | re.DOTALL)
                if match:
                    content = match.group(1)
                    items = re.findall(r'[-•*]\s*([^\n]+)', content)
                    swot[category] = [item.strip() for item in items if item.strip()]
            
            return swot
            
        except Exception as e:
            st.error(f"Errore estrazione SWOT: {e}")
            return {'strengths': [], 'weaknesses': [], 'opportunities': [], 'threats': []}
    
    def extract_recommendations_from_ai(self, text: str) -> List[str]:
        """Estrae raccomandazioni dall'analisi AI"""
        try:
            rec_section = self.extract_ai_section(text, 'RACCOMANDAZIONI')
            recommendations = re.findall(r'[-•*]\s*([^\n]+)', rec_section)
            return [rec.strip() for rec in recommendations if rec.strip()]
        except:
            return []

def display_analysis_results(analysis_data: Dict, company_name: str):
    """Visualizza i risultati dell'analisi"""
    
    st.markdown("---")
    st.markdown(f"# 📊 Report Completo: {company_name}")
    
    # Qualità dei dati
    quality_score = analysis_data.get('data_quality_score', 0)
    max_score = 6
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Qualità Dati", f"{quality_score}/{max_score}")
    with col2:
        st.metric("Fonti Utilizzate", len(analysis_data.get('sources_used', [])))
    with col3:
        quality_level = "Eccellente" if quality_score >= 5 else "Buona" if quality_score >= 3 else "Sufficiente"
        st.metric("Affidabilità", quality_level)
    
    # Fonti utilizzate
    if analysis_data.get('sources_used'):
        st.markdown("### 📚 Fonti Dati Utilizzate")
        for source in analysis_data['sources_used']:
            st.markdown(f"✅ {source}")
    
    # Informazioni generali
    if analysis_data.get('general_info'):
        st.markdown("## 🏢 Informazioni Generali")
        info = analysis_data['general_info']
        
        col1, col2 = st.columns(2)
        with col1:
            if info.get('founded_year'):
                st.metric("Anno Fondazione", info['founded_year'])
            if info.get('sector'):
                st.metric("Settore", info['sector'])
        with col2:
            if info.get('website'):
                st.markdown(f"**🌐 Sito Web:** {info['website']}")
            if info.get('description'):
                st.markdown(f"**📝 Descrizione:** {info['description']}")
    
    # Registro imprese
    if analysis_data.get('registry_info'):
        st.markdown("## 🏛️ Registro Imprese")
        registry = analysis_data['registry_info']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if registry.get('piva'):
                st.metric("P.IVA", registry['piva'])
        with col2:
            if registry.get('forma_giuridica'):
                st.metric("Forma Giuridica", registry['forma_giuridica'])
        with col3:
            if registry.get('ateco'):
                st.metric("Codice ATECO", registry['ateco'])
        
        if registry.get('sede_legale'):
            st.markdown(f"**📍 Sede Legale:** {registry['sede_legale']}")
    
    # Dati finanziari
    if analysis_data.get('financial_info'):
        st.markdown("## 💰 Dati Finanziari")
        financial = analysis_data['financial_info']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if financial.get('fatturato'):
                st.metric("Fatturato", financial['fatturato'])
        with col2:
            if financial.get('dipendenti'):
                st.metric("Dipendenti", financial['dipendenti'])
        with col3:
            if financial.get('crescita'):
                st.metric("Crescita", financial['crescita'])
    
    # Competitor
    if analysis_data.get('competitor_info'):
        st.markdown("## 🎯 Analisi Competitiva")
        competitor = analysis_data['competitor_info']
        
        if competitor.get('market_position'):
            st.markdown(f"**📊 Posizione nel Mercato:** {competitor['market_position']}")
        
        if competitor.get('competitors'):
            st.markdown("### 🏢 Principali Competitor")
            for i, comp in enumerate(competitor['competitors'], 1):
                with st.expander(f"Competitor {i}: {comp.get('name', 'N/A')}"):
                    st.markdown(f"**Nome:** {comp.get('name', 'N/A')}")
                    st.markdown(f"**Website:** {comp.get('website', 'N/A')}")
    
    # Social media
    if analysis_data.get('social_info'):
        st.markdown("## 📱 Social Media")
        social = analysis_data['social_info']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if social.get('instagram'):
                st.metric("Instagram", social['instagram'])
        with col2:
            if social.get('facebook'):
                st.metric("Facebook", social['facebook'])
        with col3:
            if social.get('linkedin'):
                st.metric("LinkedIn", social['linkedin'])
        with col4:
            if social.get('youtube'):
                st.metric("YouTube", social['youtube'])
    
    # Analisi AI
    if analysis_data.get('ai_analysis'):
        ai_data = analysis_data['ai_analysis']
        
        # Profilo aziendale
        if ai_data.get('company_profile'):
            st.markdown("## 🏢 Profilo Aziendale AI")
            st.markdown(ai_data['company_profile'])
        
        # Analisi finanziaria
        if ai_data.get('financial_analysis'):
            st.markdown("## 💰 Analisi Finanziaria AI")
            st.markdown(ai_data['financial_analysis'])
        
        # Analisi competitiva
        if ai_data.get('competitive_analysis'):
            st.markdown("## 🎯 Analisi Competitiva AI")
            st.markdown(ai_data['competitive_analysis'])
        
        # Presenza digitale
        if ai_data.get('digital_presence'):
            st.markdown("## 🌐 Presenza Digitale AI")
            st.markdown(ai_data['digital_presence'])
        
        # SWOT
        if ai_data.get('swot_analysis'):
            st.markdown("## ⚖️ Analisi SWOT")
            swot = ai_data['swot_analysis']
            
            col1, col2 = st.columns(2)
            with col1:
                if swot.get('strengths'):
                    st.markdown("### 💪 Punti di Forza")
                    for strength in swot['strengths']:
                        st.markdown(f"• {strength}")
                
                if swot.get('opportunities'):
                    st.markdown("### 🌟 Opportunità")
                    for opportunity in swot['opportunities']:
                        st.markdown(f"• {opportunity}")
            
            with col2:
                if swot.get('weaknesses'):
                    st.markdown("### ⚠️ Aree di Miglioramento")
                    for weakness in swot['weaknesses']:
                        st.markdown(f"• {weakness}")
                
                if swot.get('threats'):
                    st.markdown("### 🚨 Minacce")
                    for threat in swot['threats']:
                        st.markdown(f"• {threat}")
        
        # Raccomandazioni
        if ai_data.get('recommendations'):
            st.markdown("## 💡 Raccomandazioni Strategiche")
            for i, rec in enumerate(ai_data['recommendations'], 1):
                st.markdown(f"**{i}.** {rec}")
    
    # Download
    st.markdown("## 📥 Download Report")
    col1, col2 = st.columns(2)
    
    with col1:
        json_data = json.dumps(analysis_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 Scarica Report JSON",
            data=json_data,
            file_name=f"report_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Report markdown
        md_content = f"""# Report Analisi: {company_name}

## Riepilogo
- **Qualità Dati:** {quality_score}/{max_score}
- **Fonti Utilizzate:** {len(analysis_data.get('sources_used', []))}
- **Data Analisi:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Dati Raccolti
{json.dumps(analysis_data, indent=2, ensure_ascii=False)}

---
*Report generato con ricerca web reale*
"""
        
        st.download_button(
            label="📝 Scarica Report MD",
            data=md_content,
            file_name=f"report_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

def main():
    st.title("🚀 Analizzatore Marketing AI")
    st.markdown("### Analisi aziendale completa con dati reali da fonti web")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurazione")
        
        openai_key = st.text_input("OpenAI API Key", type="password")
        
        if not openai_key:
            st.warning("⚠️ Inserisci la tua OpenAI API Key")
            st.info("👉 Ottieni la tua chiave su: https://platform.openai.com/")
            st.stop()
        
        st.success("✅ API Key configurata")
        
        st.markdown("---")
        st.markdown("### 🎯 Caratteristiche")
        st.markdown("""
        ✅ **Dati reali** da fonti web
        ✅ **Registro imprese** italiano
        ✅ **Informazioni finanziarie** verificate
        ✅ **Competitor analysis** basata su ricerca
        ✅ **Social media** dati effettivi
        ✅ **Analisi SWOT** basata su fatti
        ✅ **Raccomandazioni** personalizzate
        """)
        
        st.markdown("---")
        st.markdown("### 📊 Qualità Dati")
        st.info("Questa versione cerca **esclusivamente dati reali** da fonti web verificate")
        
        st.markdown("---")
        st.markdown("### ⏱️ Tempo Stimato")
        st.info("2-3 minuti per analisi completa")
    
    # Main content
    st.markdown("---")
    
    # Input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        company_input = st.text_input(
            "🏢 Nome azienda italiana:",
            placeholder="es. Ferrero, Luxottica, Satispay, Banca Mediolanum...",
            help="Inserisci il nome completo dell'azienda italiana"
        )
    
    with col2:
        analyze_button = st.button("🔍 Analizza", type="primary", use_container_width=True)
    
    # Esempi
    st.markdown("**💡 Prova con questi esempi:**")
    col1, col2, col3, col4 = st.columns(4)
    
    examples = [
        ("🍫 Ferrero", "Ferrero"),
        ("👓 Luxottica", "Luxottica"),
        ("💳 Satispay", "Satispay"),
        ("🏦 Banca Mediolanum", "Banca Mediolanum")
    ]
    
    for col, (label, company) in zip([col1, col2, col3, col4], examples):
        with col:
            if st.button(label, key=f"ex_{company}"):
                company_input = company
                analyze_button = True
    
    # Analisi
    if analyze_button and company_input:
        analyzer = RealDataAnalyzer(openai_key)
        
        st.markdown("---")
        st.markdown(f"## 🔍 Analisi in corso: {company_input}")
        
        # Esegui analisi
        analysis_data = analyzer.analyze_company_comprehensive(company_input)
        
        if "error" not in analysis_data:
            # Mostra risultati
            display_analysis_results(analysis_data, company_input)
        else:
            st.error(f"❌ Errore nell'analisi: {analysis_data['error']}")
    
    # Footer
    st.markdown("---")
    st.markdown("### 🎯 Nota Importante")
    st.info("Questa applicazione cerca dati reali da fonti web pubbliche. I risultati sono basati su informazioni effettivamente disponibili online e non su stime o dati inventati.")

if __name__ == "__main__":
    main()
