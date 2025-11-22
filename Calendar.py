from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from datetime import datetime, timedelta
import DataBase.Manager as manager
import EventDataBase.Manager as event_db
import json
import calendar


def parse_event_date(date_str):
    """Парсит дату события, очищая от лишних символов"""
    if not date_str or date_str == 'Не указана':
        return None
    try:
        # Очищаем дату от лишних символов (дефисы, пробелы в начале/конце)
        cleaned_date = date_str.strip().lstrip('–-—').strip()
        return datetime.strptime(cleaned_date, '%d.%m.%Y').date()
    except ValueError:
        return None


async def show_calendar(message_or_callback, user_id=None):
    """Показать календарь пользователя"""
    # Поддержка как Message, так и CallbackQuery
    if hasattr(message_or_callback, 'message'):
        # Это CallbackQuery
        user_id = str(message_or_callback.from_user.id)
        message = message_or_callback.message
    else:
        # Это Message
        message = message_or_callback
        user_id = str(user_id) if user_id else str(message.from_user.id)
    
    user_data = manager.get_from_base(user_id)

    if not user_data or user_data.get('state') != 'completed':
        await message.answer("❌ Сначала завершите регистрацию через /start")
        return

    # Получаем мероприятия пользователя
    user_events = user_data.get('calendar', {}).get('events', {})
    upcoming_events = {}
    past_events = {}
    today_events = {}

    current_date = datetime.now().date()

    for event_id, event_data in user_events.items():
        event_date_str = event_data.get('date')
        event_date = parse_event_date(event_date_str)
        
        if event_date is None:
            # Если дата не указана или не распарсилась, считаем предстоящим
            upcoming_events[event_id] = event_data
        elif event_date == current_date:
            # События на сегодня
            today_events[event_id] = event_data
            upcoming_events[event_id] = event_data  # Также добавляем в предстоящие
        elif event_date > current_date:
            upcoming_events[event_id] = event_data
        else:
            past_events[event_id] = event_data

    # Создаем клавиатуру
    keyboard = InlineKeyboardBuilder()

    if today_events:
        keyboard.add(InlineKeyboardButton(text="📆 Сегодня", callback_data="calendar_today"))

    if upcoming_events:
        keyboard.add(InlineKeyboardButton(text="📅 Предстоящие мероприятия", callback_data="calendar_upcoming"))

    if past_events:
        keyboard.add(InlineKeyboardButton(text="📚 Прошедшие мероприятия", callback_data="calendar_past"))

    keyboard.add(InlineKeyboardButton(text="➕ Предложить мероприятие отделу", callback_data="suggest_event"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    keyboard.adjust(1)

    # Формируем текст
    text = "🗓️ **Ваш календарь мероприятий**\n\n"
    if today_events:
        text += f"📆 Сегодня: {len(today_events)}\n"
    text += f"📅 Предстоящие: {len(upcoming_events)}\n"
    text += f"📚 Прошедшие: {len(past_events)}"

    # Используем edit_text для CallbackQuery, answer для Message
    if hasattr(message_or_callback, 'message'):
        # Это CallbackQuery - используем edit_text
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        # Это Message - используем answer
        await message.answer(text, reply_markup=keyboard.as_markup())


async def show_upcoming_events(callback: CallbackQuery):
    """Показать предстоящие мероприятия"""
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    user_events = user_data.get('calendar', {}).get('events', {})
    upcoming_events = {}

    current_date = datetime.now().date()

    for event_id, event_data in user_events.items():
        event_date_str = event_data.get('date')
        event_date = parse_event_date(event_date_str)
        
        if event_date is None or event_date >= current_date:
            # Если дата не указана или будущая/сегодняшняя, считаем предстоящим
            upcoming_events[event_id] = event_data

    if not upcoming_events:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar"))
        await callback.message.edit_text(
            "📅 У вас нет предстоящих мероприятий",
            reply_markup=keyboard.as_markup()
        )
        return

    # Сортируем по дате
    def get_sort_date(item):
        event_data = item[1]
        date = parse_event_date(event_data.get('date'))
        return date if date else datetime(2099, 1, 1).date()
    
    sorted_events = sorted(upcoming_events.items(), key=get_sort_date)

    # Показываем первые 5 мероприятий
    keyboard = InlineKeyboardBuilder()

    for event_id, event_data in sorted_events[:5]:
        event_name = event_data.get('name', 'Неизвестное мероприятие')
        event_date = event_data.get('date', 'Дата не указана')
        keyboard.add(InlineKeyboardButton(
            text=f"📅 {event_date} - {event_name[:20]}...",
            callback_data=f"calendar_event_{event_id}"
        ))

    if len(sorted_events) > 5:
        keyboard.add(InlineKeyboardButton(text="📖 Показать еще...", callback_data="calendar_more_upcoming"))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar"))
    keyboard.adjust(1)

    text = "📅 **Предстоящие мероприятия:**\n\n"
    for event_id, event_data in sorted_events[:5]:
        event_name = event_data.get('name', 'Неизвестное мероприятие')
        event_date = event_data.get('date', 'Дата не указана')
        event_type = event_data.get('type', 'Тип не указан')
        text += f"• **{event_name}**\n  📅 {event_date} | {event_type}\n\n"

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await callback.answer()


async def show_past_events(callback: CallbackQuery):
    """Показать прошедшие мероприятия"""
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    user_events = user_data.get('calendar', {}).get('events', {})
    past_events = {}

    current_date = datetime.now().date()

    for event_id, event_data in user_events.items():
        event_date_str = event_data.get('date')
        event_date = parse_event_date(event_date_str)
        
        if event_date and event_date < current_date:
            past_events[event_id] = event_data

    if not past_events:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar"))
        await callback.message.edit_text(
            "📚 У вас нет прошедших мероприятий",
            reply_markup=keyboard.as_markup()
        )
        return

    # Сортируем по дате (новые сначала)
    def get_sort_date(item):
        event_data = item[1]
        date = parse_event_date(event_data.get('date'))
        return date if date else datetime(2000, 1, 1).date()
    
    sorted_events = sorted(past_events.items(), key=get_sort_date, reverse=True)

    keyboard = InlineKeyboardBuilder()

    for event_id, event_data in sorted_events[:5]:
        event_name = event_data.get('name', 'Неизвестное мероприятие')
        event_date = event_data.get('date', 'Дата не указана')
        keyboard.add(InlineKeyboardButton(
            text=f"📚 {event_date} - {event_name[:20]}...",
            callback_data=f"calendar_event_{event_id}"
        ))

    if len(sorted_events) > 5:
        keyboard.add(InlineKeyboardButton(text="📖 Показать еще...", callback_data="calendar_more_past"))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar"))
    keyboard.adjust(1)

    text = "📚 **Прошедшие мероприятия:**\n\n"
    for event_id, event_data in sorted_events[:5]:
        event_name = event_data.get('name', 'Неизвестное мероприятие')
        event_date = event_data.get('date', 'Дата не указана')
        event_type = event_data.get('type', 'Тип не указан')
        text += f"• **{event_name}**\n  📅 {event_date} | {event_type}\n\n"

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await callback.answer()


async def show_event_details(callback: CallbackQuery, event_id: str):
    """Показать детали мероприятия из календаря"""
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    event_data = user_data.get('calendar', {}).get('events', {}).get(event_id)

    if not event_data:
        await callback.answer("❌ Мероприятие не найдено")
        return

    text = f"🎯 **{event_data.get('name', 'Неизвестное мероприятие')}**\n\n"
    text += f"📅 **Дата:** {event_data.get('date', 'Не указана')}\n"
    text += f"📍 **Место:** {event_data.get('location', 'Не указано')}\n"
    text += f"💰 **Стоимость:** {event_data.get('cost', 'Не указана')}\n"
    text += f"📝 **Тип:** {event_data.get('type', 'Не указан')}\n\n"
    text += f"📋 **Описание:** {event_data.get('description', 'Описание отсутствует')}\n\n"
    text += f"🔗 **Ссылка:** {event_data.get('link', 'Не указана')}\n\n"

    # Добавляем информацию о статусе
    status = event_data.get('status', 'confirmed')
    if status == 'suggested':
        text += "📨 **Статус:** Предложено отделу (ожидает подтверждения)\n"
    elif status == 'confirmed':
        text += "✅ **Статус:** Подтверждено\n"

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar_list"))

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await callback.answer()


async def suggest_event_to_department(callback: CallbackQuery):
    """Начать процесс предложения мероприятия отделу"""
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    if user_data.get('role') != 'user':
        await callback.answer("❌ Только пользователи могут предлагать мероприятия")
        return

    department = user_data['profile'].get('department')
    if not department or department == '-':
        await callback.answer("❌ У вас не указан отдел")
        return

    # Получаем мероприятия пользователя для предложения
    user_events = user_data.get('calendar', {}).get('events', {})
    available_events = {}

    current_date = datetime.now().date()

    for event_id, event_data in user_events.items():
        event_date_str = event_data.get('date')
        event_date = parse_event_date(event_date_str)
        
        # Если дата не указана или будущая/сегодняшняя, и статус не "предложено"
        if (event_date is None or event_date >= current_date) and event_data.get('status') != 'suggested':
            available_events[event_id] = event_data

    if not available_events:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar"))
        await callback.message.edit_text(
            "❌ У вас нет мероприятий для предложения отделу",
            reply_markup=keyboard.as_markup()
        )
        return

    keyboard = InlineKeyboardBuilder()

    for event_id, event_data in available_events.items():
        event_name = event_data.get('name', 'Неизвестное мероприятие')
        event_date = event_data.get('date', 'Дата не указана')
        keyboard.add(InlineKeyboardButton(
            text=f"📅 {event_date} - {event_name[:25]}",
            callback_data=f"suggest_event_{event_id}"
        ))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar"))
    keyboard.adjust(1)

    await callback.message.edit_text(
        f"📨 **Выберите мероприятие для предложения отделу {department}:**",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def handle_suggest_event(callback: CallbackQuery, event_id: str):
    """Обработать предложение мероприятия"""
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    event_data = user_data.get('calendar', {}).get('events', {}).get(event_id)

    if not event_data:
        await callback.answer("❌ Мероприятие не найдено")
        return

    department = user_data['profile'].get('department')

    # Находим организатора отдела
    all_users = manager.get_users_from_base()
    organizer_id = None

    for uid in all_users:
        user_info = manager.get_from_base(uid)
        if (user_info and user_info.get('role') == 'organization' and
                user_info.get('profile', {}).get('department') == department):
            organizer_id = uid
            break

    if not organizer_id:
        await callback.answer("❌ Организатор отдела не найден")
        return

    # Добавляем предложение организатору
    organizer_data = manager.get_from_base(organizer_id)
    if 'suggestions' not in organizer_data:
        organizer_data['suggestions'] = {}

    suggestion_id = f"{user_id}_{event_id}"
    organizer_data['suggestions'][suggestion_id] = {
        'event_data': event_data,
        'suggested_by': user_id,
        'suggested_by_name': user_data['profile'].get('fullname', user_data['name']),
        'suggested_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'status': 'pending'
    }

    # Обновляем статус мероприятия у пользователя
    if 'calendar' not in user_data:
        user_data['calendar'] = {}
    if 'events' not in user_data['calendar']:
        user_data['calendar']['events'] = {}

    user_data['calendar']['events'][event_id]['status'] = 'suggested'

    # Сохраняем изменения
    manager.write_in_base(organizer_id, organizer_data)
    manager.write_in_base(user_id, user_data)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar"))

    await callback.message.edit_text(
        f"✅ Мероприятие предложено отделу {department}!\n"
        f"Организатор увидит его в своем профиле.",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def handle_back_to_calendar(callback: CallbackQuery):
    await show_calendar(callback, callback.from_user.id)


async def handle_back_to_calendar_list(callback: CallbackQuery):
    await show_upcoming_events(callback)


async def show_today_events(callback: CallbackQuery):
    """Показать события на сегодня"""
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    user_events = user_data.get('calendar', {}).get('events', {})
    today_events = {}

    current_date = datetime.now().date()

    for event_id, event_data in user_events.items():
        event_date_str = event_data.get('date')
        event_date = parse_event_date(event_date_str)
        
        if event_date and event_date == current_date:
            today_events[event_id] = event_data

    if not today_events:
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar"))
        await callback.message.edit_text(
            "📆 У вас нет мероприятий на сегодня",
            reply_markup=keyboard.as_markup()
        )
        return

    # Сортируем по времени (если есть) или просто показываем
    sorted_events = sorted(today_events.items(),
                           key=lambda x: x[1].get('name', ''))

    keyboard = InlineKeyboardBuilder()

    for event_id, event_data in sorted_events:
        event_name = event_data.get('name', 'Неизвестное мероприятие')
        event_time = event_data.get('time', '')
        display_text = f"📆 {event_name[:25]}"
        if event_time:
            display_text = f"📆 {event_time} - {event_name[:20]}"
        keyboard.add(InlineKeyboardButton(
            text=display_text,
            callback_data=f"calendar_event_{event_id}"
        ))

    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_calendar"))
    keyboard.adjust(1)

    text = "📆 **Мероприятия на сегодня:**\n\n"
    for event_id, event_data in sorted_events:
        event_name = event_data.get('name', 'Неизвестное мероприятие')
        event_date = event_data.get('date', 'Сегодня')
        event_type = event_data.get('type', 'Тип не указан')
        text += f"• **{event_name}**\n  📅 {event_date} | {event_type}\n\n"

    await callback.message.edit_text(text, reply_markup=keyboard.as_markup())
    await callback.answer()


async def handle_show_calendar(callback: CallbackQuery):
    """Обработчик для показа календаря из callback"""
    await show_calendar(callback, callback.from_user.id)

async def handle_show_event_details(callback: CallbackQuery):
    """Обработчик для показа деталей мероприятия"""
    event_id = callback.data.replace("calendar_event_", "")
    await show_event_details(callback, event_id)

async def handle_suggest_event_wrapper(callback: CallbackQuery):
    """Обработчик для предложения мероприятия"""
    event_id = callback.data.replace("suggest_event_", "")
    await handle_suggest_event(callback, event_id)

def register_handlers(dp):
    dp.callback_query.register(handle_show_calendar, F.data == "main_calendar")
    dp.callback_query.register(show_today_events, F.data == "calendar_today")
    dp.callback_query.register(show_upcoming_events, F.data == "calendar_upcoming")
    dp.callback_query.register(show_past_events, F.data == "calendar_past")
    dp.callback_query.register(suggest_event_to_department, F.data == "suggest_event")
    dp.callback_query.register(handle_back_to_calendar, F.data == "back_to_calendar")
    dp.callback_query.register(handle_back_to_calendar_list, F.data == "back_to_calendar_list")

    dp.callback_query.register(handle_show_event_details, F.data.startswith("calendar_event_"))
    dp.callback_query.register(handle_suggest_event_wrapper, F.data.startswith("suggest_event_"))