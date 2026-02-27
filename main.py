import flet as ft
import calendar
from datetime import date

class Calendar:
    def __init__(self, page, year, month):
        self.page = page
        self.year = year
        self.month = month
        self.selected_dates = set()
        self.view = "month"  # Default view

        self.header = ft.Text("", size=20, weight="bold")
        self.calendar_grid = ft.Column()
        self.selected_text = ft.Text()
        self.build_calendar(self.year, self.month)
        self.update_selected_text()

        self.nav = ft.Row(
            [
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.prev_month),
                self.header,
                ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=self.next_month),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.view = ft.Row(
            [
                ft.IconButton(ft.Icons.CALENDAR_VIEW_DAY, on_click=lambda e: self.set_view(e, "day"), tooltip="Day View"),
                ft.IconButton(ft.Icons.CALENDAR_VIEW_WEEK, on_click=lambda e: self.set_view(e, "week"), tooltip="Week View"),
                ft.IconButton(ft.Icons.CALENDAR_VIEW_MONTH, on_click=lambda e: self.set_view(e, "month"), tooltip="Month View", selected=True),
                ft.IconButton(ft.Icons.CALENDAR_TODAY, on_click=lambda e: self.set_view(e, "year"), tooltip="Year View"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        page.add(self.nav, self.calendar_grid, self.view, ft.Divider(), self.selected_text)

    def build_calendar(self, year, month):

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
        month_days = cal.monthdayscalendar(self.year, self.month)

        for week in month_days:
            row = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
            for day in week:
                if day == 0:
                    row.controls.append(ft.Container(width=60, height=40))
                else:
                    day_date = date(year, month, day)

                    def toggle_leave(e, d=day_date):
                        if d in self.selected_dates:
                            self.selected_dates.remove(d)
                        else:
                            self.selected_dates.add(d)
                        self.build_calendar(year, month)
                        self.update_selected_text()

                    is_selected = day_date in self.selected_dates

                    row.controls.append(
                        ft.Container(
                            content=ft.Text(str(day)),
                            width=60,
                            height=40,
                            alignment=ft.Alignment.CENTER,
                            bgcolor=ft.Colors.BLUE_200 if is_selected else None,
                            border=ft.Border.all(1, ft.Colors.GREY_300),
                            on_click=toggle_leave,
                        )
                    )
            self.calendar_grid.controls.append(row)

    def update_selected_text(self):
        if self.selected_dates:
            sorted_dates = sorted(self.selected_dates)
            self.selected_text.value = "Booked leave days:\n" + "\n".join(
                d.strftime("%Y-%m-%d") for d in sorted_dates
            )
        else:
            self.selected_text.value = "No leave booked"

    # Month navigation
    def prev_month(self,e):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.build_calendar(self.year, self.month)

    def next_month(self, e):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.build_calendar(self.year, self.month)

    def set_view(self, e, view: str):
        self.view = view
        self.build_calendar(self.year, self.month)

# Main function to run the app
def main(page: ft.Page):
    page.title = "Leave Tracker Calendar"

    today = date.today()

    # Create a calendar object
    calendar = Calendar(page, today.year, today.month)

    page.update()

# App entry point
if __name__ == "__main__":
    ft.run(main)