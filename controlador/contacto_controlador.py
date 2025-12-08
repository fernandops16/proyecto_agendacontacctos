import flet as ft
import re
import csv
from datetime import datetime
from modelo.contacto_modelo import ContactoModel
from vista.contacto_vista import ContactoView

class ContactoController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.view = ContactoView(page)
        ContactoModel.crear_tabla()
        self.crear_ui()

    # --- LIMPIAR ERRORES VISUALES ---
    def limpiar_errores(self):
        for campo in [self.nombre, self.telefono, self.correo]:
            campo.error_text = None
            campo.border_color = None

    # --- VALIDACIÓN ---
    def validar_campos(self, nombre, telefono, correo):
        self.limpiar_errores()
        valido = True

        if not nombre.strip():
            self.nombre.error_text = "El nombre no puede quedar vacío"
            self.nombre.border_color = "#FF6F00"
            self.view.mostrar_mensaje("El nombre es obligatorio.", tipo="error")
            valido = False

        if not telefono.strip() or not re.match(r"^\+?\d[\d\s]{7,15}$", telefono.strip()):
            self.telefono.error_text = "Teléfono inválido"
            self.telefono.border_color = "#FF6F00"
            self.view.mostrar_mensaje("Teléfono inválido. Ej: +595 9 XX XXX XXX", tipo="error")
            valido = False

        if correo.strip() and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo.strip()):
            self.correo.error_text = "Correo inválido"
            self.correo.border_color = "#FF6F00"
            self.view.mostrar_mensaje("Correo inválido.", tipo="error")
            valido = False

        self.page.update()
        return valido

    # --- CREACIÓN DE UI ---
    def crear_ui(self):
        self.page.title = "Agenda de contactos"
        self.page.window_width = 500
        self.page.window_height = 750
        self.page.scroll = "adaptive"

        # Paleta naranja y negro (modo oscuro por defecto)
        self.page.bgcolor = "#121212"
        self.view.color_primario = "#FF6F00"
        self.view.texto_color = "#FFFFFF"
        self.view.texto_secundario = "#CCCCCC"

        # --- Campos de agregar ---
        self.nombre = ft.TextField(
            label="Nombre", width=400, icon=ft.Icons.PERSON,
            hint_text="Nombre completo", bgcolor="#1E1E1E",
            color=self.view.texto_color, hint_style=ft.TextStyle(color="#AAAAAA")
        )
        self.telefono = ft.TextField(
            label="Teléfono", width=400, icon=ft.Icons.PHONE,
            hint_text="Ej: +595 9 XX XXX XXX", bgcolor="#1E1E1E",
            color=self.view.texto_color, hint_style=ft.TextStyle(color="#AAAAAA")
        )
        self.correo = ft.TextField(
            label="Correo", width=400, icon=ft.Icons.EMAIL,
            hint_text="ejemplo@mail.com", bgcolor="#1E1E1E",
            color=self.view.texto_color, hint_style=ft.TextStyle(color="#AAAAAA")
        )

        # --- Pantalla guardar ---
        self.pantalla_guardar = ft.Column([
            ft.Text("Agregar contacto", size=28, weight=ft.FontWeight.BOLD, color=self.view.color_primario),
            ft.Divider(thickness=2, color=self.view.color_primario),
            self.nombre, self.telefono, self.correo,
            ft.FilledButton(
                "Guardar", on_click=self.guardar_contacto,
                bgcolor=self.view.color_primario, color=self.view.texto_color, width=220,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25))
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

        # --- Pantallas eliminar y editar ---
        self.lista_eliminar = ft.Column(scroll="adaptive", spacing=12)
        self.filtro_eliminar = ft.TextField(
            label="Buscar", icon=ft.Icons.SEARCH, width=420, bgcolor="#1E1E1E",
            color=self.view.texto_color, hint_style=ft.TextStyle(color="#AAAAAA"),
            on_change=lambda e: self.cargar_lista_eliminar(e.control.value)
        )
        self.pantalla_eliminar = ft.Column([
            ft.Text("Eliminar contactos", size=28, weight=ft.FontWeight.BOLD, color=self.view.color_primario),
            ft.Divider(thickness=2, color=self.view.color_primario),
            self.filtro_eliminar,
            ft.Container(self.lista_eliminar, expand=True)
        ], expand=True)

        self.lista_editar = ft.ListView(expand=True, spacing=12)
        self.filtro_editar = ft.TextField(
            label="Buscar", icon=ft.Icons.SEARCH, width=420, bgcolor="#1E1E1E",
            color=self.view.texto_color, hint_style=ft.TextStyle(color="#AAAAAA"),
            on_change=lambda e: self.cargar_lista_editar(e.control.value)
        )
        self.pantalla_editar = ft.Column([
            ft.Text("Editar contactos", size=28, weight=ft.FontWeight.BOLD, color=self.view.color_primario),
            ft.Divider(thickness=2, color=self.view.color_primario),
            self.filtro_editar,
            self.lista_editar
        ], expand=True)

        # --- Encabezado y contenedor principal ---
        encabezado = ft.Row([
            ft.IconButton(icon=ft.Icons.MENU, on_click=lambda e: self.abrir_menu()),
            ft.Text("Agenda", size=26, weight=ft.FontWeight.BOLD, color=self.view.color_primario)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.contenedor = ft.Container(content=ft.Column([self.pantalla_guardar], expand=True))

        # --- Barra de navegación ---
        barra_nav = ft.NavigationBar(
            bgcolor=self.page.bgcolor,
            selected_index=0,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.ADD, label="Guardar"),
                ft.NavigationBarDestination(icon=ft.Icons.DELETE, label="Eliminar"),
                ft.NavigationBarDestination(icon=ft.Icons.EDIT, label="Editar"),
            ],
            on_change=lambda e: self.cambiar_pantalla(e.control.selected_index)
        )

        # --- Menu opciones ---
        self.menu_contenedor = ft.Container(
            content=ft.Column([
                ft.Text("Opciones", size=22, weight=ft.FontWeight.BOLD, color=self.view.color_primario),
                ft.ElevatedButton("Cambiar tema", on_click=lambda e: self.toggle_theme()),
                ft.ElevatedButton("Limpiar contactos", on_click=lambda e: self.limpiar_contactos()),
                ft.ElevatedButton("Exportar a CSV", on_click=lambda e: self.exportar_contactos_csv()),  # NUEVO
                ft.FilledButton("Cerrar", on_click=lambda e: self.cerrar_menu())
            ], spacing=12),
            bgcolor=self.page.bgcolor,
            padding=20,
            border_radius=ft.border_radius.all(20),
            visible=False,
            width=370,
            height=400
        )
        stack_menu = ft.Stack(controls=[self.menu_contenedor], expand=True, alignment=ft.Alignment(0, 0))

        self.page.add(ft.Stack([ft.Column([encabezado, self.contenedor], expand=True),
                                self.view.mensaje_flotante, stack_menu], expand=True), barra_nav)

    # --- FUNCIONES DE CONTACTOS ---
    def guardar_contacto(self, e):
        n, t, co = self.nombre.value.strip(), self.telefono.value.strip(), self.correo.value.strip()
        if not self.validar_campos(n, t, co):
            return
        ContactoModel.agregar_contacto(n, t, co)
        self.nombre.value = self.telefono.value = self.correo.value = ""
        self.view.mostrar_mensaje("Contacto guardado.")
        self.cargar_lista_eliminar()
        self.cargar_lista_editar()
        self.page.update()

    def cargar_lista_eliminar(self, filtro=""):
        self.lista_eliminar.controls.clear()
        contactos = ContactoModel.obtener_contactos()
        filtro = filtro.lower().strip()
        if filtro:
            contactos = [c for c in contactos if filtro in c[1].lower() or filtro in c[2].lower() or (c[3] and filtro in c[3].lower())]

        for c in contactos:
            idc = c[0]
            def borrar(e, idc=idc):
                ContactoModel.eliminar_contacto(idc)
                self.view.mostrar_mensaje("Contacto eliminado.")
                self.cargar_lista_eliminar(self.filtro_eliminar.value)
                self.cargar_lista_editar(self.filtro_editar.value)

            self.lista_eliminar.controls.append(
                ft.Card(
                    elevation=8,
                    content=ft.Container(
                        bgcolor="#1E1E1E" if self.page.bgcolor == "#121212" else "#FFF3E0",
                        border_radius=25,
                        padding=12,
                        content=ft.Row([
                            ft.Column([
                                ft.Text(c[1], color=self.view.texto_color, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Tel: {c[2]}  Correo: {c[3] if c[3] else '-'}",
                                        color=self.view.texto_secundario, size=13)
                            ], expand=True),
                            ft.IconButton(icon=ft.Icons.DELETE_FOREVER_ROUNDED, icon_color=self.view.color_primario, on_click=borrar)
                        ])
                    )
                )
            )
        self.page.update()

    def cargar_lista_editar(self, filtro=""):
        self.lista_editar.controls.clear()
        contactos = ContactoModel.obtener_contactos()
        filtro = filtro.lower().strip()
        if filtro:
            contactos = [c for c in contactos if filtro in c[1].lower() or filtro in c[2].lower() or (c[3] and filtro in c[3].lower())]

        for c in contactos:
            idc, nombrec, telc, corr = c[:4]

            campo_nombre = ft.TextField(value=nombrec, label="Nombre", expand=True,
                                        color=self.view.texto_color, bgcolor=self.nombre.bgcolor,
                                        hint_style=ft.TextStyle(color="#616161"))
            campo_tel = ft.TextField(value=telc, label="Teléfono", expand=True,
                                     color=self.view.texto_color, bgcolor=self.telefono.bgcolor,
                                     hint_style=ft.TextStyle(color="#616161"))
            campo_cor = ft.TextField(value=corr, label="Correo", expand=True,
                                     color=self.view.texto_color, bgcolor=self.correo.bgcolor,
                                     hint_style=ft.TextStyle(color="#616161"))
            campos = [campo_nombre, campo_tel, campo_cor]

            def guardar_local(e, id_=idc, campos_local=campos):
                n, t, co = [f.value.strip() for f in campos_local]

                valido = True
                for f in campos_local:
                    f.error_text = None
                    f.border_color = None

                if not n:
                    campo_nombre.error_text = "El nombre no puede quedar vacío"
                    campo_nombre.border_color = "#FF6F00"
                    valido = False

                if not t or not re.match(r"^\+?\d[\d\s]{7,15}$", t):
                    campo_tel.error_text = "Teléfono inválido"
                    campo_tel.border_color = "#FF6F00"
                    valido = False

                if co and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", co):
                    campo_cor.error_text = "Correo inválido"
                    campo_cor.border_color = "#FF6F00"
                    valido = False

                if not valido:
                    self.page.update()
                    return

                ContactoModel.editar_contacto(id_, n, t, co)
                self.view.mostrar_mensaje("Contacto actualizado.")
                self.cargar_lista_editar(self.filtro_editar.value)
                self.cargar_lista_eliminar(self.filtro_eliminar.value)

            self.lista_editar.controls.append(
                ft.Card(
                    elevation=8,
                    content=ft.Container(
                        bgcolor="#1E1E1E" if self.page.bgcolor == "#121212" else "#FFF3E0",
                        border_radius=25,
                        padding=12,
                        content=ft.Row([
                            ft.Column([campo_nombre, campo_tel, campo_cor], expand=True),
                            ft.IconButton(icon=ft.Icons.SAVE, icon_color=self.view.color_primario, on_click=guardar_local)
                        ])
                    )
                )
            )
        self.page.update()

    def cambiar_pantalla(self, index):
        self.contenedor.content.controls.clear()
        if index == 0:
            self.contenedor.content.controls.append(self.pantalla_guardar)
        elif index == 1:
            self.cargar_lista_eliminar(self.filtro_eliminar.value)
            self.contenedor.content.controls.append(self.pantalla_eliminar)
        elif index == 2:
            self.cargar_lista_editar(self.filtro_editar.value)
            self.contenedor.content.controls.append(self.pantalla_editar)
        self.page.update()

    def toggle_theme(self):
        # Alterna entre tema oscuro y claro con buena visibilidad
        if self.page.bgcolor == "#121212":
            self.page.bgcolor = "#FFF8E1"
            self.view.color_primario = "#FF6F00"
            self.view.texto_color = "#212121"
            self.view.texto_secundario = "#424242"
        else:
            self.page.bgcolor = "#121212"
            self.view.color_primario = "#FF6F00"
            self.view.texto_color = "#FFFFFF"
            self.view.texto_secundario = "#CCCCCC"

        # Ajustar TextField
        for campo in [self.nombre, self.telefono, self.correo, self.filtro_eliminar, self.filtro_editar]:
            if self.page.bgcolor == "#121212":
                campo.bgcolor = "#1E1E1E"
                campo.color = self.view.texto_color
                campo.hint_style = ft.TextStyle(color="#AAAAAA")
            else:
                campo.bgcolor = "#FFF3E0"
                campo.color = self.view.texto_color
                campo.hint_style = ft.TextStyle(color="#616161")

        self.cargar_lista_eliminar(self.filtro_eliminar.value)
        self.cargar_lista_editar(self.filtro_editar.value)
        self.page.update()

    def limpiar_contactos(self):
        ContactoModel.limpiar_todos_contactos()
        self.cargar_lista_eliminar()
        self.cargar_lista_editar()
        self.view.mostrar_mensaje("Todos los contactos eliminados.")

    def abrir_menu(self):
        self.menu_contenedor.visible = True
        self.page.update()

    def cerrar_menu(self):
        self.menu_contenedor.visible = False
        self.page.update()

    # --- NUEVA FUNCIÓN: EXPORTAR CONTACTOS A CSV ---
    def exportar_contactos_csv(self):
        contactos = ContactoModel.obtener_contactos()
        if not contactos:
            self.view.mostrar_mensaje("No hay contactos para exportar.", tipo="error")
            return

        archivo = f"contactos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            with open(archivo, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Nombre", "Teléfono", "Correo"])
                for c in contactos:
                    writer.writerow(c)
            self.view.mostrar_mensaje(f"Contactos exportados a {archivo}")
        except Exception as e:
            self.view.mostrar_mensaje(f"Error al exportar: {str(e)}", tipo="error")
