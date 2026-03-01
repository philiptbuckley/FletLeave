import flet as ft
import calendar
from datetime import date

# This is the view class that manages all the UI rendering and user interactions
class LeaveCalendarView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = None  # Will be set by the controller
        page.title = "Leave Tracker Calendar"
        self.view_mode = "month"  # Default view

        self.header = ft.Text("", size=20, weight="bold")
        self.calendar_grid = ft.Column()
        self.selected_text = ft.Text()

        # Employee drop down - will be populated with employee names and IDs from the model
        self.employeeDrop = ft.Dropdown(
            on_select=lambda e: self._employee_selected(e),
            align=ft.Alignment.TOP_LEFT,
            value=None,
            hint_text="Select Employee",
            label="Employee"
        )

        # Build up the nav row comprising of employee selector, month/year header and navigation buttons
        self.nav = ft.Row(
            [
                ft.Column(controls=[ft.Row([
                        self.employeeDrop])], expand=True),  # Employee selector
                ft.Column(controls=[ft.Row([
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.prev_clicked),
                        self.header,
                        ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=self.next_clicked),
                    ], alignment=ft.MainAxisAlignment.CENTER)], expand=True),
                ft.Column(controls=[ft.Container(expand=True)], expand=True),  # Spacer
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.view_mode = ft.Row(
            [
                ft.IconButton(ft.Icons.CALENDAR_VIEW_DAY, on_click=lambda e: self.set_view_mode(e, "day"), tooltip="Day View"),
                ft.IconButton(ft.Icons.CALENDAR_VIEW_WEEK, on_click=lambda e: self.set_view_mode(e, "week"), tooltip="Week View"),
                ft.IconButton(ft.Icons.CALENDAR_VIEW_MONTH, on_click=lambda e: self.set_view_mode(e, "month"), tooltip="Month View"),
                ft.IconButton(ft.Icons.CALENDAR_TODAY, on_click=lambda e: self.set_view_mode(e, "year"), tooltip="Year View"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        page.add(self.nav, self.calendar_grid, self.view_mode, ft.Divider(), self.selected_text)

    # Function to attach the controller to the view
    def set_controller(self, controller):
        self.controller = controller

    # ---- UI event handlers ----
    def prev_clicked(self, e):
        self.controller.prev()

    def next_clicked(self, e):
        self.controller.next()

    def set_view_mode(self, e, view: str):
        self.view_mode = view

    def _employee_selected(self, e):
        self.controller.change_employee(int(self.employeeDrop.value))

    # ---- Render methods ----
    def render_calendar(self, year, month, leave_entries, employees):

        # Update employee dropdown options based on the list of employees in the model
        self.employeeDrop.options=[ft.dropdown.Option(str(emp["id"]), emp["name"]) for emp in employees]

        self.calendar_grid.controls.clear()
        self.header.value = f"{calendar.month_name[month]} {year}"

        # Weekday headers
        week_header = ft.Row(
            controls=[
                ft.Container(content=ft.Text(day), width=60, alignment=ft.Alignment.CENTER)
                    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.calendar_grid.controls.append(week_header)

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(year, month)

        self.selected_text.value = "Booked leave:\n" + "\n"

        for week in month_days:
            row = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
            for day in week:
                if day == 0:
                    row.controls.append(ft.Container(width=60, height=40))
                else:
                    d = date(year, month, day)
                    if self.employeeDrop.value is not None:
                        is_selected = self.controller.model.get_entries_for_day(int(self.employeeDrop.value), d)
                    else:
                        is_selected = False

                    row.controls.append(
                        ft.Container(
                            content=ft.Text(str(day)),
                            width=60,
                            height=40,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=ft.Colors.BLUE_200 if is_selected else None,
                            border=ft.Border.all(1, ft.Colors.GREY_300),
                            on_click=lambda e, day_date=d: self.controller.toggle_leave(day_date),
                        )
                    )
            self.calendar_grid.controls.append(row)

        # Update the list of booked leave entries for the selected employee
        if self.employeeDrop.value is not None:
            employee_leave_entries = [e for e in leave_entries if e.employee_id == int(self.employeeDrop.value) and 
                                      e.leave_date.month == month and e.leave_date.year == year]
            if employee_leave_entries:
                sorted_entries = sorted(employee_leave_entries, key=lambda e: e.leave_date)
                self.selected_text.value += "\n".join([f"{e.leave_date}: {e.leave_type.value} ({e.duration.value})" for e in sorted_entries])
            else:
                self.selected_text.value += "No leave booked"
        else:
            self.selected_text.value = "Please select an employee to view booked leave"
        self.page.update()
