from app.utils.image_utils import detect_plaque

class ImageProcessingService:
    @staticmethod
    def process_image(image_path):
        plaque_score, processed_image_path, message = detect_plaque(image_path)
        return {
            "message": message,
            "plaque_score": plaque_score,
            "processed_image_path": processed_image_path
        }