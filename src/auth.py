from src.db import auth_sign_in, auth_sign_up, get_profile_by_username, insert_profile


def login_con_usuario(username: str, password: str):
    perfil = get_profile_by_username(username)
    if not perfil:
        raise ValueError("Usuario no encontrado.")
    return auth_sign_in(perfil["email"], password)


def registrar_usuario(username: str, email: str, password: str):
    clean_user = username.strip()
    clean_email = email.strip()

    if get_profile_by_username(clean_user):
        raise ValueError("Ese nombre de usuario ya está en uso.")

    user_obj = auth_sign_up(clean_email, password, clean_user)
    if user_obj and user_obj.id:
        try:
            insert_profile(user_obj.id, clean_user, clean_email)
        except Exception:
            pass
    return user_obj