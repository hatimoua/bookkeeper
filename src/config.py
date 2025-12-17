import os
from dotenv import load_dotenv

#Load environment variables from a .env file
load_dotenv()

class Settings:
    """
    Centralized configuration.
    This class validates  that required keys exist on startup.
    """
    def __init__(self):
        # --- PATH FIX START ---
        # 1. Get the directory where config.py lives (.../src)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Go up one level to the project root (.../bookkeeper)
        project_root = os.path.join(base_dir, "..")
        
        db_path = os.path.join(project_root, "bookkeeper.db")
        self.DATABASE_URL = f"sqlite:///{db_path}"
        
        #2. API Keys
        self.OPENAI_API_KEY = os.getenv("OPENAI_API")
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        self.LANDING_AI_API_KEY = os.getenv("LANDING_AI_API_KEY")
        
        #3. app settings
        self.SEARCH_LIMIT_K = 5  #Number of similar accounts to retrieve
        
    def _get_required_env(self, key: str) -> str:
        """Fetch env var or raise an error if missing."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"❌ Missing required environment variable: {key}")
        return value
    
settings = Settings()   