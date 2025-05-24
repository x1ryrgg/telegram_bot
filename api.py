import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")

async def authenticate_user(username: str, password: str) -> dict | None:
    """Аутентификация пользователя и получение токенов."""
    try:
        response = requests.post(
            f"{API_URL}/api/token/",
            json={"username": username, "password": password}
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

async def link_telegram_id(access_token: str, tg_id: int) -> bool:
    """Привязывает tg_id к пользователю в DRF."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.patch(
            f"{API_URL}/user/link_telegram/",
            json={"tg_id": tg_id},
            headers=headers
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Link Telegram Error: {e}")
        return False

async def refresh_access_token(refresh_token: str) -> dict | None:
    """Обновление access_token через refresh_token."""
    try:
        response = requests.post(
            f"{API_URL}/api/token/refresh/",
            json={"refresh": refresh_token}
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Refresh Error: {e}")
        return None

async def check_user_registered(tg_id: int) -> bool:
    """Проверка, есть ли пользователь с таким tg_id в БД."""
    try:
        response = requests.get(f"{API_URL}/users/?tg_id={tg_id}")
        return response.status_code == 200 and bool(response.json())
    except Exception as e:
        print(f"Check User Error: {e}")
        return False

async def get_user_orders(access_token: str) -> list | None:
    """Получение списка заказов пользователя."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{API_URL}/delivery/", headers=headers)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Orders Error: {e}")
        return None

async def get_user_history(access_token: str) -> list | None:
    """Получение списка заказов пользователя."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{API_URL}/history/", headers=headers)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Orders Error: {e}")
        return None






