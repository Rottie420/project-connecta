import os
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from Logger import Logger

class FileHandler:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def save_and_convert_image(file, control_number):
        filename = secure_filename(file.filename)
        unique_filename = f"{control_number}_{filename}"
        original_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        file.save(original_path)
        
        # Convert to WEBP format
        webp_filename = f"{control_number}.webp"
        webp_path = os.path.join(UPLOAD_FOLDER, webp_filename)
        
        try:
            # Open the image and handle orientation
            with Image.open(original_path) as img:
                img = ImageOps.exif_transpose(img)  # Correct the orientation using EXIF data
                img.save(webp_path, 'WEBP')
        except Exception as e:
            Logger.log(f"Image conversion error for {filename}: {e}")
            raise
        finally:
            # Ensure the original file is deleted safely
            if os.path.exists(original_path):
                try:
                    os.remove(original_path)
                except Exception as e:
                    Logger.log(f"Error deleting original file {filename}: {e}")
                    raise
        return f"{UPLOAD_FOLDER}/{webp_filename}"
