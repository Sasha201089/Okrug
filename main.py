import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import DataBase.Manager as manager
import json
import Head
import Filters

logging.basicConfig(level=logging.INFO)
logging.info('Библиотеки импортированы')

bot = Bot(token="8577326305:AAHhzmM1BUxd3YvW2OR857VJ_BYTI8q06y4")
dp = Dispatcher()


class RegistrationState:
    CHOOSE_ROLE = "choose_role"
    USER_LEVEL = "user_level"
    ORGANIZATION_NAME = "organization_name"
    COMPLETED = "completed"


ROLES = {
    "user": "👤 Пользователь",
    "organization": "🏢 Руководитель"
}

LEVELS = {
    "junior": "👶 Junior",
    "middle": "💼 Middle",
    "senior": "👑 Senior"
}


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name

    users = manager.get_users_from_base()

    if user_id not in users:
        user_data = {
            "name": user_name,
            "state": RegistrationState.CHOOSE_ROLE,
            "role": None,
            "profile": {}
        }
        manager.write_in_base(user_id, user_data)
        await message.answer(
            '🌟 Добро пожаловать в AI Agent!\n'
            'Платформа для поиска мероприятий.'
        )
        await ask_role(message)
    else:
        user_data = manager.get_from_base(user_id)
        if user_data.get('state') == RegistrationState.COMPLETED:
            role_name = ROLES.get(user_data['role'], 'Пользователь')
            await message.answer(
                f'👋 С возвращением, {user_name}!\n'
                f'🎭 Ваша роль: {role_name}\n'
                f'✅ Регистрация завершена'
            )
        else:
            await continue_registration(message, user_data)


async def continue_registration(message: Message, user_data):
    state = user_data.get('state')
    user_id = str(message.from_user.id)

    if state == RegistrationState.CHOOSE_ROLE:
        await ask_role(message)
    elif state == RegistrationState.USER_LEVEL:
        await ask_level(message)
    elif state == RegistrationState.ORGANIZATION_NAME:
        await message.answer('🏢 Введите ваше ФИО:')
async def ask_role(message: Message):
    keyboard = InlineKeyboardBuilder()
    for role_key, role_name in ROLES.items():
        keyboard.add(InlineKeyboardButton(text=role_name, callback_data=f"role_{role_key}"))
    keyboard.adjust(1)

    await message.answer(
        "🎭 Выберите вашу роль:",
        reply_markup=keyboard.as_markup()
    )


async def ask_level(message: Message):
    keyboard = InlineKeyboardBuilder()
    for level_key, level_name in LEVELS.items():
        keyboard.add(InlineKeyboardButton(text=level_name, callback_data=f"level_{level_key}"))
    keyboard.adjust(1)

    await message.answer(
        "🎯 Выберите ваш уровень:",
        reply_markup=keyboard.as_markup()
    )


@dp.callback_query(F.data.startswith("role_"))
async def handle_role_selection(callback: Message):
    user_id = str(callback.from_user.id)
    role = callback.data.split("_")[1]

    user_data = manager.get_from_base(user_id)
    user_data['role'] = role

    if role == "user":
        user_data['state'] = RegistrationState.USER_LEVEL
        manager.write_in_base(user_id, user_data)
        await ask_level(callback.message)
    elif role == "organization":
        user_data['state'] = RegistrationState.ORGANIZATION_NAME
        manager.write_in_base(user_id, user_data)
        await callback.message.answer('🏢 Введите название вашей организации:')

    await callback.answer()


@dp.callback_query(F.data.startswith("level_"))
async def handle_level_selection(callback: Message):
    user_id = str(callback.from_user.id)
    level = callback.data.split("_")[1]

    user_data = manager.get_from_base(user_id)
    user_data['profile']['level'] = level
    user_data['state'] = RegistrationState.COMPLETED

    manager.write_in_base(user_id, user_data)
    await complete_registration(callback.message, user_data, callback.from_user.id)
    await callback.answer()


@dp.message(F.text)
async def handle_text(message: Message):
    user_id = str(message.from_user.id)
    user_data = manager.get_from_base(user_id)

    if not user_data:
        await cmd_start(message)
        return

    state = user_data.get('state')
    text = message.text
    if user_data.get('filters', {}).get('waiting_price_input'):
        price_type = user_data['filters']['waiting_price_input']
        try:
            price = int(text)
            if price_type == 'min':
                user_data['filters']['price_min'] = price
            else:
                user_data['filters']['price_max'] = price

            user_data['filters'].pop('waiting_price_input', None)
            manager.write_in_base(user_id, user_data)

            await message.answer(
                f"✅ {('Минимальная' if price_type == 'min' else 'Максимальная')} стоимость установлена: {price} руб.")
            await Filters.show_filters_menu(message, user_id)
            return

        except ValueError:
            await message.answer("❌ Пожалуйста, введите число:")
            return

    if state == RegistrationState.ORGANIZATION_NAME:
        user_data['profile']['org_name'] = text
        user_data['state'] = RegistrationState.COMPLETED
        manager.write_in_base(user_id, user_data)
        await complete_registration(message, user_data, message.from_user.id)


async def complete_registration(message: Message, user_data, user_id):
    role_name = ROLES.get(user_data['role'])
    user_name = user_data['name']

    if user_data['role'] == 'user':
        level_name = LEVELS.get(user_data['profile']['level'], user_data['profile']['level'])
        profile_summary = f"🎯 Уровень: {level_name}"
    elif user_data['role'] == 'organization':
        profile_summary = f"🏢 Название организации: {user_data['profile']['org_name']}"

    await message.answer(
        f'✅ Регистрация завершена, {user_name}!\n\n'
        f'🎭 Роль: {role_name}\n'
        f'📊 Ваш профиль:\n{profile_summary}\n\n'
        f'🚀 Добро пожаловать в наш проект!'
    )
    await Head.show_main_menu(message)


async def main():
    Head.register_handlers(dp)
    Filters.register_handlers(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())