import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_items(user_id: str, categoria: str | None = None):
    query = (
        supabase.table("items")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )
    if categoria and categoria != "Todas":
        query = query.eq("categoria", categoria)
    res = query.execute()
    return res.data or []


def add_item(
    user_id: str,
    categoria: str,
    titulo: str,
    detalle: str = "",
    capitulo: int = 1,
    estado: str = "Viendo",
):
    payload = {
        "user_id": user_id,
        "categoria": categoria,
        "titulo": titulo,
        "detalle": detalle.strip() if detalle else None,
        "capitulo": int(capitulo),
        "estado": estado,
    }
    return supabase.table("items").insert(payload).execute()


def update_item(
    item_id: int,
    capitulo: int,
    estado: str,
    detalle: str = "",
    titulo: str | None = None,
    categoria: str | None = None,
):
    payload = {
        "capitulo": int(capitulo),
        "estado": estado,
        "detalle": detalle.strip() if detalle else None,
    }
    if titulo is not None:
        payload["titulo"] = titulo
    if categoria is not None:
        payload["categoria"] = categoria
    return supabase.table("items").update(payload).eq("id", item_id).execute()


def delete_item(item_id: int):
    return supabase.table("items").delete().eq("id", item_id).execute()
def get_tasks(user_id: str):
    res = (
        supabase.table("tasks")
        .select("*")
        .eq("user_id", user_id)
        .order("fecha_limite", desc=False)
        .execute()
    )
    return res.data or []


def add_task(
    user_id: str,
    titulo: str,
    tipo: str,
    fecha_limite: str,
    hora_limite: str = "23:59",
    aviso_dias: int = 2,
):
    payload = {
        "user_id": user_id,
        "titulo": titulo.strip(),
        "tipo": tipo,
        "fecha_limite": fecha_limite,
        "hora_limite": hora_limite or "23:59",
        "aviso_dias": int(aviso_dias),
        "completada": False,
    }
    return supabase.table("tasks").insert(payload).execute()


def toggle_task_completed(task_id: int, completada: bool):
    return (
        supabase.table("tasks")
        .update({"completada": completada})
        .eq("id", task_id)
        .execute()
    )


def delete_task(task_id: int):
    return supabase.table("tasks").delete().eq("id", task_id).execute()