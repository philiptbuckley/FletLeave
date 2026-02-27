import flet as ft
from datetime import date
from view import LeaveCalendarView
from model import LeaveModel, LeaveRepository

# ---- Conroller ---- This class will handle the user interactions and update the model and view accordingly
class CalendarController:
    def __init__(self, model: LeaveModel, view: LeaveCalendarView, repository: LeaveRepository):
        self.model = model
        self.view = view
        self.repo = repository
        self.view.set_controller(self)
        self.refresh()

    def refresh(self):
        self.view.render_calendar(self.model.year, self.model.month, self.model.leave_days)

    def toggle_leave(self, d: date):
        added = self.model.toggle_date(d)
        if added:
            self.repo.add_date(d)
        else:
            self.repo.remove_date(d)
        self.refresh()

    def prev(self):
        self.model.prev()
        self.refresh()

    def next(self):
        self.model.next()
        self.refresh()

# Main function to run the app
# MVC design pattern
#   Model -- handles the data and business logic
#       View -- handles the UI
#           Controller -- handles user interactions and updates the model and view
def main(page: ft.Page):

    # Connect up the respository to load existing leave dates from the database
    repo = LeaveRepository()
    existing_dates = repo.load_dates()

    # Create the leave calendar model
    model = LeaveModel(leave_dates=existing_dates)

    # Create the calendar view and pass top level page to it
    view = LeaveCalendarView(page)

    # Create the controller and pass the model and view to it
    controller = CalendarController(model, view, repo)

# App entry point
if __name__ == "__main__":
    ft.run(main)