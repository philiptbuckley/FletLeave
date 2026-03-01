import flet as ft
from datetime import date
from view import LeaveCalendarView
from model import LeaveEntry, LeaveModel, LeaveRepository

# ---- Conroller ---- This class will handle the user interactions and update the model and view accordingly
class CalendarController:
    def __init__(self, model: LeaveModel, view: LeaveCalendarView, repository: LeaveRepository):
        self.model = model
        self.view = view
        self.repo = repository
        self.view.set_controller(self)
        self.refresh()

    def refresh(self):
        self.view.render_calendar(self.model.year, self.model.month, self.model.leave_entries)

    def toggle_leave(self, d: date):
        entry = LeaveEntry(employee_id=self.model.current_employee_id, 
                           leave_date=d, leave_type=self.model.selected_leave_type, 
                           duration=self.model.selected_duration)
        
        if self.model.toggle_date(d):   # Returns true if leave entry was added, false if removed
            self.repo.add_entry(d, self.model.current_employee_id, self.model.selected_leave_type, self.model.selected_duration)
        else:
            self.repo.remove_entry(d, self.model.current_employee_id)
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

    # Hard code until table working
    employees = [
        {"id": 1, "name": "Phil"},
        {"id": 2, "name": "Alice"},
        {"id": 3, "name": "Bob"},
    ]

    # Connect up the respository to load existing leave dates from the database
    repo = LeaveRepository()

    existing_leave_entries = repo.load_entries(1) # Load leave entries for employee with id 1 (Phil)

    # Create the leave calendar model
    model = LeaveModel(employees=employees, leave_entries=existing_leave_entries)
    
    # Create the calendar view and pass top level page to it
    view = LeaveCalendarView(page)

    # Create the controller and pass the model and view to it
    controller = CalendarController(model, view, repo)

# App entry point
if __name__ == "__main__":
    ft.run(main)