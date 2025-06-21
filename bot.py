
import telebot
from telebot import types
from tinydb import TinyDB, Query
from datetime import datetime

API_TOKEN = '7675630051:AAF6Js1myD1bYv1MQJMnQOYw_VILJkQOKIs'
ADMIN_ID = 7912637319

bot = telebot.TeleBot(API_TOKEN)
db = TinyDB('users.json')
User = Query()

meters = {
    100: 16368,
    200: 32736,
    300: 49104,
    1000: 163680,
    2000: 327360,
    3000: 491040,
    4000: 654720,
    5000: 818400,
    10000: 1636800,
    15000: 2455200,
    20000: 3273600
}

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    user = db.get(User.id == user_id)
    if not user:
        db.insert({'id': user_id, 'points': 0, 'meter': 0, 'last_claim': str(datetime.utcnow())})
        bot.send_message(ADMIN_ID, f"🚨 مستخدم جديد دخل البوت: {user_id}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📝 معلومات حسابك", "🛒 شراء العداد")
    markup.add("💵 سحب الأرباح", "📊 كشف الحساب")
    if user_id == ADMIN_ID:
        markup.add("🧮 إضافة نقاط", "🔓 رفع الحظر")
    bot.send_message(message.chat.id, "مرحباً بك في بوت المستقبل 💰", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📝 معلومات حسابك")
def info(message):
    user = db.get(User.id == message.from_user.id)
    bot.send_message(message.chat.id, f"🔹 آيدي: {user['id']}\n🔹 نقاطك: {user['points']}\n🔹 عدادك: {user['meter']} نقطة يومياً")

@bot.message_handler(func=lambda m: m.text == "📊 كشف الحساب")
def account(message):
    info(message)

@bot.message_handler(func=lambda m: m.text == "🛒 شراء العداد")
def buy_meter(message):
    markup = types.InlineKeyboardMarkup()
    for size, price in meters.items():
        markup.add(types.InlineKeyboardButton(f"عداد {size} - {price} نقطة", callback_data=f"buy_{size}"))
    bot.send_message(message.chat.id, "اختر العداد:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy(call):
    size = int(call.data.split("_")[1])
    price = meters[size]
    user_id = call.from_user.id
    user = db.get(User.id == user_id)
    if user['points'] >= price:
        db.update({'points': user['points'] - price, 'meter': size}, User.id == user_id)
        bot.answer_callback_query(call.id, text="✅ تم الشراء")
        bot.send_message(user_id, f"✅ تم شراء عداد {size} نقطة يومياً.")
    else:
        bot.answer_callback_query(call.id, text="❌ نقاطك غير كافية")

@bot.message_handler(func=lambda m: m.text == "🧮 إضافة نقاط" and m.from_user.id == ADMIN_ID)
def add_points_start(message):
    msg = bot.send_message(ADMIN_ID, "📥 أرسل آيدي المستخدم:")
    bot.register_next_step_handler(msg, get_user_id_to_add_points)

def get_user_id_to_add_points(message):
    try:
        uid = int(message.text)
        msg = bot.send_message(ADMIN_ID, "📥 كم نقطة تريد إضافتها؟")
        bot.register_next_step_handler(msg, lambda m: do_add_points(m, uid))
    except:
        bot.send_message(ADMIN_ID, "❌ آيدي غير صالح")

def do_add_points(message, uid):
    try:
        pts = int(message.text)
        user = db.get(User.id == uid)
        if user:
            db.update({'points': user['points'] + pts}, User.id == uid)
            bot.send_message(ADMIN_ID, f"✅ تم إضافة {pts} نقطة للمستخدم {uid}")
        else:
            bot.send_message(ADMIN_ID, "❌ المستخدم غير موجود")
    except:
        bot.send_message(ADMIN_ID, "❌ قيمة غير صالحة")

@bot.message_handler(func=lambda m: m.text == "🔓 رفع الحظر" and m.from_user.id == ADMIN_ID)
def unban_user(message):
    msg = bot.send_message(ADMIN_ID, "✏️ أرسل آيدي المستخدم لإلغاء الحظر:")
    bot.register_next_step_handler(msg, lambda m: bot.send_message(ADMIN_ID, "✅ تم إلغاء الحظر (افتراضي - لا حاجة لفعل)") )

print("🤖 البوت يعمل...")
bot.infinity_polling()
