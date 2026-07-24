from database.db import Database

class EventRepository:

    def __init__(self):
        self.db = Database()

    def create_entry(
        self,
        tracker_id,
        enter_time,
        image_path
    ):

        cursor = self.db.conn.cursor()

        cursor.execute(
            """
            INSERT INTO intrusion_events
            (
                tracker_id,
                enter_time,
                image_path
            )
            VALUES (?, ?, ?)
            """,
            (
                tracker_id,
                enter_time.isoformat(),
                image_path
            )
        )

        self.db.conn.commit()

    def update_exit(
        self,
        tracker_id,
        exit_time,
        duration
    ):

        cursor = self.db.conn.cursor()

        cursor.execute(
            """
            UPDATE intrusion_events
            SET
                exit_time=?,
                duration=?

            WHERE
                tracker_id=?
                AND
                exit_time IS NULL
            """,
            (
                exit_time.isoformat(),
                duration,
                tracker_id
            )
        )

        self.db.conn.commit()

    def find_recent_events(
            self,
            limit=10
    ):
        cursor = self.db.conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM intrusion_events
            ORDER BY enter_time DESC
            LIMIT ?
            """,
            (
                limit,
            )
        )

        return cursor.fetchall()

