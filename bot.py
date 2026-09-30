import os
import sqlite3
from datetime import datetime

import telebot
from telebot import types

from flask import Flask, request

app = Flask(__name__)

# =========================
# SOZLAMALAR
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 6470817755
ADMIN_USERNAME = "@I_am_Omina"

COURSE_NAME = "LogiSchool"

OLD_PRICE = "300 000 so'm"
COURSE_PRICE = "200 000 so'm"

CARD_NUMBER = "9860190105962889"

DB_NAME = "logischool.db"


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")


bot = telebot.TeleBot(BOT_TOKEN)


# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            phone TEXT,
            step TEXT DEFAULT 'menu',
            payment_status TEXT DEFAULT 'not_paid',
            receipt_file_id TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            amount TEXT,
            receipt_file_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            reviewed_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_user(
    telegram_id,
    username=None,
    name=None,
    phone=None,
    step=None,
    payment_status=None,
    receipt_file_id=None
):
    conn = get_db()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "SELECT telegram_id FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    exists = cursor.fetchone()

    if exists:

        fields = []
        values = []

        if username is not None:
            fields.append("username = ?")
            values.append(username)

        if name is not None:
            fields.append("name = ?")
            values.append(name)

        if phone is not None:
            fields.append("phone = ?")
            values.append(phone)

        if step is not None:
            fields.append("step = ?")
            values.append(step)

        if payment_status is not None:
            fields.append("payment_status = ?")
            values.append(payment_status)

        if receipt_file_id is not None:
            fields.append("receipt_file_id = ?")
            values.append(receipt_file_id)

        fields.append("updated_at = ?")
        values.append(now)

        values.append(telegram_id)

        query = f"""
            UPDATE users
            SET {", ".join(fields)}
            WHERE telegram_id = ?
        """

        cursor.execute(query, values)

    else:

        cursor.execute("""
            INSERT INTO users (
                telegram_id,
                username,
                name,
                phone,
                step,
                payment_status,
                receipt_file_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            telegram_id,
            username,
            name,
            phone,
            step or "menu",
            payment_status or "not_paid",
            receipt_file_id,
            now,
            now
        ))

    conn.commit()
    conn.close()


def get_user(telegram_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


# =========================
# MENYU
# =========================

def main_menu():

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "📚 Kurs haqida",
        "💰 Kurs narxi"
    )

    keyboard.row(
        "📝 Kursga yozilish",
        "🎁 Bonuslar"
    )

    keyboard.row(
        "📞 Admin",
        "🏠 Bosh menyu"
    )

    return keyboard


def phone_keyboard():

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    button = types.KeyboardButton(
        "📱 Telefon raqamimni yuborish",
        request_contact=True
    )

    keyboard.add(button)

    return keyboard


def payment_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "💳 To'lov qildim",
            callback_data="payment_done"
        )
    )

    return keyboard


def admin_payment_keyboard(user_id):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            "✅ TASDIQLASH",
            callback_data=f"approve_{user_id}"
        ),
        types.InlineKeyboardButton(
            "❌ RAD ETISH",
            callback_data=f"reject_{user_id}"
        )
    )

    return keyboard


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    save_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )

    bot.send_message(
        message.chat.id,
        f"""
👋 Assalomu alaykum!

🎓 {COURSE_NAME} kursiga xush kelibsiz!

Bu bot orqali:

📚 Kurs haqida ma'lumot
💰 Kurs narxi
📝 Kursga yozilish
🧾 To'lov cheki
🎁 Bonuslar

Quyidagi menyudan foydalaning 👇
""",
        reply_markup=main_menu()
    )


# =========================
# KURS HAQIDA
# =========================

@bot.message_handler(
    func=lambda message: message.text == "📚 Kurs haqida"
)
def course_info(message):

    bot.send_message(
        message.chat.id,
        f"""
📚 {COURSE_NAME}

🚚 LOGISTIKA KURSI

Kursda:

• Logistika asoslari
• Yuk tashish
• Yuk mashinalari
• Yo'nalishlar
• Yuk narxlari
• Haydovchi bilan ishlash
• Mijoz bilan ishlash
• Buyurtma bilan ishlash
• Logistika orqali daromad qilish

💰 Eski narx: {OLD_PRICE}

🔥 Chegirmali narx:
{COURSE_PRICE}
""",
        reply_markup=main_menu()
    )


# =========================
# NARX
# =========================

@bot.message_handler(
    func=lambda message: message.text == "💰 Kurs narxi"
)
def course_price(message):

    bot.send_message(
        message.chat.id,
        f"""
💰 KURS NARXI

❌ Eski narx: {OLD_PRICE}

🔥 Hozir:
✅ {COURSE_PRICE}

🎁 Bonuslar ham mavjud!
""",
        reply_markup=main_menu()
    )


# =========================
# BONUSLAR
# =========================

@bot.message_handler(
    func=lambda message: message.text == "🎁 Bonuslar"
)
def bonuses(message):

    bot.send_message(
        message.chat.id,
        """
🎁 BONUSLAR

1️⃣ 🤖 AI VIDEO YASASH KURSI

2️⃣ 🚫 SPAMDAN CHIQISH KURSI

3️⃣ ⭐ TELEGRAM PREMIUM OLISH KURSI
""",
        reply_markup=main_menu()
    )


# =========================
# ADMIN
# =========================

@bot.message_handler(
    func=lambda message: message.text == "📞 Admin"
)
def admin(message):

    bot.send_message(
        message.chat.id,
        f"""
📞 ADMIN

Admin:
{ADMIN_USERNAME}
""",
        reply_markup=main_menu()
    )


# =========================
# RO'YXATDAN O'TISH
# =========================

@bot.message_handler(
    func=lambda message: message.text == "📝 Kursga yozilish"
)
def registration(message):

    user_id = message.from_user.id
    user = get_user(user_id)

    if user and user["payment_status"] == "approved":

        bot.send_message(
            user_id,
            "✅ Sizning to'lovingiz allaqachon tasdiqlangan!"
        )

        return

    save_user(
        telegram_id=user_id,
        username=message.from_user.username,
        step="name"
    )

    bot.send_message(
        user_id,
        """
📝 KURSga yozilish

Ism va familiyangizni yozing.

Masalan:

Omina To'xtanazarova
"""
    )


# =========================
# ISM
# =========================

@bot.message_handler(
    func=lambda message:
    get_user(message.from_user.id)
    and get_user(message.from_user.id)["step"] == "name"
)
def get_name(message):

    name = message.text.strip()

    if len(name) < 3:

        bot.send_message(
            message.chat.id,
            "❗ Ism va familiyangizni to'liq yozing."
        )

        return

    save_user(
        telegram_id=message.from_user.id,
        name=name,
        step="phone"
    )

    bot.send_message(
        message.chat.id,
        """
📱 Telefon raqamingizni yuboring 👇
""",
        reply_markup=phone_keyboard()
    )


# =========================
# TELEFON
# =========================

@bot.message_handler(content_types=["contact"])
def get_phone(message):

    user_id = message.from_user.id

    user = get_user(user_id)

    if not user:

        save_user(
            telegram_id=user_id
        )

        user = get_user(user_id)

    phone = message.contact.phone_number

    save_user(
        telegram_id=user_id,
        phone=phone,
        step="payment"
    )

    bot.send_message(
        user_id,
        f"""
✅ Ma'lumotlaringiz qabul qilindi.

👤 Ism:
{user["name"]}

📱 Telefon:
{phone}

💳 TO'LOV

🔥 Kurs narxi:
{COURSE_PRICE}

💳 Karta:
{CARD_NUMBER}

To'lov qilgach tugmani bosing.
""",
        reply_markup=payment_keyboard()
    )


# =========================
# TO'LOV
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "payment_done"
)
def payment_done(call):

    user_id = call.from_user.id

    save_user(
        telegram_id=user_id,
        step="receipt"
    )

    bot.answer_callback_query(call.id)

    bot.send_message(
        user_id,
        """
🧾 To'lov chekingizni yuboring.

📸 Chekni RASM ko'rinishida yuboring.
"""
    )


# =========================
# CHEK
# =========================

@bot.message_handler(content_types=["photo"])
def receive_receipt(message):

    user_id = message.from_user.id
    user = get_user(user_id)

    if not user:

        bot.send_message(
            user_id,
            "❗ Avval /start bosing."
        )

        return

    if user["step"] != "receipt":

        bot.send_message(
            user_id,
            "❗ Avval kursga yozilish bo'limidan o'ting."
        )

        return

    file_id = message.photo[-1].file_id

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    save_user(
        telegram_id=user_id,
        receipt_file_id=file_id,
        payment_status="pending",
        step="waiting"
    )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO payments (
            telegram_id,
            amount,
            receipt_file_id,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        COURSE_PRICE,
        file_id,
        "pending",
        now
    ))

    payment_id = cursor.lastrowid

    conn.commit()
    conn.close()

    username = message.from_user.username or "yo'q"

    admin_text = f"""
🔔 YANGI TO'LOV

🎓 Kurs:
{COURSE_NAME}

👤 Ism:
{user["name"]}

📱 Telefon:
{user["phone"]}

🆔 Telegram ID:
{user_id}

👤 Username:
@{username}

💰 Summa:
{COURSE_PRICE}

🧾 To'lov ID:
{payment_id}
"""

    bot.send_photo(
        ADMIN_ID,
        file_id,
        caption=admin_text,
        reply_markup=admin_payment_keyboard(user_id)
    )

    bot.send_message(
        user_id,
        """
✅ Chekingiz qabul qilindi!

⏳ Admin tekshirmoqda.

Tasdiqlangandan keyin sizga xabar keladi.
""",
        reply_markup=main_menu()
    )


# =========================
# TASDIQLASH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("approve_")
)
def approve_payment(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(
        call.data.replace("approve_", "")
    )

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    save_user(
        telegram_id=user_id,
        payment_status="approved",
        step="approved"
    )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE payments
        SET status = 'approved',
            reviewed_at = ?
        WHERE id = (
            SELECT id
            FROM payments
            WHERE telegram_id = ?
            AND status = 'pending'
            ORDER BY id DESC
            LIMIT 1
        )
    """, (now, user_id))

    conn.commit()
    conn.close()

    bot.answer_callback_query(
        call.id,
        "✅ Tasdiqlandi!"
    )

   bot.send_message(
    user_id,
    f"""
🎉 TABRIKLAYMIZ!

✅ To'lovingiz tasdiqlandi.

🎓 Siz {COURSE_NAME} kursiga qabul qilindingiz.

🔥 Xush kelibsiz!

📚 Kurs guruhiga qo'shilish:
👇
{https://t.me/+HXubr3jrdNBjMzky}
"""
)


# =========================
# RAD ETISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("reject_")
)
def reject_payment(call):

    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(
        call.data.replace("reject_", "")
    )

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    save_user(
        telegram_id=user_id,
        payment_status="rejected",
        step="receipt"
    )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE payments
        SET status = 'rejected',
            reviewed_at = ?
        WHERE id = (
            SELECT id
            FROM payments
            WHERE telegram_id = ?
            AND status = 'pending'
            ORDER BY id DESC
            LIMIT 1
        )
    """, (now, user_id))

    conn.commit()
    conn.close()

    bot.answer_callback_query(
        call.id,
        "❌ Rad etildi."
    )

    bot.send_message(
        user_id,
        """
❌ To'lov chekingiz tasdiqlanmadi.

Iltimos, to'g'ri chekni qaytadan yuboring.
"""
    )


# =========================
# STATISTIKA
# =========================

@bot.message_handler(commands=["stats"])
def stats(message):

    if message.from_user.id != ADMIN_ID:
        return

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE payment_status = 'pending'
    """)
    pending = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE payment_status = 'approved'
    """)
    approved = cursor.fetchone()[0]

    conn.close()

    bot.send_message(
        ADMIN_ID,
        f"""
📊 {COURSE_NAME}

👥 Jami: {total}

⏳ Kutilmoqda: {pending}

✅ Tasdiqlangan: {approved}
"""
    )


# =========================
# O'QUVCHILAR
# =========================

@bot.message_handler(commands=["students"])
def students(message):

    if message.from_user.id != ADMIN_ID:
        return

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        ORDER BY created_at DESC
    """)

    users = cursor.fetchall()

    conn.close()

    if not users:

        bot.send_message(
            ADMIN_ID,
            "Hozircha o'quvchilar yo'q."
        )

        return

    text = "👥 O'QUVCHILAR\n\n"

    for i, user in enumerate(users, 1):

        text += f"""
{i}. {user["name"] or "Noma'lum"}
📱 {user["phone"] or "Yo'q"}
💳 {user["payment_status"]}
🆔 {user["telegram_id"]}

"""

    bot.send_message(
        ADMIN_ID,
        text[:4000]
    )


# =========================
# BOSH MENYU
# =========================

@bot.message_handler(
    func=lambda message: message.text == "🏠 Bosh menyu"
)
def home(message):

    save_user(
        telegram_id=message.from_user.id,
        step="menu"
    )

    bot.send_message(
        message.chat.id,
        "🏠 Bosh menyu",
        reply_markup=main_menu()
    )


# =========================
# DATABASE
# =========================

init_db()

render_url = os.getenv("RENDER_EXTERNAL_URL")

if render_url:
    webhook_url = render_url + "/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

port = int(os.getenv("PORT", 10000))
@app.route("/", methods=["GET"])
def home_page():
    return "LogiSchool bot ishlayapti!"


@app.route("/webhook", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK"
app.run(
    host="0.0.0.0",
    port=port
)
init_db()

render_url = os.getenv("RENDER_EXTERNAL_URL")

if render_url:
    webhook_url = render_url + "/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

port = int(os.getenv("PORT", 10000))

app.run(
    host="0.0.0.0",
    port=port
)
