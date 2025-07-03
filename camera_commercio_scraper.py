import requests
from bs4 import BeautifulSoup
import re
import time
import json
import logging
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class CameraCommercioScraper:
    """
    Scraper per estrarre dati dalle Camere di Commercio italiane
    """
    
    def __init__(self, use_selenium: bool = True):
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.ua = UserAgent()
        self.driver = None
        
        if use_selenium:
            self.setup_selenium()
    
    def setup_selenium(self):
        """Configura Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={self.ua.random}')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as e:
            logger.error(f"Errore nella configurazione Selenium: {e}")
            self.use_selenium = False
    
    def search_company_basic(self, company_name: str) -> Dict:
        """
        Ricerca base di un'azienda (senza scraping reale)
        """
        try:
            # Simulazione ricerca - in produzione implementare scraping reale
            search_results = {
                "company_name": company_name,
                "search_performed": True,
                "results_found": 1,
                "companies": [{
                    "name": company_name,
                    "piva": self.generate_fake_piva(),
                    "codice_fiscale": self.generate_fake_cf(),
                    "sede_legale": self.generate_fake_address(),
                    "comune": "Milano",
                    "provincia": "MI",
                    "cap": "20121",
                    "settore": "Servizi",
                    "forma_giuridica": "SRL",
                    "capitale_sociale": "€100.000",
                    "stato": "Attiva"
                }]
            }
            
            return search_results
            
        except Exception as e:
            logger.error(f"Errore nella ricerca azienda: {e}")
            return {"error": str(e)}
    
    def search_company_advanced(self, company_name: str, use_ai: bool = True) -> Dict:
        """
        Ricerca avanzata con AI per dati più realistici
        """
        try:
            if use_ai:
                # Usa OpenAI per generare dati realistici
                from openai import OpenAI
                import os
                
                client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sei un esperto di dati aziendali italiani. Genera informazioni realistiche e verosimili per aziende italiane, includendo P.IVA, codice fiscale, sede legale, settore ATECO, forma giuridica, capitale sociale basandoti su aziende simili esistenti."},
                        {"role": "user", "content": f"Genera dati completi di Camera di Commercio per l'azienda italiana: {company_name}"}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                
                ai_content = response.choices[0].message.content
                
                # Estrai dati strutturati dal contenuto AI
                extracted_data = self.extract_company_data_from_ai(ai_content, company_name)
                
                return {
                    "company_name": company_name,
                    "search_performed": True,
                    "data_source": "AI_Enhanced",
                    "extracted_data": extracted_data,
                    "raw_ai_response": ai_content
                }
            else:
                return self.search_company_basic(company_name)
                
        except Exception as e:
            logger.error(f"Errore nella ricerca avanzata: {e}")
            return self.search_company_basic(company_name)
    
    def extract_company_data_from_ai(self, ai_content: str, company_name: str) -> Dict:
        """
        Estrae dati strutturati dal contenuto AI
        """
        try:
            data = {
                "nome_azienda": company_name,
                "piva": self.extract_with_regex(ai_content, r'P\.?\s*IVA:?\s*(\d{11})', self.generate_fake_piva()),
                "codice_fiscale": self.extract_with_regex(ai_content, r'C\.?\s*F\.?:?\s*(\d{11})', self.generate_fake_cf()),
                "sede_legale": self.extract_with_regex(ai_content, r'Sede\s+legale:?\s*([^,\n]+(?:,\s*[^,\n]+)*)', "Via Roma 1, Milano"),
                "comune": self.extract_with_regex(ai_content, r'Comune:?\s*([^,\n]+)', "Milano"),
                "provincia": self.extract_with_regex(ai_content, r'Provincia:?\s*([^,\n]+)', "MI"),
                "cap": self.extract_with_regex(ai_content, r'CAP:?\s*(\d{5})', "20121"),
                "settore_ateco": self.extract_with_regex(ai_content, r'ATECO:?\s*(\d{2,4})', "6201"),
                "descrizione_attivita": self.extract_with_regex(ai_content, r'Attività:?\s*([^.\n]+)', "Servizi informatici"),
                "forma_giuridica": self.extract_with_regex(ai_content, r'Forma\s+giuridica:?\s*([^,\n]+)', "SRL"),
                "capitale_sociale": self.extract_with_regex(ai_content, r'Capitale\s+sociale:?\s*€?\s*([\d.,]+)', "100.000"),
                "anno_costituzione": self.extract_with_regex(ai_content, r'Costituita\s+nel:?\s*(\d{4})', "2010"),
                "stato_azienda": self.extract_with_regex(ai_content, r'Stato:?\s*([^,\n]+)', "Attiva"),
                "rea": self.extract_with_regex(ai_content, r'REA:?\s*([^,\n]+)', f"MI-{self.generate_fake_rea()}"),
                "pec": self.extract_with_regex(ai_content, r'PEC:?\s*([^,\n]+)', f"{company_name.lower().replace(' ', '')}@pec.it")
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Errore nell'estrazione dati AI: {e}")
            return {"error": str(e)}
    
    def extract_with_regex(self, text: str, pattern: str, default: str) -> str:
        """
        Estrae valore usando regex con fallback
        """
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            return match.group(1).strip() if match else default
        except:
            return default
    
    def generate_fake_piva(self) -> str:
        """Genera P.IVA fake per testing"""
        import random
        return f"{random.randint(10000000000, 99999999999)}"
    
    def generate_fake_cf(self) -> str:
        """Genera Codice Fiscale fake per testing"""
        import random
        return f"{random.randint(10000000000, 99999999999)}"
    
    def generate_fake_address(self) -> str:
        """Genera indirizzo fake per testing"""
        import random
        streets = ["Via Roma", "Via Milano", "Corso Italia", "Piazza Duomo", "Via Nazionale"]
        numbers = [str(random.randint(1, 200))]
        cities = ["Milano", "Roma", "Napoli", "Torino", "Firenze"]
        
        return f"{random.choice(streets)} {random.choice(numbers)}, {random.choice(cities)}"
    
    def generate_fake_rea(self) -> str:
        """Genera numero REA fake"""
        import random
        return str(random.randint(1000000, 9999999))
    
    def get_financial_data(self, company_data: Dict) -> Dict:
        """
        Estrae dati finanziari aggiuntivi
        """
        try:
            # In produzione, qui implementeresti scraping da fonti finanziarie
            # Per ora simuliamo con dati realistici
            
            import random
            
            base_revenue = random.randint(500000, 10000000)
            
            financial_data = {
                "fatturato_2023": base_revenue,
                "fatturato_2022": int(base_revenue * 0.85),
                "fatturato_2021": int(base_revenue * 0.7),
                "fatturato_2020": int(base_revenue * 0.6),
                "fatturato_2019": int(base_revenue * 0.5),
                "patrimonio_netto": int(base_revenue * 0.15),
                "totale_attivo": int(base_revenue * 0.8),
                "numero_dipendenti": random.randint(5, 50),
                "costo_personale": int(base_revenue * 0.3),
                "risultato_esercizio": int(base_revenue * 0.1),
                "data_ultimo_bilancio": "2023-12-31"
            }
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Errore nell'estrazione dati finanziari: {e}")
            return {"error": str(e)}
    
    def get_company_structure(self, company_data: Dict) -> Dict:
        """
        Estrae struttura societaria
        """
        try:
            # Simulazione struttura societaria
            structure = {
                "soci": [
                    {
                        "nome": "Mario Rossi",
                        "quota": "51%",
                        "ruolo": "Amministratore Unico"
                    },
                    {
                        "nome": "Luigi Verdi",
                        "quota": "49%",
                        "ruolo": "Socio"
                    }
                ],
                "organi_sociali": {
                    "amministratore_unico": "Mario Rossi",
                    "collegio_sindacale": "Non presente",
                    "revisore_legale": "Dott. Paolo Bianchi"
                },
                "poteri_rappresentanza": "Amministratore Unico con firma singola"
            }
            
            return structure
            
        except Exception as e:
            logger.error(f"Errore nell'estrazione struttura societaria: {e}")
            return {"error": str(e)}
    
    def search_complete_profile(self, company_name: str) -> Dict:
        """
        Ricerca completa di un profilo aziendale
        """
        try:
            # Ricerca base
            basic_data = self.search_company_advanced(company_name)
            
            if "error" in basic_data:
                return basic_data
            
            extracted_data = basic_data.get("extracted_data", {})
            
            # Dati finanziari
            financial_data = self.get_financial_data(extracted_data)
            
            # Struttura societaria
            structure_data = self.get_company_structure(extracted_data)
            
            # Risultato completo
            complete_profile = {
                "company_name": company_name,
                "basic_info": extracted_data,
                "financial_data": financial_data,
                "company_structure": structure_data,
                "search_timestamp": time.time(),
                "data_source": "Camera di Commercio (Simulato)"
            }
            
            return complete_profile
            
        except Exception as e:
            logger.error(f"Errore nella ricerca completa: {e}")
            return {"error": str(e)}
    
    def __del__(self):
        """Cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
