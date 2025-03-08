import os
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import pandas as pd
from langdetect import detect
import pyreadr
import cv2
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch

# Load environment variables
env_mode = os.getenv('ENV_MODE', 'dev')
env_file = f'.env.{env_mode}'
load_dotenv(env_file)

PDF_FOLDER_PATH = os.getenv('PDF_FOLDER_PATH', 'sample_dataSet/pdf') #pdf folder path
IMAGE_FOLDER_PATH = os.getenv('IMAGE_FOLDER_PATH', 'sample_dataSet/images') 
EXCEL_OUTPUT_FOLDER_PATH = os.getenv('EXCEL_OUTPUT_FOLDER_PATH', 'sample_dataSet/output')
RDS_FILE_PATH = os.getenv('RDS_FILE_PATH', "./DAV_assignment.rds")  
SELECTED_SECTORS = os.getenv('SELECTED_SECTORES', '''Logistics,Conglomerates,Energy Utilities,Construction,Energy,Construction Materials,
                             Waste Management,Mining,Automotive,Metals Products,Chemicals''')
SELECTED_YEARS = os.getenv('SELECTED_YEARS', '''2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018''')
NATURE_OBJECT = {"tree", "river", "leaf", "grass", "flower", "water", "mountain", "cloud", "bird"}

# Load DETR model and processor
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

CHECK_ALL_PAGE_IMAGES = False
lang_map = {
    'en': 'eng',
    'fa': 'fas',
    'fr': 'fra',
    'de': 'deu',
    'es': 'spa',
    'it': 'ita',
    'ar': 'ara',
    'ru': 'rus',
    'pt': 'por',
    'ko': 'kor',
    'ca': 'cat',
    'hu': 'hun',
    'ja': 'jpn',
    'zh-cn': 'chi_sim'
}

def detect_pdf_language(pdf_file):
    text = " ".join([page.get_text() for page in pdf_file])
    langs = set()
    if text.strip():
        try:
            detected_langs = detect(text)
            langs.add(lang_map.get(detected_langs, 'eng'))
            tesseract_langs = '+'.join(langs)
            return tesseract_langs
        except Exception as e:
            print(f"Error in language detection: {e}")
            return "eng"
    return "eng"

def get_pdf_meta_data(pdf_path):
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    return (
        metadata.get("title", "Unknown"),
        metadata.get("author", "Unknown"),
        metadata.get("creationDate", "Unknown"),
        metadata.get("creator", "Unknown"),
        metadata.get("modDate", "Unknown"),
        metadata.get("subject", "Unknown"),
        metadata.get("keywords", "Unknown")
    )

def extract_pdf_info(filename):
    """Extract company name and year from PDF filename."""
    match = filename.split("\\")
    match = match[1].split(".pdf")
    match = match[0].split("_")
    if len(match) < 2:
        raise ValueError("Invalid filename format. Expected at least 3 parts separated by underscores.")
    return match[0], match[1]

def extract_images_pymupdf(pdf_path, output_folder, extract_cover_only=True):
    """Extract images from PDF using PyMuPDF."""
    pdf_file = fitz.open(pdf_path)
    company, year = extract_pdf_info(pdf_path)
    title, author, creationDate, creator, modDate, subject, keywords = get_pdf_meta_data(pdf_file)
    pdfLanguage = detect_pdf_language(pdf_file)
    extracted_images = []

    pages_to_process = [0] if extract_cover_only else range(pdf_file.page_count)

    for page_index in pages_to_process:
        try:
            page = pdf_file.load_page(page_index)
            for img_index, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_path = output_folder / f"{company}_{year}_page{page_index + 1}_img{img_index}.{image_ext}"
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                print(f"Image saved to: {image_path}")  # Debug statement
                extracted_images.append((company, year, image_path, title,
                                        author, creationDate, creator, modDate, subject, keywords, pdfLanguage
                                        ))
            return extracted_images
        except Exception as e:
            print(f"Error opening or processing the PDF file '{pdf_path}': {e}")
            return []

def get_rgb_percentage(image_file):
    """Calculate the percentage of red, green, and blue colors
    in the extracted images.
    """
    total_r, total_g, total_b = 0, 0, 0

    image = Image.open(image_file).convert("RGB")
    image_array = np.array(image)

    total_r += np.sum(image_array[:, :, 0])
    total_g += np.sum(image_array[:, :, 1])
    total_b += np.sum(image_array[:, :, 2])
    total_intensity = total_r + total_g + total_b
    r_percent = (total_r / total_intensity) * 100
    g_percent = (total_g / total_intensity) * 100
    b_percent = (total_b / total_intensity) * 100

    return [r_percent, g_percent, b_percent]

def add_to_excel_data_frame(all_data, excel_output):
    data = pd.DataFrame(all_data, columns=["Company", "Year", "sector",
                                          "Size",
                                          "Organization_type",
                                          "Sec_SASB",
                                          "Region",
                                          "Country",
                                          "OECD",
                                          "english_non_english",
                                          "Image Path",
                                          "Title", "Author",
                                          "Creation Date",
                                          "Creator",
                                          "modification Date",
                                          "Subject", "Keywords", "pdf Language",  # "image Text",
                                          "Red %", "Green %", "Blue %", "detected Object", "detected object count"])
    data.to_excel(excel_output, index=False)
    return data

def select_pdfs_by_sector_and_years():
    result = pyreadr.read_r(RDS_FILE_PATH)
    df_rds = result[None]
    print(df_rds.columns)

    selected_sectors = [sector.strip() for sector in SELECTED_SECTORS.split(",")]
    selected_years = [int(year.strip()) for year in SELECTED_YEARS.split(",")]

    df_selected = df_rds[df_rds["Sector"].isin(selected_sectors) & df_rds["Year"].isin(selected_years)]
    print(df_rds["Sector"])
    return dict(zip(df_selected["file"], zip(df_selected["Sector"], df_selected["Size"],
                                              df_selected["Organization_type"],
                                              df_selected["Sec_SASB"]
                                              , df_selected["Region"], df_selected["Country"], df_selected["OECD"]
                                              , df_selected["english_non_english"])))

def is_pdf_valid(pdf_path):
    try:
        pdf_file = fitz.open(pdf_path)
        page_count = pdf_file.page_count
        if page_count == 0:
            print(f"Invalid PDF (no pages): {pdf_path}")
            return False
        page = pdf_file.load_page(0)
        if not page:
            print(f"Invalid PDF (unable to load the first page): {pdf_path}")
            return False
        pdf_file.close()
        return True
    except Exception as e:
        print(f"Error opening PDF file '{pdf_path}': {e}")
        return False

def get_detect_nature_objects(image_path):
    """Detect nature objects in the image using DETR."""
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return None

    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)

        # Convert outputs to bounding boxes and labels
        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

        nature_found = set()

        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            label_name = model.config.id2label[label.item()]
            if label_name in NATURE_OBJECT:
                nature_found.add(label_name)

        return list(nature_found) if nature_found else None
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def process_pdf_files(pdfFolderPath, imageFolderPath, outputFolder, extract_cover_only):
    """Iterate over PDF files in the specified folder, create an output folder,
    and execute the corresponding extraction method.
    """
    all_data_pymupdf = []

    if not os.path.isdir(pdfFolderPath):
        print(f"Error: PDF folder ({pdfFolderPath}) does not exist!")
        return
    selected_files = select_pdfs_by_sector_and_years()

    for file in os.listdir(pdfFolderPath):
        file_path = os.path.join(pdfFolderPath, file)

        if os.path.isfile(file_path) and file.endswith(".pdf"):

            pdf_name = file.replace(".pdf", "")
            if pdf_name not in selected_files:
                continue

            if not is_pdf_valid(file_path):
                continue

            sector = selected_files[pdf_name][0]
            Size = selected_files[pdf_name][1]
            Organization_type = selected_files[pdf_name][2]
            Sec_SASB = selected_files[pdf_name][3]
            Region = selected_files[pdf_name][4]
            Country = selected_files[pdf_name][5]
            OECD = selected_files[pdf_name][6]
            english_non_english = selected_files[pdf_name][7]
            output_path_pymupdf = Path(os.path.join(imageFolderPath, 'pymupdf', file))
            output_path_pymupdf.mkdir(parents=True, exist_ok=True)

            pymupdf_images = extract_images_pymupdf(file_path, output_path_pymupdf, extract_cover_only)

            for company, year, image_path, title, author, creationDate, creator, modDate, subject, keywords, pdfLanguage in pymupdf_images:
                r, g, b = get_rgb_percentage(image_path)
                detected_bject = get_detect_nature_objects(image_path)

                all_data_pymupdf.append([company, year, sector, Size, Organization_type, Sec_SASB, Region, Country, OECD, english_non_english, str(image_path),
                                         title, author, creationDate, creator, modDate, subject, keywords, pdfLanguage
                                         , r, g, b,
                                         ','.join(detected_bject) if detected_bject is not None else '',
                                         len(detected_bject) if detected_bject is not None else 0
                                         ])

    file_path_pymupdf = os.path.join(outputFolder, "pymupdf", "output.xlsx")
    output_path_pymupdf = Path(os.path.join(outputFolder, 'pymupdf'))
    output_path_pymupdf.mkdir(parents=True, exist_ok=True)
    add_to_excel_data_frame(all_data_pymupdf, file_path_pymupdf)

# Call the main function to process all PDFs in the folder
process_pdf_files(PDF_FOLDER_PATH, IMAGE_FOLDER_PATH, EXCEL_OUTPUT_FOLDER_PATH, True)