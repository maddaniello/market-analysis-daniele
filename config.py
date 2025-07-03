import os
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

class Config:
    """Configurazione dell'applicazione"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SEMRUSH_API_KEY = os.getenv('SEMRUSH_API_KEY')
    
    # Configurazioni scraping
    SCRAPING_DELAY = 1  # secondi tra le richieste
    MAX_RETRIES = 3
    TIMEOUT = 30
    
    # User agents per web scraping
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    # Configurazioni Camera di Commercio
    CAMERA_COMMERCIO_BASE_URL = "https://www.ufficiocamerale.it"
    CAMERA_COMMERCIO_SEARCH_URL = f"{CAMERA_COMMERCIO_BASE_URL}/ricerca-imprese"
    
    # Configurazioni SEMRush
    SEMRUSH_BASE_URL = "https://api.semrush.com/"
    SEMRUSH_ENDPOINTS = {
        'domain_overview': 'domain_overview',
        'keyword_difficulty': 'keyword_difficulty',
        'backlinks': 'backlinks',
        'organic_keywords': 'organic_keywords'
    }
    
    # Configurazioni Social Media
    SOCIAL_PLATFORMS = {
        'instagram': {
            'base_url': 'https://www.instagram.com/',
            'api_endpoint': 'https://www.instagram.com/api/v1/users/web_profile_info/'
        },
        'facebook': {
            'base_url': 'https://www.facebook.com/',
            'api_endpoint': 'https://graph.facebook.com/v18.0/'
        },
        'tiktok': {
            'base_url': 'https://www.tiktok.com/',
            'api_endpoint': 'https://www.tiktok.com/api/user/detail/'
        },
        'youtube': {
            'base_url': 'https://www.youtube.com/',
            'api_endpoint': 'https://www.googleapis.com/youtube/v3/'
        }
    }
    
    # Configurazioni OpenAI
    OPENAI_MODEL = "gpt-4"
    OPENAI_MAX_TOKENS = 2000
    OPENAI_TEMPERATURE = 0.3
    
    # Configurazioni database (per versioni future)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///marketing_analyzer.db')
    
    # Configurazioni logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurazioni cache
    CACHE_TTL = 3600  # 1 ora
    
    @classmethod
    def validate_config(cls):
        """Valida la configurazione"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY non configurata")
        
        if errors:
            raise ValueError(f"Errori di configurazione: {', '.join(errors)}")
        
        return True
