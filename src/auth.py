from src.db import supabase


def login_con_usuario(username: str, password: str):
    perfil_res = (
        supabase.table("profiles")
        .select("email, username")
        .ilike("username", username.strip())
        .limit(1)
        .execute()
    )
    if not perfil_res.data:
        raise ValueError("Usuario no encontrado.")

    email_usuario = perfil_res.data[0]["email"]
    res = supabase.auth.sign_in_with_password({
        "email": email_usuario,
        "password": password,
    })
    return res.user


def registrar_usuario(username: str, email: str, password: str):
    clean_user = username.strip()
    clean_email = email.strip()

    existe = (
        supabase.table("profiles")
        .select("id")
        .ilike("username", clean_user)
        .limit(1)
        .execute()
    )
    if existe.data:
        raise ValueError("Ese nombre de usuario ya está en uso.")

    auth_res = supabase.auth.sign_up({
        "email": clean_email,
        "password": password,
        "options": {"data": {"username": clean_user}},
    })

    user_obj = getattr(auth_res, "user", None)
    if user_obj and getattr(user_obj, "id", None):
        try:
            supabase.table("profiles").insert({
                "id": user_obj.id,
                "username": clean_user,
                "email": clean_email,
            }).execute()
        except Exception:
            pass
    return user_obj