# src/school_db/db.py
# Database Connection Manager with Dual Mode (Live MySQL and In-Memory SQLite Fallback)

import os
import re
import sqlite3
from typing import Any, List, Tuple, Optional, Dict


class DatabaseManager:
    """Manages database connections, queries, and transactions."""

    def __init__(self, in_memory: bool = False, db_url: Optional[str] = None):
        # Initialize connection settings
        self.in_memory = in_memory
        self.db_url = db_url or os.getenv("DATABASE_URL")
        self._sqlite_conn: Optional[sqlite3.Connection] = None
        self._mysql_conn: Any = None
        self.mode = "sqlite" if (in_memory or not self.db_url) else "mysql"

    def connect(self):
        # Establish connection according to active mode
        if self.mode == "mysql":
            try:
                import pymysql
                # Parse DATABASE_URL or environment variables
                # mysql://user:password@host:port/dbname
                match = re.match(r"mysql://([^:]+):([^@]+)@([^:]+):?(\d+)?/(.+)", self.db_url or "")
                if match:
                    user, password, host, port_str, dbname = match.groups()
                    port = int(port_str) if port_str else 3306
                    self._mysql_conn = pymysql.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=dbname,
                        charset="utf8mb4",
                        autocommit=True
                    )
                else:
                    raise ValueError(f"Invalid DATABASE_URL format: {self.db_url}")
            except Exception as e:
                # Fallback to in-memory mode on connection failure with notification
                print(f"Notice: Live MySQL connection failed ({e}). Falling back to in-memory engine.")
                self.mode = "sqlite"
                self._sqlite_conn = self._init_sqlite_conn()
        else:
            if not self._sqlite_conn:
                self._sqlite_conn = self._init_sqlite_conn()

    def _init_sqlite_conn(self) -> sqlite3.Connection:
        # Initialize SQLite in-memory connection with custom SQL functions
        import datetime
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.create_function("CONCAT", -1, lambda *args: "".join(str(a) for a in args if a is not None))
        conn.create_function("SUBSTRING", 3, lambda s, start, length: s[start - 1 : start - 1 + length] if s else "")
        conn.create_function("CURDATE", 0, lambda: datetime.date.today().isoformat())
        conn.create_function("GREATEST", -1, lambda *args: max(args))
        conn.create_function("LEAST", -1, lambda *args: min(args))

        def _time_to_sec(val):
            if val is None:
                return 0
            if isinstance(val, (int, float)):
                return int(val)
            parts = str(val).split(":")
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2]))
            elif len(parts) == 2:
                return int(parts[0]) * 3600 + int(parts[1]) * 60
            return 0

        def _timediff(t1, t2):
            if t1 is None or t2 is None:
                return 0
            return _time_to_sec(t1) - _time_to_sec(t2)

        conn.create_function("TIME_TO_SEC", 1, _time_to_sec)
        conn.create_function("TIMEDIFF", 2, _timediff)
        return conn

    def close(self):
        # Close active connection
        if self._mysql_conn:
            self._mysql_conn.close()
            self._mysql_conn = None
        if self._sqlite_conn:
            self._sqlite_conn.close()
            self._sqlite_conn = None

    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        # Execute DDL or non-returning DML statement
        self.connect()
        if self.mode == "mysql":
            cursor = self._mysql_conn.cursor()
            cursor.execute(query, params or ())
            return cursor.rowcount
        else:
            cursor = self._sqlite_conn.cursor()
            cursor.execute(query, params or ())
            self._sqlite_conn.commit()
            return cursor.rowcount

    def execute_script(self, script_text: str):
        # Execute multi-statement SQL script with dialect adaptation
        self.connect()
        if self.mode == "mysql":
            cursor = self._mysql_conn.cursor()
            statements = self._split_mysql_script(script_text)
            for stmt in statements:
                trimmed = stmt.strip()
                if trimmed:
                    cursor.execute(trimmed)
        else:
            adapted_script = self._adapt_mysql_for_sqlite(script_text)
            self._sqlite_conn.executescript(adapted_script)

    def fetch_all(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        # Fetch all matching rows as dictionaries
        self.connect()
        if self.mode == "mysql":
            cursor = self._mysql_conn.cursor()
            cursor.execute(query, params or ())
            cols = [col[0] for col in cursor.description] if cursor.description else []
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        else:
            cursor = self._sqlite_conn.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def fetch_one(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
        # Fetch first matching row as dictionary
        results = self.fetch_all(query, params)
        return results[0] if results else None

    def _split_mysql_script(self, script_text: str) -> List[str]:
        # Split MySQL script handling custom DELIMITER declarations
        delimiter = ";"
        statements = []
        current_block: List[str] = []

        for line in script_text.splitlines():
            line_str = line.strip()
            if line_str.upper().startswith("DELIMITER"):
                parts = line_str.split()
                if len(parts) > 1:
                    delimiter = parts[1]
                continue

            if delimiter != ";" and line_str.endswith(delimiter):
                line_without_delim = line[:line.rfind(delimiter)]
                current_block.append(line_without_delim)
                statements.append("\n".join(current_block))
                current_block = []
            elif delimiter == ";" and line_str.endswith(";"):
                current_block.append(line)
                statements.append("\n".join(current_block))
                current_block = []
            else:
                current_block.append(line)

        if current_block:
            statements.append("\n".join(current_block))

        return statements

    def _adapt_mysql_for_sqlite(self, script_text: str) -> str:
        # Translate MySQL-specific syntax to SQLite compatible statements
        text = script_text

        # Remove DELIMITER declarations
        text = re.sub(r"(?i)^DELIMITER\s+.*$", "", text, flags=re.MULTILINE)

        # Replace AUTO_INCREMENT with AUTOINCREMENT (in SQLite, primary key must be INTEGER PRIMARY KEY)
        text = re.sub(r"(?i)INT\s+AUTO_INCREMENT\s+PRIMARY\s+KEY", "INTEGER PRIMARY KEY AUTOINCREMENT", text)
        text = re.sub(r"(?i)AUTO_INCREMENT", "", text)

        # Translate CREATE OR REPLACE VIEW for SQLite compatibility
        text = re.sub(r"(?i)CREATE\s+OR\s+REPLACE\s+VIEW\s+(\w+)", r"DROP VIEW IF EXISTS \1;\nCREATE VIEW \1", text)

        # Remove MySQL engine and charset clauses
        text = re.sub(r"(?i)ENGINE\s*=\s*\w+", "", text)
        text = re.sub(r"(?i)DEFAULT\s+CHARSET\s*=\s*\w+", "", text)

        # Convert ENUM(...) to TEXT
        text = re.sub(r"(?i)ENUM\s*\([^)]+\)", "TEXT", text)

        # Remove ON UPDATE CASCADE / RESTRICT that might not be supported in some SQLite setups
        # Keep foreign keys standard

        # Filter out stored procedures / triggers that use procedural MySQL syntax if not supported by SQLite
        # When running in SQLite mode, we execute standard DDL and analytical views, while procedures
        # are emulated in Python service layer
        blocks = []
        for stmt in text.split(";"):
            cleaned = stmt.strip()
            if not cleaned:
                continue
            # Skip CREATE PROCEDURE in SQLite (handled via Python service layer)
            if re.search(r"(?i)CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE", cleaned):
                continue
            # Skip CREATE TRIGGER if using MySQL procedural block (BEGIN ... END)
            if re.search(r"(?i)CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER", cleaned) and "BEGIN" in cleaned.upper():
                continue
            blocks.append(cleaned)

        return ";\n".join(blocks) + ";"
