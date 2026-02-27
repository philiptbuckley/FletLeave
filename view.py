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

        self.nav = ft.Row(
            [
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.prev_clicked),
                self.header,
                ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=self.next_clicked),
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

    # ---- Render methods ----
    def render_calendar(self, year, month, leave_dates):

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

        self.selected_text.value = "Booked leave days:\n" + "\n"

        booked_leave = False
        for week in month_days:
            row = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
            for day in week:
                if day == 0:
                    row.controls.append(ft.Container(width=60, height=40))
                else:
                    day_date = date(year, month, day)

                    if day_date in leave_dates:
                        background_color = ft.Colors.BLUE_200
                        self.selected_text.value += f"{day_date.strftime('%Y-%m-%d')}\n"
                        booked_leave = True
                    else:
                        background_color = None

                    row.controls.append(
                        ft.Container(
                            content=ft.Text(str(day)),
                            width=60,
                            height=40,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=background_color,
                            border=ft.Border.all(1, ft.Colors.GREY_300),
                            on_click=lambda e, d=day_date: self.controller.toggle_leave(d),
                        )
                    )
            self.calendar_grid.controls.append(row)

        if not booked_leave:
            self.selected_text.value += "No leave booked"

        self.page.update()
