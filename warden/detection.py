from typing import Tuple

import boto3


def detect_trucks(photo: str, bucket: str, max_labels=40) -> Tuple[int, float]:
    client = boto3.client('rekognition', region_name='us-east-1')
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MaxLabels=max_labels,
        Features=["GENERAL_LABELS", "IMAGE_PROPERTIES"],
        Settings={"GeneralLabels": {"LabelInclusionFilters": ["Truck"]}}
    )

    trucks = response['Labels'][0]
    truck_count = len(trucks['Instances'])
    avg_confidence = sum(instance['Confidence'] for instance in trucks['Instances']) / truck_count if truck_count > 0 else 0

    return truck_count, avg_confidence


if __name__ == '__main__':
    tc, ac = detect_trucks('wando_welch_main_gate_2024-07-09_14:17:10.jpg', 'wando-warden')
    print(f'trucks: {tc} | avg. conf. {ac:.2f}')
