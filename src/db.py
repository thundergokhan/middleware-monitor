import sqlite3
import time
import os
from src.utils.logger import get_logger

DB_NAME = 'monitor.db'

class Database:
    def __init__(self):
        self.logger = get_logger("Database")
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(DB_NAME)

    def _init_db(self):
        """
        Initialize the database schema if it doesn't exist.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL,
                    status INTEGER NOT NULL,
                    response_time REAL NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")

    def save_result(self, result):
        """
        Save a single health check result.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO history (service_name, status, response_time, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                result['name'],
                1 if result['status'] else 0,
                result['response_time'],
                result['timestamp']
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to save result for {result.get('name')}: {e}")

    def get_history(self, service_name, limit=20):
        """
        Retrieve history for a specific service.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT status, response_time, timestamp 
                FROM history 
                WHERE service_name = ? 
                ORDER BY timestamp ASC
            ''', (service_name,))
            
            # Fetch all and slice locally or use subquery for strict "last N" in correct order
            # Simple approach: Fetch all matching (might be large over time, but okay for demo), 
            # or better: SELECT ... ORDER BY timestamp DESC LIMIT ? then reverse in code.
            
            rows = cursor.fetchall() # Get everything for the graph to be full
            conn.close()
            
            # If we want only the last 'limit' points:
            if len(rows) > limit:
                rows = rows[-limit:]
                
            history = []
            for row in rows:
                history.append({
                    "status": bool(row[0]),
                    "response_time": row[1],
                    "timestamp": row[2]
                })
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get history for {service_name}: {e}")
            return []
