import flet as ft

from model import LeaveType, LeaveDuration

def create_day_cell(day_number, leave_type: LeaveType, leave_duration: LeaveDuration=None, on_click=None):
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
            on_click=on_click,
        )

    return ft.Container(
        content=ft.Text(str(day_number)),
        width=60,
        height=60,
        alignment=ft.Alignment.CENTER,
        border=ft.border.all(1, bg_color),
        bgcolor=bg_color,
        gradient=bg_gradient,
        on_click=on_click
    )


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Row([
            create_day_cell(1, LeaveType.HOLIDAY, leave_duration=LeaveDuration.AM),
            create_day_cell(2, LeaveType.SICK, leave_duration=LeaveDuration.PM),
            create_day_cell(3, LeaveType.UNPAID, leave_duration=LeaveDuration.FULL),
            create_day_cell(4, None)])
    )


ft.run(main)