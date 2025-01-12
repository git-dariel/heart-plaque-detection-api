from flask import Blueprint, jsonify, request
from app.middlewares.upload_middleware import handle_file_upload
from app.services.image_processing_service import ImageProcessingService
from app.services.cloudinary_service import CloudinaryService
import os

image_route = Blueprint("image_route", __name__)

@image_route.route("/api/detect-plaque", methods=["POST"])
def detect_plaque():
    file_path, error = handle_file_upload()
    if error:
        return jsonify({"error": error}), 400
    
    # Upload original image to Cloudinary
    original_image_url = CloudinaryService.upload_original_image(file_path)
    if not original_image_url:
        return jsonify({"error": "Failed to upload original image"}), 500

    # Process the image
    result = ImageProcessingService.process_image(file_path)
    
    # Upload processed image to Cloudinary
    processed_image_url = CloudinaryService.upload_processed_image(result["processed_image_path"])
    if not processed_image_url:
        return jsonify({"error": "Failed to upload processed image"}), 500

    return jsonify({
        "message": result["message"],
        "plaque_score": result["plaque_score"],
        "original_image_url": original_image_url,
        "processed_image_url": processed_image_url
    })

@image_route.route("/api/get/processed-image/<image_id>", methods=["GET"])
def get_processed_image(image_id):
    try:
        # Get the image URL from Cloudinary
        image_url = f"https://res.cloudinary.com/{os.environ.get('CLOUDINARY_CLOUD_NAME')}/image/upload/processed_ct_scans/{image_id}"
        return jsonify({"image_url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500