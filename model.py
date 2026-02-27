import sqlite3
from datetime import date

# This is the model class and the data and business logic will be handled here
class LeaveModel:
    def __init__(self, leave_dates=None):
        today = date.today()
        self.year = today.year
        self.month = today.month
        self.leave_days = leave_dates or set()

    def toggle_date(self, d: date):
        if d in self.leave_days:
            self.leave_days.remove(d)
            return False # Removed
        else:
            self.leave_days.add(d)
            return True # Added

    # Backward navigation
    def prev(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1

    # Forward navigation
    def next(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1


# This class will handle the database interactions for storing and retrieving leave dates.
# Keeping it separate from the model allows us to easily swap out the storage mechanism in 
# the future if needed (e.g., switch to a different database or use an API).
class LeaveRepository:
    def __init__(self, db_path="leave_calendar.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS leave_dates (
                leave_date TEXT PRIMARY KEY
            )
        """)
        self.conn.commit()

    def load_dates(self):
        cursor = self.conn.execute("SELECT leave_date FROM leave_dates")
        return {date.fromisoformat(row[0]) for row in cursor.fetchall()}

    def add_date(self, d: date):
        self.conn.execute(
            "INSERT OR IGNORE INTO leave_dates (leave_date) VALUES (?)",
            (d.isoformat(),)
        )
        self.conn.commit()

    def remove_date(self, d: date):
        self.conn.execute(
            "DELETE FROM leave_dates WHERE leave_date = ?",
            (d.isoformat(),)
        )
        self.conn.commit()