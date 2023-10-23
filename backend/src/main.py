from fastapi import FastAPI, UploadFile, Query, HTTPException
from fastapi.responses import Response
from PIL import Image
from io import BytesIO
import rasterio
import numpy as np
from pydantic import BaseModel

app = FastAPI()


# Pydantic model for image attributes
class ImageAttributes(BaseModel):
    width: int
    height: int
    bands: int
    coordinate_reference_system: str
    bounding_box: tuple


# Function to open and extract image attributes
def open_image(file):
    try:
        # Open the image file with rasterio
        with rasterio.open(file) as dataset:
            # Close SpooledTemporaryFile to avoid `Bad file descriptor` error
            file.close()

            return ImageAttributes(
                width=dataset.width,
                height=dataset.height,
                bands=dataset.count,
                coordinate_reference_system=dataset.crs.to_string(),
                bounding_box=dataset.bounds,
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Function to create a thumbnail image
def create_thumbnail(file, resolution=100):
    try:
        # Open the image file with rasterio
        with rasterio.open(file) as dataset:
            # Extract the bands for RGB composition
            data = dataset.read([4, 3, 2])
            # Close SpooledTemporaryFile to avoid `Bad file descriptor` error
            file.close()

            # Normalize the data with the Typical Range and convert to 8-bit unsigned integers
            data = (data * (255 / 4000)).astype(np.uint8)
            # Merge the three matrices to a matrix with triplets with values (R,B,G)
            data = np.rec.fromarrays([data[0], data[1], data[2]])

            # Create a Pillow image
            image = Image.fromarray(data, mode="RGB")

            # Create a thumbnail
            image.thumbnail((resolution, resolution))

            # Save the thumbnail to a BytesIO object
            thumbnail_io = BytesIO()
            image.save(thumbnail_io, format="PNG")

        # Return the thumbnail as a response
        return Response(content=thumbnail_io.getvalue(),
                        media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Test route
@app.get(
    "/",
    summary="Root Endpoint",
    description="A simple root endpoint for testing the FastAPI application.")
async def root():
    return {"message": "Hello from FastApi Backend!"}


# Endpoint to get image attributes
@app.post(
    "/attributes",
    summary="Get Image Attributes",
    description=
    "Upload an image file and retrieve its attributes such as width, height, bands, CRS, and bounding box."
)
async def get_image_attributes(image_file: UploadFile):
    return open_image(image_file.file)


# Endpoint to get a thumbnail
@app.post(
    "/thumbnail",
    summary="Get Thumbnail",
    description=
    "Upload an image file and generate a thumbnail with an optional resolution setting."
)
async def get_thumbnail(
    image_file: UploadFile,
    resolution: int = Query(100,
                            description="Thumbnail resolution (pixels).")):
    return create_thumbnail(image_file.file, resolution)
