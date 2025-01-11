import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return file_path
    return None

def detect_plaque(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image could not be loaded.")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Create a copy for heart region detection
    heart_image = gray.copy()
    
    # Apply threshold to separate heart from background
    _, heart_mask = cv2.threshold(heart_image, 50, 255, cv2.THRESH_BINARY)
    
    # Apply morphological operations to clean up heart mask
    kernel = np.ones((5,5), np.uint8)
    heart_mask = cv2.morphologyEx(heart_mask, cv2.MORPH_CLOSE, kernel)
    heart_mask = cv2.morphologyEx(heart_mask, cv2.MORPH_OPEN, kernel)
    
    # Find heart contours
    heart_contours, _ = cv2.findContours(heart_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest contour (assumed to be the heart)
    heart_contour = max(heart_contours, key=cv2.contourArea)
    
    # Create heart region mask
    heart_region = np.zeros_like(gray)
    cv2.drawContours(heart_region, [heart_contour], -1, 255, -1)
    
    # Apply minimal Gaussian blur
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Intensity thresholds for plaque detection
    thresholds = [
        (160, 14),  # High intensity
        (140, 11),  # Medium intensity
        (125, 8)    # Low intensity
    ]
    
    # Initialize detection parameters
    processed_image = image.copy()
    plaque_score = 0
    plaque_count = 0
    total_plaque_area = 0
    processed_regions = np.zeros_like(gray)
    
    def process_contour(contour, min_contrast):
        area = cv2.contourArea(contour)
        if 0.5 < area < 3000:
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            
            # Skip if region already processed
            if cv2.countNonZero(cv2.bitwise_and(processed_regions, mask)) > 0:
                return False, 0, 0
            
            # Extract region properties
            roi = cv2.bitwise_and(blurred, blurred, mask=mask)
            roi_values = roi[roi != 0]
            
            if len(roi_values) > 0:
                mean_intensity = np.mean(roi_values)
                max_intensity = np.max(roi_values)
                std_intensity = np.std(roi_values)
                
                # Analyze surrounding tissue
                x, y, w, h = cv2.boundingRect(contour)
                x1, y1 = max(0, x-3), max(0, y-3)
                x2, y2 = min(gray.shape[1], x+w+3), min(gray.shape[0], y+h+3)
                
                surround_mask = np.zeros_like(gray)
                cv2.rectangle(surround_mask, (x1, y1), (x2, y2), 255, -1)
                cv2.drawContours(surround_mask, [contour], -1, 0, -1)
                
                surround = cv2.bitwise_and(blurred, blurred, mask=surround_mask)
                surround_values = surround[surround != 0]
                
                if len(surround_values) > 0:
                    # Calculate contrast metrics
                    surround_mean = np.mean(surround_values)
                    surround_std = np.std(surround_values)
                    contrast = mean_intensity - surround_mean
                    max_contrast = max_intensity - surround_mean
                    local_variation = std_intensity / (mean_intensity + 1e-6)
                    
                    # Adjust detection parameters based on spot size
                    if area < 1:
                        contrast_multiplier = 0.5
                        variation_threshold = 0.8
                        intensity_boost = 1.2
                    elif area < 2:
                        contrast_multiplier = 0.55
                        variation_threshold = 0.75
                        intensity_boost = 1.18
                    elif area < 3:
                        contrast_multiplier = 0.6
                        variation_threshold = 0.7
                        intensity_boost = 1.15
                    elif area < 5:
                        contrast_multiplier = 0.65
                        variation_threshold = 0.65
                        intensity_boost = 1.12
                    elif area < 10:
                        contrast_multiplier = 0.75
                        variation_threshold = 0.6
                        intensity_boost = 1.08
                    else:
                        contrast_multiplier = 1.0
                        variation_threshold = 0.5
                        intensity_boost = 1.0
                    
                    # Evaluate plaque criteria
                    is_significant_contrast = (contrast > min_contrast * contrast_multiplier and 
                                            max_contrast > min_contrast * 1.02)
                    is_distinct_from_background = (mean_intensity > surround_mean * 1.04 * intensity_boost)
                    is_not_noise = local_variation < variation_threshold
                    is_not_normal_variation = (contrast / surround_std) > 1.4
                    
                    # Adjust contrast requirements based on tissue intensity
                    if surround_mean < 85:
                        min_contrast_multiplier = 1.6
                    elif surround_mean < 100:
                        min_contrast_multiplier = 1.4
                    elif surround_mean < 120:
                        min_contrast_multiplier = 1.2
                    elif surround_mean < 140:
                        min_contrast_multiplier = 1.0
                    else:
                        min_contrast_multiplier = 0.8
                    
                    # Validate intensity levels
                    intensity_valid = True
                    if mean_intensity < 95:
                        intensity_valid = max_contrast > min_contrast * 1.7
                    elif mean_intensity < 110:
                        intensity_valid = max_contrast > min_contrast * 1.5
                    elif mean_intensity < 130:
                        intensity_valid = max_contrast > min_contrast * 1.3
                    elif mean_intensity < 150:
                        intensity_valid = max_contrast > min_contrast * 1.1
                    
                    # Apply additional criteria for bright regions
                    if mean_intensity > 145:
                        intensity_boost *= 1.15
                        if area < 5:
                            contrast_multiplier *= 0.7
                    
                    if area < 5 and mean_intensity > 150:
                        intensity_valid = True
                        min_contrast_multiplier *= 0.7
                    
                    if area < 2 and mean_intensity > 140:
                        intensity_boost *= 1.2
                        contrast_multiplier *= 0.6
                    
                    # Validate plaque detection
                    if (is_significant_contrast and 
                        is_distinct_from_background and 
                        is_not_noise and 
                        is_not_normal_variation and
                        contrast > min_contrast * min_contrast_multiplier and
                        intensity_valid):
                        
                        cv2.drawContours(processed_regions, [contour], -1, 255, -1)
                        return True, area, mean_intensity
        return False, 0, 0
    
    # Process all intensity levels
    for threshold, min_contrast in thresholds:
        _, mask = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)
        mask = cv2.bitwise_and(mask, mask, mask=heart_region)
        
        # Minimal closing to avoid connecting non-plaque regions
        close_kernel = np.ones((2,2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            is_plaque, area, intensity = process_contour(contour, min_contrast)
            if is_plaque:
                plaque_score += area * (intensity / 255.0)
                total_plaque_area += area
                plaque_count += 1
                
                # Calculate circle size
                actual_radius = np.sqrt(area / np.pi)
                (x, y), _ = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                
                # Adjust radius based on size
                if area < 5:  # Very small plaques
                    radius = int(actual_radius * 2.0)  # Reduced padding
                elif area < 10:  # Small plaques
                    radius = int(actual_radius * 1.5)  # Reduced padding
                else:
                    radius = int(actual_radius * 1.2)  # Minimal padding for larger spots
                
                radius = max(radius, 2)
                
                # Adjust line thickness based on radius
                thickness = 1 if radius < 5 else 2
                
                # Draw red circle
                cv2.circle(processed_image, center, radius, (0, 0, 255), thickness)
    
    # Calculate final score based on both size and count
    size_score = min(total_plaque_area / 1000, 100)
    count_score = min(plaque_count * 15, 100)
    plaque_score = max(size_score, count_score)
    
    # Determine the message based on plaque characteristics
    if plaque_count == 0:
        message = "Normal"
    elif plaque_count == 1 and total_plaque_area < 300:
        message = "Moderate Calcification"
    else:
        message = "Severe Calcification"
    
    # Save the processed image
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    processed_image_filename = 'processed_' + os.path.basename(image_path)
    processed_image_path = os.path.join(upload_folder, processed_image_filename)
    cv2.imwrite(processed_image_path, processed_image)
    
    return plaque_score, processed_image_path, message