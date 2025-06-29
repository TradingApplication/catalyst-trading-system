#!/usr/bin/env python3
"""
Name of System: Catalyst Trading System
Name of file: database_utils.py
Version: 1.0.0
Last Updated: 2025-06-29
REVISION HISTORY:
  - v1.0.0 (2025-06-29) - Basic database utilities

Purpose: Shared database utilities for all services
"""

import sqlite3
import os
from typing import Optional, Dict, Any

class DatabaseServiceMixin:
    """
    Mixin class providing database functionality to services
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        self.db_path = db_path or os.environ.get(
            'DATABASE_PATH', 
            '/tmp//tmp/trading_system.db'  # Use /tmp for DigitalOcean App Platform
        )
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount