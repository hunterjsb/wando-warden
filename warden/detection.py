import boto3


def detect_labels(photo, bucket):
    client = boto3.client('rekognition', region_name='us-east-1')
    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                    MaxLabels=10,
                                    # Uncomment to use image properties and filtration settings
                                    #Features=["GENERAL_LABELS", "IMAGE_PROPERTIES"],
                                    #Settings={"GeneralLabels": {"LabelInclusionFilters":["Cat"]},
                                    # "ImageProperties": {"MaxDominantColors":10}}
                                    )

    print('Detected labels for ' + photo)
    print()
    for label in response['Labels']:
        print("Label: " + label['Name'])
        print("Confidence: " + str(label['Confidence']))
        print("Instances:")

        for instance in label['Instances']:
            print(" Bounding box")
            print(" Top: " + str(instance['BoundingBox']['Top']))
            print(" Left: " + str(instance['BoundingBox']['Left']))
            print(" Width: " + str(instance['BoundingBox']['Width']))
            print(" Height: " + str(instance['BoundingBox']['Height']))
            print(" Confidence: " + str(instance['Confidence']))
            print()

        print("Parents:")
        for parent in label['Parents']:
            print(" " + parent['Name'])

        print("Aliases:")
        for alias in label['Aliases']:
            print(" " + alias['Name'])

            print("Categories:")
        for category in label['Categories']:
            print(" " + category['Name'])
            print("----------")
            print()

    if "ImageProperties" in str(response):
        print("Background:")
        print(response["ImageProperties"]["Background"])
        print()
        print("Foreground:")
        print(response["ImageProperties"]["Foreground"])
        print()
        print("Quality:")
        print(response["ImageProperties"]["Quality"])
        print()

    return len(response['Labels'])


def main():
    photo = 'example.jpg'
    bucket = 'wando-warden'
    label_count = detect_labels(photo, bucket)
    print("Labels detected: " + str(label_count))


if __name__ == "__main__":
    main()
