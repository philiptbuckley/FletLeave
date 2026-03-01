import sqlite3
import flet as ft
from datetime import date
from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class LeaveEntry:
    employee_id: int
    leave_date: date
    leave_type: LeaveType
    duration: LeaveDuration

class LeaveTypeInfo:
    def __init__(self, name, color):
        self.name = name
        self.color = color

class LeaveType(Enum):
    PUBLIC = LeaveTypeInfo("Public Holiday", ft.Colors.AMBER_700)
    HOLIDAY = LeaveTypeInfo("Holiday", ft.Colors.YELLOW_200)
    SHUTDOWN = LeaveTypeInfo("Shutdown", ft.Colors.BROWN_600)
    SICK = LeaveTypeInfo("Sick", ft.Colors.PINK_200)
    UNPAID = LeaveTypeInfo("Unpaid", ft.Colors.GREY_200)

class LeaveDuration(Enum):
    FULL = "Full day"
    AM = "Morning"
    PM = "Afternoon"

# This is the model class and the data and business logic will be handled here
class LeaveModel:
    def __init__(self, employees, leave_entries=None):
        today = date.today()
        self.year = today.year
        self.month = today.month
        self.employees = employees
        self.current_employee_id = None
        self.selected_leave_type = LeaveType.HOLIDAY
        self.selected_duration = LeaveDuration.FULL
        self.leave_entries = leave_entries or []

    # Lookup existing leave entries for the current employee and given day
    def get_entries_for_day(self, employee_id, day):
        for entry in self.leave_entries:
            if entry.employee_id == employee_id and entry.leave_date == day:
                return entry
        return None

    def add_leave(self, entry: LeaveEntry):
        self.leave_entries.append(entry)

    def remove_leave(self, employee_id, day):
        self.leave_entries = [
            e for e in self.leave_entries
            if not (e.employee_id == employee_id and e.leave_date == day)
        ]    

    def toggle_date(self, d: date):
        if self.get_entries_for_day(self.current_employee_id, d):
            self.remove_leave(self.current_employee_id, d)
            return False # Removed
        else:
            entry = LeaveEntry(employee_id=self.current_employee_id, 
                               leave_date=d, leave_type=self.selected_leave_type, 
                               duration=self.selected_duration)
            self.add_leave(entry)
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

class EmployeeRepository:
    def __init__(self, db_path="leave_calendar.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT)
        """)
        self.conn.commit()

    def load_employees(self):
        cursor = self.conn.execute("SELECT id, name FROM employees")
        return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]

# This class will handle the database interactions for storing and retrieving leave dates.
# Keeping it separate from the model allows us to easily swap out the storage mechanism in 
# the future if needed (e.g., switch to a different database or use an API).
class LeaveRepository:
    def __init__(self, db_path="leave_calendar.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS leave_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                leave_date TEXT,
                leave_type TEXT,
                duration TEXT)
        """)
                # FOREIGN KEY (employee_id) REFERENCES employees(id)
        self.conn.commit()

    def load_entries(self, employee_id):
        cursor = self.conn.execute("SELECT employee_id, leave_date, leave_type, duration FROM leave_entries")
        return [LeaveEntry(employee_id=row[0], leave_date=date.fromisoformat(row[1]), leave_type=LeaveType[row[2]], duration=LeaveDuration[row[3]]) for row in cursor.fetchall()]

    def add_entry(self, d: date, employee_id, leave_type, duration):
        self.conn.execute(
            "INSERT OR IGNORE INTO leave_entries (employee_id, leave_date, leave_type, duration) VALUES (?, ?, ?, ?)",
            (employee_id, d.isoformat(), leave_type.name, duration.name)
        )
        self.conn.commit()

    def remove_entry(self, d: date, employee_id):
        self.conn.execute(
            "DELETE FROM leave_entries WHERE leave_date = ? AND employee_id = ?",
            (d.isoformat(), employee_id)
        )
        self.conn.commit()