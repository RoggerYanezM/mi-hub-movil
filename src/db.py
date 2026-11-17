import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_items(user_id: str, categoria: str):
    response = supabase.table("items").select("*").eq("user_id", user_id).eq("categoria", categoria).order("id", desc=True).execute()
    return response.data

def add_item(user_id: str, categoria: str, titulo: str, detalle: str = "", capitulo: int = 1, estado: str = "Viendo"):
    supabase.table("items").insert({
        "user_id": user_id,
        "categoria": categoria,
        "titulo": titulo,
        "detalle": detalle,
        "capitulo": capitulo,
        "estado": estado
    }).execute()

def update_capitulo(item_id: int, nuevo_cap: int):
    supabase.table("items").update({"capitulo": nuevo_cap}).eq("id", item_id).execute()

def delete_item(item_id: int):
    supabase.table("items").delete().eq("id", item_id).execute()