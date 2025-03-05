from pathlib import Path
import os
def ensure_directory_exists(directory):
        Path(directory).mkdir(parents=True, exist_ok=True)

def is_dir(folder_path):
      return   os.path.isdir(folder_path)

def get_file_path(folder_path,file_path):
   return os.path.join(folder_path, file_path)

