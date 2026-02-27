import flet as ft
import calendar
from datetime import date

def main(page: ft.Page):
    page.title = "Leave Tracker Calendar"

    today = date.today()
    current_year = today.year
    current_month = today.month
    current_view = "month"

    selected_dates = set()

    header = ft.Text("", size=20, weight="bold")
    calendar_grid = ft.Column()
    selected_text = ft.Text()

    def build_calendar(year, month):
        header.value = f"{calendar.month_name[month]} {year}"
        calendar_grid.controls.clear()

        # Weekday headers
        week_header = ft.Row(
            controls=[
                ft.Container(content=ft.Text(day), width=60, alignment=ft.Alignment.CENTER)
                    for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        calendar_grid.controls.append(week_header)

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(year, month)

        for week in month_days:
            row = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
            for day in week:
                if day == 0:
                    row.controls.append(ft.Container(width=60, height=40))
                else:
                    day_date = date(year, month, day)

                    def toggle_leave(e, d=day_date):
                        if d in selected_dates:
                            selected_dates.remove(d)
                        else:
                            selected_dates.add(d)
                        build_calendar(year, month)
                        update_selected_text()

                    is_selected = day_date in selected_dates

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
            calendar_grid.controls.append(row)

        page.update()

    def update_selected_text():
        if selected_dates:
            sorted_dates = sorted(selected_dates)
            selected_text.value = "Booked leave days:\n" + "\n".join(
                d.strftime("%Y-%m-%d") for d in sorted_dates
            )
        else:
            selected_text.value = "No leave booked"
        page.update()

    # Month navigation
    def prev_month(e):
        nonlocal current_month, current_year
        current_month -= 1
        if current_month == 0:
            current_month = 12
            current_year -= 1
        build_calendar(current_year, current_month)

    def next_month(e):
        nonlocal current_month, current_year
        current_month += 1
        if current_month == 13:
            current_month = 1
            current_year += 1
        build_calendar(current_year, current_month)

    def set_view(e, view: str):
        nonlocal current_view
        current_view = view
        build_calendar(current_year, current_month)

    nav = ft.Row(
        [
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=prev_month),
            header,
            ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=next_month),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    view = ft.Row(
        [
            ft.IconButton(ft.Icons.CALENDAR_VIEW_DAY, on_click=lambda e: set_view(e, "day"), tooltip="Day View"),
            ft.IconButton(ft.Icons.CALENDAR_VIEW_WEEK, on_click=lambda e: set_view(e, "week"), tooltip="Week View"),
            ft.IconButton(ft.Icons.CALENDAR_VIEW_MONTH, on_click=lambda e: set_view(e, "month"), tooltip="Month View", selected=True),
            ft.IconButton(ft.Icons.CALENDAR_TODAY, on_click=lambda e: set_view(e, "year"), tooltip="Year View"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    build_calendar(current_year, current_month)
    update_selected_text()

    page.add(nav, calendar_grid, view, ft.Divider(), selected_text)


ft.run(main)