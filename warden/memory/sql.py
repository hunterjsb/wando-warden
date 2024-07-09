from typing import Tuple
from decimal import Decimal

import boto3
try:
    import sqlite3
except ImportError:
    sqlite3 = None
import mysql.connector
import psycopg2

from warden.memory.base import DatabaseMemory, Memory


class SQLiteMemory(DatabaseMemory):
    import_failed = sqlite3 is None

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS truck_detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    camera_name TEXT,
                    timestamp TEXT,
                    truck_count INTEGER,
                    avg_confidence REAL
                )
            ''')

    def save(self, obj: Tuple[int, float], name: str) -> None:
        camera_name, timestamp = name.split('|')
        truck_count, avg_confidence = obj
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO truck_detections (camera_name, timestamp, truck_count, avg_confidence)
                VALUES (?, ?, ?, ?)
            ''', (camera_name, timestamp, truck_count, avg_confidence))

    def load(self, name: str) -> Tuple[int, float]:
        camera_name, timestamp = name.split('|')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT truck_count, avg_confidence FROM truck_detections
                WHERE camera_name = ? AND timestamp = ?
            ''', (camera_name, timestamp))
            result = cursor.fetchone()
        if result is None:
            raise KeyError(f"No data found for {name}")
        return result


class MySQLMemory(DatabaseMemory):
    def __init__(self, host: str, user: str, password: str, database: str):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self._create_table()

    def _create_table(self):
        with mysql.connector.connect(**self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS truck_detections (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    camera_name VARCHAR(255),
                    timestamp VARCHAR(255),
                    truck_count INT,
                    avg_confidence FLOAT
                )
            ''')

    def save(self, obj: Tuple[int, float], name: str) -> None:
        camera_name, timestamp = name.split('|')
        truck_count, avg_confidence = obj
        with mysql.connector.connect(**self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO truck_detections (camera_name, timestamp, truck_count, avg_confidence)
                VALUES (%s, %s, %s, %s)
            ''', (camera_name, timestamp, truck_count, avg_confidence))
            conn.commit()

    def load(self, name: str) -> Tuple[int, float]:
        camera_name, timestamp = name.split('|')
        with mysql.connector.connect(**self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT truck_count, avg_confidence FROM truck_detections
                WHERE camera_name = %s AND timestamp = %s
            ''', (camera_name, timestamp))
            result = cursor.fetchone()
        if result is None:
            raise KeyError(f"No data found for {name}")
        return result


class PostgreSQLMemory(DatabaseMemory):
    def __init__(self, host: str, user: str, password: str, database: str):
        self.config = f"host={host} user={user} password={password} dbname={database}"
        self._create_table()

    def _create_table(self):
        with psycopg2.connect(self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS truck_detections (
                    id SERIAL PRIMARY KEY,
                    camera_name TEXT,
                    timestamp TEXT,
                    truck_count INTEGER,
                    avg_confidence REAL
                )
            ''')

    def save(self, obj: Tuple[int, float], name: str) -> None:
        camera_name, timestamp = name.split('|')
        truck_count, avg_confidence = obj
        with psycopg2.connect(self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO truck_detections (camera_name, timestamp, truck_count, avg_confidence)
                VALUES (%s, %s, %s, %s)
            ''', (camera_name, timestamp, truck_count, avg_confidence))

    def load(self, name: str) -> Tuple[int, float]:
        camera_name, timestamp = name.split('|')
        with psycopg2.connect(self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT truck_count, avg_confidence FROM truck_detections
                WHERE camera_name = %s AND timestamp = %s
            ''', (camera_name, timestamp))
            result = cursor.fetchone()
        if result is None:
            raise KeyError(f"No data found for {name}")
        return result


class DynamoDBMemory(Memory[Tuple[int, float]]):
    def __init__(self, table_name: str, region_name: str):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)

    def save(self, obj: Tuple[int, float], name: str) -> None:
        camera_name, timestamp = name.split('|')
        truck_count, avg_confidence = obj
        self.table.put_item(
            Item={
                'camera_name': camera_name,
                'timestamp': timestamp,
                'truck_count': truck_count,
                'avg_confidence': Decimal(f"{avg_confidence:.2f}")
            }
        )

    def load(self, name: str) -> Tuple[int, float]:  # might be Decimal
        camera_name, timestamp = name.split('|')
        response = self.table.get_item(
            Key={
                'camera_name': camera_name,
                'timestamp': timestamp
            }
        )
        if 'Item' not in response:
            raise KeyError(f"No data found for {name}")
        item = response['Item']
        return item['truck_count'], item['avg_confidence']
