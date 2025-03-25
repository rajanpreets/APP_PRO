import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FDA_API_KEY = os.getenv("FDA_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Model Settings
GROQ_MODEL = "mixtral-8x7b-32768"  # or "llama2-70b-4096"
TEMPERATURE = 0.7
MAX_TOKENS = 2000

# API Settings
FDA_BASE_URL = "https://api.fda.gov"
CLINICAL_TRIALS_BASE_URL = "https://clinicaltrials.gov/api/query/study_fields"
NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
SERPER_BASE_URL = "https://google.serper.dev/search"

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", "5000"))
HOST = os.getenv("HOST", "0.0.0.0")

# CORS Settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Cache Settings
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour in seconds

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))  # 1 hour in seconds 