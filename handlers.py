from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from api import (authenticate_user, refresh_access_token, get_user_orders, check_user_registered, link_telegram_id,
                 get_user_history)
from cache import get_tokens_redis, save_tokens_redis, delete_tokens_redis
from config import format_order, get_status_orders, get_status_history, format_history

dp_router = Router()

class AuthState(StatesGroup):
    username = State()
    password = State()


@dp_router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    tokens = await get_tokens_redis(tg_id)

    if tokens:
        await message.answer("✅ Вы уже авторизованы! Доступные команды:\n/delivery – ваши заказы")
    else:
        await message.answer("🔐 Введите ваш **username** от аккаунта DRF:")
        await state.set_state(AuthState.username)


@dp_router.message(AuthState.username)
async def handle_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Теперь введите ваш **пароль**:")
    await state.set_state(AuthState.password)


@dp_router.message(AuthState.password)
async def handle_password(message: Message, state: FSMContext):
    data = await state.get_data()
    username = data["username"]
    password = message.text
    tg_id = message.from_user.id

    tokens = await authenticate_user(username, password)
    if not tokens:
        await message.answer("❌ Ошибка авторизации. Проверьте данные!")
        await state.clear()
        return

    if not await save_tokens_redis(tg_id, tokens):
        await message.answer("❌ Ошибка сохранения токенов. Попробуйте позже.")
        await state.clear()
        return

    success = await link_telegram_id(tokens["access"], tg_id)
    if not success:
        await message.answer("❌ Ошибка привязки аккаунта. Попробуйте позже.")
        await state.clear()
        return

    await message.answer("✅ Успешная авторизация! Доступные команды:\n/delivery – ваши заказы"
                         "\n/history - история покупок")
    await state.clear()


@dp_router.message(Command("delivery"))
async def delivery_handler(message: Message):
    tg_id = message.from_user.id

    tokens = await get_tokens_redis(tg_id)

    if not tokens:
        await message.answer("❌ Требуется авторизация! /start")
        return

    orders = await get_user_orders(tokens["access"])

    if orders is None:
        new_tokens = await refresh_access_token(tokens["refresh"])
        if new_tokens:
            await save_tokens_redis(tg_id, new_tokens)
            orders = await get_user_orders(new_tokens["access"])

    if not orders:
        await message.answer("📭 У вас пока нет заказов.")
        return

    delivered = [o for o in orders if o['status'] == 'delivered']
    on_the_way = [o for o in orders if o['status'] == 'on the way']

    response = ["📦 <b>Ваши заказы</b>"]

    if delivered:
        response.append("\n🎁 <b>Готовы к выдаче:</b>")
        response.extend(format_order(o) for o in delivered)

    if on_the_way:
        response.append("\n🚚 <b>В пути:</b>")
        response.extend(format_order(o) for o in on_the_way)

    full_message = "\n".join(response)
    if len(full_message) > 4000:  # Ограничение Telegram
        parts = [full_message[i:i + 4000] for i in range(0, len(full_message), 4000)]
        for part in parts:
            await message.answer(part)
    else:
        await message.answer(full_message)


@dp_router.message(Command("history"))
async def history_history(message: Message):
    tg_id = message.from_user.id

    tokens = await get_tokens_redis(tg_id)

    if not tokens:
        await message.answer("❌ Требуется авторизация! /start")
        return

    histories = await get_user_history(tokens["access"])

    if histories is None:
        new_tokens = await refresh_access_token(tokens["refresh"])
        if new_tokens:
            await save_tokens_redis(tg_id, new_tokens)
            histories = await get_user_history(new_tokens["access"])

    if not histories:
        await message.answer("📭 Ваша история покупок пуста.")
        return

    response = [
        "🛒 <b>История покупок</b>",
        f"Всего покупок: {len(histories)}\n"
    ]

    response.extend(format_history(item) for item in histories)

    full_message = "\n".join(response)
    for part in [full_message[i:i + 4000] for i in range(0, len(full_message), 4000)]:
        await message.answer(part)


@dp_router.message(Command("check"))
async def get_tg_id_handler(message: Message):
    tg_id = message.from_user.id
    tokens = await get_tokens_redis(tg_id)
    await message.answer(f"{tokens}")


@dp_router.message(Command("delete"))
async def delete_token_handler(message: Message):
    tg_id = message.from_user.id
    try:
        delete = await delete_tokens_redis(tg_id)
        if delete:
            await message.answer("Токены удалены из кэша")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

