import boto3


def detect_labels(photo, bucket):
    client = boto3.client('rekognition', region_name='us-east-1')
    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                    MaxLabels=30,
                                    # Uncomment to use image properties and filtration settings
                                    Features=["GENERAL_LABELS", "IMAGE_PROPERTIES"],
                                    Settings={"GeneralLabels": {"LabelInclusionFilters": ["Truck"]}}
                                    # "ImageProperties": {"MaxDominantColors":10}}
                                    )

    print(f'Detected labels for {photo}')
    print(response)

    return len(response['Labels'])


def main():
    photo = 'example.jpg'
    bucket = 'wando-warden'
    label_count = detect_labels(photo, bucket)
    print("Labels detected: " + str(label_count))


if __name__ == "__main__":
    main()
