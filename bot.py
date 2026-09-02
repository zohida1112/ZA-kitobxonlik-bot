import asyncio
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    FSInputFile,
    Message,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable topilmadi.")

ADMIN_ID = 2145096152

CHANNELS = [
    {
        "name": "Akramova's ingliz tili",
        "id": -1002433804028,
        "link": "https://t.me/+ErMs2VobF7g2ODk6",
    },
    {
        "name": "Akramova's ona tili",
        "id": -1002057889458,
        "link": "https://t.me/+KLdpDQe8Yg9lODFi",
    },
    {
        "name": "Akramova's blog",
        "id": -1001932666340,
        "link": "https://t.me/+ODoIV-uWYF42ZTAy",
    },
    {
        "name": "Akramova's turk tili",
        "id": -1003675326192,
        "link": "https://t.me/+iPcCx6r6NiBmZTBi",
    },
]

FINAL_CHANNEL_ID = -1004380468196
REFERRAL_TARGET = 1
REFERRAL_PHOTO = "referral.jpg"

QUESTIONS = [
    {
        "q": "1. Asar voqealari boshida hikoyachi Buriyoda necha kundan beri bo‘lgan edi?",
        "options": ["Uch kun", "To‘rt kun", "Olti kun", "O‘n kun"],
        "correct": 2,
    },
    {
        "q": "2. Hikoyachi bilan safarda kim hamroh bo‘ladi?",
        "options": ["Tovarish Yak", "Baxtiyor", "Xon Man Men", "Mayda Xon"],
        "correct": 1,
    },
    {
        "q": "3. Tovarish Yak asarda qanday vazifani bajaradi?",
        "options": ["Jurnalist", "Mehmonxona boshlig‘i", "Tarjimon va yo‘l boshlovchi", "Elchi"],
        "correct": 2,
    },
    {
        "q": "4. Hikoyachi nima sababdan Baxtiyordan ko‘ra imtiyozliroq munosabat ko‘radi?",
        "options": [
            "Mashhur yozuvchi bo‘lgani uchun",
            "Delegatsiya rahbari deb belgilanganligi uchun",
            "Rus tilini yaxshi bilgani uchun",
            "Xon Man Men bilan tanish bo‘lgani uchun",
        ],
        "correct": 1,
    },
    {
        "q": "5. Tovarish Yak hikoyachining mayiz va turshak sovg‘asini nega rad etadi?",
        "options": [
            "Ularni yoqtirmagani uchun",
            "Bunday sovg‘ani olish ularda rasm emasligini aytadi",
            "Sovg‘ani Baxtiyorga berishni so‘raydi",
            "Olib ketishga ruxsat bo‘lmagani uchun",
        ],
        "correct": 1,
    },
    {
        "q": "6. Sovg‘a masalasidagi ziddiyat orqali asarda nima kinoya qilinadi?",
        "options": [
            "Mehmonlarning kambag‘alligi",
            "Yuqori va quyi tabaqalarga nisbatan ikki xil mezon",
            "O‘zbeklarning sovg‘a berish odati",
            "Sayohat qilish qiyinligi",
        ],
        "correct": 1,
    },
    {
        "q": "7. Hikoyachining Yakni “tilla baliqcha”ga o‘xshatishi nimaga ishora qiladi?",
        "options": [
            "Yakning boyligiga",
            "Uning iste’dodli, ammo cheklangan muhitda yashayotganiga",
            "Uning baliq ovlashni yaxshi ko‘rishiga",
            "Uning mamlakatdan ketishga tayyor ekaniga",
        ],
        "correct": 1,
    },
    {
        "q": "8. Hikoyachi Xoniya shahrining tashqi ko‘rinishi bilan ichki hayoti o‘rtasida qanday qarama-qarshilikni ko‘radi?",
        "options": [
            "Shahar eski, odamlar boy",
            "Tashqaridan ozoda va mukammal, ichki hayotda esa cheklov va soxtalik mavjud",
            "Shahar kambag‘al, odamlar esa erkin",
            "Shahar gavjum, mehmonxonalar esa bo‘sh",
        ],
        "correct": 1,
    },
    {
        "q": "9. Hikoyachi nima uchun namunaviy tug‘ruqxonaga borishni istamaydi?",
        "options": [
            "Kasal bo‘lib qolgani uchun",
            "Yak bilan janjallashgani uchun",
            "Majburiy dasturga kinoya bilan munosabat bildirgani uchun",
            "Baxtiyor borishni taqiqlagani uchun",
        ],
        "correct": 2,
    },
    {
        "q": "10. Asarda “tovarish” so‘ziga alohida munosabat bildirilishining asosiy sababi nima?",
        "options": [
            "So‘z tarjima qilinmagani uchun",
            "Uning mafkuraviy mazmuni bilan haqiqiy “o‘rtoq” tushunchasi o‘rtasidagi ziddiyat ko‘rsatilgani uchun",
            "Baxtiyor bu so‘zni tushunmagani uchun",
            "Buriyo tilida bunday so‘z bo‘lmagani uchun",
        ],
        "correct": 1,
    },
    {
        "q": "11. Afrikalik sayyoh hikoyachining O‘zbekiston nishoniga nega qiziqib qoladi?",
        "options": [
            "O‘zbekiston haqida hech eshitmagani uchun",
            "Turli davlatlarning nishonlarini yig‘gani uchun",
            "Uni qimmatbaho deb o‘ylagani uchun",
            "Xon Man Men nishoniga o‘xshatgani uchun",
        ],
        "correct": 1,
    },
    {
        "q": "12. Afrikalikning mamlakatni nihoyatda zerikarli deb ta’riflashi hikoyachiga qanday ta’sir qiladi?",
        "options": [
            "Uni ranjitadi",
            "U keskin qarshi chiqadi",
            "Uning ichida yurgan tuyg‘uni aniq ifodalab beradi",
            "Uni darhol vatanga qaytishga undaydi",
        ],
        "correct": 2,
    },
    {
        "q": "13. Tovarish Yakning ko‘plab savollarga bir qolipda javob berishi uning qaysi xususiyatini ochib beradi?",
        "options": [
            "Hazilkashligini",
            "Mafkuraviy qarashlarga qattiq bog‘langanligini",
            "Bilimsizligini",
            "Mehmonlardan qo‘rqishini",
        ],
        "correct": 1,
    },
    {
        "q": "14. Hikoyachi bilan Tovarish Yak munosabatlari sovuqlashgach, Yak asosan kim orqali u bilan muloqot qila boshlaydi?",
        "options": ["Saida orqali", "Baxtiyor orqali", "Haydovchi orqali", "Elchixona xodimi orqali"],
        "correct": 1,
    },
    {
        "q": "15. Tovarish Yakning “Vatanga xizmat qilish kerak avval!” degan mazmundagi gapi nimaga javoban aytiladi?",
        "options": [
            "Nega chet elga chiqmayotganiga",
            "Nega uylanmaganiga",
            "Nega ishini o‘zgartirmayotganiga",
            "Nega harbiy kiyim kiyganiga",
        ],
        "correct": 1,
    },
    {
        "q": "16. Hikoyachi va Baxtiyorning turli sharoitda kutib olinishi orqali asarda nima hajv qilinadi?",
        "options": [
            "Mehmonxona xizmatining sifati",
            "Tenglikni da’vo qiluvchi tuzumdagi mansabparastlik va tabaqalanish",
            "Sayyohlarning talabchanligi",
            "Ikki qahramon o‘rtasidagi adovat",
        ],
        "correct": 1,
    },
    {
        "q": "17. Hikoyachi Yakga “Tilla baliqcha” she’rining mazmunini tushuntirish orqali nimaga erishmoqchi bo‘ladi?",
        "options": [
            "O‘zbek adabiyotini targ‘ib qilishga",
            "Yakning o‘zi yashayotgan muhit haqida o‘ylashiga",
            "Uni xafa qilishga",
            "Safarni uzaytirishga",
        ],
        "correct": 1,
    },
    {
        "q": "18. Hikoyachi keyinchalik Sharqiy Buriyodan qochganlar orasida Yak ham bo‘lishi mumkinligini nega o‘ylaydi?",
        "options": [
            "Yak avvaldan qochishni rejalashtirgan",
            "Yakning qarashlarida shubha paydo bo‘lganini sezgan",
            "Baxtiyor shunday xabar bergan",
            "Yak unga xat yozgan",
        ],
        "correct": 1,
    },
    {
        "q": "19. Xoniyaning nihoyatda ozoda va tartibli tasvirlanishi asarda qanday badiiy vazifa bajaradi?",
        "options": [
            "Sayyohlik targ‘iboti vazifasini",
            "Keyinchalik ochiladigan soxtalik va erksizlik bilan kontrast yaratadi",
            "Qahramonning shaharda qolishini asoslaydi",
            "Faqat tabiat go‘zalligini tasvirlaydi",
        ],
        "correct": 1,
    },
    {
        "q": "20. Xoniyadagi deyarli barcha odamlarning ko‘ksidagi bir xil nishon nimaning belgisi sifatida tasvirlanadi?",
        "options": [
            "Anjuman qatnashchisi ekanining",
            "Kasbining",
            "Xon Man Men shaxsiga sig‘inishning",
            "Milliy kiyimning",
        ],
        "correct": 2,
    },
    {
        "q": "21. Shaharda qariya, nogiron va jismonan nosog‘lom kishilarning deyarli ko‘rinmasligi nimaga bog‘liq edi?",
        "options": [
            "Aholining nihoyatda sog‘lomligiga",
            "Ularning boshqa davlatga ketganiga",
            "Ularning shahardan chiqarilishi yoki maxsus joylarga joylashtirilishiga",
            "Ularning ishlamasligiga",
        ],
        "correct": 2,
    },
    {
        "q": "22. Xon Man Menning besh yoshli holati aks etgan pannodagi tasvirning hajviy mohiyati nimada?",
        "options": [
            "U bolaligidan rassom bo‘lgan deb ko‘rsatiladi",
            "U besh yoshidayoq mamlakatni ozod qilish va kommunizm qurish haqida o‘ylagan deb talqin qilinadi",
            "U besh yoshida hukmdor bo‘lgan",
            "U bolaligida mamlakatdan ketgan",
        ],
        "correct": 1,
    },
    {
        "q": "23. Hikoyachi va Baxtiyor binolarning orqa tomonida nimani ko‘rib hayratga tushadilar?",
        "options": [
            "Hashamatli bog‘larni",
            "Yashirin harbiy qismlarni",
            "Pardozsiz beton va tiqilinch yashash sharoitini",
            "Xorijiy sayyohlarni",
        ],
        "correct": 2,
    },
    {
        "q": "24. Mazkur epizoddagi “medalning ikkinchi tomoni” ifodasi nimani anglatadi?",
        "options": [
            "Qahramonlarga medal berilishini",
            "Tashqi dabdaba ortida yashiringan haqiqiy hayotni",
            "Xon Man Menning mukofotlarini",
            "Anjuman natijalarini",
        ],
        "correct": 1,
    },
    {
        "q": "25. Tovarish Yak tuzgan sayohat dasturi nima uchun hikoyachi va Baxtiyorning ensasini qotiradi?",
        "options": [
            "Dastur juda qimmat bo‘lgani uchun",
            "Ularning istaklari deyarli hisobga olinmay, asosan mafkuraviy joylar kiritilgani uchun",
            "Dasturda hech qanday muzey bo‘lmagani uchun",
            "Faqat sport tadbirlari kiritilgani uchun",
        ],
        "correct": 1,
    },
    {
        "q": "26. Partiya tarixi muzeyida Baxtiyor qurultoy uzoq vaqt chaqirilmagani haqida savol berganda Yak qanday mazmunda javob beradi?",
        "options": [
            "Bu qonun buzilishi ekanini tan oladi",
            "Bu xalq va partiya faollarining xohishiga ko‘ra bo‘lganini aytadi",
            "Savolga umuman javob bermaydi",
            "Qurultoy har yili o‘tkazilganini aytadi",
        ],
        "correct": 1,
    },
    {
        "q": "27. Baxtiyorning muzeydagi xatti-harakati uning obrazida qanday o‘zgarishni ko‘rsatadi?",
        "options": [
            "U yanada indamas bo‘lib qoladi",
            "Avvalgi yuvoshligidan chiqib, dadil savollar bera boshlaydi",
            "Tovarish Yak tarafini oladi",
            "Safarni tark etadi",
        ],
        "correct": 1,
    },
    {
        "q": "28. Hikoyachining “endi tug‘masman” degan kinoyali gapi nimaga qaratilgan?",
        "options": [
            "Tug‘ruqxonaning yomonligiga",
            "Majburiy va ma’nosiz sayohat dasturiga",
            "Baxtiyorning haziliga",
            "Shifokorlarga",
        ],
        "correct": 1,
    },
    {
        "q": "29. “O‘n kun — o‘n yil” ifodasi eng avvalo nimani anglatadi?",
        "options": [
            "Safar aslida o‘n yil davom etganini",
            "Nazorat va bir xillik tufayli o‘n kun qahramonlarga nihoyatda uzoq tuyulganini",
            "Hikoyachi o‘n yildan keyin qaytganini",
            "Buriyoda vaqt boshqacha hisoblanishini",
        ],
        "correct": 1,
    },
    {
        "q": "30. Xoniyaning tashqi go‘zalligi bilan odamlarning hayoti o‘rtasidagi qarama-qarshilik qanday asosiy fikrni kuchaytiradi?",
        "options": [
            "Zamonaviy shaharlar doimo zerikarli bo‘ladi",
            "Tashqi dabdaba inson erkinligi va haqiqiy farovonlik mavjudligini anglatmaydi",
            "Sayyohlar mahalliy hayotni tushunmaydi",
            "Shahar go‘zalligi siyosatga bog‘liq emas",
        ],
        "correct": 1,
    },
]

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
db = sqlite3.connect("users.db", check_same_thread=False)
db.row_factory = sqlite3.Row

db.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        referrer_id INTEGER,
        verified INTEGER DEFAULT 0,
        referral_count INTEGER DEFAULT 0,
        reward_given INTEGER DEFAULT 0
    )
    """
)

db.execute(
    """
    CREATE TABLE IF NOT EXISTS attempts (
        user_id INTEGER PRIMARY KEY,
        current_question INTEGER DEFAULT 0,
        score INTEGER DEFAULT 0,
        started_at TEXT,
        finished_at TEXT,
        completed INTEGER DEFAULT 0
    )
    """
)
db.commit()


def add_user(user_id, full_name=None, username=None, referrer_id=None):
    existing = db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if existing:
        db.execute(
            "UPDATE users SET full_name=?, username=? WHERE user_id=?",
            (full_name, username, user_id),
        )
    else:
        db.execute(
            """
            INSERT INTO users (user_id, full_name, username, referrer_id)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, full_name, username, referrer_id),
        )
    db.commit()


def get_user(user_id):
    return db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()


def mark_verified(user_id):
    db.execute("UPDATE users SET verified=1 WHERE user_id=?", (user_id,))
    db.commit()


def add_referral(referrer_id):
    db.execute(
        "UPDATE users SET referral_count=referral_count+1 WHERE user_id=?",
        (referrer_id,),
    )
    db.commit()


def mark_reward_given(user_id):
    db.execute("UPDATE users SET reward_given=1 WHERE user_id=?", (user_id,))
    db.commit()


def required_channels_keyboard():
    rows = [
        [InlineKeyboardButton(text=ch["name"], url=ch["link"])]
        for ch in CHANNELS
    ]
    rows.append(
        [InlineKeyboardButton(text="✅ A’zo bo‘ldim", callback_data="check_channels")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def test_start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Testni boshlash", callback_data="start_test")]
        ]
    )


async def is_member_of_required_channels(user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch["id"], user_id)
            if member.status in {
                ChatMemberStatus.LEFT,
                ChatMemberStatus.KICKED,
            }:
                return False
        except Exception:
            return False
    return True


async def is_final_channel_member(user_id):
    try:
        member = await bot.get_chat_member(FINAL_CHANNEL_ID, user_id)
        return member.status not in {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED}
    except Exception:
        return False


async def give_access(user_id, chat_id):
    user = get_user(user_id)
    if not user:
        return

    if user["reward_given"]:
        await bot.send_message(
            chat_id,
            "✅ Sizga asosiy kanalga kirish huquqi avval berilgan.\n\n"
            "Kanalga kirganingizdan so‘ng testni shu botda ishlashingiz mumkin.",
            reply_markup=test_start_keyboard(),
        )
        return

    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    invite = await bot.create_chat_invite_link(
        chat_id=FINAL_CHANNEL_ID,
        expire_date=expire,
        member_limit=1,
        name=f"user_{user_id}",
    )
    mark_reward_given(user_id)

    await bot.send_message(
        chat_id,
        "🎉 Tabriklaymiz! Referal sharti bajarildi.\n\n"
        "Quyidagi havola orqali kitobxonlik kanaliga kiring. "
        "Havola 24 soat amal qiladi va bir kishi uchun mo‘ljallangan:\n\n"
        f"{invite.invite_link}\n\n"
        "Kanalga kirganingizdan keyin testni shu botda ishlashingiz mumkin.",
        reply_markup=test_start_keyboard(),
    )


async def send_referral_post(chat_id, user_id):
    me = await bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user_id}"

    caption = (
        "📚 HAR HAFTA KITOB O‘QING VA SOVRINLARNI QO‘LGA KIRITING!\n\n"
        "Blogim obunachilari uchun kichik kitobxonlik konkursi tashkil qildim! 🥳\n\n"
        "Birgalikda har hafta kamida 30 sahifa kitob o‘qiymiz va o‘qilgan qism "
        "bo‘yicha test ishlaymiz. Eng yuqori natija ko‘rsatgan ishtirokchilar "
        "pul mukofoti va til kurslari uchun vaucherlarni qo‘lga kiritadi! 🏆\n\n"
        "🥇 1-o‘rin: 50 000 so‘m + 100 000 so‘mlik til kursi vaucheri\n"
        "🥈 2-o‘rin: 30 000 so‘m + 50 000 so‘mlik til kursi vaucheri\n"
        "🥉 3-o‘rin: 20 000 so‘m + 40 000 so‘mlik til kursi vaucheri\n\n"
        "📖 Kitob o‘qing.\n"
        "🧠 Bilimingizni oshiring.\n"
        "💰 Sovrinlarni qo‘lga kiriting!\n\n"
        "Ham ilmli, ham pulli bo‘lishingiz mumkin! 😉\n\n"
        "👇👇👇👇👇\n"
        "Konkursda ishtirok etish uchun quyidagi havola orqali qo‘shiling:\n"
        f"{ref_link}"
    )

    share_url = f"https://t.me/share/url?url={quote(ref_link)}&text={quote('Kitobxonlik konkursiga qo‘shiling!')}"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Do‘stga yuborish", url=share_url)],
            [InlineKeyboardButton(text="🔄 Referalni tekshirish", callback_data="check_referral")],
        ]
    )

    photo_path = os.path.join(os.path.dirname(__file__), REFERRAL_PHOTO)
    if os.path.exists(photo_path):
        await bot.send_photo(
            chat_id,
            FSInputFile(photo_path),
            caption=caption,
            reply_markup=keyboard,
        )
    else:
        await bot.send_message(chat_id, caption, reply_markup=keyboard)


async def after_verification(user_id, chat_id):
    user = get_user(user_id)
    if not user:
        return

    if user["referral_count"] >= REFERRAL_TARGET:
        await give_access(user_id, chat_id)
    else:
        await bot.send_message(
            chat_id,
            "✅ A’zolik tasdiqlandi!\n\n"
            "Endi 1 nafar do‘stingizni shaxsiy havolangiz orqali taklif qiling. "
            "U ham 4 ta kanalga a’zo bo‘lib, a’zoligini tasdiqlashi kerak.",
        )
        await send_referral_post(chat_id, user_id)


@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    referrer_id = None

    parts = message.text.split(maxsplit=1)
    if len(parts) == 2:
        try:
            possible_referrer = int(parts[1].strip())
            if possible_referrer != user_id:
                referrer_id = possible_referrer
        except ValueError:
            pass

    add_user(
        user_id,
        message.from_user.full_name,
        message.from_user.username,
        referrer_id,
    )

    user = get_user(user_id)
    already_verified = bool(user["verified"])

    if not await is_member_of_required_channels(user_id):
        await message.answer(
            "Assalomu alaykum! Konkursda qatnashish uchun avval quyidagi "
            "4 ta kanalga a’zo bo‘ling.",
            reply_markup=required_channels_keyboard(),
        )
        return

    if not already_verified:
        mark_verified(user_id)
        user = get_user(user_id)
        rid = user["referrer_id"]
        if rid and get_user(rid):
            add_referral(rid)
            try:
                ref_user = get_user(rid)
                await bot.send_message(
                    rid,
                    f"🎉 Yangi referal tasdiqlandi!\n"
                    f"Referallaringiz: {ref_user['referral_count']}/{REFERRAL_TARGET}",
                )
            except Exception:
                pass

    await after_verification(user_id, message.chat.id)


@dp.callback_query(F.data == "check_channels")
async def check_channels_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    add_user(
        user_id,
        callback.from_user.full_name,
        callback.from_user.username,
        None,
    )
    user = get_user(user_id)

    if not await is_member_of_required_channels(user_id):
        await callback.answer("❌ Hali barcha kanallarga a’zo emassiz.", show_alert=True)
        return

    if not user["verified"]:
        mark_verified(user_id)
        user = get_user(user_id)
        rid = user["referrer_id"]
        if rid and get_user(rid):
            add_referral(rid)
            try:
                ref_user = get_user(rid)
                await bot.send_message(
                    rid,
                    f"🎉 Yangi referal tasdiqlandi!\n"
                    f"Referallaringiz: {ref_user['referral_count']}/{REFERRAL_TARGET}",
                )
            except Exception:
                pass

    await callback.answer("✅ A’zolik tasdiqlandi!")
    await after_verification(user_id, callback.message.chat.id)


@dp.callback_query(F.data == "check_referral")
async def check_referral_callback(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Avval /start bosing.", show_alert=True)
        return

    if user["referral_count"] >= REFERRAL_TARGET:
        await callback.answer("✅ Referal sharti bajarildi!")
        await give_access(callback.from_user.id, callback.message.chat.id)
    else:
        await callback.answer(
            f"Hozircha {user['referral_count']}/{REFERRAL_TARGET} ta referal.",
            show_alert=True,
        )


def question_keyboard(question_index):
    labels = ["A", "B", "C", "D"]
    rows = []
    for i, option in enumerate(QUESTIONS[question_index]["options"]):
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{labels[i]}) {option}",
                    callback_data=f"answer:{question_index}:{i}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_question(chat_id, question_index):
    q = QUESTIONS[question_index]
    await bot.send_message(
        chat_id,
        q["q"],
        reply_markup=question_keyboard(question_index),
    )


@dp.callback_query(F.data == "start_test")
async def start_test_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    if not user or not user["reward_given"]:
        await callback.answer(
            "Avval referal shartini bajarib, asosiy kanalga kirish huquqini oling.",
            show_alert=True,
        )
        return

    # Qo‘shimcha nazorat: kanalga haqiqatan kirganini tekshirish.
    if not await is_final_channel_member(user_id):
        await callback.answer(
            "Avval kitobxonlik kanaliga kiring, so‘ng testni boshlang.",
            show_alert=True,
        )
        return

    attempt = db.execute(
        "SELECT * FROM attempts WHERE user_id=?",
        (user_id,),
    ).fetchone()

    if attempt and attempt["completed"]:
        await callback.answer("Siz bu testni avval ishlagansiz.", show_alert=True)
        return

    if not attempt:
        db.execute(
            """
            INSERT INTO attempts
            (user_id, current_question, score, started_at, completed)
            VALUES (?, 0, 0, ?, 0)
            """,
            (user_id, datetime.now(timezone.utc).isoformat()),
        )
        db.commit()
        current = 0
    else:
        current = attempt["current_question"]

    await callback.answer()
    await send_question(callback.message.chat.id, current)


@dp.callback_query(F.data.startswith("answer:"))
async def answer_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    attempt = db.execute(
        "SELECT * FROM attempts WHERE user_id=?",
        (user_id,),
    ).fetchone()

    if not attempt or attempt["completed"]:
        await callback.answer("Test faol emas.", show_alert=True)
        return

    _, q_index_text, answer_text = callback.data.split(":")
    q_index = int(q_index_text)
    selected = int(answer_text)

    if q_index != attempt["current_question"]:
        await callback.answer("Bu savolga javob allaqachon qabul qilingan.", show_alert=True)
        return

    score = attempt["score"]
    if selected == QUESTIONS[q_index]["correct"]:
        score += 1

    next_question = q_index + 1

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    if next_question >= len(QUESTIONS):
        finished = datetime.now(timezone.utc)
        db.execute(
            """
            UPDATE attempts
            SET current_question=?, score=?, finished_at=?, completed=1
            WHERE user_id=?
            """,
            (next_question, score, finished.isoformat(), user_id),
        )
        db.commit()

        percent = round(score / len(QUESTIONS) * 100)
        await callback.answer("Javob qabul qilindi.")
        await bot.send_message(
            callback.message.chat.id,
            "✅ Test yakunlandi!\n\n"
            f"Natijangiz: {score}/{len(QUESTIONS)}\n"
            f"Foiz: {percent}%\n\n"
            "Natijangiz saqlandi.",
        )

        if user_id != ADMIN_ID:
            user = get_user(user_id)
            name = user["full_name"] or str(user_id)
            username = f"@{user['username']}" if user["username"] else "username yo‘q"
            try:
                await bot.send_message(
                    ADMIN_ID,
                    "📊 Yangi test natijasi\n\n"
                    f"Ishtirokchi: {name}\n"
                    f"Telegram: {username}\n"
                    f"ID: {user_id}\n"
                    f"Natija: {score}/{len(QUESTIONS)} ({percent}%)",
                )
            except Exception:
                pass
        return

    db.execute(
        """
        UPDATE attempts
        SET current_question=?, score=?
        WHERE user_id=?
        """,
        (next_question, score, user_id),
    )
    db.commit()

    await callback.answer("Javob qabul qilindi.")
    await send_question(callback.message.chat.id, next_question)


@dp.message(Command("results"))
async def results_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    rows = db.execute(
        """
        SELECT
            a.user_id,
            a.score,
            a.started_at,
            a.finished_at,
            u.full_name,
            u.username
        FROM attempts a
        LEFT JOIN users u ON u.user_id=a.user_id
        WHERE a.completed=1
        ORDER BY a.score DESC, a.finished_at ASC
        """
    ).fetchall()

    if not rows:
        await message.answer("Hozircha yakunlangan test natijalari yo‘q.")
        return

    text = "🏆 TEST NATIJALARI\n\n"
    for i, row in enumerate(rows, start=1):
        username = f"@{row['username']}" if row["username"] else "—"
        text += (
            f"{i}. {row['full_name'] or row['user_id']}\n"
            f"   {username} | {row['score']}/{len(QUESTIONS)}\n"
        )

    if len(text) <= 4000:
        await message.answer(text)
    else:
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            await message.answer(chunk)


@dp.message(Command("myresult"))
async def my_result_handler(message: Message):
    row = db.execute(
        "SELECT * FROM attempts WHERE user_id=? AND completed=1",
        (message.from_user.id,),
    ).fetchone()

    if not row:
        await message.answer("Sizda hali yakunlangan test natijasi yo‘q.")
        return

    percent = round(row["score"] / len(QUESTIONS) * 100)
    await message.answer(
        f"📊 Natijangiz: {row['score']}/{len(QUESTIONS)} ({percent}%)"
    )


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
