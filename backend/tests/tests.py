from PIL import Image
from io import BytesIO
from src.main import open_image, create_thumbnail

test_image = "./tests/S2L2A_2022-06-09.tiff"

# Create a BytesIO object for testing
def create_test_image():
    with open(test_image, "rb") as f:
        return BytesIO(f.read())

# Test case for the get_image_attributes endpoint
def test_get_image_attributes():
    test_image = create_test_image()
    response = open_image(test_image)
    data = response.model_dump_json()
    assert "width" in data
    assert "height" in data
    assert "bands" in data
    assert "coordinate_reference_system" in data
    assert "bounding_box" in data

# Test case for the get_thumbnail endpoint
def test_get_thumbnail():
    test_image = create_test_image()
    resolution = 50
    response = create_thumbnail(test_image, resolution)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    thumbnail_data = response.body
    img = Image.open(BytesIO(thumbnail_data))
    assert resolution in img.size 
