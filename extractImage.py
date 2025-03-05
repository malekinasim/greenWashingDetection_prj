import os
from pathlib import Path
import fitz # PyMuPDF
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import pandas as pd
from langdetect import detect
from pdf2image import convert_from_path
import cv2
import pyreadr
from ultralytics import YOLO



# Load environment variables
env_mode = os.getenv('ENV_MODE', 'dev')  
env_file = f'.env.{env_mode}'
load_dotenv(env_file)


PDF_FOLDER_PATH = os.getenv('PDF_FOLDER_PATH', 'sample_dataSet') 
IMAGE_FOLDER_PATH = os.getenv('IMAGE_FOLDER_PATH', 'sample_dataSet/images') 
EXCEL_OUTPUT_FOLDER_PATH = os.getenv('EXCEL_OUTPUT_FOLDER_PATH', 'sample_dataSet/output')
RDS_FILE_PATH = os.getenv('RDS_FILE_PATH',"./DAV_assignment.rds" )
NATURE_OBJECT = {"tree", "river", "leaf", "grass", "flower", "water", "mountain", "cloud", "bird","cat","dog","cow","horse","sheep","elephant","bear","zebra","giraffe","frisbee"}



model = YOLO("yolov8x.pt")  
CHECK_ALL_PAGE_IMAGES=False
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

def extract_images_pymupdf(pdf_path, output_folder,extract_cover_only=True):
    """Extract images from PDF using PyMuPDF."""
    pdf_file = fitz.open(pdf_path)
    company, year = extract_pdf_info(pdf_path)
    title, author, creationDate, creator, modDate, subject, keywords =get_pdf_meta_data(pdf_file)
    pdfLanguage=detect_pdf_language(pdf_file)
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
                image_path = output_folder / f"{company}_{year}_page{page_index+1}_img{img_index}.{image_ext}"
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                extracted_images.append((company, year,image_path,title,
                                        author,creationDate,creator,modDate,subject,keywords,pdfLanguage
                ))
            return extracted_images
        except Exception as e:
            print(f"Error opening or processing the PDF file '{pdf_path}': {e}")
            return []



def get_best_preprocessing(image):
    """تست خودکار تبدیل تصویر به GRAY یا HSV و انتخاب بهترین گزینه"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_gray = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours_gray, _ = cv2.findContours(binary_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2]
    _, binary_v = cv2.threshold(v, 200, 255, cv2.THRESH_BINARY_INV)
    contours_v, _ = cv2.findContours(binary_v, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return (v, "HSV") if len(contours_v) > len(contours_gray) else (gray, "GRAY")

def extract_images_opencv(pdf_path, output_folder, extract_cover_only=True):
    """Extract images from PDF using OpenCV."""
    if extract_cover_only:
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
    else:
        images = convert_from_path(pdf_path)
    
    company, year = extract_pdf_info(pdf_path)
    pdf_file = fitz.open(pdf_path)
    title, author, creationDate, creator, moddate, subject, keywords = get_pdf_meta_data(pdf_file)
    pdfLanguage = detect_pdf_language(pdf_file)
    extracted_images = []
    
    for i, image in enumerate(images):
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        processed_img = get_best_preprocessing(img_cv)

        blurred = cv2.GaussianBlur(processed_img, (5, 5), 0)

        edges = cv2.Canny(blurred, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for j, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            img_height, img_width = img_cv.shape[:2]
            min_width = img_width * 0.05  # حداقل 5 درصد از عرض تصویر
            min_height = img_height * 0.05  # حداقل 5 درصد از ارتفاع تصویر

            if w > min_width and h > min_height:
                extracted_image = img_cv[y:y+h, x:x+w]
                image_filename = output_folder / f"{company}_{year}_page{i+1}_img{j+1}.png"
                cv2.imwrite(str(image_filename), extracted_image)
                extracted_images.append((company, year, image_filename, title,
                                     author, creationDate, creator, moddate, subject, keywords, pdfLanguage))
    return extracted_images

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

def add_to_excel_data_frame(all_data,excel_output):
     data = pd.DataFrame(all_data, columns=["Company", "Year","sector",
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
                                             "Subject","Keywords","pdf Language",#"image Text",
                                              "Red %", "Green %", "Blue %"
                                            #   ,"detected Object",
                                            #   "detected nature Obj",
                                            #   "detected nature object count"
                                              ])
     data.to_excel(excel_output, index=False)
     return data
     

def select_pdfs_by_sector_and_years():

    result = pyreadr.read_r(RDS_FILE_PATH)  
    df_rds = result[None]  
    print(df_rds.columns)

    selected_sectors = [sector.strip() for sector in SELECTED_SECTORS.split(",")]
    selected_years = [int(year.strip()) for year in SELECTED_YEARS.split(",")]

    df_selected= df_rds[df_rds["Sector"].isin(selected_sectors) & df_rds["Year"].isin(selected_years) ] 
    print(df_rds["Sector"])
    return  dict(zip(df_selected["file"],zip( df_selected["Sector"],df_selected["Size"],
                     df_selected["Organization_type"],
                     df_selected["Sec_SASB"]
                     ,df_selected["Region"],df_selected["Country"],df_selected["OECD"]
                     ,df_selected["english_non_english"])))


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
   
    try:
        results = model(image_path)  

        nature_found = set()  
        all_found = set()  


        output_folder =  os.path.join(os.path.dirname(image_path) , "detect_output") 
        os.makedirs(output_folder, exist_ok=True)
        
        for result in results:
            img = Image.fromarray(result.plot()) 
            output_path = os.path.join(output_folder, os.path.basename(image_path))
            img.save(output_path)
            
        # confidence = result.boxes.conf.item() 
        # box_Cordinate = result.boxes.xyxy.cpu().numpy() 

            boxes = result.boxes.xyxy.cpu().numpy()  
            confidences = result.boxes.conf.cpu().numpy() 
            labels = result.boxes.cls.cpu().numpy()
        
            for i, label in enumerate(labels):
                confidence = confidences[i]
                box = boxes[i]
                class_name = result.names[int(label)]  
                if class_name in NATURE_OBJECT:
                    nature_found.add(f"Detected {class_name} with confidence {confidence} at {box}")
                all_found.add(f"Detected {class_name} with confidence {confidence} at {box}")

        return [list(all_found) if all_found else [],list(nature_found) if nature_found else []]
    except Exception as e:
        return [[],[]]



def process_pdf_files(pdfFolderPath, imageFolderPath, outputFolder,extract_cover_only,method='PYMUPDF'):
    """Iterate over PDF files in the specified folder, create an output folder, 
    and execute the corresponding extraction method.
    """
    all_data_pymupdf=[]
     
    if not os.path.isdir(pdfFolderPath):
        print(f"Error: PDF folder ({pdfFolderPath}) does not exist!")
        return
    selected_files = select_pdfs_by_sector_and_years()
    

    for file in os.listdir(pdfFolderPath):
        file_path = os.path.join(pdfFolderPath, file)


        if os.path.isfile(file_path) and file.endswith(".pdf") :
            
        
           pdf_name = file.replace(".pdf", "")
           if pdf_name not in selected_files:
            continue 
           
           if not is_pdf_valid(file_path):
              continue 
           
           sector=selected_files[pdf_name][0]
           Size=selected_files[pdf_name][1]
           Organization_type=selected_files[pdf_name][2]
           Sec_SASB=selected_files[pdf_name][3]
           Region=selected_files[pdf_name][4]
           Country=selected_files[pdf_name][5]
           OECD=selected_files[pdf_name][6]
           english_non_english=selected_files[pdf_name][7]  
           output_path_pymupdf = Path(os.path.join(imageFolderPath,'pymupdf' if method=='PYMUPDF' else "opencv", file))
           output_path_pymupdf.mkdir(parents=True, exist_ok=True)
           
           if(method=='PYMUPDF'):
              images = extract_images_pymupdf(file_path, output_path_pymupdf,extract_cover_only)
           else:
              images = extract_images_opencv(file_path, output_path_pymupdf,extract_cover_only)
               
    
           for company, year,image_path,title,author,creationDate,creator,modDate,subject,keywords,pdfLanguage in images :
                r, g, b = get_rgb_percentage(image_path)

               # detected_bject,detected_nature_obj=get_detect_nature_objects(image_path)
                
                all_data_pymupdf.append([company, year,sector,Size,Organization_type,Sec_SASB,Region,Country,OECD,english_non_english ,str(image_path),
                                         title,author,creationDate,creator,modDate,subject,keywords,pdfLanguage 
                                         , r, g, b
                                        #  ,
                                        #  ','.join(detected_bject) if detected_bject is not None or len(detected_bject)==0  else '', 
                                        #  ','.join(detected_nature_obj) if detected_nature_obj is not None or len(detected_nature_obj)==0  else '', 
                                        #  len(detected_nature_obj) if detected_nature_obj is not None else 0
                                         ])
           
    file_path_pymupdf= os.path.join(outputFolder, "pymupdf" if method=="PYMUPDF" else "opencv","output.xlsx")
    output_path_pymupdf = Path(os.path.join(outputFolder, "pymupdf" if method=="PYMUPDF" else "opencv"))
    output_path_pymupdf.mkdir(parents=True, exist_ok=True)
    add_to_excel_data_frame(all_data_pymupdf,file_path_pymupdf)

    

process_pdf_files(PDF_FOLDER_PATH,IMAGE_FOLDER_PATH,EXCEL_OUTPUT_FOLDER_PATH ,True,"OPENCV")
# detected_bject,nature_object=get_detect_nature_objects("sample_dataSet/images/pymupdf/ChinaResourcesCementlHoldingsLimited_2014.pdf/ChinaResourcesCementlHoldingsLimited_2014_page1_img1.jpeg")

# print(detected_bject)
# print(nature_object)