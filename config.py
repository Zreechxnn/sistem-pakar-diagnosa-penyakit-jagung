import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, 'knowledge_base.txt')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = "https://api.deepseek.com" 