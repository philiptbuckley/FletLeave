import flet as ft
from datetime import date
from view import LeaveCalendarView
from model import LeaveEntry, LeaveModel, LeaveRepository, Employee, EmployeeRepository

# ---- Conroller ---- This class will handle the user interactions and update the model and view accordingly
class CalendarController:
    def __init__(self, model: LeaveModel, view: LeaveCalendarView, 
                 leave_repo: LeaveRepository, employee_repo: EmployeeRepository):
        self.model = model
        self.view = view
        self.leave = leave_repo
        self.employees = employee_repo
        self.view.set_controller(self)
        self.refresh()

    def refresh(self):
        self.view.render_calendar(self.model.year, self.model.month, 
                                  self.model.leave_entries, self.model.employees)

    def toggle_leave(self, d: date):
        entry = LeaveEntry(employee_id=self.model.current_employee_id, 
                           leave_date=d, leave_type=self.model.selected_leave_type, 
                           duration=self.model.selected_duration)
        
        if self.model.toggle_date(d):   # Returns true if leave entry was added, false if removed
            self.leave.add_entry(d, self.model.current_employee_id, self.model.selected_leave_type, self.model.selected_duration)
        else:
            self.leave.remove_entry(d, self.model.current_employee_id)
        self.refresh()

    def set_leave_for_day(self, d: date, leave_type, duration, description: str):
        # Replace any existing entry for this employee/day with the specified leave
        # Ensure model and repository are consistent
        # Remove existing
        self.leave.remove_entry(d, self.model.current_employee_id)
        self.model.remove_leave(self.model.current_employee_id, d)
        # Add new
        entry = LeaveEntry(employee_id=self.model.current_employee_id,
                           leave_date=d, leave_type=leave_type, duration=duration, description=description)
        self.model.add_leave(entry)
        self.leave.add_entry(d, self.model.current_employee_id, leave_type, duration, description)
        self.refresh()

    def clear_leave_for_day(self, d: date):
        # Remove leave for the current employee on the given day
        self.leave.remove_entry(d, self.model.current_employee_id)
        self.model.remove_leave(self.model.current_employee_id, d)
        self.refresh()

    def prev(self):
        self.model.prev()
        self.refresh()

    def next(self):
        self.model.next()
        self.refresh()

    def change_employee(self, employee_id: int):
        self.model.current_employee_id = employee_id
        self.refresh()

    # Return a list of leave entries for employee
    def get_leave_entries_for_employee(self, employee_id):
        return self.model.get_leave_entries(employee_id=employee_id)

    def get_employee_name(self, employee_id):
        return self.model.get_employee_name(employee_id)

    def get_employee_abbrev(self, employee_id):
        return self.model.get_employee_abbrev(employee_id)
    
    def get_employee_id_by_name(self, name):
        for emp in self.model.employees:
            if emp.name == name:
                return emp.id

    def add_employee(self, emp_name: str, emp_abbrev=None) -> int:
        employee = Employee(id=None, name=emp_name, abbrev=emp_abbrev)  # Create object
        id = self.employees.add_employee(emp_name, emp_abbrev)          # Add to the database and get new ID
        if id > 0:       # Add to the database
            employee.__setattr__('id', id)                              # Save the id in the object
            self.model.add_employee(employee)                           # Add to the model
            self.refresh()
            return id
        else:
            return 0
        
    def delete_employee(self, employee_id) -> bool:
        if self.employees.remove_employee(employee_id) > 0:             # Remove from the database
            self.model.remove_employee(employee_id)                     # Remove from the model
            self.refresh()
            return True
        else:
            return False

    # Update the employee in the database and model
    def update_employee(self, emp_id, emp_name: str, emp_abbrev=None) -> bool:
        if self.employees.update_employee(emp_id, emp_name, emp_abbrev) > 0:  # Update in the database
            self.model.update_employee(emp_id, emp_name, emp_abbrev)          # Update in the model
            self.refresh()
            return True
        else:
            return False

# Main function to run the app
# MVC design pattern
#   Model -- handles the data and business logic
#       View -- handles the UI
#           Controller -- handles user interactions and updates the model and view
def main(page: ft.Page):

    # Connect up the respository (database) and load existing leave entries for the employee(s)
    leave_repo = LeaveRepository()
    emp_repo = EmployeeRepository()
    employees = emp_repo.load_employees() # Load employee list from database
    existing_leave_entries = leave_repo.load_entries() # Load all leave entries

    # Create the leave calendar model
    model = LeaveModel(employees=employees, leave_entries=existing_leave_entries)
    
    # Create the calendar view and pass top level page to it
    view = LeaveCalendarView(page)

    # Create the controller and pass the model and view to it
    CalendarController(model, view, leave_repo, emp_repo)

# App entry point
if __name__ == "__main__":
    ft.run(main)