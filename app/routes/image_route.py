from flask import Blueprint, jsonify
from flasgger import swag_from
from app.middlewares.upload_middleware import handle_file_upload
from app.services.image_processing_service import ImageProcessingService
from app.services.cloudinary_service import CloudinaryService
import os
import cv2

image_route = Blueprint("image_route", __name__)

@image_route.route("/api/detect-plaque", methods=["POST"])
@swag_from({
    "parameters": [
        {
            "name": "file",
            "in": "formData",
            "type": "file",
            "required": True,
            "description": "The image file to be uploaded"
        }
    ],
    "responses": {
        200: {
            "description": "Plaque detection results",
            "examples": {
                "application/json": {
                    "message": "Severe Calcification",
                    "plaque_score": 85.0,
                    "original_image_url": "http://example.com/original.png",
                    "processed_image_url": "http://example.com/processed.png",
                }
            }
        },
        400: {
            "description": "Invalid input",
            "examples": {
                "application/json": {
                    "error": "No file uploaded"
                }
            }
        },
        500: {
            "description": "Internal server error",
            "examples": {
                "application/json": {
                    "error": "Failed to upload original image"
                }
            }
        }
    }
})
def detect_plaque():
    image, error = handle_file_upload()
    if error:
        return jsonify({"error": error}), 400
    
    # Upload original image to Cloudinary
    # Convert image to bytes for Cloudinary upload
    _, buffer = cv2.imencode(".png", image)
    original_image_bytes = buffer.tobytes()
    original_image_url = CloudinaryService.upload_original_image(original_image_bytes)
    if not original_image_url:
        return jsonify({"error": "Failed to upload original image"}), 500

    # Process the image
    result = ImageProcessingService.process_image(image)
    
    # Upload processed image to Cloudinary
    processed_image_url = CloudinaryService.upload_processed_image(result["processed_image_bytes"])
    if not processed_image_url:
        return jsonify({"error": "Failed to upload processed image"}), 500

    return jsonify({
        "message": result["message"],
        "plaque_score": result["plaque_score"],
        "original_image_url": original_image_url,
        "processed_image_url": processed_image_url
    })

@image_route.route("/api/get/processed-image/<image_id>", methods=["GET"])
@swag_from({
     "parameters": [
        {
            "name": "image_id",
            "in": "path",
            "type": "string",
            "required": True,
            "description": "The ID of the processed image"
        }
    ],
    "responses": {
        200: {
            "description": "URL of the processed image",
            "examples": {
                "application/json": {
                    "image_url": "http://example.com/processed_image.png"
                }
            }
        },
        500: {
            "description": "Internal server error",
            "examples": {
                "application/json": {
                    "error": "Error message"
                }
            }
        }
    }
})
def get_processed_image(image_id):
    try:
        # Get the image URL from Cloudinary
        image_url = f"https://res.cloudinary.com/{os.environ.get('CLOUDINARY_CLOUD_NAME')}/image/upload/processed_ct_scans/{image_id}"
        return jsonify({"image_url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500