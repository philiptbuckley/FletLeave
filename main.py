import flet as ft
from datetime import date
from view import LeaveCalendarView
from model import LeaveEntry, LeaveModel, LeaveRepository, EmployeeRepository

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

    def set_leave_for_day(self, d: date, leave_type, duration):
        # Replace any existing entry for this employee/day with the specified leave
        # Ensure model and repository are consistent
        # Remove existing
        self.leave.remove_entry(d, self.model.current_employee_id)
        self.model.remove_leave(self.model.current_employee_id, d)
        # Add new
        entry = LeaveEntry(employee_id=self.model.current_employee_id,
                           leave_date=d, leave_type=leave_type, duration=duration)
        self.model.add_leave(entry)
        self.leave.add_entry(d, self.model.current_employee_id, leave_type, duration)
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
    existing_leave_entries = leave_repo.load_entries(employees) # Load leave entries for first employee

    # Create the leave calendar model
    model = LeaveModel(employees=employees, leave_entries=existing_leave_entries)
    
    # Create the calendar view and pass top level page to it
    view = LeaveCalendarView(page)

    # Create the controller and pass the model and view to it
    controller = CalendarController(model, view, leave_repo, emp_repo)

# App entry point
if __name__ == "__main__":
    ft.run(main)