from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from aiogram.filters import Command
import DataBase.Manager as manager
import Filters

async def show_main_menu(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📅 Календарь", callback_data="main_calendar"))
    keyboard.add(InlineKeyboardButton(text="🔍 Поиск", callback_data="main_search"))
    keyboard.add(InlineKeyboardButton(text="👤 Профиль", callback_data="main_profile"))
    keyboard.adjust(1)

    await message.answer(
        "🏠 Вы на главной странице AI Agent!\n"
        "Выберите действие:",
        reply_markup=keyboard.as_markup()
    )


async def show_user_profile(message: Message, user_id):
    user_data = manager.get_from_base(str(user_id))

    if not user_data or user_data.get('state') != 'completed':
        await message.answer("❌ Сначала завершите регистрацию через /start")
        return

    role_name = get_role_display_name(user_data['role'])
    profile_text = format_profile_text(user_data)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    keyboard.adjust(1)

    await message.answer(profile_text, reply_markup=keyboard.as_markup())


def get_role_display_name(role):
    roles = {
        "user": "👤 Пользователь",
        "organization": "🏢 Руководитель"
    }
    return roles.get(role, "Пользователь")


def get_level_display_name(level):
    levels = {
        "junior": "👶 Junior",
        "middle": "💼 Middle",
        "senior": "👑 Senior"
    }
    return levels.get(level, level)


def format_profile_text(user_data):
    role_name = get_role_display_name(user_data['role'])
    profile_text = f"👤 {user_data['name']}\n🎭 {role_name}\n\n"

    if user_data['role'] == 'user':
        level = user_data['profile'].get('level', 'Не указан')
        level_name = get_level_display_name(level)
        profile_text += f"🎯 Уровень: {level_name}"
    elif user_data['role'] == 'organization':
        org_name = user_data['profile'].get('org_name', 'Не указано')
        profile_text += f"🏢 Организация: {org_name}"

    return profile_text


async def handle_main_calendar(callback):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))

    await callback.message.edit_text(
        "📅 Функция календаря в разработке...",
        reply_markup=keyboard.as_markup()
    )


async def handle_main_search(callback):
    '''keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))

    await callback.message.edit_text(
        "🔍 Функция поиска в разработке...",
        reply_markup=keyboard.as_markup()
    )'''
    await Filters.show_filters_menu(callback.message, callback.from_user.id)
    await callback.answer()


async def handle_main_profile(callback):
    await show_user_profile(callback.message, callback.from_user.id)


async def handle_back_to_main(callback):
    await show_main_menu(callback.message)


def register_handlers(dp):
    dp.message.register(show_main_menu, Command("main"))

    dp.callback_query.register(handle_main_calendar, F.data == "main_calendar")
    dp.callback_query.register(handle_main_search, F.data == "main_search")
    dp.callback_query.register(handle_main_profile, F.data == "main_profile")
    dp.callback_query.register(handle_back_to_main, F.data == "back_to_main")