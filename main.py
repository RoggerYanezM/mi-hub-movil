import flet as ft
from src.db import supabase, get_items, add_item, update_capitulo, delete_item

def main(page: ft.Page):
    page.title = "MyLife Hub Móvil"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 390
    page.window.height = 844
    page.padding = 15

    # Contenedor principal de vistas
    main_container = ft.Column(expand=True)

    def mostrar_login():
        main_container.controls.clear()
        
        email_input = ft.TextField(label="Correo electrónico", prefix_icon=ft.Icons.EMAIL)
        pass_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
        error_text = ft.Text(color=ft.Colors.RED_400)

        def hacer_login(e):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email_input.value,
                    "password": pass_input.value
                })
                page.session.set("user", res.user)
                cargar_dashboard()
            except Exception as ex:
                error_text.value = "Error al iniciar sesión. Verifica tus datos."
                page.update()

        def hacer_registro(e):
            try:
                supabase.auth.sign_up({
                    "email": email_input.value,
                    "password": pass_input.value
                })
                error_text.value = "¡Cuenta creada! Revisa tu correo o inicia sesión."
                page.update()
            except Exception as ex:
                error_text.value = "Error en el registro."
                page.update()

        main_container.controls.append(
            ft.Column([
                ft.VerticalDivider(height=50),
                ft.Text("⚡ MyLife Hub", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text("Tu espacio personal en la nube", size=14, color=ft.Colors.GREY_400),
                ft.VerticalDivider(height=20),
                email_input,
                pass_input,
                error_text,
                ft.ElevatedButton("Iniciar Sesión", on_click=hacer_login, width=350, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                ft.OutlinedButton("Registrarse", on_click=hacer_registro, width=350),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    def cargar_dashboard():
        user = page.session.get("user")
        if not user:
            mostrar_login()
            return

        main_container.controls.clear()
        
        # Componente de la lista de animes
        lista_vista = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        def actualizar_lista():
            lista_vista.controls.clear()
            items = get_items(user.id, "Anime")
            
            for item in items:
                item_id = item["id"]
                cap_actual = item["capitulo"]
                
                def sumar_cap(e, i_id=item_id, c=cap_actual):
                    update_capitulo(i_id, c + 1)
                    actualizar_lista()

                def borrar(e, i_id=item_id):
                    delete_item(i_id)
                    actualizar_lista()

                tarjeta = ft.Container(
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border_radius=12,
                    padding=12,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column([
                                ft.Text(item["titulo"], size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Capítulo: {cap_actual} | {item['estado']}", size=13, color=ft.Colors.BLUE_200),
                            ]),
                            ft.Row([
                                ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=ft.Colors.GREEN_400, on_click=sumar_cap, tooltip="+1 Cap"),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=borrar),
                            ])
                        ]
                    )
                )
                lista_vista.controls.append(tarjeta)
            page.update()

        # Input para agregar anime rápido
        input_titulo = ft.TextField(label="Nuevo Anime / Serie", expand=True)
        
        def guardar_nuevo(e):
            if input_titulo.value:
                add_item(user.id, "Anime", input_titulo.value, capitulo=1, estado="Viendo")
                input_titulo.value = ""
                actualizar_lista()

        btn_guardar = ft.IconButton(icon=ft.Icons.SEND, icon_color=ft.Colors.BLUE_400, on_click=guardar_nuevo)

        # Estructura del Panel Principal
        panel_anime = ft.Column([
            ft.Text("📺 Mis Animes en Curso", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([input_titulo, btn_guardar]),
            ft.Divider(),
            lista_vista
        ], expand=True)

        def cambiar_tab(e):
            index = e.control.selected_index
            if index == 0:
                panel_anime.visible = True
            else:
                panel_anime.visible = False
            page.update()

        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.TV, label="Animes"),
                ft.NavigationBarDestination(icon=ft.Icons.CHECK_CIRCLE_OUTLINE, label="Tareas"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Perfil"),
            ],
            on_change=cambiar_tab
        )

        main_container.controls.append(panel_anime)
        actualizar_lista()
        page.update()

    mostrar_login()

ft.app(target=main)