import os
from dotenv import load_dotenv
from transformers import DetrImageProcessor, DetrForObjectDetection
from ultralytics import YOLO
load_dotenv()

PDF_FOLDER_PATH = os.getenv('PDF_FOLDER_PATH', 'data\\sample_pdfs')
IMAGE_FOLDER_PATH = os.getenv('IMAGE_FOLDER_PATH', 'data\\extracted_images')
EXCEL_OUTPUT_FOLDER_PATH = os.getenv('EXCEL_OUTPUT_FOLDER_PATH', 'data\\output')

SELECTED_SECTORS = os.getenv('SELECTED_SECTORES','''Household and Personal Products,Financial Services,Conglomerates,Tourism/Leisure,Telecommunications,Equipment,Technology Hardware,
Mining,Forest and Paper Products,Food and Beverage Products,Other,Chemicals,Energy Utilities,Consumer Durables,Energy,Non-Profit / Services,
Construction,Retailers,Construction Materials,Computers,Water Utilities,Public Agency,Media,Tobacco,Logistics,
Textiles and Apparel,Automotive,Real Estate,Universities,Metals Products,Healthcare Services,Healthcare Products,Aviation,
Commercial Services,Waste Management,Railroad,Agriculture,Toys''')
SELECTED_YEARS = os.getenv('SELECTED_YEARS','''1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018''')
RDS_FILE_PATH = os.getenv('RDS_FILE_PATH',"data\\DAV_assignment.rds" )
IMAGE_SIZE_THRESHOLD_COEF=float(os.getenv('IMAGE_SIZE_THRESHOALD_COEF',0.05 ))

processor_DETR = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model_DETR = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

NATURE_OBJECT = {'Leaf', 'Sea', 'Tree', 'cloud', 'forest', 'grass',
                  'lake', 'river', 'sky', 'water', 'mountain', 'hill', 'valley', 'desert', 'sand', 'rock', 'stone', 'snow', 'ice', 'fire', 'smoke', 'ash', 'dust', 'fog', 'mist', 'haze', 'cloud', 'rain', 'snow', 'wind', 'storm', 'thunder', 'lightning', 'sun', 'moon', 'star', 'planet', 'comet', 'meteor', 
                 'asteroid', 'galaxy', 'universe', 'earth', 'moon'}

model_YOLO = YOLO("../runs/detect/train/weights/best.pt")  

LANG_MAP = {
    'en': 'eng',    # English
    'fa': 'fas',    # Persian (Farsi)
    'fr': 'fra',    # French
    'de': 'deu',    # German
    'es': 'spa',    # Spanish
    'it': 'ita',    # Italian
    'ar': 'ara',    # Arabic
    'ru': 'rus',    # Russian
    'pt': 'por',    # Portuguese
    'ko': 'kor',    # Korean
    'ca': 'cat',    # Catalan
    'hu': 'hun',    # Hungarian
    'ja': 'jpn',    # Japanese
    'zh-cn': 'chi_sim',  # Simplified Chinese
    'zh-tw': 'chi_tra',  # Traditional Chinese
    'hi': 'hin',    # Hindi
    'tr': 'tur',    # Turkish
    'nl': 'nld',    # Dutch
    'sv': 'swe',    # Swedish
    'pl': 'pol',    # Polish
    'da': 'dan',    # Danish
    'fi': 'fin',    # Finnish
    'el': 'ell',    # Greek
    'he': 'heb',    # Hebrew
    'th': 'tha',    # Thai
    'vi': 'vie',    # Vietnamese
    'id': 'ind',    # Indonesian
    'ms': 'msa',    # Malay
    'uk': 'ukr',    # Ukrainian
    'cs': 'ces',    # Czech
    'ro': 'ron',    # Romanian
    'bg': 'bul',    # Bulgarian
    'hr': 'hrv',    # Croatian
    'sk': 'slk',    # Slovak
    'sl': 'slv',    # Slovenian
    'sr': 'srp',    # Serbian
    'lt': 'lit',    # Lithuanian
    'lv': 'lav',    # Latvian
    'et': 'est',    # Estonian
    'bn': 'ben',    # Bengali
    'ta': 'tam',    # Tamil
    'ur': 'urd',    # Urdu
    'ml': 'mal',    # Malayalam
    'te': 'tel',    # Telugu
    'mr': 'mar',    # Marathi
    'kn': 'kan',    # Kannada
    'gu': 'guj',    # Gujarati
    'pa': 'pan',    # Punjabi
    'si': 'sin',    # Sinhala
}

