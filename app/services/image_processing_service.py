from app.utils.image_utils import detect_plaque

class ImageProcessingService:
    @staticmethod
    def process_image(image):
        plaque_score, processed_image_bytes, message = detect_plaque(image)
        return {
            "message": message,
            "plaque_score": plaque_score,
            "processed_image_bytes": processed_image_bytes
        }