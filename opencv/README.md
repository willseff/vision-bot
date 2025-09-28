# OpenCV Super-Resolution API

A FastAPI application that provides image upscaling using OpenCV's EDSR super-resolution models.

## Features

- REST API for image upscaling
- Supports 2x, 3x, and 4x upscaling using FSRCNN model
- Accepts image uploads (JPEG, PNG, etc.)
- Returns upscaled images as PNG
- Health check endpoint
- Model availability check

## API Endpoints

### POST /upscale
Upscale an uploaded image.

**Parameters:**
- `file`: Image file to upscale
- `scale`: Upscaling factor (2, 3, or 4) - defaults to 2

**Example usage:**
```bash
curl -X POST "http://localhost:8000/upscale" \
     -H "accept: image/png" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@image.jpg" \
     -F "scale=2" \
     --output upscaled.png
```

### GET /
Health check endpoint.

### GET /models
Check which upscaling models are available.

## Local Development

1. Build the Docker image:
```bash
docker build -f Dockerfile.cpu -t opencv-superres:cpu .
```

2. Run the container:
```bash
docker run -p 8000:8000 opencv-superres:cpu
```

3. Test the API:
```bash
curl http://localhost:8000/
```

## Deployment to Azure Container Apps

### Prerequisites
- Azure CLI installed
- Logged in to Azure (`az login`)
- Azure Container Apps extension (`az extension add --name containerapp`)

### Deploy

1. Create a resource group (if not exists):
```bash
az group create --name my-resource-group --location eastus
```

2. Create an Azure Container Registry (ACR):
```bash
az acr create --resource-group my-resource-group --name myacr --sku Basic
```

3. Build and push the image:
```bash
az acr build --registry myacr --image opencv-superres:v1 .
```

4. Create the Container App:
```bash
az containerapp create \
  --name opencv-superres \
  --resource-group my-resource-group \
  --image myacr.azurecr.io/opencv-superres:v1 \
  --target-port 8000 \
  --ingress external \
  --query properties.configuration.ingress.fqdn
```

The command will output the FQDN of your deployed app.

### Using Azure Developer CLI (azd)

If you prefer using azd for infrastructure as code:

1. Initialize azd in the project:
```bash
azd init
```

2. Create infrastructure files (you may need to adapt these):
   - Create `infra/main.bicep` for the container app infrastructure
   - Create `azure.yaml` for azd configuration

3. Deploy:
```bash
azd up
```

## Model Information

The application uses EDSR (Enhanced Deep Super-Resolution) models:
- EDSR_x2.pb: 2x upscaling
- EDSR_x3.pb: 3x upscaling
- EDSR_x4.pb: 4x upscaling

Models are automatically downloaded during Docker build from the official EDSR repository.

## Performance Notes

- EDSR provides higher quality upscaling than FSRCNN but is slower
- Processing time depends on image size and scale factor
- CPU-only implementation (no GPU acceleration)