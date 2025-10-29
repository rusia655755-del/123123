#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import StateFilter
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# ========== === НАСТРОЙКИ (редактируй тут) === ==========
API_TOKEN = "8431308016:AAEvKejj9VzGe7mesnv5bBhlzGmRhqs0dwY"  # токен бота
ADMIN_CHAT_ID = -1003244858296  # ID группы или твой Telegram ID

WELCOME_TEXT = """
💂‍♂️ Добро пожаловать!
Это официальный бот набора на военную службу по контракту.

📋 Мы поможем подобрать регион и вакансию, а также оформить направление для заключения контракта.

Примеры вакансий:
 • Стрелок-пулемётчик
 • Водитель БТР
 • Медицинский инструктор
 • Связист

🪖 Контракт заключается с Министерством обороны Российской Федерации. (Служба по контракту Министерства Обороны РФ набор осуществляется военкоматами на основании Указа Президента РФ №915 от 01.12.2023.)

⚖️ Правовые основания:
 • Контракт о прохождении военной службы заключается в соответствии со статьёй 34 Федерального закона № 53-ФЗ от 28.03.1998 г. «О воинской обязанности и военной службе».

 • Выплаты и социальные гарантии регулируются Федеральным законом № 306-ФЗ от 07.11.2011 г. «О денежном довольствии военнослужащих и предоставлении им отдельных выплат».

➡️ Нажмите «📋 Подать заявку», чтобы подать заявку и узнать подробности о службе по контракту
"""

REGIONS = [
    "Москва — г. Москва по условиям 2,3млн рублей выплата, 290тыс руб зарплата + 50тыс руб региональная надбавка, списание Долгов до 10млн, места детям а детские сады/школы, при проезде из другого города, проживание на время ВВК и проезд оплачивается\n\n",
    "Московская область — по условиям 3млн рублей выплата, 290тыс руб зарплата + 20тыс руб надбавка за детей, списание Долгов до 10млн, места детям, проживание и проезд оплачиваются\n\n",
    "Ленинградская область — условия: 2,4млн рублей выплата, 290тыс руб зарплата + 20тыс руб надбавка за ребёнка, списание долгов, проживание и проезд оплачиваются\n\n",
    "Рязань — условия: 1,5млн рублей выплата, 290тыс руб зарплата + 20тыс руб надбавка, списание долгов, проживание и проезд оплачиваются\n\n",
    "Вологда — условия: 1,2млн рублей выплата, 290тыс руб зарплата + 20тыс руб надбавка, списание долгов, проживание и проезд оплачиваются\n\n",
    "Смоленск — условия: 1,2млн рублей выплата, 290тыс руб зарплата + 20тыс руб надбавка, списание долгов, проживание и проезд оплачиваются\n\n",
]

VACANCIES_EXAMPLES = [
    "Стрелок-пулемётчик",
    "Водитель БТР и др. военной техники (набор по специальности или ВУС)",
    "Медицинский инструктор (набор по специальности или ВУС)",
    "Связист (набор по специальности или ВУС)",
    "Стрелок",
    "Водитель гуманитарных грузов (B,C)",
    "Охрана государственно важных объектов",
    "РемБат (набор по специальности или ВУС)",
    "Бпла (набор по специальности или ВУС)",
    "Сварщик (набор по специальности или ВУС)",
    "Техник (набор по специальности или ВУС)",
    "Дезелист (набор по специальности или ВУС)",
    "Материальное обеспечение (набор по специальности или ВУС)",
]

DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "submissions.csv")
XLSX_FILE = os.path.join(DATA_DIR, "submissions.xlsx")
# ========== === /НАСТРОЙКИ === ==========

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
os.makedirs(DATA_DIR, exist_ok=True)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Подать заявку"), KeyboardButton(text="📍 Условия по регионам")],
        [KeyboardButton(text="ℹ️ Отношение / информация"), KeyboardButton(text="📂 Основные доступные вакансии")]
    ],
    resize_keyboard=True
)

# FSM состояния
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

# Сохраняем заявки
def save_submission_to_files(submission: dict):
    df_new = pd.DataFrame([submission])
    if not os.path.exists(CSV_FILE):
        df_new.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    else:
        df_existing = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
        df_total = pd.concat([df_existing, df_new], ignore_index=True)
        df_total.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    try:
        df_total = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
        df_total.to_excel(XLSX_FILE, index=False)
    except Exception as e:
        logger.exception("Ошибка при записи в XLSX: %s", e)

# ================== Хэндлеры ==================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu)

@dp.message(lambda m: m.text == "📍 Условия по регионам")
async def show_regions(message: types.Message):
    text = "📍 Доступные регионы и условия:\n\n" + "\n".join(f"• {r}" for r in REGIONS)
    await message.answer(text)

@dp.message(lambda m: m.text == "ℹ️ Отношение / информация")
async def info_relation(message: types.Message):
    text = (
        "📄 Мы оформляем отношение, помогаем подобрать вакансию и регион, "
        "а также сопровождаем кандидата при оформлении документов.\n\n"
        "Если кандидат обратится к нам через этот бот — мы подберём подходящую вакансию и регион.\n\n"
        "Отношение (ходатайство) в военной службе — это документ, который выдаёт командир воинской части, в котором выражается согласие на принятие гражданина на военную службу по контракту или перевод военнослужащего в эту часть"
    )
    await message.answer(text)

@dp.message(lambda m: m.text == "📂 Основные доступные вакансии")
async def show_vacancies(message: types.Message):
    text = "📌 Основные доступные вакансии:\n\n" + "\n".join(f"• {v}" for v in VACANCIES_EXAMPLES)
    await message.answer(text)

@dp.message(lambda m: m.text == "📋 Подать заявку")
async def start_survey(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО полностью (Фамилия Имя Отчество):")
    await state.set_state(Form.fio)

# Обработчики состояний
@dp.message(StateFilter(Form.fio))
async def process_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text.strip())
    await message.answer("Контактный телефон:")
    await state.set_state(Form.phone)

@dp.message(StateFilter(Form.phone))
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await message.answer("Есть ли проблемы со здоровьем? Если нет — напишите 'Нет'.")
    await state.set_state(Form.health)

@dp.message(StateFilter(Form.health))
async def process_health(message: types.Message, state: FSMContext):
    await state.update_data(health=message.text.strip())
    await message.answer("Были ли вы ранее на военной службе или в СВО? (Если да — укажите ВУС и опыт, иначе 'Нет')")
    await state.set_state(Form.service)

@dp.message(StateFilter(Form.service))
async def process_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text.strip())
    await message.answer("Возраст (цифрами):")
    await state.set_state(Form.age)

@dp.message(StateFilter(Form.age))
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text.strip())
    await message.answer("Категория водительских прав (например: B, C; или 'Нет'):")
    await state.set_state(Form.rights)

@dp.message(StateFilter(Form.rights))
async def process_rights(message: types.Message, state: FSMContext):
    await state.update_data(rights=message.text.strip())
    await message.answer("Образование / специальность:")
    await state.set_state(Form.education)

@dp.message(StateFilter(Form.education))
async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text.strip())
    await message.answer("Профессиональный опыт / место работы (если есть):")
    await state.set_state(Form.experience)

@dp.message(StateFilter(Form.experience))
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text.strip())
    await message.answer("Желаемая должность или вакансия, куда вы хотите попасть:")
    await state.set_state(Form.position)

@dp.message(StateFilter(Form.position))
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text.strip())
    data = await state.get_data()

    submission = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fio": data.get("fio", ""),
        "phone": data.get("phone", ""),
        "health": data.get("health", ""),
        "service": data.get("service", ""),
        "age": data.get("age", ""),
        "rights": data.get("rights", ""),
        "education": data.get("education", ""),
        "experience": data.get("experience", ""),
        "position": data.get("position", ""),
    }

    try:
        save_submission_to_files(submission)
    except Exception as e:
        logger.exception("Не удалось сохранить заявку в файл: %s", e)

    admin_text = (
        "📋 <b>Новая заявка</b>\n\n"
        f"👤 <b>ФИО:</b> {submission['fio']}\n"
        f"📞 <b>Телефон:</b> {submission['phone']}\n"
        f"💊 <b>Здоровье:</b> {submission['health']}\n"
        f"🎖️ <b>Служба/СВО:</b> {submission['service']}\n"
        f"🎂 <b>Возраст:</b> {submission['age']}\n"
        f"🚗 <b>Права:</b> {submission['rights']}\n"
        f"🎓 <b>Образование:</b> {submission['education']}\n"
        f"💼 <b>Опыт:</b> {submission['experience']}\n"
        f"📌 <b>Желаемая вакансия:</b> {submission['position']}\n"
        f"🕒 <b>Время:</b> {submission['timestamp']}\n"
    )

    try:
        await bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")
    except Exception as e:
        logger.exception("Не удалось отправить заявку админу: %s", e)

    await message.answer("✅ Спасибо! Ваша заявка принята и отправлена. Мы с вами свяжемся.", reply_markup=main_menu)
    await state.clear()

@dp.message()
async def default_handler(message: types.Message):
    await message.answer("Выберите опцию в меню или нажмите /start для начала.", reply_markup=main_menu)

if __name__ == "__main__":
    import asyncio
    logger.info("Bot started")

    asyncio.run(dp.start_polling(bot))

@dp.message(Command("admin"))
async def admin_command(message: types.Message):
    # Проверяем, что сообщение отправлено админом
    if message.from_user.id != ADMIN_CHAT_ID:
        await message.answer("🚫 У вас нет доступа к админ-командам.")
        return

    # Проверяем, есть ли файл с заявками
    csv_exists = os.path.exists(CSV_FILE)
    xlsx_exists = os.path.exists(XLSX_FILE)

    # Считаем количество строк (заявок)
    submissions_count = 0
    last_time = "—"
    if csv_exists:
        try:
            df = pd.read_csv(CSV_FILE)
            submissions_count = len(df)
            if submissions_count > 0 and "timestamp" in df.columns:
                last_time = df["timestamp"].iloc[-1]
        except Exception as e:
            logger.exception("Ошибка чтения CSV: %s", e)

    # Формируем сообщение
    text = (
        "⚙️ <b>Админ-панель</b>\n\n"
        f"📊 Всего заявок: <b>{submissions_count}</b>\n"
        f"🕒 Последняя заявка: <b>{last_time}</b>\n"
        f"📂 CSV файл: <code>{CSV_FILE}</code>\n"
        f"📘 Excel файл: <code>{XLSX_FILE}</code>\n"
    )

    await message.answer(text, parse_mode="HTML")

    # Прикрепляем Excel-файл, если есть
    if xlsx_exists:
        try:
            file = types.FSInputFile(XLSX_FILE)
            await bot.send_document(ADMIN_CHAT_ID, file, caption="📎 Последние заявки (Excel)")
        except Exception as e:
            logger.exception("Не удалось отправить Excel файл: %s", e)


