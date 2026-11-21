import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or ""


class SimpleUser:
    def __init__(self, user_id: str, email: str):
        self.id = user_id
        self.email = email


def _request(method: str, path: str, body: dict | None = None, token: str | None = None, extra_headers: dict | None = None):
    url = f"{SUPABASE_URL}{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {token or SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(err_body)
            msg = err_json.get("msg") or err_json.get("message") or err_json.get("error_description") or err_body
        except Exception:
            msg = err_body or str(e)
        raise RuntimeError(msg)


def auth_sign_in(email: str, password: str) -> SimpleUser:
    res = _request(
        "POST",
        "/auth/v1/token?grant_type=password",
        {"email": email, "password": password},
    )
    user_data = res.get("user") or {}
    return SimpleUser(user_data.get("id", ""), user_data.get("email", email))


def auth_sign_up(email: str, password: str, username: str) -> SimpleUser | None:
    res = _request(
        "POST",
        "/auth/v1/signup",
        {"email": email, "password": password, "data": {"username": username}},
    )
    user_data = (res or {}).get("user") or res or {}
    if user_data.get("id"):
        return SimpleUser(user_data["id"], user_data.get("email", email))
    return None


def get_profile_by_username(username: str):
    q = urllib.parse.quote(username.strip())
    res = _request("GET", f"/rest/v1/profiles?select=email,username&username=ilike.{q}&limit=1")
    return res[0] if res else None


def insert_profile(user_id: str, username: str, email: str):
    return _request(
        "POST",
        "/rest/v1/profiles",
        {"id": user_id, "username": username, "email": email},
        extra_headers={"Prefer": "return=minimal"},
    )


def get_items(user_id: str, categoria: str | None = None):
    uid = urllib.parse.quote(user_id)
    path = f"/rest/v1/items?select=*&user_id=eq.{uid}&order=created_at.desc"
    if categoria and categoria != "Todas":
        cat = urllib.parse.quote(categoria)
        path += f"&categoria=eq.{cat}"
    return _request("GET", path) or []


def add_item(user_id: str, categoria: str, titulo: str, detalle: str = "", capitulo: int = 1, estado: str = "Viendo"):
    payload = {
        "user_id": user_id,
        "categoria": categoria,
        "titulo": titulo,
        "detalle": detalle.strip() if detalle else None,
        "capitulo": int(capitulo),
        "estado": estado,
    }
    return _request("POST", "/rest/v1/items", payload, extra_headers={"Prefer": "return=minimal"})


def update_item(item_id: int, capitulo: int, estado: str, detalle: str = "", titulo: str | None = None, categoria: str | None = None):
    payload = {
        "capitulo": int(capitulo),
        "estado": estado,
        "detalle": detalle.strip() if detalle else None,
    }
    if titulo is not None:
        payload["titulo"] = titulo
    if categoria is not None:
        payload["categoria"] = categoria
    return _request("PATCH", f"/rest/v1/items?id=eq.{item_id}", payload, extra_headers={"Prefer": "return=minimal"})


def delete_item(item_id: int):
    return _request("DELETE", f"/rest/v1/items?id=eq.{item_id}")


def get_tasks(user_id: str):
    uid = urllib.parse.quote(user_id)
    return _request("GET", f"/rest/v1/tasks?select=*&user_id=eq.{uid}&order=fecha_limite.asc") or []


def add_task(user_id: str, titulo: str, tipo: str, fecha_limite: str, hora_limite: str = "23:59", aviso_dias: int = 2):
    payload = {
        "user_id": user_id,
        "titulo": titulo.strip(),
        "tipo": tipo,
        "fecha_limite": fecha_limite,
        "hora_limite": hora_limite or "23:59",
        "aviso_dias": int(aviso_dias),
        "completada": False,
    }
    return _request("POST", "/rest/v1/tasks", payload, extra_headers={"Prefer": "return=minimal"})


def toggle_task_completed(task_id: int, completada: bool):
    return _request("PATCH", f"/rest/v1/tasks?id=eq.{task_id}", {"completada": completada}, extra_headers={"Prefer": "return=minimal"})


def delete_task(task_id: int):
    return _request("DELETE", f"/rest/v1/tasks?id=eq.{task_id}")