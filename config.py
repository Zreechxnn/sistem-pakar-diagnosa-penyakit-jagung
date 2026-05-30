import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, 'knowledge_base.txt')