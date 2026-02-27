from datetime import date

# This is the model class and the data and business logic will be handled here
class LeaveModel:
    def __init__(self):
        today = date.today()
        self.year = today.year
        self.month = today.month
        self.leave_days = set()

    def toggle_date(self, d: date):
        if d in self.leave_days:
            self.leave_days.remove(d)
        else:
            self.leave_days.add(d)

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
