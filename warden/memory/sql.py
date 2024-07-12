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
                    timestamp INTEGER,
                    truck_count INTEGER,
                    avg_confidence REAL,
                    ts_approx BOOLEAN
                )
            ''')

    def save(self, obj: Tuple[int, float], name: str) -> None:
        ts_approx = name.endswith('_approx')
        camera_name, timestamp = name.split('|')
        truck_count, avg_confidence = obj
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO truck_detections (camera_name, timestamp, truck_count, avg_confidence, ts_approx)
                VALUES (?, ?, ?, ?, ?)
            ''', (camera_name, int(timestamp), truck_count, avg_confidence, ts_approx))

    def load(self, name: str) -> Tuple[int, float, bool]:
        camera_name, timestamp = name.split('|')
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT truck_count, avg_confidence, ts_approx FROM truck_detections
                WHERE camera_name = ? AND timestamp = ?
            ''', (camera_name, int(timestamp)))
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
                    timestamp BIGINT,
                    truck_count INT,
                    avg_confidence FLOAT,
                    ts_approx BOOLEAN
                )
            ''')

    def save(self, obj: Tuple[int, float], name: str) -> None:
        ts_approx = name.endswith('_approx')
        camera_name, timestamp = name.split('|')
        truck_count, avg_confidence = obj
        with mysql.connector.connect(**self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO truck_detections (camera_name, timestamp, truck_count, avg_confidence, ts_approx)
                VALUES (%s, %s, %s, %s, %s)
            ''', (camera_name, int(timestamp), truck_count, avg_confidence, ts_approx))
            conn.commit()

    def load(self, name: str):
        camera_name, timestamp = name.split('|')
        with mysql.connector.connect(**self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT truck_count, avg_confidence, ts_approx FROM truck_detections
                WHERE camera_name = %s AND timestamp = %s
            ''', (camera_name, int(timestamp)))
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
                    timestamp BIGINT,
                    truck_count INTEGER,
                    avg_confidence REAL,
                    ts_approx BOOLEAN
                )
            ''')

    def save(self, obj: Tuple[int, float], name: str) -> None:
        ts_approx = name.endswith('_approx')
        camera_name, timestamp = name.split('|')
        truck_count, avg_confidence = obj
        with psycopg2.connect(self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO truck_detections (camera_name, timestamp, truck_count, avg_confidence, ts_approx)
                VALUES (%s, %s, %s, %s, %s)
            ''', (camera_name, int(timestamp), truck_count, avg_confidence, ts_approx))

    def load(self, name: str) -> Tuple[int, float, bool]:
        camera_name, timestamp = name.split('|')
        with psycopg2.connect(self.config) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT truck_count, avg_confidence, ts_approx FROM truck_detections
                WHERE camera_name = %s AND timestamp = %s
            ''', (camera_name, int(timestamp)))
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
        camera_name, timestamp, approx = name.split('|')
        ts_approx = approx == 'true'
        truck_count, avg_confidence = obj
        self.table.put_item(
            Item={
                'camera_name': camera_name,
                'timestamp': int(timestamp),  # Convert to int
                'truck_count': truck_count,
                'avg_confidence': Decimal(f"{avg_confidence:.2f}"),
                'ts_approx': ts_approx
            }
        )

    def load(self, name: str) -> Tuple[int, float, bool]:  # Return type updated
        camera_name, timestamp = name.split('|')
        response = self.table.get_item(
            Key={
                'camera_name': camera_name,
                'timestamp': int(timestamp)  # Convert to int
            }
        )
        if 'Item' not in response:
            raise KeyError(f"No data found for {name}")
        item = response['Item']
        return item['truck_count'], item['avg_confidence'], item['ts_approx']
