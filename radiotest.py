import flet as ft

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
                    bgcolor=ft.Colors.WHITE,
                ),

                ft.Container(
                    content=content,
                    padding=15,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                )                # Box content
            ],
        )

        self.width = width

def main(page: ft.Page):
    radio_group = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="1", label="Option 1"),
            ft.Radio(value="2", label="Option 2"),
            ft.Radio(value="3", label="Option 3"),
        ])
    )

    group = GroupBox("Select an option", radio_group, width=300)

    page.add(group)

    page.update()

if __name__ == "__main__":
    ft.run(main)