import sqlite3


class Database:

    def __init__(self):
        self.conn = sqlite3.connect(
            "intrusion.db",
            check_same_thread=False
        )

        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS intrusion_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracker_id INTEGER,
            enter_time TEXT,
            exit_time TEXT,
            duration REAL,
            image_path TEXT
        )
        """)

        self.conn.commit()