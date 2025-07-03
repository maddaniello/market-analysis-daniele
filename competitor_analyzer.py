import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, List, Optional
from openai import OpenAI
import re
import time
from urllib.parse import urljoin, urlparse
import concurrent.futures
from config import Config

logger = logging.getLogger(__name__)

class CompetitorAnalyzer:
    """
    Analizzatore per identificare e analizzare i competitor
    """
    
    def __init__(self, openai_api_key: str, semrush_api_key: Optional[str] = None):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.semrush_api_key = semrush_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENTS[0]
        })
    
    def identify_competitors(self, company_name: str, industry: str, location: str = "Italia") -> List[Dict]:
        """
        Identifica i principali competitor usando AI
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Sei un esperto analista di mercato specializzato nell'identificazione di competitor. Fornisci informazioni accurate e aggiornate sui principali competitor diretti e indiretti nel mercato italiano."},
                    {"role": "user", "content": f"Identifica i 7 principali competitor di {company_name} nel settore {industry} in {location}. Per ogni competitor fornisci: nome completo, sito web, dimensioni aziendali stimate, punti di forza principali, quota di mercato stimata, e perché è considerato un competitor."}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            ai_content = response.choices[0].message.content
            competitors = self.parse_competitors_from_ai(ai_content)
            
            # Arricchisci i dati dei competitor
            enriched_competitors = []
            for competitor in competitors:
                enriched_data = self.enrich_competitor_data(competitor)
                enriched_competitors.append(enriched_data)
            
            return enriched_competitors[:7]  # Limita a 7 competitor
            
        except Exception as e:
            logger.error(f"Errore nell'identificazione competitor: {e}")
            return []
    
    def parse_competitors_from_ai(self, ai_content: str) -> List[Dict]:
        """
        Estrae lista competitor dal contenuto AI
        """
        competitors = []
        
        try:
            # Dividi il contenuto in blocchi per ogni competitor
            sections = re.split(r'\n\s*\n', ai_content)
            
            for section in sections:
                if any(keyword in section.lower() for keyword in ['competitor', 'concorrente', 'azienda', 'società']):
                    competitor_data = self.extract_competitor_info(section)
                    if competitor_data:
                        competitors.append(competitor_data)
            
            return competitors
            
        except Exception as e:
            logger.error(f"Errore nel parsing competitor: {e}")
            return []
    
    def extract_competitor_info(self, text: str) -> Optional[Dict]:
        """
        Estrae informazioni su un singolo competitor
        """
        try:
            # Estrai nome
            name_patterns = [
                r'(?:Competitor|Concorrente)\s*\d*[:.]?\s*([^,\n]+)',
                r'(\b[A-Z][a-zA-Z\s&]+(?:S\.r\.l\.|S\.p\.A\.|S\.r\.l|S\.p\.A|SRL|SPA|Ltd|Inc|Corp)?)\b',
                r'Nome:\s*([^,\n]+)',
                r'Azienda:\s*([^,\n]+)'
            ]
            
            name = None
            for pattern in name_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    break
            
            if not name:
                return None
            
            # Estrai sito web
            website_patterns = [
                r'(?:sito|website|web|www).*?:\s*((?:https?://)?(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.(?:[a-zA-Z]{2,})+)',
                r'((?:https?://)?(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.(?:com|it|org|net|eu))'
            ]
            
            website = None
            for pattern in website_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    website = match.group(1).strip()
                    if not website.startswith('http'):
                        website = 'https://' + website
                    break
            
            # Se non trovato, genera un sito plausibile
            if not website:
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
                website = f"https://www.{clean_name}.it"
            
            competitor_data = {
                "name": name,
                "website": website,
                "description": text[:200] + "..." if len(text) > 200 else text,
                "market_share": self.extract_market_share(text),
                "company_size": self.extract_company_size(text),
                "strengths": self.extract_strengths(text),
                "raw_text": text
            }
            
            return competitor_data
            
        except Exception as e:
            logger.error(f"Errore nell'estrazione info competitor: {e}")
            return None
    
    def extract_market_share(self, text: str) -> str:
        """Estrae quota di mercato dal testo"""
        patterns = [
            r'quota\s+(?:di\s+)?mercato:?\s*([^,\n]+)',
            r'market\s+share:?\s*([^,\n]+)',
            r'(\d+(?:\.\d+)?%)\s*(?:del\s+)?mercato'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Non specificata"
    
    def extract_company_size(self, text: str) -> str:
        """Estrae dimensioni aziendali dal testo"""
        patterns = [
            r'(?:dimensioni|size|dipendenti):?\s*([^,\n]+)',
            r'(\d+)\s*dipendenti',
            r'(piccola|media|grande|multinazionale)\s*(?:azienda|impresa)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Non specificata"
    
    def extract_strengths(self, text: str) -> List[str]:
        """Estrae punti di forza dal testo"""
        strengths = []
        
        # Cerca sezioni sui punti di forza
        strength_patterns = [
            r'(?:punti\s+di\s+forza|strengths|vantaggi).*?:(.*?)(?:\n\s*\n|\n[A-Z]|$)',
            r'(innovativ[ao]|leader|specializzat[ao]|qualità|esperienza|tecnologia)'
        ]
        
        for pattern in strength_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, str) and len(match.strip()) > 10:
                    strengths.append(match.strip())
        
        return strengths[:3]  # Limita a 3 punti di forza
    
    def enrich_competitor_data(self, competitor: Dict) -> Dict:
        """
        Arricchisce i dati del competitor con informazioni aggiuntive
        """
        try:
            # Analisi del sito web
            website_data = self.analyze_competitor_website(competitor.get('website', ''))
            
            # Dati SEO stimati
            seo_data = self.estimate_competitor_seo(competitor.get('name', ''))
            
            # Social media presence
            social_data = self.estimate_social_presence(competitor.get('name', ''))
            
            enriched_competitor = {
                **competitor,
                "website_analysis": website_data,
                "seo_metrics": seo_data,
                "social_presence": social_data,
                "last_updated": time.time()
            }
            
            return enriched_competitor
            
        except Exception as e:
            logger.error(f"Errore nell'arricchimento dati competitor: {e}")
            return competitor
    
    def analyze_competitor_website(self, website: str) -> Dict:
        """
        Analizza il sito web del competitor
        """
        try:
            if not website:
                return {"error": "Nessun sito web fornito"}
            
            response = self.session.get(website, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Estrai informazioni base
            title = soup.title.string if soup.title else "Titolo non trovato"
            description = ""
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # Conta elementi principali
            analysis = {
                "title": title,
                "description": description,
                "has_blog": bool(soup.find('a', href=re.compile(r'blog|news|articoli', re.I))),
                "has_ecommerce": bool(soup.find('a', href=re.compile(r'shop|store|prodotti|acquista', re.I))),
                "has_contact": bool(soup.find('a', href=re.compile(r'contact|contatti', re.I))),
                "language": soup.find('html').get('lang', 'it') if soup.find('html') else 'it',
                "page_size": len(response.content),
                "load_time": response.elapsed.total_seconds()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Errore nell'analisi sito web {website}: {e}")
            return {"error": str(e)}
    
    def estimate_competitor_seo(self, competitor_name: str) -> Dict:
        """
        Stima metriche SEO del competitor
        """
        try:
            # Usa AI per stimare metriche SEO realistiche
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Sei un esperto SEO che stima metriche realistiche per aziende italiane basandoti su dimensioni, settore e presenza online."},
                    {"role": "user", "content": f"Stima le metriche SEO per {competitor_name}: traffico organico mensile, keyword posizionate, domain authority, backlinks, basandoti su aziende simili nel mercato italiano."}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            ai_content = response.choices[0].message.content
            
            # Estrai metriche numeriche
            seo_metrics = {
                "organic_traffic": self.extract_number_from_text(ai_content, r'traffico.*?(\d+)', 15000),
                "keywords": self.extract_number_from_text(ai_content, r'keyword.*?(\d+)', 1200),
                "domain_authority": self.extract_number_from_text(ai_content, r'authority.*?(\d+)', 35),
                "backlinks": self.extract_number_from_text(ai_content, r'backlink.*?(\d+)', 2500),
                "estimated_monthly_value": self.extract_number_from_text(ai_content, r'valore.*?(\d+)', 8000),
                "ai_analysis": ai_content
            }
            
            return seo_metrics
            
        except Exception as e:
            logger.error(f"Errore nella stima SEO competitor: {e}")
            return {"error": str(e)}
    
    def estimate_social_presence(self, competitor_name: str) -> Dict:
        """
        Stima presenza social del competitor
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Sei un esperto di social media marketing che stima la presenza social di aziende italiane basandoti su dimensioni, settore e tipologia di business."},
                    {"role": "user", "content": f"Stima la presenza social media di {competitor_name}: follower su Instagram, Facebook, LinkedIn, engagement rate, frequenza di posting, qualità dei contenuti."}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            ai_content = response.choices[0].message.content
            
            social_metrics = {
                "instagram_followers": self.extract_number_from_text(ai_content, r'instagram.*?(\d+)', 5000),
                "facebook_followers": self.extract_number_from_text(ai_content, r'facebook.*?(\d+)', 3000),
                "linkedin_followers": self.extract_number_from_text(ai_content, r'linkedin.*?(\d+)', 2000),
                "engagement_rate": round(self.extract_number_from_text(ai_content, r'engagement.*?(\d+)', 200) / 100, 2),
                "posting_frequency": self.extract_text_from_content(ai_content, r'frequenza.*?([^.\n]+)', "2-3 post/settimana"),
                "content_quality": self.extract_text_from_content(ai_content, r'qualità.*?([^.\n]+)', "Media-Alta"),
                "ai_analysis": ai_content
            }
            
            return social_metrics
            
        except Exception as e:
            logger.error(f"Errore nella stima social competitor: {e}")
            return {"error": str(e)}
    
    def extract_number_from_text(self, text: str, pattern: str, default: int) -> int:
        """Estrae numero dal testo con fallback"""
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1).replace(',', '').replace('.', ''))
            return default
        except:
            return default
    
    def extract_text_from_content(self, text: str, pattern: str, default: str) -> str:
        """Estrae testo dal contenuto con fallback"""
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            return default
        except:
            return default
    
    def compare_competitors(self, main_company: Dict, competitors: List[Dict]) -> Dict:
        """
        Confronta l'azienda principale con i competitor
        """
        try:
            comparison_data = {
                "main_company": main_company.get('company_name', 'Azienda Principale'),
                "competitors_count": len(competitors),
                "comparison_metrics": {},
                "competitive_positioning": {},
                "recommendations": []
            }
            
            # Confronta metriche chiave
            main_seo = main_company.get('seo_data', {})
            main_social = main_company.get('social_data', {})
            
            # Calcola medie competitor
            competitor_averages = self.calculate_competitor_averages(competitors)
            
            # Confronto SEO
            comparison_data["comparison_metrics"]["seo"] = {
                "main_organic_traffic": main_seo.get('organic_traffic', 0),
                "competitor_avg_traffic": competitor_averages.get('organic_traffic', 0),
                "main_keywords": main_seo.get('organic_keywords', 0),
                "competitor_avg_keywords": competitor_averages.get('keywords', 0),
                "main_backlinks": main_seo.get('backlinks', 0),
                "competitor_avg_backlinks": competitor_averages.get('backlinks', 0)
            }
            
            # Confronto Social
            comparison_data["comparison_metrics"]["social"] = {
                "main_instagram": main_social.get('instagram', {}).get('followers', 0),
                "competitor_avg_instagram": competitor_averages.get('instagram_followers', 0),
                "main_facebook": main_social.get('facebook', {}).get('followers', 0),
                "competitor_avg_facebook": competitor_averages.get('facebook_followers', 0)
            }
            
            # Posizionamento competitivo
            comparison_data["competitive_positioning"] = self.analyze_competitive_positioning(
                main_company, competitors
            )
            
            # Raccomandazioni
            comparison_data["recommendations"] = self.generate_competitive_recommendations(
                main_company, competitors, comparison_data["comparison_metrics"]
            )
            
            return comparison_data
            
        except Exception as e:
            logger.error(f"Errore nel confronto competitor: {e}")
            return {"error": str(e)}
    
    def calculate_competitor_averages(self, competitors: List[Dict]) -> Dict:
        """
        Calcola medie delle metriche dei competitor
        """
        try:
            if not competitors:
                return {}
            
            totals = {
                "organic_traffic": 0,
                "keywords": 0,
                "backlinks": 0,
                "instagram_followers": 0,
                "facebook_followers": 0,
                "linkedin_followers": 0
            }
            
            count = len(competitors)
            
            for competitor in competitors:
                seo = competitor.get('seo_metrics', {})
                social = competitor.get('social_presence', {})
                
                totals["organic_traffic"] += seo.get('organic_traffic', 0)
                totals["keywords"] += seo.get('keywords', 0)
                totals["backlinks"] += seo.get('backlinks', 0)
                totals["instagram_followers"] += social.get('instagram_followers', 0)
                totals["facebook_followers"] += social.get('facebook_followers', 0)
                totals["linkedin_followers"] += social.get('linkedin_followers', 0)
            
            averages = {key: value // count for key, value in totals.items()}
            
            return averages
            
        except Exception as e:
            logger.error(f"Errore nel calcolo medie competitor: {e}")
            return {}
    
    def analyze_competitive_positioning(self, main_company: Dict, competitors: List[Dict]) -> Dict:
        """
        Analizza il posizionamento competitivo
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Sei un esperto di strategia competitiva che analizza il posizionamento di un'azienda rispetto ai suoi competitor principali."},
                    {"role": "user", "content": f"Analizza il posizionamento competitivo di {main_company.get('company_name', 'Azienda')} rispetto a questi competitor: {[c.get('name', '') for c in competitors[:3]]}. Fornisci analisi di forze/debolezze relative, opportunità di differenziazione, e posizionamento nel mercato."}
                ],
                max_tokens=1500,
                temperature=0.4
            )
            
            positioning_analysis = response.choices[0].message.content
            
            return {
                "positioning_summary": positioning_analysis,
                "competitive_advantages": self.extract_competitive_advantages(positioning_analysis),
                "areas_for_improvement": self.extract_improvement_areas(positioning_analysis),
                "differentiation_opportunities": self.extract_differentiation_opportunities(positioning_analysis)
            }
            
        except Exception as e:
            logger.error(f"Errore nell'analisi posizionamento: {e}")
            return {"error": str(e)}
    
    def extract_competitive_advantages(self, text: str) -> List[str]:
        """Estrae vantaggi competitivi dal testo"""
        advantages = []
        
        patterns = [
            r'vantaggio[^.]*\.([^.]+)',
            r'punti?\s+di\s+forza[^.]*\.([^.]+)',
            r'superiore[^.]*\.([^.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    advantages.append(match.strip())
        
        return advantages[:5]
    
    def extract_improvement_areas(self, text: str) -> List[str]:
        """Estrae aree di miglioramento dal testo"""
        areas = []
        
        patterns = [
            r'(?:migliorare|potenziare|sviluppare)[^.]*\.([^.]+)',
            r'punti?\s+di\s+debolezza[^.]*\.([^.]+)',
            r'opportunità[^.]*\.([^.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    areas.append(match.strip())
        
        return areas[:5]
    
    def extract_differentiation_opportunities(self, text: str) -> List[str]:
        """Estrae opportunità di differenziazione dal testo"""
        opportunities = []
        
        patterns = [
            r'differenziazione[^.]*\.([^.]+)',
            r'opportunità[^.]*\.([^.]+)',
            r'nicchia[^.]*\.([^.]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    opportunities.append(match.strip())
        
        return opportunities[:3]
    
    def generate_competitive_recommendations(self, main_company: Dict, competitors: List[Dict], metrics: Dict) -> List[str]:
        """
        Genera raccomandazioni competitive
        """
        try:
            competitor_names = [c.get('name', '') for c in competitors[:3]]
            
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Sei un consulente di strategia competitiva che fornisce raccomandazioni concrete e attuabili per migliorare il posizionamento competitivo."},
                    {"role": "user", "content": f"Genera 7 raccomandazioni strategiche specifiche per {main_company.get('company_name', 'Azienda')} per competere meglio contro {competitor_names}. Basati su dati SEO, social media, e positioning. Fornisci azioni concrete e misurabili."}
                ],
                max_tokens=1500,
                temperature=0.4
            )
            
            recommendations_text = response.choices[0].message.content
            
            # Estrai raccomandazioni specifiche
            recommendations = []
            lines = recommendations_text.split('\n')
            
            for line in lines:
                if line.strip() and (line.strip().startswith(('•', '-', '*')) or re.match(r'^\d+\.', line.strip())):
                    recommendations.append(line.strip())
            
            return recommendations[:7]
            
        except Exception as e:
            logger.error(f"Errore nella generazione raccomandazioni: {e}")
            return []
