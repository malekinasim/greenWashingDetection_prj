import os
from dotenv import load_dotenv

load_dotenv()

PDF_FOLDER_PATH = os.getenv('PDF_FOLDER_PATH', 'data\\sample_pdfs')
IMAGE_FOLDER_PATH = os.getenv('IMAGE_FOLDER_PATH', 'data\\extracted_images')
EXCEL_OUTPUT_FOLDER_PATH = os.getenv('EXCEL_OUTPUT_FOLDER_PATH', 'data\\output')

SELECTED_SECTORS = os.getenv('SELECTED_SECTORES','''Logistics,Conglomerates,Energy Utilities,Construction,Energy,Construction Materials,
                             Waste Management,Mining,Automotive,Metals Products,Chemicals''')
SELECTED_YEARS = os.getenv('SELECTED_YEARS','''2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018''')
RDS_FILE_PATH = os.getenv('RDS_FILE_PATH',"data\\DAV_assignment.rds" )

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

