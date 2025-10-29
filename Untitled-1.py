#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ========== === НАСТРОЙКИ === ==========
API_TOKEN = "8431308016:AAEvKejj9VzGe7mesnv5bBhlzGmRhqs0dwY"

# ID группы (куда приходят заявки)
ADMIN_CHAT_ID = -1001234567890  # <-- вставь ID супергруппы

# ID твоего личного Telegram аккаунта
OWNER_ID = 556091656  # <-- твой личный Telegram ID (@userinfobot покажет)

# Приветственный текст
WELCOME_TEXT = """
💂‍♂️ Добро пожаловать! Это бот набора на службу по контракту.

📋 Мы поможем подобрать регион и вакансию, а также оформить отношение.

Примеры вакансий:
- Стрелок-пулемётчик
- Водитель БТР
- Медицинский инструктор
- Связист

Нажмите «📋 Начать опрос», чтобы подать заявку.
"""

# Регионы
REGIONS = [
    "Москва — г. Москва по условиям 2,3 млн рублей выплата, 290 тыс руб зарплата + 50 тыс руб надбавка...",
    "Московская область — 3 млн рублей выплата, 290 тыс руб зарплата + 20 тыс надбавка за детей...",
    "Ленинградская область — 2,4 млн рублей выплата, 290 тыс руб зарплата + 20 тыс руб надбавка за ребенка...",
    "Рязань — 1,5 млн рублей выплата, 290 тыс руб зарплата + 20 тыс руб надбавка за ребенка...",
    "Вологда — 1,2 млн рублей выплата, 290 тыс руб зарплата + 20 тыс руб надбавка за ребенка...",
    "Смоленск — 1,2 млн рублей выплата, 290 тыс руб зарплата + 20 тыс руб надбавка за ребенка...",
]

# Вакансии
VACANCIES_EXAMPLES = [
    "Стрелок-пулемётчик",
    "Водитель БТР и др. техники (по ВУС)",
    "Медицинский инструктор (по ВУС)",
    "Связист (по ВУС)",
    "Охрана объектов",
    "РемБат (по ВУС)",
    "Бпла (по ВУС)",
    "Сварщик (по ВУС)",
    "Дизелист (по ВУС)",
    "Материальное обеспечение (по ВУС)",
]

DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "submissions.csv")
XLSX_FILE = os.path.join(DATA_DIR, "submissions.xlsx")

# ========= Настройка логов ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs(DATA_DIR, exist_ok=True)

# ========= Инициализация ==========
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========= Главное меню ==========
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Начать опрос"), KeyboardButton(text="📍 Условия по регионам")],
        [KeyboardButton(text="ℹ️ Отношение / информация"), KeyboardButton(text="📂 Примеры вакансий")]
    ],
    resize_keyboard=True
)

# ========= FSM ==========
class Form(StatesGroup):
    fio = State()
    phone = State()
    health = State()
    service = State()
    age = State()
    rights = State()
    education = State()
    experience = State()
    position = State()

# ========= Функция сохранения ==========
def save_submission_to_files(submission: dict):
    df_new = pd.DataFrame([submission])
    if not os.path.exists(CSV_FILE):
        df_new.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    else:
        df_existing = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
        df_total = pd.concat([df_existing, df_new], ignore_index=True)
        df_total.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    df_total.to_excel(XLSX_FILE, index=False)

# ========= Команды ==========
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu)

@dp.message(lambda m: m.text == "📍 Условия по регионам")
async def show_regions(message: types.Message):
    text = "📍 Доступные регионы:\n\n" + "\n".join([f"• {r}" for r in REGIONS])
    await message.answer(text)

@dp.message(lambda m: m.text == "ℹ️ Отношение / информация")
async def info_relation(message: types.Message):
    text = (
        "📄 Мы оформляем отношение, помогаем подобрать вакансию и регион, "
        "а также сопровождаем кандидата при оформлении документов."
    )
    await message.answer(text)

@dp.message(lambda m: m.text == "📂 Примеры вакансий")
async def show_vacancies(message: types.Message):
    text = "📌 Примеры вакансий:\n\n" + "\n".join([f"• {v}" for v in VACANCIES_EXAMPLES])
    await message.answer(text)

@dp.message(lambda m: m.text == "📋 Начать опрос")
async def start_survey(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО полностью:")
    await state.set_state(Form.fio)

# === Вопросы формы ===
@dp.message(Form.fio)
async def process_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите контактный телефон:")
    await state.set_state(Form.phone)

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Есть ли проблемы со здоровьем?")
    await state.set_state(Form.health)

@dp.message(Form.health)
async def process_health(message: types.Message, state: FSMContext):
    await state.update_data(health=message.text)
    await message.answer("Были ли вы на военной службе / СВО? Если да — ВУС и опыт:")
    await state.set_state(Form.service)

@dp.message(Form.service)
async def process_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await message.answer("Возраст:")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Категория прав:")
    await state.set_state(Form.rights)

@dp.message(Form.rights)
async def process_rights(message: types.Message, state: FSMContext):
    await state.update_data(rights=message.text)
    await message.answer("Образование / специальность:")
    await state.set_state(Form.education)

@dp.message(Form.education)
async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await message.answer("Профессиональный опыт / место работы:")
    await state.set_state(Form.experience)

@dp.message(Form.experience)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await message.answer("Желаемая должность или вакансия:")
    await state.set_state(Form.position)

@dp.message(Form.position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    data = await state.get_data()

    submission = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **data
    }
    save_submission_to_files(submission)

    admin_text = (
        "📋 <b>Новая заявка</b>\n\n"
        f"👤 <b>ФИО:</b> {data['fio']}\n"
        f"📞 <b>Телефон:</b> {data['phone']}\n"
        f"💊 <b>Здоровье:</b> {data['health']}\n"
        f"🎖️ <b>Служба:</b> {data['service']}\n"
        f"🎂 <b>Возраст:</b> {data['age']}\n"
        f"🚗 <b>Права:</b> {data['rights']}\n"
        f"🎓 <b>Образование:</b> {data['education']}\n"
        f"💼 <b>Опыт:</b> {data['experience']}\n"
        f"📌 <b>Вакансия:</b> {data['position']}\n"
    )

    try:
        await bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Не удалось отправить админу: {e}")

    await message.answer("✅ Ваша заявка отправлена!", reply_markup=main_menu)
    await state.clear()

# ========= Команда /admin ==========
@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    """Простая админ-команда для проверки состояния и получения Excel"""
    
    if message.from_user.id != OWNER_ID:
        await message.answer("🚫 У вас нет доступа к админ-командам.")
        return

    csv_exists = os.path.exists(CSV_FILE)
    xlsx_exists = os.path.exists(XLSX_FILE)

    submissions_count = 0
    last_time = "—"
    if csv_exists:
        try:
            df = pd.read_csv(CSV_FILE)
            submissions_count = len(df)
            if submissions_count > 0 and "timestamp" in df.columns:
                last_time = df["timestamp"].iloc[-1]
        except Exception as e:
            logger.exception("Ошибка при чтении CSV: %s", e)

    text = (
        "⚙️ <b>Админ-панель</b>\n\n"
        f"📊 Всего заявок: <b>{submissions_count}</b>\n"
        f"🕒 Последняя заявка: <b>{last_time}</b>\n"
        f"📂 CSV файл: <code>{CSV_FILE}</code>\n"
        f"📘 Excel файл: <code>{XLSX_FILE}</code>\n"
    )

    await message.answer(text, parse_mode="HTML")

    if xlsx_exists:
        try:
            file = FSInputFile(XLSX_FILE)
            await bot.send_document(OWNER_ID, file, caption="📎 Последние заявки (Excel)")
        except Exception as e:
            logger.exception("Не удалось отправить Excel файл: %s", e)

# ========= Обработчик по умолчанию ==========
@dp.message()
async def default_handler(message: types.Message):
    await message.answer("Выберите опцию в меню или нажмите /start для начала.", reply_markup=main_menu)

# ========= Запуск ==========
if __name__ == "__main__":
    import asyncio
    logger.info("Bot started")
    asyncio.run(dp.start_polling(bot))

