def local_jpg():
    """Saves a red square to ../images and tried to load a non-existent photo to show error handling"""
    from warden.memory import LocalPhotoMemory
    from PIL import Image

    # Create a sample image
    sample_image = Image.new('RGB', (100, 100), color='red')

    # Initialize the LocalPhotoMemory
    photo_memory = LocalPhotoMemory("../images")
    photo_memory.save(sample_image, "red_square")
    loaded_image = photo_memory.load("red_square.jpg")
    loaded_image.show()

    # You can also try loading a non-existent image to see the error handling
    try:
        photo_memory.load("non_existent.jpg")
    except FileNotFoundError as e:
        print(f"Error: {e}")
