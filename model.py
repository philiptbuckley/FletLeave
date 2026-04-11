import json
import sqlite3
import flet as ft
from datetime import date
from enum import Enum
from dataclasses import dataclass

class LeaveTypeInfo:
    def __init__(self, name, color):
        self.name = name
        self.color = color

class LeaveType(Enum):
    PUBLIC = LeaveTypeInfo("Public Holiday", ft.Colors.AMBER_700)
    HOLIDAY = LeaveTypeInfo("Holiday", ft.Colors.YELLOW_600)
    SHUTDOWN = LeaveTypeInfo("Shutdown", ft.Colors.BROWN_600)
    SICK = LeaveTypeInfo("Sick", ft.Colors.PINK_200)
    UNPAID = LeaveTypeInfo("Unpaid", ft.Colors.GREY_200)
    XTRA = LeaveTypeInfo("Extra Work", ft.Colors.LIME_ACCENT_400)

class LeaveDuration(Enum):
    FULL = "Full day"
    AM = "AM only"
    PM = "PM only"

@dataclass(frozen=True)
class LeaveEntry:
    employee_id: int
    leave_date: date
    leave_type: LeaveType
    duration: LeaveDuration
    description: str

@dataclass(frozen=False)    # We need to be able to set the ID after creating the object
class Employee:
    id: int
    name: str
    abbrev: str
    regular_work_days: list = None  # Optional list of integers representing regular work days (0=Monday, 6=Sunday)

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

    # Lookup existing leave entries with optional employee filter (if employee_id is None, returns all entries for the day)
    def get_entries_for_day(self, day, employee_id=None):
        return self.get_leave_entries(employee_id=employee_id, from_date=day, to_date=day)
    
    # Return all entries for an optional employee with date range filter
    def get_leave_entries(self, employee_id=None, from_date=None, to_date=None):
        entries = []
        for entry in self.leave_entries:
            if employee_id is not None and entry.employee_id != employee_id:
                continue
            if from_date is not None and entry.leave_date < from_date:
                continue
            if to_date is not None and entry.leave_date > to_date:
                continue
            entries.append(entry)
        return entries

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
        
    def get_employee_working_days(self, employee_id):
        for emp in self.employees:
            if emp.id == employee_id:
                return emp.regular_work_days
        return None

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

    def get_employee_name(self, employee_id):
        for emp in self.employees:
            if emp.id == employee_id:
                return emp.name
        return "Unknown"

    def get_employee_abbrev(self, employee_id):
        for emp in self.employees:
            if emp.id == employee_id:
                abbrev = emp.abbrev
                if abbrev is not None and abbrev.strip() != "":
                    return abbrev
                # If employee has two or more words in their name, use the first letter of the first two words as the abbreviation
                if len(emp.name.split()) >= 2:
                    return "".join([word[0] for word in emp.name.split()[:2]]).upper()
                # Otherwise, use the first two letters of their name as the abbreviation
                return emp["name"][:2].upper()
        return "??"
    
    def add_employee(self, emp: Employee):
        self.employees.append(emp)

    def remove_employee(self, employee_id):
        self.employees = [e for e in self.employees if e.id != employee_id]
        # Also remove any leave entries for this employee
        self.leave_entries = [e for e in self.leave_entries if e.employee_id != employee_id]

    # Update employee details in the model
    def update_employee(self, emp_id, emp_name: str, emp_abbrev: str, emp_working_days: list):
        for emp in self.employees:
            if emp.id == emp_id:
                emp.name = emp_name
                emp.abbrev = emp_abbrev
                emp.regular_work_days = emp_working_days
                break

class EmployeeRepository:
    def __init__(self, db_path="leave_calendar.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                abbrev CHAR(2) UNIQUE)
        """)
        self.conn.commit()

    def load_employees(self):
        cursor = self.conn.execute("SELECT id, name, abbrev, regular_work_days FROM employees")
        return [Employee(id=row[0], name=row[1], abbrev=row[2], regular_work_days=json.loads(row[3]) if row[3] else []) for row in cursor.fetchall()]

    def add_employee(self, name: str, abbrev: str, regular_work_days: list = None) -> int:
        self.conn.execute(
            "INSERT OR IGNORE INTO employees (name, abbrev, regular_work_days) VALUES (?, ?, ?)",
            (name, abbrev, json.dumps(regular_work_days) if regular_work_days else None)
        )
        self.conn.commit()
        cursor = self.conn.execute("SELECT last_insert_rowid()")
        return int(cursor.fetchone()[0])
    
    def remove_employee(self, employee_id) -> int:
        result = self.conn.execute(
            "DELETE FROM employees WHERE id = ?",
            (employee_id,)
        )
        self.conn.commit()
        return result.rowcount
    
    # Update employee record in the database
    def update_employee(self, emp_id, name: str, abbrev: str, regular_work_days: list = None) -> int:
        result = self.conn.execute(
            "UPDATE employees SET name = ?, abbrev = ?, regular_work_days = ? WHERE id = ?",
            (name, abbrev, json.dumps(regular_work_days) if regular_work_days else None, emp_id)
        )
        self.conn.commit()
        return result.rowcount

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
                duration TEXT,
                description TEXT)
        """)
                # FOREIGN KEY (employee_id) REFERENCES employees(id)
        self.conn.commit()

    def load_entries(self):
        cursor = self.conn.execute("SELECT employee_id, leave_date, leave_type, duration, description FROM leave_entries")
        return [LeaveEntry(employee_id=row[0], leave_date=date.fromisoformat(row[1]), leave_type=LeaveType[row[2]], duration=LeaveDuration[row[3]], description=row[4]) for row in cursor.fetchall()]

    def add_entry(self, d: date, employee_id, leave_type, duration, description: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO leave_entries (employee_id, leave_date, leave_type, duration, description) VALUES (?, ?, ?, ?, ?)",
            (employee_id, d.isoformat(), leave_type.name, duration.name, description)
        )
        self.conn.commit()

    def remove_entry(self, d: date, employee_id):
        self.conn.execute(
            "DELETE FROM leave_entries WHERE leave_date = ? AND employee_id = ?",
            (d.isoformat(), employee_id)
        )
        self.conn.commit()