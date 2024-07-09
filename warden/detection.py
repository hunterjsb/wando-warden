from typing import Tuple

import boto3


def detect_trucks(photo: str, bucket: str) -> Tuple[int, float]:
    client = boto3.client('rekognition', region_name='us-east-1')
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MaxLabels=30,
        Features=["GENERAL_LABELS", "IMAGE_PROPERTIES"],
        Settings={"GeneralLabels": {"LabelInclusionFilters": ["Truck"]}}
    )

    truck_instances = []
    for label in response['Labels']:
        if label['Name'].lower() in ['truck', 'vehicle']:
            truck_instances.extend(label['Instances'])

    truck_count = len(truck_instances)
    avg_confidence = sum(instance['Confidence'] for instance in truck_instances) / truck_count if truck_count > 0 else 0

    return truck_count, avg_confidence
