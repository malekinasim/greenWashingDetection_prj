from langdetect import detect
from src.config import LANG_MAP
def detect_pdf_language(text):
    try:
        return LANG_MAP.get(detect(text), 'eng') if text.strip() else 'eng'
    except:
        return 'eng'
