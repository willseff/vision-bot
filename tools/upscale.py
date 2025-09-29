import os
import base64
import json
import requests
import asyncio
from io import BytesIO
from PIL import Image
from typing import Optional

def upscale_image(scale: int = 2) -> str:
    """
    Upscale the uploaded image using the deployed OpenCV service on Azure Container Apps.
    
    Args:
        scale: Upscaling factor (2, 3, or 4, default: 2)
    
    Returns:
        JSON string containing the upscaled image as base64 and metadata
    """
    import streamlit as st
    
    # Validate scale parameter
    if scale not in [2, 3, 4]:
        return json.dumps({"error": "Scale must be 2, 3, or 4"})
    
    # Get image data from session state
    image_data_b64 = getattr(st.session_state, 'uploaded_image_data', None)
    if not image_data_b64:
        return json.dumps({"error": "No image data available. Please upload an image first."})
    
    try:
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_data_b64)
        
        # Open image with PIL to get metadata
        original_image = Image.open(BytesIO(image_bytes))
        original_width, original_height = original_image.size
        original_format = original_image.format or 'JPEG'
        
        # Prepare the image file for upload to the API
        files = {
            'file': ('image.jpg', image_bytes, 'image/jpeg')
        }
        
        # Call the Azure Container Apps endpoint
        api_url = "https://willseff-upscaler.nicerock-8f679d6b.eastus.azurecontainerapps.io/upscale"
        params = {'scale': scale}
        
        response = requests.post(
            api_url,
            files=files,
            params=params,
            timeout=30  # 30 second timeout
        )
        
        if response.status_code != 200:
            return json.dumps({
                "error": f"API request failed with status {response.status_code}: {response.text}"
            })
        
        # Get the upscaled image bytes
        upscaled_bytes = response.content
        
        # Convert to base64 for return
        upscaled_b64 = base64.b64encode(upscaled_bytes).decode('utf-8')
        
        # Calculate expected dimensions
        expected_width = original_width * scale
        expected_height = original_height * scale
        
        return json.dumps({
            "success": True,
            "upscaled_image_b64": upscaled_b64,
            "scale_factor": scale,
            "original_size": {"width": original_width, "height": original_height},
            "upscaled_size": {"width": expected_width, "height": expected_height},
            "original_format": original_format,
            "upscaled_format": "PNG",
            "api_endpoint": api_url
        })
        
    except requests.exceptions.Timeout:
        return json.dumps({"error": "Request timed out. The upscaling process may take longer for large images."})
    except requests.exceptions.ConnectionError:
        return json.dumps({"error": "Failed to connect to the upscaling service. Please check if the service is running."})
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Request failed: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to upscale image: {str(e)}"})



