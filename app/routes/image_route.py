from flask import Blueprint, jsonify, request
from app.middlewares.upload_middleware import handle_file_upload
from app.services.image_processing_service import ImageProcessingService

image_route = Blueprint("image_route", __name__)

@image_route.route("/api/detect-plaque", methods=["POST"])
def detect_plaque():
    file_path, error = handle_file_upload()
    if error:
        return jsonify({"error": error}), 400
    
    result = ImageProcessingService.process_image(file_path)

    return jsonify({
        "message": result["message"],
        "plaque_score": result["plaque_score"],
        "processed_image_path": result["processed_image_path"]
    })