import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
OPENROUTER_API_KEY: str = os.environ["OPENROUTER_API_KEY"]
APIFY_API_TOKEN: str = os.environ["APIFY_API_TOKEN"]
ELEVENLABS_API_KEY: str = os.environ["ELEVENLABS_API_KEY"]
ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# Optional GDrive folder; falls back to local file if unset
GDRIVE_FOLDER_ID: str = os.getenv("GDRIVE_FOLDER_ID", "")

# --- Paths ---
ROOT_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "output"
DATA_DIR = ROOT_DIR / "data"
VIDEO_DIR = ROOT_DIR / "video"
OUTPUT_DIR.mkdir(exist_ok=True)

# --- LLM ---
# google/gemini-flash-1.5:free has higher rate limits than llama free tier
LLM_MODEL = "openrouter/nvidia/nemotron-3-super-120b-a12b:free"
LLM_BASE_URL = "https://openrouter.ai/api/v1"
# Fallback models tried in order if primary is rate-limited
LLM_FALLBACK_MODELS = [
    "openrouter/meta-llama/llama-3.3-70b-instruct:free",
    "openrouter/qwen/qwen-2.5-72b-instruct:free",
    "openrouter/mistralai/mistral-7b-instruct:free",
]

# --- Apify ---
# Meta Ads Library scraper actor
APIFY_ACTOR_ID = "apify/facebook-ads-library-scraper"

# Search terms targeting CWT's trading niche
CWT_SEARCH_TERMS = [
    "trading signals",
    "stock market profits",
    "options trading strategy",
    "day trading system",
    "financial freedom trading",
]

# --- Image generation ---
# Pollinations.ai — completely free, no API key required
IMAGE_GEN_BASE_URL = "https://image.pollinations.ai/prompt"
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920  # vertical format for social media

# --- Video ---
VIDEO_FPS = 30
VIDEO_DURATION_SECONDS = 60
