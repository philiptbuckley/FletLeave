import flet as ft
import calendar
from datetime import date
from model import LeaveType, LeaveDuration

class GroupBox(ft.Container):
    def __init__(self, title: str, content: ft.Control, width=None):
        super().__init__()

        self.content = ft.Column(
            spacing=0,
            controls=[
                # Title
                ft.Container(
                    content=ft.Text(title, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.only(left=8, right=8),
                ),

                # Box content
                ft.Container(
                    content=content,
                    padding=15,
                    border=ft.border.all(1, ft.Colors.BLACK),
                    border_radius=8,
                    expand=False,
                ),
            ],
        )

        self.width = width

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
        # and the view selector buttons and store them as instance variables so we can update them later when rendering the calendar
        self.nav, self.view_mode = self.build_nav()

        # Add the controls onto the page
        page.add(self.nav, self.calendar_grid, self.view_mode, ft.Divider(), self.selected_text)

        # Prepare leave type and duration dialog (reused for all day clicks)
        self.leave_dialog = self.build_leave_dialog()

    def build_nav(self):
        nav = ft.Row(
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

        view_mode = ft.Row(
            [
                ft.IconButton(ft.Icons.CALENDAR_VIEW_DAY, on_click=lambda e: self.set_view_mode(e, "day"), tooltip="Day View"),
                ft.IconButton(ft.Icons.CALENDAR_VIEW_WEEK, on_click=lambda e: self.set_view_mode(e, "week"), tooltip="Week View"),
                ft.IconButton(ft.Icons.CALENDAR_VIEW_MONTH, on_click=lambda e: self.set_view_mode(e, "month"), tooltip="Month View"),
                ft.IconButton(ft.Icons.CALENDAR_TODAY, on_click=lambda e: self.set_view_mode(e, "year"), tooltip="Year View"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        return nav, view_mode

    def build_leave_dialog(self):
        # Dialog / popup for selecting leave type and duration (reused for all day clicks)
        self._dialog_day = None

        # RadioGroups for leave type and duration; we'll re-use these in the dialog
        self.leave_type_group = ft.RadioGroup(
            content=ft.Column([ft.Radio(label=lt.value.name, value=lt.name) for lt in LeaveType], tight=True)
        )
        self.leave_duration_group = ft.RadioGroup(
            content=ft.Column([ft.Radio(label=d.value, value=d.name) for d in LeaveDuration], tight=True)
        )

        return ft.AlertDialog(
            content=ft.Column(controls = [
                ft.Row([
                    GroupBox("Leave Type", self.leave_type_group, width=200),
                    ft.Column(controls=[
                        GroupBox("Duration", self.leave_duration_group, width=200),
                        ft.TextField(label="Number of Days", value="1", width=200, 
                                     label_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                                     border=ft.border.all(1, ft.Colors.GREY_400)),
                    ], expand = False, alignment=ft.MainAxisAlignment.START, spacing=35), 
                ]),
                ft.TextField(label="Description or comments", hint_text="Holiday in Ibiza", width=410),
            ]
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._close_dialog),
                ft.TextButton("Clear", on_click=self._clear_leave),
                ft.TextButton("Apply", on_click=self._apply_leave),
            ],
        )

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

    def create_day_cell(self, day_number, leave_type: LeaveType, leave_duration: LeaveDuration=None):
        bg_gradient = None
        bg_color = leave_type.value.color if leave_type else ft.Colors.WHITE
        if leave_duration == LeaveDuration.AM:
            bg_gradient = ft.LinearGradient(
                begin=ft.Alignment.TOP_RIGHT,
                end=ft.Alignment.BOTTOM_LEFT,
                colors=[ft.Colors.WHITE, bg_color],
                stops=[0.5, 0.5]
            )
        elif leave_duration == LeaveDuration.PM:
            bg_gradient = ft.LinearGradient(
                begin=ft.Alignment.TOP_RIGHT,
                end=ft.Alignment.BOTTOM_LEFT,
                colors=[bg_color, ft.Colors.WHITE],
                stops=[0.5, 0.5]
            )
        elif leave_duration == LeaveDuration.FULL:
            ft.Container(
                content=ft.Text(str(day_number)),
                width=60,
                height=60,
                alignment=ft.Alignment.CENTER,
                border=ft.border.all(1, bg_color),
                bgcolor=bg_color,
                gradient=bg_gradient,
            )

        return ft.Container(
            content=ft.Text(str(day_number)),
            width=60,
            height=60,
            alignment=ft.Alignment.CENTER,
            border=ft.border.all(1, bg_color),
            bgcolor=bg_color,
            gradient=bg_gradient,
        )

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
                entry_exists = None
                if day == 0:
                    row.controls.append(ft.Container(width=60, height=40))
                else:
                    d = date(year, month, day)
                    if self.employeeDrop.value is not None:
                        entry_exists = self.controller.model.get_entries_for_day(int(self.employeeDrop.value), d)
                        if entry_exists:
                            bgcolour = entry_exists.leave_type.value.color
                        else:
                            bgcolour = None
                    else:
                        bgcolour = None

                    cell = self.create_day_cell(
                                        day, 
                                        entry_exists.leave_type if entry_exists else None, 
                                        entry_exists.duration if entry_exists else None)
                    cell.on_click = lambda e, day_date=d: self._open_leave_dialog(day_date)
                    row.controls.append(cell)
            self.calendar_grid.controls.append(row)

        # Update the list of booked leave entries for the selected employee
        if self.employeeDrop.value is not None:
            employee_leave_entries = [e for e in leave_entries if e.employee_id == int(self.employeeDrop.value) and 
                                      e.leave_date.month == month and e.leave_date.year == year]
            if employee_leave_entries:
                sorted_entries = sorted(employee_leave_entries, key=lambda e: e.leave_date)
                self.selected_text.value += "\n".join([f"{e.leave_date}: {e.leave_type.value.name} ({e.duration.value})" for e in sorted_entries])
            else:
                self.selected_text.value += "No leave booked"
        else:
            self.selected_text.value = "Please select an employee to view booked leave"
        self.page.update()

    # ---- Leave dialog handlers ----
    def _open_leave_dialog(self, d: date):

        # Can't create or view leave entries if no employee selected - show a message and return early
        if self.employeeDrop.value is None:
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Please select an employee to create or edit leave")))
            return
        
        self._dialog_day = d
        # Pre-select existing values if an entry exists
        entry = self.controller.model.get_entries_for_day(int(self.employeeDrop.value), d)

        if entry:
            selected_type = entry.leave_type.name
            selected_dur = entry.duration.name
        else:
            selected_type = self.controller.model.selected_leave_type.name
            selected_dur = self.controller.model.selected_duration.name

        # set the radio group selections
        self.leave_type_group.value = selected_type
        self.leave_duration_group.value = selected_dur

        # Flet sometimes requires show_dialog to actually render the dialog
        self.leave_dialog.open = True
        self.page.show_dialog(self.leave_dialog)
        # page.update() may not be needed but safe
        self.page.update()

    def _clear_leave(self, e):
        if self._dialog_day:
            self.controller.clear_leave_for_day(self._dialog_day)
        self._close_dialog()

    def _apply_leave(self, e):
        # read the values from the radio groups
        selected_type_name = self.leave_type_group.value
        selected_dur_name = self.leave_duration_group.value

        if selected_type_name and selected_dur_name and self._dialog_day:
            lt = LeaveType[selected_type_name]
            du = LeaveDuration[selected_dur_name]
            self.controller.set_leave_for_day(self._dialog_day, lt, du)

        self._close_dialog()

    def _close_dialog(self, e=None):
        self.leave_dialog.open = False
        self.page.update()
