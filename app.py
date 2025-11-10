import flet as ft
from controlador.contacto_controlador import ContactoController

def main(page: ft.Page):
    ContactoController(page)

ft.app(target=main)
