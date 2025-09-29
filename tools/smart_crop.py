import os
import base64
import json
from io import BytesIO
from PIL import Image
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.imageanalysis.models import VisualFeatures

from config.settings import Config

endpoint = Config.VISION_STUDIO_ENDPOINT
key = Config.VISION_STUDIO_KEY

client = ImageAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

def smart_crop_image(aspect_ratios: list[float] = None) -> str:
    """
    Analyze the uploaded image and return smart crop suggestions.
    Uses synchronous Azure client for compatibility with Streamlit.
    
    Args:
        aspect_ratios: List of aspect ratios for smart cropping (default: [0.9, 1.33])
    
    Returns:
        JSON string containing smart crop results and metadata
    """
    import streamlit as st
    
    # Get image data from session state
    image_data_b64 = getattr(st.session_state, 'uploaded_image_data', None)
    if not image_data_b64:
        return json.dumps({"error": "No image data available. Please upload an image first."})
    
    if aspect_ratios is None:
        aspect_ratios_local = [0.9, 1.33]
    else:
        aspect_ratios_local = aspect_ratios
    
    # Decode base64 string to bytes
    try:
        image_bytes = base64.b64decode(image_data_b64)
    except Exception as e:
        return json.dumps({"error": f"Failed to decode base64 image data: {str(e)}"})
    
    visual_features = [VisualFeatures.SMART_CROPS]
    
    try:
        # Use synchronous client for Streamlit compatibility
        result = client.analyze(
            image_data=image_bytes,
            visual_features=visual_features,
            smart_crops_aspect_ratios=aspect_ratios_local,
            gender_neutral_caption=True,
            language="en"
        )
    except Exception as e:
        return json.dumps({"error": f"Failed to analyze image: {str(e)}"})
    
    smart_crops = []
    if result.smart_crops is not None:
        for smart_crop in result.smart_crops.list:
            smart_crops.append({
                "aspect_ratio": smart_crop.aspect_ratio,
                "bounding_box": {
                    "x": smart_crop.bounding_box["x"],
                    "y": smart_crop.bounding_box["y"],
                    "w": smart_crop.bounding_box["w"],
                    "h": smart_crop.bounding_box["h"]
                }
            })
    
    return json.dumps({
        "smart_crops": smart_crops,
        "image_height": result.metadata.height,
        "image_width": result.metadata.width,
        "model_version": result.model_version
    })


def crop_image(x: int, y: int, width: int, height: int) -> str:
    """
    Crop the uploaded image using the specified bounding box coordinates.
    
    Args:
        x: X coordinate of the top-left corner
        y: Y coordinate of the top-left corner  
        width: Width of the crop area
        height: Height of the crop area
    
    Returns:
        JSON string containing the cropped image as base64 and metadata
    """
    import streamlit as st
    
    # Get image data from session state
    image_data_b64 = getattr(st.session_state, 'uploaded_image_data', None)
    if not image_data_b64:
        return json.dumps({"error": "No image data available. Please upload an image first."})
    
    try:
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_data_b64)
        
        # Open image with PIL
        image = Image.open(BytesIO(image_bytes))
        
        # Crop the image
        cropped_image = image.crop((x, y, x + width, y + height))
        
        # Convert back to bytes
        output_buffer = BytesIO()
        cropped_image.save(output_buffer, format=image.format or 'JPEG')
        cropped_bytes = output_buffer.getvalue()
        
        # Encode as base64
        cropped_b64 = base64.b64encode(cropped_bytes).decode('utf-8')
        
        return json.dumps({
            "success": True,
            "cropped_image_b64": cropped_b64,
            "crop_coordinates": {"x": x, "y": y, "width": width, "height": height},
            "original_size": {"width": image.width, "height": image.height},
            "cropped_size": {"width": cropped_image.width, "height": cropped_image.height},
            "format": image.format or 'JPEG'
        })
        
    except Exception as e:
        return json.dumps({"error": f"Failed to crop image: {str(e)}"})