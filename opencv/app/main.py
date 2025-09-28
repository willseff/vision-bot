from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import io
import os

app = FastAPI(title="OpenCV Super-Resolution API", description="API for upscaling images using OpenCV's EDSR model")

# Initialize super-resolution model
sr = cv2.dnn_superres.DnnSuperResImpl_create()

# Model paths - will be downloaded in Dockerfile
MODEL_DIR = "/app/models"
EDSR_X2 = os.path.join(MODEL_DIR, "EDSR_x2.pb")
EDSR_X3 = os.path.join(MODEL_DIR, "EDSR_x3.pb")
EDSR_X4 = os.path.join(MODEL_DIR, "EDSR_x4.pb")

@app.on_event("startup")
async def startup_event():
    """Load the super-resolution models on startup"""
    try:
        if os.path.exists(EDSR_X2):
            sr.readModel(EDSR_X2)
            sr.setModel("edsr", 2)
            print("EDSR x2 model loaded successfully")
        else:
            print(f"Warning: Model file {EDSR_X2} not found")
    except Exception as e:
        print(f"Error loading model: {e}")

@app.post("/upscale")
async def upscale_image(
    file: UploadFile = File(...),
    scale: int = 2
):
    """
    Upscale an uploaded image using FSRCNN model.

    - **file**: Image file to upscale (JPEG, PNG, etc.)
    - **scale**: Upscaling factor (2, 3, or 4)
    """
    if scale not in [2, 3, 4]:
        raise HTTPException(status_code=400, detail="Scale must be 2, 3, or 4")

    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Load appropriate model
        model_path = {
            2: EDSR_X2,
            3: EDSR_X3,
            4: EDSR_X4
        }.get(scale)

        if not os.path.exists(model_path):
            raise HTTPException(status_code=500, detail=f"Model for scale {scale}x not available")

        sr.readModel(model_path)
        sr.setModel("edsr", scale)

        # Upscale image
        upscaled = sr.upsample(img)

        # Encode as PNG
        success, encoded_img = cv2.imencode('.png', upscaled)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to encode upscaled image")

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(encoded_img.tobytes()),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=upscaled_{scale}x.png"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "OpenCV Super-Resolution API", "status": "running"}

@app.get("/models")
async def list_models():
    """Check which models are available"""
    models = {}
    for scale, path in [(2, EDSR_X2), (3, EDSR_X3), (4, EDSR_X4)]:
        models[f"{scale}x"] = os.path.exists(path)
    return models