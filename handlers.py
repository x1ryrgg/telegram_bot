from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils import markdown
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from api import (authenticate_user, refresh_access_token, get_user_delivery, check_user_registered, link_telegram_id,
                 get_user_history)
from cache import get_tokens_redis, save_tokens_redis, delete_tokens_redis
from config import format_order, get_status_orders, get_status_history, format_history, auth_required
from keyboards import main_keyboard

dp_router = Router()

class AuthState(StatesGroup):
    username = State()
    password = State()


@dp_router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    tokens = await get_tokens_redis(tg_id)

    if tokens:
        await message.answer("✅ Вы уже авторизованы! \n"
                             "Выберите нужный пункт в клавиатуре.", reply_markup=main_keyboard())
    else:
        await message.answer(text=markdown.text("🔐 Введите ваш", markdown.bold("username"), "от аккаунта магазина:"),
                             parse_mode=ParseMode.MARKDOWN_V2)
        await state.set_state(AuthState.username)


@dp_router.message(AuthState.username)
async def handle_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer(text=markdown.text("🔐 Теперь введите ваш ", markdown.bold("пароль"), ":"),
                         parse_mode=ParseMode.MARKDOWN_V2)
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

    await message.answer("✅ Успешная авторизация!\n "
                         "Выберите нужный пункт в клавиатуре. ", reply_markup=main_keyboard())
    await state.clear()


@dp_router.message(F.text == 'Доставка')
@auth_required
async def delivery_handler(message: Message, access_token: str):
    orders = await get_user_delivery(access_token)

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
    for part in [full_message[i:i + 4000] for i in range(0, len(full_message), 4000)]:
        await message.answer(part, parse_mode=ParseMode.HTML)


@dp_router.message(F.text == 'История покупок')
@auth_required
async def history_handler(message: Message, access_token: str):
    histories = await get_user_history(access_token)

    if not histories:
        await message.answer("📭 Ваша история покупок пуста.")
        return

    response = [
        "🛒 <b>История покупок</b>",
        f"<b>Всего покупок: {len(histories)}</b>\n"
    ]

    response.extend(format_history(item) for item in histories)

    full_message = "\n".join(response)
    for part in [full_message[i:i + 4000] for i in range(0, len(full_message), 4000)]:
        await message.answer(part, parse_mode=ParseMode.HTML)


@dp_router.message(F.text == 'Выйти из акканута')
async def delete_token_handler(message: Message):
    tg_id = message.from_user.id
    try:
        success = await delete_tokens_redis(tg_id)
        if success:
            await message.answer("✅ Вы успешно вышли из аккаунта.\n"
                    "Для повторной авторизации используйте /start", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(
                "⚠️ Не удалось выйти из аккаунта. Попробуйте позже.",
                reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@dp_router.message()
async def message_handler(message: Message):
    await message.answer('Подождите секунду...')
    if message.text:
        await message.answer(message.text, entities=message.entities)