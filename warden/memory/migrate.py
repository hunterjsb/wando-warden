import json
from datetime import datetime
import pytz
import boto3
from decimal import Decimal


def convert_est_to_utc_timestamp(est_timestamp_str):
    est_tz = pytz.timezone('America/New_York')  # EST timezone
    # Remove '_approx' from the timestamp string if present
    est_timestamp_str = est_timestamp_str.replace('_approx', '')
    est_datetime = datetime.strptime(est_timestamp_str, '%Y-%m-%d_%H:%M:%S')
    est_datetime = est_tz.localize(est_datetime)  # Localize the datetime to EST
    utc_datetime = est_datetime.astimezone(pytz.UTC)  # Convert to UTC
    return int(utc_datetime.timestamp() * 1000)  # Convert to milliseconds


# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('ww_truck_detections')

# Read the JSON data
with open('truck_detections.txt', 'r') as file:
    data = json.load(file)

# Insert each item into DynamoDB
for item in data:
    timestamp = item['timestamp']
    ts_approx = '_approx' in timestamp
    utc_timestamp = convert_est_to_utc_timestamp(timestamp)

    dynamodb_item = {
        'camera_name': item['camera_name'],
        'timestamp': utc_timestamp,
        'truck_count': item['truck_count'],
        'avg_confidence': Decimal(str(item['avg_confidence'])),
        'ts_approx': ts_approx
    }

    table.put_item(Item=dynamodb_item)
    print(f"Inserted item: {item['camera_name']} at {utc_timestamp}")

print("All items inserted successfully!")
