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


def s3_jpg():
    from warden.memory import S3PhotoMemory
    from PIL import Image

    # Initialize the S3PhotoMemory
    s3_memory = S3PhotoMemory('wando-warden', region_name='us-east-1')

    # Save an image
    image = Image.open('example.jpg')
    s3_memory.save(image, 'example.jpg')

    # Load an image
    loaded_image = s3_memory.load('peep.jpg')
    loaded_image.show()


def dynamo_results():
    from warden.memory import DynamoDBMemory

    memory = DynamoDBMemory('truck_detections', 'us-east-1')

    # Test saving
    memory.save((5, 0.95), 'camera1|2023-05-01_12:00:00')
    memory.save((3, 0.87), 'camera2|2023-05-01_13:00:00')

    # Test loading
    try:
        result1 = memory.load('camera1|2023-05-01_12:00:00')
        print(f"Loaded data for camera1: {result1}")
    except KeyError as e:
        print(str(e))

    try:
        result2 = memory.load('camera2|2023-05-01_13:00:00')
        print(f"Loaded data for camera2: {result2}")
    except KeyError as e:
        print(str(e))

    # Test loading non-existent item
    try:
        memory.load('camera3|2023-05-01_14:00:00')
    except KeyError as e:
        print(str(e))


if __name__ == '__main__':
    dynamo_results()
