from aiogram import Bot, Dispatcher, executor, types
import datetime
import asyncio
from config import token
from aiogram.types import Message
import sqlite3

conn = sqlite3.connect("diary.db")
cursor = conn.cursor()


# ---------- КАТЕГОРИИ ----------
CATEGORIES = {
    "Задача 📌": ["сделать", "нужно", "купить", "план"],
    "Здоровье 🏥": ["врач", "болит", "аптека", "таблетки", "больница"],
    "Учёба 📚": ["урок", "дз", "экзамен", "школа"],
    "Работа 💼": ["работа", "проект", "клиент"],
    "Личное 💬": ["друг", "семья", "люблю"]
}

def detect_category(text: str) -> str:
    text = text.lower()
    for category, words in CATEGORIES.items():
        for w in words:
            if w in text:
                return category
    return "Мысль 💭"

DAY_ALIASES = {
    "понедельник": "Понедельник",
    "вторник": "Вторник",
    "сред": "Среда",
    "четверг": "Четверг",
    "пятниц": "Пятница",
    "суббот": "Суббота",
    "воскрес": "Воскресенье",
    "завтра": "Завтра"
}

WEEK_DAYS = [
    "понедельник", "вторник", "среда",
    "четверг", "пятница", "суббота", "воскресенье"
]

def parse_week_task(text: str):
    text = text.lower()

    for key, day_name in DAY_ALIASES.items():
        if f"до {key}" in text:
            task = text.split(f"до {key}")[0].strip()
            if task:
                return day_name, task

    return None, None

# ---------- BOT ----------
BOT_TOKEN = token

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)



cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    category TEXT,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    remind_time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS week_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    day TEXT,
    task TEXT
)
""")
conn.commit()

# ---------- /start ----------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "📔 Умный дневник + напоминания\n\n"
        "📝 Просто напиши текст — я сохраню запись\n"
        "⏰ /remind — добавить напоминание\n" 
        "/weekclear - очистить план на неделю\n"
        "/week - показать план на неделю\n"
        "/weekadd - добавить план на неделю\n"
        "📋 /reminder — посмотреть напоминания"
    )

# ---------- /weekadd ----------

DAYS = [
    "понедельник", "вторник", "среда",
    "четверг", "пятница", "суббота", "воскресенье"
]

@dp.message_handler(commands=["weekadd"])
async def add_week_plan(message: types.Message):
    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        await message.answer(
            "❌ Формат:\n/weekadd Понедельник задача"
        )
        return

    day = parts[1].lower()
    task = parts[2]

    if day not in DAYS:
        await message.answer("❌ Неверный день недели")
        return

    cursor.execute(
        "INSERT INTO week_plan (user_id, day, task) VALUES (?, ?, ?)",
        (message.from_user.id, day.capitalize(), task)
    )
    conn.commit()

    await message.answer(f"✅ Добавлено:\n{day.capitalize()} — {task}")

# ---------- /week ----------

@dp.message_handler(commands=["week"])
async def show_week_plan(message: types.Message):
    cursor.execute(
        "SELECT day, task FROM week_plan WHERE user_id = ?",
        (message.from_user.id,)
    )
    rows = cursor.fetchall()

    if not rows:
        await message.answer("📭 План на неделю пуст")
        return

    unique = set()   # ← тут магия
    msg = "📅 План на неделю:\n\n"

    for day, task in rows:
        key = (day, task)
        if key not in unique:
            unique.add(key)
            msg += f"• {day}: {task}\n"

    await message.answer(msg)


# ---------- /weekclear ----------

@dp.message_handler(commands=["weekclear"])
async def clear_week_plan(message: types.Message):
    cursor.execute(
        "DELETE FROM week_plan WHERE user_id = ?",
        (message.from_user.id,)
    )
    conn.commit()

    await message.answer("🧹 План на неделю очищен")


# ---------- УМНЫЙ REMIND ----------
@dp.message_handler(commands=["remind"])
async def add_reminder(message: types.Message):
    try:
        args = message.text.split()

        if "-" in args[1]:
            date_part = args[1]
            time_part = args[2]
            text = " ".join(args[3:])
        else:
            date_part = f"{args[1]}-{args[2]}-{args[3]}"
            time_part = args[4]
            text = " ".join(args[5:])

        remind_dt = datetime.datetime.strptime(
            f"{date_part} {time_part}", "%Y-%m-%d %H:%M"
        )

        cursor.execute(
            "INSERT INTO reminders (user_id, text, remind_time) VALUES (?, ?, ?)",
            (
                message.from_user.id,
                text,
                remind_dt.strftime("%Y-%m-%d %H:%M")
            )
        )
        conn.commit()

        await message.answer(
            f"⏰ Напоминание сохранено\n📅 {remind_dt.strftime('%Y-%m-%d %H:%M')}"
        )

    except Exception as e:
        await message.answer(
            "❌ Неверный формат\n"
            "Примеры:\n"
            "/remind 2026-01-02 20:30 Запись к врачу\n"
            "/remind 2026 01 02 20:30 Запись к врачу"
        )


# ---------- ПОКАЗ НАПОМИНАНИЙ ----------
@dp.message_handler(commands=["reminder"])
async def show_reminders(message: types.Message):
    cursor.execute(
        "SELECT text, remind_time FROM reminders WHERE user_id = ? ORDER BY remind_time",
        (message.from_user.id,)
    )
    rows = cursor.fetchall()

    if not rows:
        await message.answer("📭 У тебя нет напоминаний")
        return

    msg = "⏰ Твои напоминания:\n\n"
    for i, (text, time) in enumerate(rows, start=1):
        msg += f"{i}. 📅 {time}\n📝 {text}\n\n"

    await message.answer(msg)


# ---------- ДОБАВЛЕНИЕ ЗАПИСИ ----------
@dp.message_handler()
async def handle_text(message: types.Message):
    day, task = parse_week_task(message.text)

    # --------- ЕСЛИ ЭТО ПЛАН НА НЕДЕЛЮ ---------
    if day:
        cursor.execute(
            "SELECT 1 FROM week_plan WHERE user_id = ? AND day = ? AND task = ?",
            (message.from_user.id, day, task)
        )

        if cursor.fetchone():
            await message.answer("⚠️ Такая задача уже есть в плане")
            return

        cursor.execute(
            "INSERT INTO week_plan (user_id, day, task) VALUES (?, ?, ?)",
            (message.from_user.id, day, task)
        )
        conn.commit()

        await message.answer(
            f"📅 Добавил в план:\n• {day}: {task}"
        )
        return

    # --------- ИНАЧЕ ЭТО ОБЫЧНАЯ ЗАПИСЬ ---------
    category = detect_category(message.text)

    cursor.execute(
        "INSERT INTO entries (user_id, text, category, date) VALUES (?, ?, ?, ?)",
        (
            message.from_user.id,
            message.text,
            category,
            str(datetime.date.today())
        )
    )
    conn.commit()

    await message.answer(
        f"📔 Запись сохранена\n🧠 Тип записи: {category}"
    )


# ---------- ПРОВЕРКА НАПОМИНАНИЙ ----------
async def reminder_checker():
    while True:
        now = datetime.datetime.now()

        cursor.execute("SELECT id, user_id, text, remind_time FROM reminders")
        rows = cursor.fetchall()

        for r_id, user_id, text, time_str in rows:
            remind_time = datetime.datetime.strptime(
                time_str, "%Y-%m-%d %H:%M"
            )

            if remind_time <= now:
                await bot.send_message(
                    user_id,
                    f"⏰ Напоминание:\n{text}"
                )
                cursor.execute(
                    "DELETE FROM reminders WHERE id = ?",
                    (r_id,)
                )
                conn.commit()

        await asyncio.sleep(30)


# ---------- START ----------
async def on_startup(dp):
    asyncio.create_task(reminder_checker())

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
