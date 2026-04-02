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
        self.DAY_CELL_SIZE = 60
        self.page = page
        self.controller = None  # Will be set by the controller
        page.title = "Leave Tracker Calendar"
        self.view_mode = "month"  # Default view

        self.header = ft.Text("", size=20, weight="bold")
        self.calendar_grid = ft.Column()
        self.leave_summary = ft.Column(
            controls=[ft.Text()],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

        # Employee drop down - will be populated with employee names and IDs from the model when rendering the calendar
        self.employeeDrop = ft.Dropdown(
            on_select=lambda e: self._employee_selected(e),
            align=ft.Alignment.TOP_LEFT,
            value="all",
            hint_text="Select Employee",
            label="Employee"
        )

        # Build up the nav row comprising of employee selector, month/year header and navigation buttons
        # and the view selector buttons and store them as instance variables so we can update them later when rendering the calendar
        self.nav, self.view_mode = self.build_nav()

        # Create a text control for the leave summary title
        self.leave_summary_title = ft.Container(
            content=ft.Text("", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            margin=ft.margin.only(bottom=0)
        )

        # Add the controls onto the page
        page.add(ft.Row([
            ft.Column(self.employeeDrop, width=200),
            ft.IconButton(ft.Icons.ADD, on_click = lambda e: self._open_employee_dialog()),
            ft.IconButton(ft.Icons.EDIT, on_click = lambda e: self._open_employee_dialog(self.employeeDrop.value)),
            ft.Column(controls=[self.nav, self.calendar_grid], expand=True, width=400),
            ft.Column(controls=[ft.Container(expand=False), self.build_key()],width=200)
        ], vertical_alignment=ft.CrossAxisAlignment.START), self.leave_summary_title, ft.Divider(), self.leave_summary)

        # Prepare leave and employee dialog (reused for all inocations)
        self.leave_dialog = self.build_leave_dialog()
        self.employee_dialog = self.build_employee_dialog()

    def build_key(self):
        self.key_column = ft.Column(controls=[ft.Text("Key:", weight=ft.FontWeight.BOLD)], expand=True, alignment=ft.Alignment.TOP_RIGHT, )
        for lt in LeaveType:
            self.key_column.controls.append(
                ft.Row([
                    ft.Container(width=20, height=20, bgcolor=lt.value.color, border=ft.border.all(1, lt.value.color)),
                        ft.Text(lt.value.name, text_align=ft.TextAlign.RIGHT)
                    ], alignment=ft.Alignment.TOP_RIGHT)
        )
        return self.key_column

    def build_nav(self):
        nav = ft.Row(
            [
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.prev_clicked),
                self.header,
                ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=self.next_clicked),
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

        # RadioGroups for leave type and duration; leave description text. We'll re-use these in the dialog
        self.leave_type_group = ft.RadioGroup(
            content=ft.Column([ft.Radio(label=lt.value.name, value=lt.name) for lt in LeaveType], tight=True)
        )
        self.leave_duration_group = ft.RadioGroup(
            content=ft.Column([ft.Radio(label=d.value, value=d.name) for d in LeaveDuration], tight=True)
        )
        self.leave_description = ft.TextField(label="Description or comments", hint_text="Holiday in Ibiza", width=410)

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
                self.leave_description,
            ]
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._close_dialog),
                ft.TextButton("Clear", on_click=self._clear_leave),
                ft.TextButton("Apply", on_click=self._apply_leave),
            ],
        )

    def build_employee_dialog(self):
        # Dialog / popup for adding / editing employees
        self.employee_input_name = ft.TextField(label="Employee name", width=300,
                                    label_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                                    border=ft.border.all(1, ft.Colors.GREY_400))
        self.employee_input_abbrev = ft.TextField(label="Initials", width=90, capitalization=True, max_length=2,
                                    label_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
                                    border=ft.border.all(1, ft.Colors.GREY_400))
        return ft.AlertDialog(
            content = ft.Column(controls = [self.employee_input_name, self.employee_input_abbrev]),
            actions=[
                ft.TextButton("Cancel", on_click=self._close_employee_dialog),
                ft.TextButton("Delete", on_click=self._delete_employee),
                ft.TextButton("Add", on_click=self._add_employee),
                ft.TextButton("Update", on_click=self._update_employee, visible=False),
            ]
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
        if self.employeeDrop.value == "all":
            self.controller.change_employee(None)
        else:
            self.controller.change_employee(int(self.employeeDrop.value))

    # Render the cell for a given day, applying background color or gradient based on the leave type and duration
    # entries is a list of leave entries for the day. If empty render as normal, if all leave is the same type colour the cell with that type, 
    # if multiple leave types then show a dark background and annotate the cell with the employee abbreviation(s) and show a tooltip with the 
    # details of each entry
    def create_day_cell(self, day_number, day_entries: list):

        # If list empty, render normal cell
        if day_entries is None or len(day_entries) == 0:
            return ft.Container(
                content=ft.Text(str(day_number)),
                width=self.DAY_CELL_SIZE,
                height=self.DAY_CELL_SIZE,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.WHITE,
            )

        else:
            # Render cell and annotate with employee, leave type and duration
        
            # Create the tooltip text and list of employee abbreviations
            abbrev_texts = []
            tooltip_text = ""

            # If all entries are of the same type and duration, render with that type's color and gradient
            same_leave_type = len(set((entry.leave_type, entry.duration) for entry in day_entries)) == 1
            
            for entry in day_entries:
                emp_name = self.controller.get_employee_name(entry.employee_id)
                emp_abbrev = self.controller.get_employee_abbrev(entry.employee_id)
                # Make the abbreviation text white if the background is the leave type colour
                abbrev_texts.append(ft.Text(emp_abbrev, size=10, color=ft.Colors.BLACK if same_leave_type else entry.leave_type.value.color))
                tooltip_text += f"{emp_name}: {entry.leave_type.value.name} {entry.duration.value}\n"
            
            if (same_leave_type):
                entry = day_entries[0]
                leave_type = entry.leave_type
                leave_duration = entry.duration
            # otherwise it's a mixture of leave types/durations - render with a dark background and show employee abbrevs in the cell with a tooltip showing the details of each entry
            else:
                return ft.Container(
                    content=ft.Stack([
                        ft.Container(content=ft.Text(str(day_number), color=ft.Colors.GREY), alignment=ft.Alignment.CENTER),
                        ft.Container(content=ft.Row(abbrev_texts, spacing=2), alignment=ft.Alignment.BOTTOM_LEFT),
                    ]),
                    width=self.DAY_CELL_SIZE,
                    height=self.DAY_CELL_SIZE,
                    bgcolor=ft.Colors.GREY_800,
                    tooltip=tooltip_text.strip()
                )

        # If we have a single leave type/duration, we can colour the cell with the leave type color and apply a gradient based on the duration (AM/PM)
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
            content=ft.Stack([
                ft.Container(content=ft.Text(str(day_number), color=ft.Colors.GREY), alignment=ft.Alignment.CENTER),
                ft.Container(content=ft.Row(abbrev_texts, spacing=2), alignment=ft.Alignment.BOTTOM_LEFT),
            ]),
            width=self.DAY_CELL_SIZE,
            height=self.DAY_CELL_SIZE,
            alignment=ft.Alignment.CENTER,
            border=ft.border.all(1, bg_color),
            bgcolor=bg_color,
            gradient=bg_gradient,
            tooltip=tooltip_text.strip()
        )

    # ---- Render methods ----
    def render_calendar(self, year, month, leave_entries, employees):

        # Update employee dropdown options based on the list of employees in the model
        self.employeeDrop.options = [ft.dropdown.Option("all", "All Employees")] + [ft.dropdown.Option(str(emp.id), emp.name) for emp in employees]
        # Add a separator option after the "All Employees" option for better UX
        self.employeeDrop.options.insert(1, ft.dropdown.Option(None, "----------------", disabled=True))

        self.calendar_grid.controls.clear()
        self.header.value = f"{calendar.month_name[month]} {year}"

        # Weekday headers
        week_header = ft.Row(
            controls=[
                ft.Container(content=ft.Text(day), width=self.DAY_CELL_SIZE, alignment=ft.Alignment.CENTER)
                    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.calendar_grid.controls.append(week_header)

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(year, month)

        self.leave_summary_title.content.value = f"Booked leave for {self.employeeDrop.text if self.employeeDrop.value != 'all' else 'All Employees'}"

        # Filter the list of leave entries by employee if selected in dropdown
        if self.employeeDrop.value != "all":
            leave_entries = list(filter(lambda e: e.employee_id == int(self.employeeDrop.value), 
                                        leave_entries))

        for week in month_days:
            row = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
            for day in week:
                entry_exists = None
                if day == 0:
                    row.controls.append(ft.Container(width=self.DAY_CELL_SIZE, height=self.DAY_CELL_SIZE))
                else:
                    d = date(year, month, day)
                    # Filter the list of leave entries to find if there's an entry for this day (and employee if selected)
                    day_entries = list(filter(lambda e: e.leave_date == d, leave_entries))
                    cell = self.create_day_cell(day, day_entries)
                    cell.on_click = lambda e, d=d: self._open_leave_dialog(d)
                    row.controls.append(cell)
            self.calendar_grid.controls.append(row)

        # Filter leave entries for this date range
        leave_entries = list(filter(lambda e: e.leave_date.month == month and e.leave_date.year == year, leave_entries))

        # Update the selected_text control to show the leave entries for the month
        # If there are no entries, show "No leave booked". If there are entries, show the date, employee name (if employee filter is not applied), leave type and duration, and description if exists
        self.leave_summary.controls[0].value = ""
        if len(leave_entries) > 0:
            # Sort the entries by date
            leave_entries = sorted(leave_entries, key=lambda e: e.leave_date)
            for e in leave_entries:
                emp_name = ""
                if self.employeeDrop.value == "all":
                    emp_name = f"{self.controller.get_employee_name(e.employee_id)} ({self.controller.get_employee_abbrev(e.employee_id)})"
                self.leave_summary.controls[0].value += f"{e.leave_date} ({e.duration.value}): {emp_name} {e.leave_type.value.name} {f'- {e.description}' if e.description else ''}\n"
        else:
            self.leave_summary.controls[0].value += "No leave booked"
        self.page.update()

    # ---- Employee dialog handlers ----
    def _open_employee_dialog(self, emp=None):

        # If emp not specified assume this is an add new operation
        if emp == None:
            # Add code goes here

            # Update the dialog title and buttons visibility for add vs edit operation
            self.employee_dialog.title = "Add Employee"
            self.employee_input_name.value = ""
            self.employee_input_abbrev.value = ""
            self.employee_dialog.actions[2].visible = True
            self.employee_dialog.actions[3].visible = False

        # Must have an employee selected if it's edit
        elif emp == "all":
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Please select an employee to edit")))
            return
        
        else:
            # Edit code goes here
            # Load the employee info from the database
            self.employee_dialog.title = "Update Employee"
            self.employee_input_name.value = self.controller.model.get_employee_name(int(emp))
            self.employee_input_abbrev.value = self.controller.model.get_employee_abbrev(int(emp))
            self.employee_dialog.actions[2].visible = False
            self.employee_dialog.actions[3].visible = True

        # Flet sometimes requires show_dialog to actually render the dialog
        self.employee_dialog.open = True
        self.page.show_dialog(self.employee_dialog)
        # page.update() may not be needed but safe
        self.page.update()

    def _close_employee_dialog(self, e=None):
        self.employee_dialog.open = False
        self.page.update()

    def _add_employee(self, e):
        new_id = self.controller.add_employee(self.employee_input_name.value, self.employee_input_abbrev.value)
        if new_id > 0:
            self.employeeDrop.text = self.employee_input_name.value # Update the dropdown with updated employee name
            self.employeeDrop.value = new_id
            self.page.show_dialog(ft.SnackBar(content=ft.Text(f"{self.employeeDrop.text} added successfully")))
            self.controller.change_employee(new_id) # Set the new employee as the selected employee in the dropdown and refresh the calendar to show the new employee's leave (if any)
        else:
             self.page.show_dialog(ft.SnackBar(content=ft.Text(f"Failed to save {self.employee_input_name.value} to database - name and initials must be unique")))
        self._close_employee_dialog()

    def _update_employee(self, e):
        if self.controller.update_employee (int(self.employeeDrop.value), self.employee_input_name.value, self.employee_input_abbrev.value):
            self.employeeDrop.text = self.employee_input_name.value # Update the dropdown with updated employee name
            self.page.show_dialog(ft.SnackBar(content=ft.Text(f"{self.employeeDrop.text} updated successfully")))
            self.controller.refresh()  # Refresh the calendar to show the updated employee name in the dropdown and calendar
        else:             
            self.page.show_dialog(ft.SnackBar(content=ft.Text(f"Failed to update {self.employeeDrop.text} - name and initials must be unique")))
        self._close_employee_dialog()

    def _delete_employee(self, e):
        # Check if any leave booked for the employee and if so show a confirmation dialog before deleting
        if len(self.controller.get_leave_entries_for_employee(int(self.employeeDrop.value))) > 0:
            def confirm_delete(e):
                self._delete_employee_confirmed(e)
                confirm_dialog.open = False
                self.page.update()

            def cancel_delete(e):
                confirm_dialog.open = False
                self.page.update()            

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Confirm Delete"),
                content=ft.Column(controls=[
                    ft.Text(f"{self.employeeDrop.text} has leave booked. Are you sure you want to delete?"),
                    ft.Text("This will remove the employee and all their booked leave.")
                ]),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.TextButton("Delete", on_click=confirm_delete),
                ],
            )
            confirm_dialog.open = True
            self.page.show_dialog(confirm_dialog)
        else:
            self._delete_employee_confirmed(e)

    def _delete_employee_confirmed(self, e):
        if self.controller.delete_employee (int(self.employeeDrop.value)):
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Employee deleted successfully")))
            self.employeeDrop.value = "all" # Reset to "All Employees" after deletion
            self.controller.refresh()  # Refresh the calendar to show the new employee in the dropdown and
        else:
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Failed to delete employee")))
        self._close_employee_dialog()
        
    # ---- Leave dialog handlers ----
    def _open_leave_dialog(self, d: date):

        self._dialog_day = d
        # Pre-select existing values if an entry exists
        entry = self.controller.model.get_entries_for_day(d, None if self.employeeDrop.value == "all" else int(self.employeeDrop.value))

        # If more than 1 entry pmompt user to select an employee first
        if len(entry) > 1:
            self.page.show_dialog(ft.SnackBar(content=ft.Text("Please select an employee to create or edit leave")))
            return
        elif len(entry) == 1:
            selected_type = entry[0].leave_type.name
            selected_dur = entry[0].duration.name
            selected_description = entry[0].description
        else:   # No existing entry - set defaults for add new leave
            selected_type = self.controller.model.selected_leave_type.name
            selected_dur = self.controller.model.selected_duration.name
            selected_description = ""

        # set the radio group selections & desciptive text
        self.leave_type_group.value = selected_type
        self.leave_duration_group.value = selected_dur
        self.leave_description.value = selected_description

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
            self.controller.set_leave_for_day(self._dialog_day, lt, du, self.leave_description.value)

        self._close_dialog()

    def _close_dialog(self, e=None):
        self.leave_dialog.open = False
        self.page.update()
