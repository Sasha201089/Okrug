from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from aiogram.filters import Command
import DataBase.Manager as manager


class FilterState:
    ROLE = "role"
    THEME = "theme"
    FORMAT = "format"
    PARTICIPATION = "participation"
    PAYMENT = "payment"
    PRICE = "price"
    DURATION = "duration"
    COMPLETED = "completed"


ROLES_FILTER = {
    "data-scientist": "Data Scientist",
    "backend": "Backend-разработчик",
    "analyst": "Product Analyst",
    "designer": "Дизайнер / UX",
    "team-lead": "Team Lead",
    "product_manager": "Product Manager",
    "hr": "HR / рекрутёр",
    "other": "Другой"
}

THEMES_FILTER = {
    "d443_science": "D443 Science",
    "backend": "Backend",
    "fintech": "Финтех",
    "team-management": "Управление командами",
    "design": "Дизайн",
    "other": "Другое"
}

FORMATS_FILTER = {
    "conference": "Конференция",
    "masterclass": "Мастер-классы",
    "career": "Карьерные",
    "meetup": "Митапы",
    "hackathon": "Хакатоны"
}

PARTICIPATION_FILTER = {
    "offline": "Офлайн",
    "online": "Онлайн",
    "hybrid": "Гибрид"
}

PAYMENT_FILTER = {
    "free": "Бесплатные",
    "company-paid": "Оплата компании",
    "partial": "Частичная доплата"
}

DURATION_FILTER = {
    "1-day": "1 день",
    "2-4-days": "2-4 дня",
    "5-7-days": "5-7 дней",
    "over-7-days": "Свыше 7 дней"
}


async def handle_set_price_min(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    if 'filters' not in user_data:
        user_data['filters'] = {}

    user_data['filters']['waiting_price_input'] = 'min'
    manager.write_in_base(user_id, user_data)

    await callback.message.edit_text(
        "💰 Введите минимальную стоимость (в рублях):",
        reply_markup=InlineKeyboardBuilder()
        .add(InlineKeyboardButton(text="⬅️ Назад", callback_data="filter_price"))
        .as_markup()
    )
    await callback.answer()


async def handle_set_price_max(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    if 'filters' not in user_data:
        user_data['filters'] = {}

    user_data['filters']['waiting_price_input'] = 'max'
    manager.write_in_base(user_id, user_data)

    await callback.message.edit_text(
        "💰 Введите максимальную стоимость (в рублях):",
        reply_markup=InlineKeyboardBuilder()
        .add(InlineKeyboardButton(text="⬅️ Назад", callback_data="filter_price"))
        .as_markup()
    )
    await callback.answer()
async def show_filters_menu(message: Message, user_id):
    user_id = str(user_id)
    user_data = manager.get_from_base(user_id)

    if not user_data or user_data.get('state') != 'completed':
        await message.answer("❌ Сначала завершите регистрацию через /start")
        return

    current_filters = user_data.get('filters', {})

    filters_text = "🔍 **Настройки фильтров**\n\n"

    if current_filters.get('roles'):
        roles_text = ", ".join([ROLES_FILTER.get(r, r) for r in current_filters['roles']])
        filters_text += f"👤 **Роли:** {roles_text}\n"
    else:
        filters_text += "👤 **Роли:** Не выбрано\n"

    if current_filters.get('themes'):
        themes_text = ", ".join([THEMES_FILTER.get(t, t) for t in current_filters['themes']])
        filters_text += f"🎯 **Темы:** {themes_text}\n"
    else:
        filters_text += "🎯 **Темы:** Не выбрано\n"

    if current_filters.get('formats'):
        formats_text = ", ".join([FORMATS_FILTER.get(f, f) for f in current_filters['formats']])
        filters_text += f"📅 **Форматы:** {formats_text}\n"
    else:
        filters_text += "📅 **Форматы:** Не выбрано\n"

    if current_filters.get('participation'):
        participation_text = ", ".join([PARTICIPATION_FILTER.get(p, p) for p in current_filters['participation']])
        filters_text += f"📍 **Участие:** {participation_text}\n"
    else:
        filters_text += "📍 **Участие:** Не выбрано\n"

    if current_filters.get('payment'):
        payment_text = ", ".join([PAYMENT_FILTER.get(p, p) for p in current_filters['payment']])
        filters_text += f"💰 **Оплата:** {payment_text}\n"
    else:
        filters_text += "💰 **Оплата:** Не выбрано\n"

    if current_filters.get('price_min') or current_filters.get('price_max'):
        price_min = current_filters.get('price_min', 0)
        price_max = current_filters.get('price_max', 100000)
        filters_text += f"💵 **Стоимость:** {price_min} - {price_max} руб.\n"
    else:
        filters_text += "💵 **Стоимость:** Не настроено\n"

    if current_filters.get('durations'):
        durations_text = ", ".join([DURATION_FILTER.get(d, d) for d in current_filters['durations']])
        filters_text += f"⏱️ **Длительность:** {durations_text}\n"
    else:
        filters_text += "⏱️ **Длительность:** Не выбрано\n"

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="👤 Роли", callback_data="filter_roles"))
    keyboard.add(InlineKeyboardButton(text="🎯 Тема", callback_data="filter_theme"))
    keyboard.add(InlineKeyboardButton(text="📅 Формат мероприятия", callback_data="filter_format"))
    keyboard.add(InlineKeyboardButton(text="📍 Формат участия", callback_data="filter_participation"))
    keyboard.add(InlineKeyboardButton(text="💰 Вид оплаты", callback_data="filter_payment"))
    keyboard.add(InlineKeyboardButton(text="💵 Стоимость", callback_data="filter_price"))
    keyboard.add(InlineKeyboardButton(text="⏱️ Длительность", callback_data="filter_duration"))
    keyboard.add(InlineKeyboardButton(text="✅ Применить фильтры", callback_data="apply_filters"))
    keyboard.add(InlineKeyboardButton(text="🗑️ Сбросить фильтры", callback_data="reset_filters"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    keyboard.adjust(2)

    await message.answer(filters_text, reply_markup=keyboard.as_markup())


async def handle_filter_roles(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)
    current_filters = user_data.get('filters', {})
    selected_roles = current_filters.get('roles', [])

    keyboard = InlineKeyboardBuilder()

    for role_key, role_name in ROLES_FILTER.items():
        is_selected = "✅" if role_key in selected_roles else "⚪"
        keyboard.add(InlineKeyboardButton(text=f"{is_selected} {role_name}", callback_data=f"role_select_{role_key}"))

    keyboard.add(InlineKeyboardButton(text="📝 Другая роль (текст)", callback_data="role_other_input"))
    keyboard.add(InlineKeyboardButton(text="✅ Готово", callback_data="filter_roles_done"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters"))
    keyboard.adjust(1)

    await callback.message.edit_text(
        "👤 **Выберите роли:**\n(можно выбрать несколько)",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def handle_filter_theme(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)
    current_filters = user_data.get('filters', {})
    selected_themes = current_filters.get('themes', [])

    keyboard = InlineKeyboardBuilder()

    for theme_key, theme_name in THEMES_FILTER.items():
        is_selected = "✅" if theme_key in selected_themes else "⚪"
        keyboard.add(
            InlineKeyboardButton(text=f"{is_selected} {theme_name}", callback_data=f"theme_select_{theme_key}"))

    keyboard.add(InlineKeyboardButton(text="📝 Другая тема (текст)", callback_data="theme_other_input"))
    keyboard.add(InlineKeyboardButton(text="✅ Готово", callback_data="filter_theme_done"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters"))
    keyboard.adjust(1)

    await callback.message.edit_text(
        "🎯 **Выберите темы:**\n(можно выбрать несколько)",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def handle_filter_format(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)
    current_filters = user_data.get('filters', {})
    selected_formats = current_filters.get('formats', [])

    keyboard = InlineKeyboardBuilder()

    for format_key, format_name in FORMATS_FILTER.items():
        is_selected = "✅" if format_key in selected_formats else "⚪"
        keyboard.add(
            InlineKeyboardButton(text=f"{is_selected} {format_name}", callback_data=f"format_select_{format_key}"))

    keyboard.add(InlineKeyboardButton(text="✅ Готово", callback_data="filter_format_done"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters"))
    keyboard.adjust(1)

    await callback.message.edit_text(
        "📅 **Выберите форматы мероприятий:**\n(можно выбрать несколько)",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def handle_filter_participation(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)
    current_filters = user_data.get('filters', {})
    selected_participation = current_filters.get('participation', [])

    keyboard = InlineKeyboardBuilder()

    for part_key, part_name in PARTICIPATION_FILTER.items():
        is_selected = "✅" if part_key in selected_participation else "⚪"
        keyboard.add(
            InlineKeyboardButton(text=f"{is_selected} {part_name}", callback_data=f"participation_select_{part_key}"))

    keyboard.add(InlineKeyboardButton(text="✅ Готово", callback_data="filter_participation_done"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters"))
    keyboard.adjust(1)

    await callback.message.edit_text(
        "📍 **Выберите формат участия:**\n(можно выбрать несколько)",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def handle_filter_payment(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)
    current_filters = user_data.get('filters', {})
    selected_payment = current_filters.get('payment', [])

    keyboard = InlineKeyboardBuilder()

    for pay_key, pay_name in PAYMENT_FILTER.items():
        is_selected = "✅" if pay_key in selected_payment else "⚪"
        keyboard.add(InlineKeyboardButton(text=f"{is_selected} {pay_name}", callback_data=f"payment_select_{pay_key}"))

    keyboard.add(InlineKeyboardButton(text="✅ Готово", callback_data="filter_payment_done"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters"))
    keyboard.adjust(1)

    await callback.message.edit_text(
        "💰 **Выберите вид оплаты:**\n(можно выбрать несколько)",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def handle_filter_duration(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)
    current_filters = user_data.get('filters', {})
    selected_durations = current_filters.get('durations', [])

    keyboard = InlineKeyboardBuilder()

    for dur_key, dur_name in DURATION_FILTER.items():
        is_selected = "✅" if dur_key in selected_durations else "⚪"
        keyboard.add(InlineKeyboardButton(text=f"{is_selected} {dur_name}", callback_data=f"duration_select_{dur_key}"))

    keyboard.add(InlineKeyboardButton(text="✅ Готово", callback_data="filter_duration_done"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters"))
    keyboard.adjust(1)

    await callback.message.edit_text(
        "⏱️ **Выберите длительность:**\n(можно выбрать несколько)",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def handle_filter_price(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)
    current_filters = user_data.get('filters', {})

    price_min = current_filters.get('price_min', 0)
    price_max = current_filters.get('price_max', 100000)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="💰 Установить минимальную цену", callback_data="set_price_min"))
    keyboard.add(InlineKeyboardButton(text="💰 Установить максимальную цену", callback_data="set_price_max"))
    keyboard.add(InlineKeyboardButton(text="✅ Готово", callback_data="back_to_filters"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_filters"))
    keyboard.adjust(1)

    await callback.message.edit_text(
        f"💵 **Настройка стоимости:**\n\n"
        f"Минимальная цена: {price_min} руб.\n"
        f"Максимальная цена: {price_max} руб.\n\n"
        f"Используйте кнопки ниже для настройки:",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()


async def handle_role_selection(callback: CallbackQuery):
    print("HHHHHHHHHHH")
    user_id = str(callback.from_user.id)
    role_key = callback.data.split("_")[2]

    user_data = manager.get_from_base(user_id)
    if 'filters' not in user_data:
        user_data['filters'] = {}
    if 'roles' not in user_data['filters']:
        user_data['filters']['roles'] = []

    if role_key in user_data['filters']['roles']:
        user_data['filters']['roles'].remove(role_key)
    else:
        user_data['filters']['roles'].append(role_key)

    manager.write_in_base(user_id, user_data)
    await callback.answer()
    await handle_filter_roles(callback)


async def handle_theme_selection(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    theme_key = callback.data.split("_")[2]

    user_data = manager.get_from_base(user_id)
    if 'filters' not in user_data:
        user_data['filters'] = {}
    if 'themes' not in user_data['filters']:
        user_data['filters']['themes'] = []

    if theme_key in user_data['filters']['themes']:
        user_data['filters']['themes'].remove(theme_key)
    else:
        user_data['filters']['themes'].append(theme_key)

    manager.write_in_base(user_id, user_data)
    await callback.answer()
    await handle_filter_theme(callback)


async def handle_format_selection(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    format_key = callback.data.split("_")[2]

    user_data = manager.get_from_base(user_id)
    if 'filters' not in user_data:
        user_data['filters'] = {}
    if 'formats' not in user_data['filters']:
        user_data['filters']['formats'] = []

    if format_key in user_data['filters']['formats']:
        user_data['filters']['formats'].remove(format_key)
    else:
        user_data['filters']['formats'].append(format_key)

    manager.write_in_base(user_id, user_data)
    await callback.answer()
    await handle_filter_format(callback)


async def handle_participation_selection(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    part_key = callback.data.split("_")[2]

    user_data = manager.get_from_base(user_id)
    if 'filters' not in user_data:
        user_data['filters'] = {}
    if 'participation' not in user_data['filters']:
        user_data['filters']['participation'] = []

    if part_key in user_data['filters']['participation']:
        user_data['filters']['participation'].remove(part_key)
    else:
        user_data['filters']['participation'].append(part_key)

    manager.write_in_base(user_id, user_data)
    await callback.answer()
    await handle_filter_participation(callback)


async def handle_payment_selection(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    pay_key = callback.data.split("_")[2]

    user_data = manager.get_from_base(user_id)
    if 'filters' not in user_data:
        user_data['filters'] = {}
    if 'payment' not in user_data['filters']:
        user_data['filters']['payment'] = []

    if pay_key in user_data['filters']['payment']:
        user_data['filters']['payment'].remove(pay_key)
    else:
        user_data['filters']['payment'].append(pay_key)

    manager.write_in_base(user_id, user_data)
    await handle_filter_payment(callback)


async def handle_duration_selection(callback: CallbackQuery):
    print("HHHHHHHHHHH")
    user_id = str(callback.from_user.id)
    dur_key = callback.data.split("_")[2]

    user_data = manager.get_from_base(user_id)
    if 'filters' not in user_data:
        user_data['filters'] = {}
    if 'durations' not in user_data['filters']:
        user_data['filters']['durations'] = []

    if dur_key in user_data['filters']['durations']:
        user_data['filters']['durations'].remove(dur_key)
    else:
        user_data['filters']['durations'].append(dur_key)

    manager.write_in_base(user_id, user_data)
    await callback.answer()
    await handle_filter_duration(callback)


async def handle_apply_filters(callback: CallbackQuery):
    await callback.message.edit_text(
        "✅ Фильтры применены!\n\n"
        "Теперь вы можете использовать поиск мероприятий с выбранными настройками.",
        reply_markup=InlineKeyboardBuilder()
        .add(InlineKeyboardButton(text="⬅️ Назад к фильтрам", callback_data="back_to_filters"))
        .as_markup()
    )
    await callback.answer()


async def handle_reset_filters(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    user_data = manager.get_from_base(user_id)

    user_data['filters'] = {}
    manager.write_in_base(user_id, user_data)

    await callback.message.edit_text(
        "🗑️ Все фильтры сброшены!",
        reply_markup=InlineKeyboardBuilder()
        .add(InlineKeyboardButton(text="⬅️ Назад к фильтрам", callback_data="back_to_filters"))
        .as_markup()
    )
    await callback.answer()


async def handle_back_to_filters(callback: CallbackQuery):
    await show_filters_menu(callback.message, callback.from_user.id)

async def handle_filter_roles_done(callback: CallbackQuery):
    await show_filters_menu(callback.message, callback.from_user.id)

async def handle_filter_duration_done(callback: CallbackQuery):
    await show_filters_menu(callback.message, callback.from_user.id)

async def catch_all_handler(callback: CallbackQuery):
    print(f"CATCH ALL: {callback.data}")
    await callback.answer(f"Получен: {callback.data}")

def register_handlers(dp):
    dp.message.register(show_filters_menu, Command("filters"))
    dp.callback_query.register(handle_set_price_min, F.data == "set_price_min")
    dp.callback_query.register(handle_set_price_max, F.data == "set_price_max")
    dp.callback_query.register(handle_filter_roles, F.data == "filter_roles")
    dp.callback_query.register(handle_filter_theme, F.data == "filter_theme")
    dp.callback_query.register(handle_filter_format, F.data == "filter_format")
    dp.callback_query.register(handle_filter_participation, F.data == "filter_participation")
    dp.callback_query.register(handle_filter_payment, F.data == "filter_payment")
    dp.callback_query.register(handle_filter_price, F.data == "filter_price")
    dp.callback_query.register(handle_filter_duration, F.data == "filter_duration")
    dp.callback_query.register(handle_back_to_filters, F.data == "filter_roles_done")
    dp.callback_query.register(handle_back_to_filters, F.data == "filter_duration_done")
    dp.callback_query.register(handle_role_selection, F.data.startswith("role_select_"))
    dp.callback_query.register(handle_theme_selection, F.data.startswith("theme_select_"))
    dp.callback_query.register(handle_format_selection, F.data.startswith("format_select_"))
    dp.callback_query.register(handle_participation_selection, F.data.startswith("participation_select_"))
    dp.callback_query.register(handle_payment_selection, F.data.startswith("payment_select_"))
    dp.callback_query.register(handle_duration_selection, F.data.startswith("duration_select_"))
    dp.callback_query.register(handle_apply_filters, F.data == "apply_filters")
    dp.callback_query.register(handle_reset_filters, F.data == "reset_filters")
    dp.callback_query.register(handle_back_to_filters, F.data == "back_to_filters")
    dp.callback_query.register(handle_back_to_filters, F.data == "filter_theme_done")
    dp.callback_query.register(handle_back_to_filters, F.data == "filter_format_done")
    dp.callback_query.register(handle_back_to_filters, F.data == "filter_participation_done")
    dp.callback_query.register(handle_back_to_filters, F.data == "filter_payment_done")

    #dp.callback_query.register(handle_back_to_filters, F.data.endswith("_done"))
