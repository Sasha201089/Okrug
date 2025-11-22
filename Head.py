from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from aiogram.filters import Command
import DataBase.Manager as manager
import Filters
import Calendar
from datetime import datetime


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

    if user_data.get('role') == 'organization':
        pending_suggestions = count_pending_suggestions(user_data)
        if pending_suggestions > 0:
            keyboard.add(InlineKeyboardButton(
                text=f"📨 Предложения отдела ({pending_suggestions})",
                callback_data="profile_manage_suggestions"
            ))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    keyboard.adjust(1)

    await message.answer(profile_text, reply_markup=keyboard.as_markup())


def count_pending_suggestions(user_data):
    suggestions = user_data.get('suggestions', {})
    pending_count = 0
    for suggestion in suggestions.values():
        if suggestion.get('status') == 'pending':
            pending_count += 1
    return pending_count


async def manage_suggestions(callback):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    if user_data.get('role') != 'organization':
        await callback.answer("❌ Только организаторы могут управлять предложениями")
        return

    suggestions = user_data.get('suggestions', {})
    pending_suggestions = {k: v for k, v in suggestions.items() if v.get('status') == 'pending'}

    if not pending_suggestions:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="⬅️ Назад в профиль", callback_data="main_profile"))
        await callback.message.edit_text(
            "📨 Нет новых предложений от отдела",
            reply_markup=keyboard.as_markup()
        )
        return

    keyboard = InlineKeyboardBuilder()

    for suggestion_id, suggestion_data in pending_suggestions.items():
        event_data = suggestion_data.get('event_data', {})
        # Получаем название мероприятия - может быть в разных местах
        event_name = suggestion_data.get('event_name') or event_data.get('name') or event_data.get('название', 'Неизвестное мероприятие')
        suggested_by = suggestion_data.get('suggested_by_name', 'Неизвестный сотрудник')

        # Сокращаем текст кнопки и используем короткий ID
        short_suggestion_id = suggestion_id[:20]  # Берем только первые 20 символов
        keyboard.add(InlineKeyboardButton(
            text=f"📨 {event_name[:20]}... от {suggested_by[:10]}",
            callback_data=f"ps_{short_suggestion_id}"  # ps - profile suggestion
        ))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_profile"))
    keyboard.adjust(1)

    await callback.message.edit_text(
        f"📨 **Предложения от отдела {user_data['profile'].get('department')}:**\n\n"
        f"Найдено предложений: {len(pending_suggestions)}",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def view_suggestion_details(callback, suggestion_id: str):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    # Если suggestion_id короткий (из ps_ префикса), находим полный ID
    suggestions = user_data.get('suggestions', {})
    if suggestion_id not in suggestions:
        # Ищем по началу ID
        for full_id in suggestions.keys():
            if full_id.startswith(suggestion_id):
                suggestion_id = full_id
                break
    
    suggestion = suggestions.get(suggestion_id)

    if not suggestion:
        await callback.answer("❌ Предложение не найдено")
        return

    event_data = suggestion['event_data']
    
    # Получаем название мероприятия - может быть в разных местах
    event_name = suggestion.get('event_name') or event_data.get('name') or event_data.get('название', 'Неизвестное мероприятие')
    
    # Получаем остальные поля с поддержкой разных форматов (английские и русские ключи)
    event_date = event_data.get('date') or event_data.get('дата проведения', 'Не указана')
    event_location = event_data.get('location') or event_data.get('место проведения', 'Не указано')
    event_cost = event_data.get('cost') or event_data.get('стоимость', 'Не указана')
    event_type = event_data.get('type') or event_data.get('тип', 'Не указан')
    event_description = event_data.get('description') or event_data.get('описание', 'Описание отсутствует')
    event_link = event_data.get('link') or event_data.get('ссылка', 'Не указана')

    text = f"📨 **Предложение мероприятия**\n\n"
    text += f"👤 **От:** {suggestion.get('suggested_by_name', 'Неизвестный сотрудник')}\n"
    text += f"📅 **Дата предложения:** {suggestion.get('suggested_date', 'Не указана')}\n\n"
    text += f"🎯 **Мероприятие:** {event_name}\n"
    text += f"📅 **Дата:** {event_date}\n"
    text += f"📍 **Место:** {event_location}\n"
    text += f"💰 **Стоимость:** {event_cost}\n"
    text += f"📝 **Тип:** {event_type}\n\n"
    text += f"📋 **Описание:** {event_description}\n\n"
    text += f"🔗 **Ссылка:** {event_link}"

    keyboard = InlineKeyboardBuilder()
    # Используем короткий ID для callback_data (ограничение Telegram - 64 байта)
    short_id = suggestion_id[:20]
    keyboard.add(InlineKeyboardButton(text="✅ Принять", callback_data=f"profile_accept_{short_id}"))
    keyboard.add(InlineKeyboardButton(text="❌ Отклонить", callback_data=f"profile_reject_{short_id}"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="profile_manage_suggestions"))
    keyboard.adjust(2)

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await callback.answer()


async def accept_suggestion(callback, suggestion_id: str):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    # Если suggestion_id короткий, находим полный ID
    suggestions = user_data.get('suggestions', {})
    if suggestion_id not in suggestions:
        # Ищем по началу ID
        for full_id in suggestions.keys():
            if full_id.startswith(suggestion_id):
                suggestion_id = full_id
                break

    suggestion = suggestions.get(suggestion_id)

    if not suggestion:
        await callback.answer("❌ Предложение не найдено")
        return

    event_data = suggestion['event_data']
    department = user_data['profile'].get('department')
    
    # Нормализуем данные мероприятия - приводим к единому формату
    event_name = suggestion.get('event_name') or event_data.get('name') or event_data.get('название', 'Неизвестное мероприятие')
    normalized_event = {
        'name': event_name,
        'date': event_data.get('date') or event_data.get('дата проведения', 'Не указана'),
        'location': event_data.get('location') or event_data.get('место проведения', 'Не указано'),
        'cost': event_data.get('cost') or event_data.get('стоимость', 'Не указана'),
        'type': event_data.get('type') or event_data.get('тип', 'Не указан'),
        'description': event_data.get('description') or event_data.get('описание', ''),
        'link': event_data.get('link') or event_data.get('ссылка', ''),
        'status': 'confirmed',
        'added_by_organizer': True,
        'added_date': datetime.now().strftime('%d.%m.%Y')
    }

    all_users = manager.get_users_from_base()
    department_users = []

    for uid in all_users:
        user_info = manager.get_from_base(uid)
        if (user_info and user_info.get('role') == 'user' and
                user_info.get('profile', {}).get('department') == department):
            department_users.append(uid)

    # Создаем уникальный event_id на основе названия и времени
    # Очищаем название от недопустимых символов для использования в ID
    safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in event_name[:20])
    event_id = f"dept_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"

    # Добавляем мероприятие всем пользователям отдела и организатору
    # Важно: сначала добавляем пользователям, потом организатору отдельно
    all_recipients = list(department_users)  # Копируем список пользователей
    if user_id not in all_recipients:  # Добавляем организатора, если его еще нет
        all_recipients.append(user_id)

    for uid in all_recipients:
        user_info = manager.get_from_base(uid)
        if not user_info:
            continue
        if 'calendar' not in user_info:
            user_info['calendar'] = {}
        if 'events' not in user_info['calendar']:
            user_info['calendar']['events'] = {}

        user_info['calendar']['events'][event_id] = normalized_event.copy()

        manager.write_in_base(uid, user_info)

    user_data['suggestions'][suggestion_id]['status'] = 'accepted'
    manager.write_in_base(user_id, user_data)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="profile_manage_suggestions"))

    await callback.message.edit_text(
        f"✅ Мероприятие добавлено в календарь отдела {department}!\n"
        f"Участников: {len(department_users) + 1}",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def reject_suggestion(callback, suggestion_id: str):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    # Если suggestion_id короткий, находим полный ID
    suggestions = user_data.get('suggestions', {})
    if suggestion_id not in suggestions:
        # Ищем по началу ID
        for full_id in suggestions.keys():
            if full_id.startswith(suggestion_id):
                suggestion_id = full_id
                break

    suggestion = suggestions.get(suggestion_id)

    if not suggestion:
        await callback.answer("❌ Предложение не найдено")
        return

    user_data['suggestions'][suggestion_id]['status'] = 'rejected'
    manager.write_in_base(user_id, user_data)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="profile_manage_suggestions"))

    await callback.message.edit_text(
        "❌ Предложение отклонено",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()
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
        fullname = user_data['profile'].get('fullname', 'Не указано')
        level = user_data['profile'].get('level', 'Не указан')
        level_name = get_level_display_name(level)
        department = user_data['profile'].get('department', '-')

        profile_text += f"📝 ФИО: {fullname}\n"
        profile_text += f"🎯 Уровень: {level_name}\n"
        profile_text += f"🏢 Отдел: {department}"

    elif user_data['role'] == 'organization':
        org_name = user_data['profile'].get('org_name', 'Не указано')
        department = user_data['profile'].get('department', 'Не указано')

        profile_text += f"🏢 Организация: {org_name}\n"
        profile_text += f"🏢 Отдел: {department}"

    return profile_text


async def handle_main_calendar(callback):
    await Calendar.show_calendar(callback.message, callback.from_user.id)



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
    async def handle_view_suggestion(callback: CallbackQuery):
        short_id = callback.data.replace("ps_", "")
        await view_suggestion_details(callback, short_id)
    
    async def handle_accept_suggestion(callback: CallbackQuery):
        short_id = callback.data.replace("profile_accept_", "")
        await accept_suggestion(callback, short_id)
    
    async def handle_reject_suggestion(callback: CallbackQuery):
        short_id = callback.data.replace("profile_reject_", "")
        await reject_suggestion(callback, short_id)
    
    dp.callback_query.register(manage_suggestions, F.data == "profile_manage_suggestions")
    dp.callback_query.register(handle_view_suggestion, F.data.startswith("ps_"))
    dp.callback_query.register(handle_accept_suggestion, F.data.startswith("profile_accept_"))
    dp.callback_query.register(handle_reject_suggestion, F.data.startswith("profile_reject_"))