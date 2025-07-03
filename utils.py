import re
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse, urljoin
import hashlib
import os
from functools import wraps
import streamlit as st

logger = logging.getLogger(__name__)

class DataValidator:
    """Valida e pulisce i dati estratti"""
    
    @staticmethod
    def validate_piva(piva: str) -> bool:
        """Valida formato P.IVA italiana"""
        if not piva or not isinstance(piva, str):
            return False
        
        # Rimuovi spazi e caratteri speciali
        piva = re.sub(r'[^\d]', '', piva)
        
        # Deve essere 11 cifre
        if len(piva) != 11:
            return False
        
        # Algoritmo di controllo P.IVA
        odd_sum = sum(int(piva[i]) for i in range(0, 10, 2))
        even_sum = sum(int(piva[i]) * 2 if int(piva[i]) * 2 < 10 else int(piva[i]) * 2 - 9 for i in range(1, 10, 2))
        
        control_digit = (10 - ((odd_sum + even_sum) % 10)) % 10
        
        return int(piva[10]) == control_digit
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Valida formato URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def clean_company_name(name: str) -> str:
        """Pulisce e normalizza nome azienda"""
        if not name:
            return ""
        
        # Rimuovi forme giuridiche comuni
        legal_forms = ['s.r.l.', 'srl', 's.p.a.', 'spa', 's.r.l', 's.p.a', 'ltd', 'inc', 'corp', 'llc']
        name_clean = name.lower()
        
        for form in legal_forms:
            name_clean = re.sub(rf'\b{form}\b', '', name_clean)
        
        # Rimuovi spazi extra e capitalizza
        name_clean = ' '.join(name_clean.split())
        return name_clean.title()
    
    @staticmethod
    def normalize_metrics(data: Dict) -> Dict:
        """Normalizza metriche numeriche"""
        normalized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Prova a convertire stringhe numeriche
                numeric_value = DataValidator.extract_numeric_value(value)
                normalized[key] = numeric_value if numeric_value is not None else value
            elif isinstance(value, (int, float)):
                normalized[key] = value
            elif isinstance(value, dict):
                normalized[key] = DataValidator.normalize_metrics(value)
            else:
                normalized[key] = value
        
        return normalized
    
    @staticmethod
    def extract_numeric_value(text: str) -> Optional[float]:
        """Estrae valore numerico da testo"""
        if not text:
            return None
        
        # Rimuovi valute e simboli
        clean_text = re.sub(r'[€$£¥₹]', '', str(text))
        
        # Trova numeri con decimali
        number_pattern = r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)'
        matches = re.findall(number_pattern, clean_text)
        
        if matches:
            # Prendi il primo numero trovato
            number_str = matches[0]
            # Normalizza separatori
            number_str = number_str.replace(',', '.')
            try:
                return float(number_str)
            except:
                return None
        
        return None

class CacheManager:
    """Gestisce cache per ridurre chiamate API"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valore dalla cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Salva valore in cache"""
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """Pulisce cache"""
        self.cache.clear()
    
    def generate_key(self, *args) -> str:
        """Genera chiave cache da parametri"""
        key_string = '|'.join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()

class RateLimiter:
    """Gestisce rate limiting per API"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Verifica se è possibile fare una richiesta"""
        now = time.time()
        
        # Rimuovi richieste vecchie
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        return len(self.requests) < self.max_requests
    
    def make_request(self):
        """Registra una richiesta"""
        if self.can_make_request():
            self.requests.append(time.time())
            return True
        return False
    
    def wait_time(self) -> float:
        """Calcola tempo di attesa necessario"""
        if not self.requests:
            return 0
        
        oldest_request = min(self.requests)
        return max(0, self.time_window - (time.time() - oldest_request))

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator per retry automatico in caso di errori"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Tentativo {attempt + 1} fallito per {func.__name__}: {e}")
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

class DataExporter:
    """Esporta dati in vari formati"""
    
    @staticmethod
    def to_json(data: Dict, indent: int = 2) -> str:
        """Esporta in JSON"""
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    
    @staticmethod
    def to_csv(data: List[Dict]) -> str:
        """Esporta in CSV"""
        if not data:
            return ""
        
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    @staticmethod
    def to_markdown(data: Dict, title: str = "Report") -> str:
        """Esporta in Markdown"""
        markdown = f"# {title}\n\n"
        markdown += f"*Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}*\n\n"
        
        def dict_to_markdown(d: Dict, level: int = 2) -> str:
            md = ""
            for key, value in d.items():
                if isinstance(value, dict):
                    md += f"{'#' * level} {key.replace('_', ' ').title()}\n\n"
                    md += dict_to_markdown(value, level + 1)
                elif isinstance(value, list):
                    md += f"{'#' * level} {key.replace('_', ' ').title()}\n\n"
                    for item in value:
                        if isinstance(item, dict):
                            md += dict_to_markdown(item, level + 1)
                        else:
                            md += f"- {item}\n"
                    md += "\n"
                else:
                    md += f"**{key.replace('_', ' ').title()}**: {value}\n\n"
            return md
        
        markdown += dict_to_markdown(data)
        return markdown

class StreamlitUtils:
    """Utility per Streamlit"""
    
    @staticmethod
    def show_progress(steps: List[str], current_step: int):
        """Mostra progress bar con steps"""
        progress = current_step / len(steps)
        st.progress(progress)
        
        if current_step < len(steps):
            st.info(f"📋 Step {current_step + 1}/{len(steps)}: {steps[current_step]}")
    
    @staticmethod
    def display_metrics_grid(metrics: Dict, cols: int = 4):
        """Mostra metriche in griglia"""
        metric_items = list(metrics.items())
        rows = [metric_items[i:i+cols] for i in range(0, len(metric_items), cols)]
        
        for row in rows:
            columns = st.columns(len(row))
            for col, (key, value) in zip(columns, row):
                with col:
                    if isinstance(value, (int, float)):
                        st.metric(key.replace('_', ' ').title(), f"{value:,}")
                    else:
                        st.metric(key.replace('_', ' ').title(), str(value))
    
    @staticmethod
    def display_comparison_table(data: List[Dict], title: str = "Confronto"):
        """Mostra tabella di confronto"""
        st.subheader(title)
        
        if not data:
            st.warning("Nessun dato disponibile per il confronto")
            return
        
        import pandas as pd
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    
    @staticmethod
    def create_download_buttons(data: Dict, filename_base: str):
        """Crea bottoni per download in vari formati"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            json_data = DataExporter.to_json(data)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"{filename_base}.json",
                mime="application/json"
            )
        
        with col2:
            md_data = DataExporter.to_markdown(data, filename_base)
            st.download_button(
                label="📝 Download Markdown",
                data=md_data,
                file_name=f"{filename_base}.md",
                mime="text/markdown"
            )
        
        with col3:
            # Placeholder per PDF (da implementare)
            st.button("📋 Download PDF", disabled=True, help="Funzione in sviluppo")

class ErrorHandler:
    """Gestisce errori e logging"""
    
    @staticmethod
    def log_error(error: Exception, context: str = ""):
        """Logga errore con contesto"""
        logger.error(f"Errore in {context}: {type(error).__name__}: {str(error)}")
    
    @staticmethod
    def display_error(error: Exception, user_message: str = "Si è verificato un errore"):
        """Mostra errore all'utente"""
        st.error(f"❌ {user_message}")
        
        with st.expander("Dettagli tecnici"):
            st.code(f"{type(error).__name__}: {str(error)}")
    
    @staticmethod
    def safe_execute(func, *args, **kwargs):
        """Esegue funzione con gestione errori"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.log_error(e, func.__name__)
            return None

class WebScraper:
    """Utility per web scraping sicuro"""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @retry_on_failure(max_retries=3)
    def get_page(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """Ottiene pagina web con retry"""
        try:
            time.sleep(self.delay)  # Rate limiting
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Errore nel recupero di {url}: {e}")
            return None
    
    def extract_text(self, html: str, selector: str) -> Optional[str]:
        """Estrae testo usando CSS selector"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else None
        except Exception as e:
            logger.error(f"Errore nell'estrazione testo: {e}")
            return None

class ConfigManager:
    """Gestisce configurazioni dinamiche"""
    
    def __init__(self):
        self.config = self.load_default_config()
    
    def load_default_config(self) -> Dict:
        """Carica configurazione di default"""
        return {
            'scraping': {
                'delay': 1.0,
                'timeout': 30,
                'max_retries': 3,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'openai': {
                'model': 'gpt-4',
                'max_tokens': 2000,
                'temperature': 0.3,
                'requests_per_minute': 20
            },
            'cache': {
                'ttl': 3600,
                'max_size': 1000
            },
            'export': {
                'formats': ['json', 'markdown', 'csv'],
                'max_file_size': 10 * 1024 * 1024  # 10MB
            }
        }
    
    def get(self, key: str, default=None):
        """Ottiene valore di configurazione"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Imposta valore di configurazione"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

# Istanze globali
cache_manager = CacheManager()
config_manager = ConfigManager()
data_validator = DataValidator()
rate_limiter = RateLimiter(max_requests=20, time_window=60)

# Funzioni utility globali
def format_number(num: float, format_type: str = 'standard') -> str:
    """Formatta numeri per display"""
    if pd.isna(num) or num is None:
        return "N/A"
    
    if format_type == 'currency':
        return f"€{num:,.2f}"
    elif format_type == 'percentage':
        return f"{num:.1f}%"
    elif format_type == 'compact':
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:,.0f}"
    else:
        return f"{num:,.0f}"

def sanitize_filename(filename: str) -> str:
    """Sanitizza nome file per export"""
    # Rimuovi caratteri non validi
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limita lunghezza
    sanitized = sanitized[:100]
    # Rimuovi spazi multipli
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized

def get_company_domain(company_name: str) -> str:
    """Genera domain probabile da nome azienda"""
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
    return f"www.{clean_name}.it"

def validate_api_key(api_key: str, service: str = 'openai') -> bool:
    """Valida formato API key"""
    if not api_key:
        return False
    
    if service == 'openai':
        return api_key.startswith('sk-') and len(api_key) > 40
    elif service == 'semrush':
        return len(api_key) > 20
    else:
        return len(api_key) > 10
