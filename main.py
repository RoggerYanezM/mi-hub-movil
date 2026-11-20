from datetime import date, datetime, timedelta
import flet as ft
from src.auth import login_con_usuario, registrar_usuario
from src.db import (
    add_item,
    add_task,
    delete_item,
    delete_task,
    get_items,
    get_tasks,
    toggle_task_completed,
    update_item,
)


CATEGORIAS = ["Anime", "Serie", "Manga", "Película", "Otro"]
ESTADOS = ["Viendo", "Pendiente", "Completado", "Pausado"]
TIPOS_TAREA = ["Entrega", "Proyecto", "Personal", "Estudio"]


def calcular_estado_fecha(fecha_str: str, aviso_dias: int, hora_str: str = ""):
    hoy = date.today()
    try:
        fecha_lim = datetime.strptime(str(fecha_str)[:10], "%Y-%m-%d").date()
    except ValueError:
        return ("Sin fecha", ft.Colors.GREY_400, False)

    dias_restantes = (fecha_lim - hoy).days
    aviso = max(0, int(aviso_dias or 0))
    hora_fmt = f" a las {hora_str[:5]}" if hora_str else ""

    if dias_restantes < 0:
        return (f"Vencida hace {abs(dias_restantes)} d{hora_fmt}", ft.Colors.RED_400, True)
    if dias_restantes == 0:
        return (f"Vence hoy{hora_fmt}", ft.Colors.RED_400, True)
    if dias_restantes <= aviso:
        aviso_txt = "Vence mañana" if dias_restantes == 1 else f"Vence en {dias_restantes} días"
        return (f"{aviso_txt}{hora_fmt}", ft.Colors.AMBER_300, True)
    return (f"En {dias_restantes} días ({fecha_lim}){hora_fmt}", ft.Colors.BLUE_200, False)


def main(page: ft.Page):
    page.title = "MyLife Hub"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 400
    page.window.height = 844
    page.padding = 0

    estado_app = {
        "user": None,
        "username": "",
        "seccion": 0,
        "filtro_cat": "Todas",
        "aviso_default": 2,
        "cat_default": "Anime",
        "estado_default": "Viendo",
        "mostrar_completadas": True,
    }
    root_view = ft.Column(expand=True)
    page.add(root_view)

    def mostrar_login(e=None):
        page.drawer = None
        page.appbar = None
        root_view.controls.clear()

        user_input = ft.TextField(
            label="Usuario",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=12,
        )
        pass_input = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=12,
        )
        msg_text = ft.Text(color=ft.Colors.RED_400, size=13)

        def on_login(ev):
            u = (user_input.value or "").strip()
            p = pass_input.value or ""
            if not u or not p:
                msg_text.value = "Ingresa tu usuario y contraseña."
                page.update()
                return
            try:
                user = login_con_usuario(u, p)
                estado_app["user"] = user
                estado_app["username"] = u
                abrir_app_principal()
            except Exception as ex:
                msg_text.value = str(ex)
                page.update()

        root_view.controls.append(
            ft.Container(
                expand=True,
                padding=24,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.BOLT_ROUNDED, size=48, color=ft.Colors.BLUE_400),
                        ft.Text("MyLife Hub", size=28, weight=ft.FontWeight.BOLD),
                        ft.Text("Tu espacio personal organizado", size=14, color=ft.Colors.GREY_400),
                        ft.Container(height=16),
                        user_input,
                        pass_input,
                        msg_text,
                        ft.Button(
                            "Iniciar Sesión",
                            on_click=on_login,
                            width=340,
                            height=46,
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE,
                        ),
                        ft.TextButton("¿No tienes cuenta? Crear cuenta", on_click=mostrar_registro),
                    ],
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
            )
        )
        page.update()

    def mostrar_registro(e=None):
        page.drawer = None
        page.appbar = None
        root_view.controls.clear()

        user_reg = ft.TextField(label="Nombre de usuario", prefix_icon=ft.Icons.PERSON_ADD, border_radius=12)
        email_reg = ft.TextField(label="Correo electrónico", prefix_icon=ft.Icons.EMAIL_OUTLINED, border_radius=12)
        pass_reg = ft.TextField(
            label="Contraseña (mín. 6 caracteres)",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=12,
        )
        msg_reg = ft.Text(color=ft.Colors.RED_400, size=13)

        def on_registro(ev):
            u = (user_reg.value or "").strip()
            em = (email_reg.value or "").strip()
            pw = pass_reg.value or ""
            if not u or not em or not pw:
                msg_reg.color = ft.Colors.RED_400
                msg_reg.value = "Completa todos los campos."
                page.update()
                return
            try:
                registrar_usuario(u, em, pw)
                msg_reg.color = ft.Colors.GREEN_400
                msg_reg.value = "¡Cuenta creada! Ahora puedes iniciar sesión."
                page.update()
            except Exception as ex:
                msg_reg.color = ft.Colors.RED_400
                msg_reg.value = str(ex)
                page.update()

        root_view.controls.append(
            ft.Container(
                expand=True,
                padding=24,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    [
                        ft.Text("Crear Cuenta", size=26, weight=ft.FontWeight.BOLD),
                        ft.Text("Registra tu usuario para iniciar sesión", size=14, color=ft.Colors.GREY_400),
                        ft.Container(height=12),
                        user_reg,
                        email_reg,
                        pass_reg,
                        msg_reg,
                        ft.Button(
                            "Registrarse",
                            on_click=on_registro,
                            width=340,
                            height=46,
                            bgcolor=ft.Colors.GREEN_600,
                            color=ft.Colors.WHITE,
                        ),
                        ft.TextButton("¿Ya tienes cuenta? Iniciar sesión", on_click=mostrar_login),
                    ],
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
            )
        )
        page.update()

    def abrir_app_principal():
        user = estado_app["user"]
        if not user:
            mostrar_login()
            return

        content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=14)
        titulo_appbar = ft.Text("Inicio", size=18, weight=ft.FontWeight.BOLD)

        def abrir_dialogo_nuevo(e=None):
            dd_cat = ft.Dropdown(
                label="Categoría",
                value=estado_app["cat_default"],
                options=[ft.dropdown.Option(c) for c in CATEGORIAS],
                border_radius=12,
            )
            tf_titulo = ft.TextField(label="Título (ej. Bleach, Breaking Bad)", border_radius=12)
            tf_cap = ft.TextField(
                label="Capítulo actual",
                value="1",
                keyboard_type=ft.KeyboardType.NUMBER,
                border_radius=12,
            )
            dd_estado = ft.Dropdown(
                label="Estado",
                value=estado_app["estado_default"],
                options=[ft.dropdown.Option(est) for est in ESTADOS],
                border_radius=12,
            )
            tf_detalle = ft.TextField(
                label="Detalle / Nota (opcional)",
                hint_text="Ej. Temporada 2, Crunchyroll...",
                border_radius=12,
            )
            err_dlg = ft.Text(color=ft.Colors.RED_400, size=12)

            def guardar_dlg(ev):
                titulo = (tf_titulo.value or "").strip()
                if not titulo:
                    err_dlg.value = "Escribe un título."
                    page.update()
                    return
                try:
                    cap_num = int((tf_cap.value or "1").strip())
                except ValueError:
                    err_dlg.value = "El capítulo debe ser un número."
                    page.update()
                    return

                add_item(
                    user_id=user.id,
                    categoria=dd_cat.value or "Anime",
                    titulo=titulo,
                    detalle=tf_detalle.value or "",
                    capitulo=cap_num,
                    estado=dd_estado.value or "Viendo",
                )
                page.pop_dialog()
                render_seccion(estado_app["seccion"])

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Nuevo Guardado", weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    [dd_cat, tf_titulo, tf_cap, dd_estado, tf_detalle, err_dlg],
                    tight=True,
                    spacing=10,
                    width=320,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    ft.Button(
                        "Guardar",
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        on_click=guardar_dlg,
                    ),
                ],
            )
            page.show_dialog(dlg)

        def abrir_dialogo_editar(item: dict):
            dd_cat = ft.Dropdown(
                label="Categoría",
                value=item.get("categoria") or "Anime",
                options=[ft.dropdown.Option(c) for c in CATEGORIAS],
                border_radius=12,
            )
            tf_titulo = ft.TextField(
                label="Título",
                value=item.get("titulo") or "",
                border_radius=12,
            )
            tf_cap = ft.TextField(
                label="Capítulo actual",
                value=str(item.get("capitulo") or 1),
                keyboard_type=ft.KeyboardType.NUMBER,
                border_radius=12,
            )
            dd_estado = ft.Dropdown(
                label="Estado",
                value=item.get("estado") or "Viendo",
                options=[ft.dropdown.Option(est) for est in ESTADOS],
                border_radius=12,
            )
            tf_detalle = ft.TextField(
                label="Detalle / Nota",
                value=item.get("detalle") or "",
                border_radius=12,
            )
            err_dlg = ft.Text(color=ft.Colors.RED_400, size=12)

            def actualizar_dlg(ev):
                titulo = (tf_titulo.value or "").strip()
                if not titulo:
                    err_dlg.value = "El título no puede quedar vacío."
                    page.update()
                    return
                try:
                    cap_num = int((tf_cap.value or "1").strip())
                except ValueError:
                    err_dlg.value = "El capítulo debe ser un número."
                    page.update()
                    return

                update_item(
                    item_id=item["id"],
                    capitulo=cap_num,
                    estado=dd_estado.value or "Viendo",
                    detalle=tf_detalle.value or "",
                    titulo=titulo,
                    categoria=dd_cat.value or "Anime",
                )
                page.pop_dialog()
                render_seccion(estado_app["seccion"])

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Actualizar progreso", weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    [dd_cat, tf_titulo, tf_cap, dd_estado, tf_detalle, err_dlg],
                    tight=True,
                    spacing=10,
                    width=320,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    ft.Button(
                        "Actualizar",
                        bgcolor=ft.Colors.GREEN_600,
                        color=ft.Colors.WHITE,
                        on_click=actualizar_dlg,
                    ),
                ],
            )
            page.show_dialog(dlg)

        def abrir_dialogo_nueva_tarea(e=None):
            fecha_inicial = date.today() + timedelta(days=2)
            tf_titulo_t = ft.TextField(
                label="Tarea o pendiente",
                hint_text="Ej. Entregar informe, revisar avance...",
                border_radius=12,
            )
            dd_tipo_t = ft.Dropdown(
                label="Tipo de tarea",
                value="Entrega",
                options=[ft.dropdown.Option(t) for t in TIPOS_TAREA],
                border_radius=12,
            )
            tf_fecha_t = ft.TextField(
                label="Fecha límite",
                value=fecha_inicial.strftime("%Y-%m-%d"),
                read_only=True,
                border_radius=12,
            )
            tf_hora_t = ft.TextField(
                label="Horario límite (HH:MM)",
                value="23:59",
                hint_text="Ej. 18:30 o 23:59",
                prefix_icon=ft.Icons.SCHEDULE,
                border_radius=12,
            )
            tf_aviso_t = ft.TextField(
                label="Avisar cuántos días antes",
                value=str(estado_app["aviso_default"]),
                keyboard_type=ft.KeyboardType.NUMBER,
                border_radius=12,
            )
            err_t = ft.Text(color=ft.Colors.RED_400, size=12)

            def al_elegir_fecha(ev):
                valor = ev.control.value
                if valor:
                    fecha_sel = valor.date() if isinstance(valor, datetime) else valor
                    tf_fecha_t.value = fecha_sel.strftime("%Y-%m-%d")
                    page.update()

            date_picker = ft.DatePicker(
                value=fecha_inicial,
                first_date=date(2024, 1, 1),
                last_date=date(2035, 12, 31),
                on_change=al_elegir_fecha,
            )

            def abrir_calendario(ev):
                page.show_dialog(date_picker)

            def guardar_t(ev):
                titulo = (tf_titulo_t.value or "").strip()
                fecha_str = (tf_fecha_t.value or "").strip()
                hora_str = (tf_hora_t.value or "23:59").strip()
                if not titulo:
                    err_t.value = "Escribe el nombre de la tarea."
                    page.update()
                    return
                try:
                    datetime.strptime(fecha_str, "%Y-%m-%d")
                except ValueError:
                    err_t.value = "Selecciona una fecha válida del calendario."
                    page.update()
                    return
                try:
                    datetime.strptime(hora_str, "%H:%M")
                except ValueError:
                    err_t.value = "Usa el formato de hora HH:MM (ej. 14:30)."
                    page.update()
                    return
                try:
                    aviso_num = max(0, int((tf_aviso_t.value or "2").strip()))
                except ValueError:
                    err_t.value = "Los días de aviso deben ser un número."
                    page.update()
                    return

                add_task(
                    user_id=user.id,
                    titulo=titulo,
                    tipo=dd_tipo_t.value or "Personal",
                    fecha_limite=fecha_str,
                    hora_limite=hora_str,
                    aviso_dias=aviso_num,
                )
                page.pop_dialog()
                render_seccion(2)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Nueva Tarea", weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    [
                        tf_titulo_t,
                        dd_tipo_t,
                        ft.Row(
                            [
                                ft.Container(expand=True, content=tf_fecha_t),
                                ft.IconButton(
                                    icon=ft.Icons.CALENDAR_MONTH,
                                    icon_color=ft.Colors.BLUE_400,
                                    tooltip="Elegir en calendario",
                                    on_click=abrir_calendario,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        tf_hora_t,
                        tf_aviso_t,
                        err_t,
                    ],
                    tight=True,
                    spacing=10,
                    width=320,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog()),
                    ft.Button(
                        "Crear tarea",
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        on_click=guardar_t,
                    ),
                ],
            )
            page.show_dialog(dlg)

        def build_guardados_list(categoria_filtro: str = "Todas", solo_lectura: bool = False):
            col = ft.Column(spacing=10)
            items = get_items(user.id, categoria_filtro)
            if not items:
                col.controls.append(
                    ft.Container(
                        padding=20,
                        border_radius=12,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        content=ft.Text("Aún no tienes registros en esta categoría.", color=ft.Colors.GREY_400),
                    )
                )
                return col

            for item in items:
                item_id = item["id"]
                cap_actual = item.get("capitulo", 1)
                cat = item.get("categoria", "Anime")
                est = item.get("estado", "Viendo")
                det = item.get("detalle")

                subtitulo_lineas = [
                    ft.Text(
                        f"{cat}  •  Cap. {cap_actual}  •  {est}",
                        size=13,
                        color=ft.Colors.BLUE_200,
                    )
                ]
                if det:
                    subtitulo_lineas.append(
                        ft.Text(det, size=12, color=ft.Colors.GREY_400)
                    )

                acciones = []
                if not solo_lectura:
                    def on_edit(e, it=item):
                        abrir_dialogo_editar(it)

                    def on_delete(e, i_id=item_id):
                        delete_item(i_id)
                        render_seccion(estado_app["seccion"])

                    acciones = [
                        ft.IconButton(
                            icon=ft.Icons.EDIT_OUTLINED,
                            icon_color=ft.Colors.AMBER_300,
                            tooltip="Actualizar capítulo / estado",
                            on_click=on_edit,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Eliminar",
                            on_click=on_delete,
                        ),
                    ]

                col.controls.append(
                    ft.Container(
                        padding=14,
                        border_radius=14,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(
                                    [
                                        ft.Text(item.get("titulo", "Sin título"), size=16, weight=ft.FontWeight.BOLD),
                                        *subtitulo_lineas,
                                    ],
                                    spacing=3,
                                    expand=True,
                                ),
                                *([ft.Row(acciones, spacing=0)] if acciones else []),
                            ],
                        ),
                    )
                )
            return col

        def render_seccion(idx: int):
            estado_app["seccion"] = idx
            content_area.controls.clear()
            todos = get_items(user.id, "Todas")
            tareas = get_tasks(user.id)

            total_caps = sum(int(x.get("capitulo", 0) or 0) for x in todos)
            en_curso = sum(1 for x in todos if x.get("estado") == "Viendo")
            alertas_activas = [
                t for t in tareas
                if not t.get("completada")
                and calcular_estado_fecha(
                    t.get("fecha_limite", ""), t.get("aviso_dias", 2), t.get("hora_limite", "")
                )[2]
            ]

            if idx == 0:
                titulo_appbar.value = "Inicio"
                inicio_controles = [
                    ft.Container(
                        padding=16,
                        border_radius=16,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        content=ft.Column(
                            [
                                ft.Text(f"Hola, {estado_app['username']}", size=22, weight=ft.FontWeight.BOLD),
                                ft.Text("Resumen general de tu espacio", size=13, color=ft.Colors.GREY_400),
                                ft.Container(height=8),
                                ft.Row(
                                    [
                                        ft.Container(
                                            expand=True,
                                            padding=12,
                                            border_radius=12,
                                            bgcolor=ft.Colors.SURFACE_CONTAINER,
                                            content=ft.Column(
                                                [
                                                    ft.Text(str(len(todos)), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
                                                    ft.Text("Guardados", size=12, color=ft.Colors.GREY_400),
                                                ],
                                                spacing=2,
                                            ),
                                        ),
                                        ft.Container(
                                            expand=True,
                                            padding=12,
                                            border_radius=12,
                                            bgcolor=ft.Colors.SURFACE_CONTAINER,
                                            content=ft.Column(
                                                [
                                                    ft.Text(str(en_curso), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_300),
                                                    ft.Text("Viendo", size=12, color=ft.Colors.GREY_400),
                                                ],
                                                spacing=2,
                                            ),
                                        ),
                                        ft.Container(
                                            expand=True,
                                            padding=12,
                                            border_radius=12,
                                            bgcolor=ft.Colors.SURFACE_CONTAINER,
                                            content=ft.Column(
                                                [
                                                    ft.Text(str(total_caps), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_300),
                                                    ft.Text("Capítulos", size=12, color=ft.Colors.GREY_400),
                                                ],
                                                spacing=2,
                                            ),
                                        ),
                                    ],
                                    spacing=8,
                                ),
                            ],
                            spacing=4,
                        ),
                    ),
                ]

                if alertas_activas:
                    inicio_controles.append(
                        ft.Container(
                            padding=14,
                            border_radius=14,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=ft.Colors.AMBER_300, size=20),
                                            ft.Text(
                                                f"Avisos de tareas ({len(alertas_activas)})",
                                                size=15,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                    *[
                                        ft.Text(
                                            f"• {al.get('titulo')} — {calcular_estado_fecha(al.get('fecha_limite', ''), al.get('aviso_dias', 2), al.get('hora_limite', ''))[0]}",
                                            size=13,
                                            color=calcular_estado_fecha(
                                                al.get("fecha_limite", ""), al.get("aviso_dias", 2), al.get("hora_limite", "")
                                            )[1],
                                        )
                                        for al in alertas_activas[:3]
                                    ],
                                ],
                                spacing=4,
                            ),
                        )
                    )

                inicio_controles.extend([
                    ft.Text("Guardados", size=16, weight=ft.FontWeight.BOLD),
                    build_guardados_list("Todas", solo_lectura=True),
                ])
                content_area.controls.extend(inicio_controles)

            elif idx == 1:
                titulo_appbar.value = "Lista de Guardados"

                def cambiar_filtro(ev):
                    estado_app["filtro_cat"] = ev.control.value or "Todas"
                    render_seccion(1)

                filtro_dd = ft.Dropdown(
                    label="Filtrar por categoría",
                    value=estado_app["filtro_cat"],
                    options=[ft.dropdown.Option("Todas")] + [ft.dropdown.Option(c) for c in CATEGORIAS],
                    border_radius=12,
                    expand=True,
                    on_select=cambiar_filtro,
                )

                content_area.controls.extend([
                    ft.Row(
                        [
                            filtro_dd,
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE,
                                icon_size=32,
                                icon_color=ft.Colors.BLUE_400,
                                tooltip="Nuevo guardado",
                                on_click=abrir_dialogo_nuevo,
                            ),
                        ]
                    ),
                    build_guardados_list(estado_app["filtro_cat"], solo_lectura=False),
                ])

            elif idx == 2:
                titulo_appbar.value = "Tareas"
                content_area.controls.append(
                    ft.Button(
                        "Agregar nueva tarea",
                        icon=ft.Icons.ADD_TASK,
                        width=370,
                        height=44,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        on_click=abrir_dialogo_nueva_tarea,
                    )
                )

                if alertas_activas:
                    content_area.controls.append(
                        ft.Container(
                            padding=12,
                            border_radius=12,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            content=ft.Text(
                                f"Tienes {len(alertas_activas)} tarea(s) dentro de su ventana de aviso previo.",
                                size=13,
                                color=ft.Colors.AMBER_300,
                            ),
                        )
                    )

                tareas_visibles = (
                    tareas
                    if estado_app["mostrar_completadas"]
                    else [t for t in tareas if not t.get("completada")]
                )

                if not tareas_visibles:
                    content_area.controls.append(
                        ft.Container(
                            padding=20,
                            border_radius=12,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            content=ft.Text("No hay tareas para mostrar.", color=ft.Colors.GREY_400),
                        )
                    )
                else:
                    for t in tareas_visibles:
                        t_id = t["id"]
                        esta_hecha = bool(t.get("completada"))
                        texto_alerta, color_alerta, _ = calcular_estado_fecha(
                            t.get("fecha_limite", ""),
                            t.get("aviso_dias", 2),
                            t.get("hora_limite", ""),
                        )

                        def on_toggle(e, tid=t_id, val=esta_hecha):
                            toggle_task_completed(tid, not val)
                            render_seccion(2)

                        def on_del_task(e, tid=t_id):
                            delete_task(tid)
                            render_seccion(2)

                        content_area.controls.append(
                            ft.Container(
                                padding=14,
                                border_radius=14,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                content=ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            [
                                                ft.Checkbox(value=esta_hecha, on_change=on_toggle),
                                                ft.Column(
                                                    [
                                                        ft.Text(
                                                            t.get("titulo", "Sin título"),
                                                            size=15,
                                                            weight=ft.FontWeight.BOLD,
                                                        ),
                                                        ft.Text(
                                                            f"{t.get('tipo', 'Personal')}  •  {texto_alerta}",
                                                            size=12,
                                                            color=ft.Colors.GREY_400 if esta_hecha else color_alerta,
                                                        ),
                                                    ],
                                                    spacing=2,
                                                ),
                                            ],
                                            expand=True,
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_color=ft.Colors.RED_400,
                                            tooltip="Eliminar tarea",
                                            on_click=on_del_task,
                                        ),
                                    ],
                                ),
                            )
                        )

            elif idx == 3:
                titulo_appbar.value = "Configuración"

                def toggle_tema(e):
                    page.theme_mode = (
                        ft.ThemeMode.LIGHT
                        if page.theme_mode == ft.ThemeMode.DARK
                        else ft.ThemeMode.DARK
                    )
                    page.update()

                def on_aviso_default(ev):
                    try:
                        estado_app["aviso_default"] = max(0, int((ev.control.value or "2").strip()))
                    except ValueError:
                        pass

                def on_cat_default(ev):
                    estado_app["cat_default"] = ev.control.value or "Anime"

                def on_estado_default(ev):
                    estado_app["estado_default"] = ev.control.value or "Viendo"

                def on_toggle_completadas(ev):
                    estado_app["mostrar_completadas"] = bool(ev.control.value)

                def cerrar_sesion(e):
                    estado_app["user"] = None
                    estado_app["username"] = ""
                    mostrar_login()

                content_area.controls.append(
                    ft.Container(
                        padding=16,
                        border_radius=14,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        content=ft.Column(
                            [
                                ft.Text("Preferencias", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Sesión activa: @{estado_app['username']}", size=12, color=ft.Colors.BLUE_200),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Tema (Oscuro / Claro)"),
                                        ft.OutlinedButton("Cambiar", on_click=toggle_tema),
                                    ],
                                ),
                                ft.Divider(),
                                ft.Text("Tareas y avisos", size=15, weight=ft.FontWeight.BOLD),
                                ft.TextField(
                                    label="Días de aviso previo por defecto",
                                    value=str(estado_app["aviso_default"]),
                                    keyboard_type=ft.KeyboardType.NUMBER,
                                    border_radius=12,
                                    on_change=on_aviso_default,
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Mostrar completadas en Tareas"),
                                        ft.Switch(
                                            value=estado_app["mostrar_completadas"],
                                            on_change=on_toggle_completadas,
                                        ),
                                    ],
                                ),
                                ft.Divider(),
                                ft.Text("Guardados por defecto", size=15, weight=ft.FontWeight.BOLD),
                                ft.Dropdown(
                                    label="Categoría inicial",
                                    value=estado_app["cat_default"],
                                    options=[ft.dropdown.Option(c) for c in CATEGORIAS],
                                    border_radius=12,
                                    on_select=on_cat_default,
                                ),
                                ft.Dropdown(
                                    label="Estado inicial",
                                    value=estado_app["estado_default"],
                                    options=[ft.dropdown.Option(est) for est in ESTADOS],
                                    border_radius=12,
                                    on_select=on_estado_default,
                                ),
                                ft.Divider(),
                                ft.Button(
                                    "Cerrar sesión",
                                    on_click=cerrar_sesion,
                                    bgcolor=ft.Colors.RED_600,
                                    color=ft.Colors.WHITE,
                                ),
                            ],
                            spacing=12,
                        ),
                    )
                )

            page.update()

        async def on_drawer_change(e):
            idx = e.control.selected_index
            await page.close_drawer()
            render_seccion(idx)

        page.drawer = ft.NavigationDrawer(
            selected_index=0,
            on_change=on_drawer_change,
            controls=[
                ft.Container(
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Text("⚡ MyLife Hub", size=22, weight=ft.FontWeight.BOLD),
                            ft.Text(f"@{estado_app['username']}", size=13, color=ft.Colors.BLUE_300),
                        ],
                        spacing=2,
                    ),
                ),
                ft.Divider(),
                ft.NavigationDrawerDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Inicio"),
                ft.NavigationDrawerDestination(icon=ft.Icons.BOOKMARKS_OUTLINED, selected_icon=ft.Icons.BOOKMARKS, label="Lista de Guardados"),
                ft.NavigationDrawerDestination(icon=ft.Icons.TASK_ALT, selected_icon=ft.Icons.TASK, label="Tareas"),
                ft.Divider(),
                ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Configuración"),
            ],
        )

        async def abrir_menu(e):
            await page.show_drawer()

        page.appbar = ft.AppBar(
            leading=ft.IconButton(icon=ft.Icons.MENU, on_click=abrir_menu),
            title=titulo_appbar,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
        )

        root_view.controls.clear()
        root_view.controls.append(ft.Container(expand=True, padding=16, content=content_area))
        render_seccion(0)

    mostrar_login()


ft.run(main)