import flet as ft
import os

os.environ["GDK_BACKEND"] = "x11"

def main(page: ft.Page):
    page.add(ft.Text("Olá, openSUSE!", size=30, color="green"))

ft.run(main)