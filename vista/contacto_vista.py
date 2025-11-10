import flet as ft
import threading
import time

class ContactoView:
    def __init__(self, page):
        self.page = page

        # Paleta
        self.SPOTIFY_VERDE = "#1DB954"
        self.FONDO_OSCURO = "#191414"
        self.FONDO_CLARO = "#F5F5F5"
        self.TEXTO_OSCURO = "#FFFFFF"
        self.TEXTO_CLARO = "#000000"
        self.TEXTO_SECUNDARIO_OSCURO = "#B3B3B3"
        self.TEXTO_SECUNDARIO_CLARO = "#555555"

        self.page.bgcolor = self.FONDO_OSCURO
        self.texto_color = self.TEXTO_OSCURO
        self.texto_secundario = self.TEXTO_SECUNDARIO_OSCURO
        self.color_primario = self.SPOTIFY_VERDE

        # Mensaje flotante
        self.mensaje_flotante = ft.Column(
            expand=False, visible=False,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.page.overlay.append(self.mensaje_flotante)

    def mostrar_mensaje(self, msg, tipo="success"):
        color_bg = self.SPOTIFY_VERDE if tipo=="success" else "#FF5555"
        mensaje = ft.Container(
            content=ft.Text(msg, color=self.TEXTO_OSCURO, weight=ft.FontWeight.BOLD, size=16),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=color_bg,
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=15, color="#00000080", offset=ft.Offset(0, 4)),
        )
        self.mensaje_flotante.controls.clear()
        self.mensaje_flotante.controls.append(mensaje)
        self.mensaje_flotante.visible = True
        self.page.update()

        def ocultar():
            time.sleep(2)
            self.mensaje_flotante.visible = False
            self.page.update()
        threading.Thread(target=ocultar, daemon=True).start()
