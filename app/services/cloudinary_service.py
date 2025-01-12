import cloudinary.uploader
from flask import current_app
import os

class CloudinaryService:
    @staticmethod
    def upload_image(file_path, folder):
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                resource_type="image"
            )
            return result["secure_url"]
        except Exception as e:
            current_app.logger.error(f"Error uploading image to Cloudinary: {str(e)}")
            return None
    
    @staticmethod
    def upload_original_image(file_path):
        return CloudinaryService.upload_image(file_path, "original_ct_scans")

    @staticmethod
    def upload_processed_image(file_path):
        return CloudinaryService.upload_image(file_path, "processed_ct_scans")