import flet as ft
import re
from modelo.contacto_modelo import ContactoModel
from vista.contacto_vista import ContactoView

class ContactoController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.view = ContactoView(page)
        ContactoModel.crear_tabla()
        self.crear_ui()

    # --- VALIDACIÓN ---
    def validar_campos(self, nombre, telefono, correo):
        if not nombre.strip():
            self.view.mostrar_mensaje("¡Ups! El nombre no puede estar vacío.", tipo="error")
            return False
        if not telefono.strip() or not re.match(r"^\+?\d[\d\s]{7,15}$", telefono.strip()):
            self.view.mostrar_mensaje("Teléfono inválido. Ej: +595 9 XX XXX XXX", tipo="error")
            return False
        if correo.strip() and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo.strip()):
            self.view.mostrar_mensaje("Correo inválido.", tipo="error")
            return False
        return True

    # --- CREACIÓN DE UI ---
    def crear_ui(self):
        self.page.title = "Agenda de Contactos"
        self.page.window_width = 500
        self.page.window_height = 750
        self.page.scroll = "adaptive"

        # Campos de agregar
        self.nombre = ft.TextField(label="Nombre", width=400, icon=ft.Icons.PERSON, hint_text="Nombre completo")
        self.telefono = ft.TextField(label="Teléfono", width=400, icon=ft.Icons.PHONE, hint_text="Ej: +595 9 XX XXX XXX")
        self.correo = ft.TextField(label="Correo", width=400, icon=ft.Icons.EMAIL, hint_text="ejemplo@mail.com")

        # Pantalla guardar
        self.pantalla_guardar = ft.Column([
            ft.Text("📇 Agregar Nuevo Contacto", size=28, weight=ft.FontWeight.BOLD, color=self.view.color_primario),
            ft.Divider(thickness=2, color=self.view.color_primario),
            self.nombre, self.telefono, self.correo,
            ft.FilledButton("💾 Guardar Contacto", on_click=self.guardar_contacto,
                            bgcolor=self.view.color_primario, color=self.view.texto_color, width=220,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

        # Pantallas eliminar y editar
        self.lista_eliminar = ft.Column(scroll="adaptive", spacing=12)
        self.filtro_eliminar = ft.TextField(label="Buscar contacto", icon=ft.Icons.SEARCH, width=420,
                                            on_change=lambda e: self.cargar_lista_eliminar(e.control.value))
        self.pantalla_eliminar = ft.Column([
            ft.Text("🗑️ Eliminar Contactos", size=28, weight=ft.FontWeight.BOLD, color=self.view.color_primario),
            ft.Divider(thickness=2, color=self.view.color_primario),
            self.filtro_eliminar,
            ft.Container(self.lista_eliminar, expand=True)
        ], expand=True)

        self.lista_editar = ft.ListView(expand=True, spacing=12)
        self.filtro_editar = ft.TextField(label="Buscar contacto", icon=ft.Icons.SEARCH, width=420,
                                         on_change=lambda e: self.cargar_lista_editar(e.control.value))
        self.pantalla_editar = ft.Column([
            ft.Text("✏️ Editar Contactos", size=28, weight=ft.FontWeight.BOLD, color=self.view.color_primario),
            ft.Divider(thickness=2, color=self.view.color_primario),
            self.filtro_editar,
            self.lista_editar
        ], expand=True)

        # Encabezado y contenedor principal
        encabezado = ft.Row(controls=[
            ft.IconButton(icon=ft.Icons.MENU, on_click=lambda e: self.abrir_menu()),
            ft.Text("📖 Agenda de Contactos", size=26, weight=ft.FontWeight.BOLD, color=self.view.color_primario)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.contenedor = ft.Container(content=ft.Column([self.pantalla_guardar], expand=True))

        # Barra de navegación
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

        # Menu opciones
        self.menu_contenedor = ft.Container(
            content=ft.Column([
                ft.Text("⚙️ Opciones", size=22, weight=ft.FontWeight.BOLD, color=self.view.color_primario),
                ft.ElevatedButton("🌗 Cambiar Tema", on_click=lambda e: self.toggle_theme()),
                ft.ElevatedButton("🧹 Limpiar Contactos", on_click=lambda e: self.limpiar_contactos()),
                ft.FilledButton("❌ Cerrar", on_click=lambda e: self.cerrar_menu())
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

    # --- FUNCIONES DE CONTROLLER ---
    def guardar_contacto(self, e):
        n, t, co = self.nombre.value.strip(), self.telefono.value.strip(), self.correo.value.strip()
        if not self.validar_campos(n, t, co):
            return
        ContactoModel.agregar_contacto(n, t, co)
        self.nombre.value = self.telefono.value = self.correo.value = ""
        self.view.mostrar_mensaje("Contacto guardado exitosamente 🎉")
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
            idc = c[0]  # Captura correcta de id
            def borrar(e, idc=idc):
                ContactoModel.eliminar_contacto(idc)
                self.view.mostrar_mensaje("Contacto eliminado correctamente 🗑️")
                self.cargar_lista_eliminar(self.filtro_eliminar.value)
                self.cargar_lista_editar(self.filtro_editar.value)

            self.lista_eliminar.controls.append(
                ft.Card(
                    elevation=8,
                    content=ft.Container(
                        bgcolor="#282828" if self.page.bgcolor != self.view.FONDO_CLARO else self.page.bgcolor,
                        border_radius=25,
                        padding=12,
                        content=ft.Row([
                            ft.Column([
                                ft.Text(c[1], color=self.view.texto_color, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"📞 {c[2]}  ✉️ {c[3] if c[3] else '-'}", color=self.view.texto_secundario, size=13)
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
            campos = [
                ft.TextField(value=nombrec, label="Nombre", expand=True, color=self.view.texto_color, bgcolor=self.page.bgcolor),
                ft.TextField(value=telc, label="Teléfono", expand=True, color=self.view.texto_color, bgcolor=self.page.bgcolor),
                ft.TextField(value=corr, label="Correo", expand=True, color=self.view.texto_color, bgcolor=self.page.bgcolor)
            ]

            # Captura correcta de idc y campos en lambda
            def guardar_local(e, id_=idc, campos_local=campos):
                n, t, co = [f.value.strip() for f in campos_local]
                if not self.validar_campos(n, t, co):
                    return
                ContactoModel.editar_contacto(id_, n, t, co)
                self.view.mostrar_mensaje("Contacto actualizado ✨")
                self.cargar_lista_editar(self.filtro_editar.value)
                self.cargar_lista_eliminar(self.filtro_eliminar.value)

            self.lista_editar.controls.append(
                ft.Card(
                    elevation=8,
                    content=ft.Container(
                        bgcolor="#282828" if self.page.bgcolor != self.view.FONDO_CLARO else self.page.bgcolor,
                        border_radius=25,
                        padding=12,
                        content=ft.Row([
                            ft.Column(campos, expand=True),
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
        if self.page.bgcolor == self.view.FONDO_OSCURO:
            self.page.bgcolor = self.view.FONDO_CLARO
            self.view.texto_color = self.view.TEXTO_CLARO
            self.view.texto_secundario = self.view.TEXTO_SECUNDARIO_CLARO
        else:
            self.page.bgcolor = self.view.FONDO_OSCURO
            self.view.texto_color = self.view.TEXTO_OSCURO
            self.view.texto_secundario = self.view.TEXTO_SECUNDARIO_OSCURO
        self.cargar_lista_eliminar(self.filtro_eliminar.value)
        self.cargar_lista_editar(self.filtro_editar.value)
        self.page.update()

    def limpiar_contactos(self):
        ContactoModel.limpiar_todos_contactos()
        self.cargar_lista_eliminar()
        self.cargar_lista_editar()
        self.view.mostrar_mensaje("Todos los contactos fueron eliminados con éxito 🧹")

    def abrir_menu(self):
        self.menu_contenedor.visible = True
        self.page.update()

    def cerrar_menu(self):
        self.menu_contenedor.visible = False
        self.page.update()
