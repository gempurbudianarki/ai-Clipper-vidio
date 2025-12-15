import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MEGALLM_API_KEY = os.getenv("MEGALLM_API_KEY")
    MEGALLM_BASE_URL = os.getenv("MEGALLM_BASE_URL", "https://ai.megallm.io/v1")

    MODEL_DEEPSEEK = os.getenv("MODEL_DEEPSEEK")
    MODEL_QWEN = os.getenv("MODEL_QWEN")

settings = Settings()
