from flask import request
from app.utils.image_utils import save_uploaded_file

def handle_file_upload():
    if "file" not in request.files:
        return None, "No file uploaded"
    file = request.files["file"]
    file_path = save_uploaded_file(file)
    if not file_path:
        return None, "Invalid file type"
    return file_path, None