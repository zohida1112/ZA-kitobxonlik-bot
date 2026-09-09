import asyncio
import os
import sqlite3
import json
import random
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


TEST2_QUESTIONS = [{'q': 'Qari Mayorning yig‘ilishidagi kalamushlar masalasi bo‘yicha ovoz berishda qaysi holat yuz beradi?', 'options': ['Faqat cho‘chqalar kalamushlarni safga olishga rozi bo‘ladi', 'Uchta it qarshi chiqadi, mushuklar esa har ikki tomon uchun ovoz beradi', 'Barcha hayvonlar bir ovozdan qarshi chiqadi', 'Benjamin va Boxer betaraf qoladi'], 'correct': 1}, {'q': 'Qari Mayorning inson hukmronligiga qarshi dalilining markazida qaysi fikr turadi?', 'options': ['Inson hayvonlardan kuchliroq, ammo kamroq ishlaydi', 'Inson mahsulot yaratmay turib, hayvonlar mehnati mahsulini o‘zlashtiradi', 'Inson yerga ishlov bera olmaydi, chunki texnikasi yo‘q', 'Inson faqat go‘sht uchun hayvon boqadi'], 'correct': 1}, {'q': 'Mayor Boxerning qariganidan keyingi taqdiri haqida qanday bashorat qiladi?', 'options': ['Uni boshqa fermaga sotishadi', 'Unga nafaqa beriladi', 'Uni hayvonlar uchun ozuqa tayyorlaydigan korxonaga sotishadi', 'Uni daladagi yengil ishga o‘tkazishadi'], 'correct': 2}, {'q': 'Mayorning tushi uning xotirasida nimani qayta tiklaydi?', 'options': ['Yoshligidagi qo‘zg‘olonni', 'Onasi va boshqa cho‘chqalar kuylagan qadimiy qo‘shiqni', 'Insonlarsiz ferma tasvirini', 'Bolaligida ko‘rgan boshqa fermani'], 'correct': 1}, {'q': '“Angliya hayvonlari” qo‘shig‘i bir necha bor takrorlangach yuz bergan voqea qaysi?', 'options': ['Napoleon yig‘ilishni to‘xtatadi', 'Jones miltiqdan qorong‘ilikka o‘q uzadi', 'Hayvonlar omborni egallaydi', 'Mayor hushidan ketadi'], 'correct': 1}, {'q': 'Mayor vafotidan keyin hayvonizm g‘oyalarini yoyish vazifasini asosan kimlar zimmasiga oladi?', 'options': ['Boxer, Clover va Benjamin', 'Snowball, Napoleon va Squealer', 'Mollie, Moses va Muriel', 'Itlar va qo‘ylar'], 'correct': 1}, {'q': 'Molliening hayvonizmni qabul qilishdagi ichki qarama-qarshiligini eng aniq ko‘rsatgan ikki narsa qaysilar?', 'options': ['Pichan va suli', 'Shakar va lentalar', 'Arpa va olma', 'Uy va yumshoq karavot'], 'correct': 1}, {'q': 'Qo‘zg‘olonning kutilmaganda boshlanishiga bevosita nima sabab bo‘ladi?', 'options': ['Jones bir hayvonni o‘ldiradi', 'Snowball yashirin buyruq beradi', 'Hayvonlar kun bo‘yi ovqatsiz qolib, keyin qamchi bilan uriladi', 'Fermaga boshqa odamlar bostirib kiradi'], 'correct': 2}, {'q': 'Qo‘zg‘olondan keyin Jones hukmronligini anglatuvchi buyumlardan qaysi biri olovga tashlanadi?', 'options': ['Hayvon so‘yadigan pichoqlar', 'Zanjirlar', 'Xipchinlar', 'Jilovlar'], 'correct': 2}, {'q': 'Qo‘zg‘olondan keyingi ilk tun oldidan Napoleon hayvonlarga qanday mukofot beradi?', 'options': ['Har biriga ikki ulush makkajo‘xori, har bir itga ikki pechenye', 'Har biriga olma, cho‘chqalarga sut', 'Har biriga suli, itlarga uch pechenye', 'Har biriga pichan, cho‘chqalarga makkajo‘xori'], 'correct': 0}, {'q': 'Jonesning uyiga kirilganda Molliening boshqalardan ajralib qolishiga nima sabab bo‘ladi?', 'options': ['Shakar topib olishi', 'Yumshoq karavotda yotib qolishi', 'Ikki ko‘k lentani yelkasiga qadab, o‘zini oynada tomosha qilishi', 'Odamlarning kiyimlarini kiyib ko‘rishi'], 'correct': 2}, {'q': '“To‘rt oyoqlilar — do‘st, ikki oyoqlilar — dushman” qoidasiga qushlar e’tiroz bildirganda Snowball qanday asos keltiradi?', 'options': ['Qanot oyoqning boshqa shaklidir', 'Qushlar odamlar singari yerda yurmaydi', 'Qanot ushlash uchun emas, uchish uchun yaratilgan; shu sababli uni oyoq sifatida qabul qilish kerak', 'Qushlar hayvonizm qoidalaridan mustasno'], 'correct': 2}, {'q': '“Molxona jangi”da Snowballning dastlabki hujumi qanday tashkil etiladi?', 'options': ['Qo‘ylar oldinga, otlar orqadan hujum qiladi', '35 kaptar odamlar ustidan axlat tashlaydi, keyin g‘ozlar boldirlarini cho‘qiydi', 'Itlar odamlarni darvoza tomon quvadi', 'Boxer va Clover birinchi bo‘lib hujum qiladi'], 'correct': 1}, {'q': 'Snowball jang taktikasini shakllantirishda qaysi manbadan foydalangan edi?', 'options': ['Napoleon yozgan harbiy reja', 'Jonesning eski kundaligi', 'Yuliy Sezar qo‘shinlarini qanday boshqargani haqidagi kitob', 'Ingliz harbiylari haqidagi gazeta'], 'correct': 2}, {'q': 'Snowball fermadan quvilganidan keyin Boxerning avvalgi shioriga qaysi yangi shior qo‘shiladi?', 'options': ['“To‘rt oyoq yaxshi, ikki oyoq yomon”', '“Napoleonning hamma so‘zlari haqiqat”', '“Snowball xoin”', '“Hayvonlar hech qachon taslim bo‘lmaydi”'], 'correct': 1}, {'q': 'Snowball haydalgach, Napoleon shamol tegirmonini qurish haqida qachon buyruq beradi?', 'options': ['Ertasi kuni', 'Ikkinchi yakshanbada', 'Uchinchi yakshanbada', 'Bir oy o‘tgach'], 'correct': 2}, {'q': 'Napoleonning shamol tegirmoni haqidagi qarori hayvonlarni nega ayniqsa hayratga soladi?', 'options': ['Tegirmon Jonesning rejasi bo‘lganligi uchun', 'Napoleon ilgari bu loyihaga qarshi turgani uchun', 'Tegirmon qurib bitkazilganligi uchun', 'Snowball tegirmon qurilishiga qarshi bo‘lgani uchun'], 'correct': 1}, {'q': 'Fermada biror buyum yo‘qolishi yoki zarar ko‘rishi Snowballga yuklanadigan darajaga yetganini qaysi voqea ayniqsa ko‘rsatadi?', 'options': ['Yo‘qolgan kalit don qopi tagidan topilsa ham Snowball haqidagi ayblov davom etadi', 'Napoleon Snowballni fermada ushlab oladi', 'Benjamin uning izlarini ko‘radi', 'Mollie Snowball bilan uchrashganini tan oladi'], 'correct': 0}, {'q': 'Napoleon hukmronligi kuchaygan sari cho‘chqalarga nisbatan shakllangan odatlardan qaysi biri matnda aniq qayd etilgan?', 'options': ['Har kuni oltin nishon taqish', 'Boshqa hayvonlar ularga yo‘l bo‘shatishi va yakshanba kunlari dumlariga yashil lenta taqishlari', 'Faqat Napoleon lenta taqishi', 'Cho‘chqalarning dalada ishlashi taqiqlanishi'], 'correct': 1}, {'q': 'Ferma iqtisodiy qiyinchilikka duch kelgan davrda tuxum sotish shartnomasi haftasiga nechta tuxumgacha oshiriladi?', 'options': ['300', '400', '500', '600'], 'correct': 3}, {'q': 'Oziq-ovqat ulushlari keskin kamaygan bir paytda cho‘chqalarning turmushidagi qaysi tafovut ayniqsa ko‘zga tashlanadi?', 'options': ['Ular ham boshqalar bilan bir xil och qoladi', 'Cho‘chqalar to‘lishib boradi va arpa ularga ajratiladi', 'Ular fermani tark etadi', 'Ularning ham pivo ulushi bekor qilinadi'], 'correct': 1}, {'q': 'Arpa taqsimotida Napoleonning o‘ziga beriladigan miqdor qanday ko‘rsatiladi?', 'options': ['Bir paunt pivo', '0,5 gallon pivo', 'Ikki gallon pivo', 'Bir krujka pivo'], 'correct': 1}, {'q': 'Yog‘och savdosida Frederick Napoleonni qanday aldaydi?', 'options': ['Yog‘ochni olib ketib, umuman pul bermaydi', 'Pulning faqat yarmini beradi', '5 funtlik to‘lovni qalbaki pul bilan amalga oshiradi', 'Yog‘och o‘rniga texnika berishni va’da qilib yo‘qoladi'], 'correct': 2}, {'q': 'Frederick bergan pullarning soxta ekanligi qachon ma’lum bo‘ladi?', 'options': ['O‘sha zahoti', 'Ertasi kuni', 'Uch kundan keyin', 'Bir haftadan keyin'], 'correct': 2}, {'q': '“Shamol tegirmoni jangi”dan keyin tirik qolganlarga berilgan mukofotlar qaysi javobda to‘g‘ri moslashtirilgan?', 'options': ['Hayvonlarga olma; qushlarga ikki o‘lchov makkajo‘xori; itlarga uch pechenye', 'Hayvonlarga ikki olma; qushlarga arpa; itlarga bir pechenye', 'Hayvonlarga shakar; qushlarga suli; itlarga ikki pechenye', 'Barcha hayvonlarga bir xil makkajo‘xori'], 'correct': 0}, {'q': 'Moses keyinchalik fermaga qaytganida cho‘chqalarning unga munosabatidagi ziddiyat nimadan iborat?', 'options': ['Shakartog‘ni rasman tan olishadi, ammo Mosesni quvishadi', 'Uning hikoyalarini yolg‘on deyishadi, ammo ishlamasdan fermada yashashi va pivo ulushi olishiga ruxsat berishadi', 'Uni targ‘ibot rahbari qilishadi', 'Unga hikoya aytish taqiqlanadi'], 'correct': 1}, {'q': 'Cho‘chqalarning ikki oyoqda yurishi sahnasida Napoleonni boshqalardan ajratib turuvchi eng muhim detal qaysi?', 'options': ['U yashil bayroq ko‘tarib chiqadi', 'U oldingi tuyog‘ida qamchi ushlab chiqadi', 'U Snowballning rasmini ko‘tarib chiqadi', 'U ikki oyoqda yurmaydi'], 'correct': 1}, {'q': 'Asar boshidagi insonlarga qarshi kurash tamoyili bilan Napoleonning qamchi ko‘tarib chiqishi o‘rtasidagi eng keskin qarama-qarshilik nimada?', 'options': ['Hayvonlar inson hukmronligi belgilarini yo‘q qilgan, Napoleon esa aynan hukmronlik ramzi bo‘lgan qamchini qo‘liga olgan', 'Napoleon fermadan chiqib ketgan', 'Cho‘chqalar ishlashni boshlagan', 'Hayvonlar yana Jonesni xo‘jayin deb tan olgan'], 'correct': 0}, {'q': 'Asarning so‘nggi sahnasida Napoleon va Pilkington o‘rtasidagi janjalning bevosita sababi nima edi?', 'options': ['Shamol tegirmonining egaligi', 'Yog‘och uchun to‘lov', 'Karta o‘yinidagi tuz qarg‘a', 'Ferma chegarasi'], 'correct': 2}, {'q': 'Asarning yakuniy sahnasini to‘liq ifodalovchi holat qaysi?', 'options': ['Hayvonlar odamlarni fermadan ikkinchi marta haydab chiqaradilar', 'Napoleon odamlarni aldab, ular ustidan mutlaq g‘alaba qiladi', 'Derazadan qarayotgan hayvonlar cho‘chqalar bilan odamlarning yuzlarini bir-biridan ajrata olmay qoladilar', 'Cho‘chqalar hayvonizmning dastlabki qoidalarini qayta tiklaydilar'], 'correct': 2}]

TEST2_TIME_LIMIT_MINUTES = 20


bot = Bot(BOT_TOKEN)
dp = Dispatcher()

db = sqlite3.connect("users.db", check_same_thread=False)
db.row_factory = sqlite3.Row

# -------------------- DATABASE --------------------

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

# 1-kitob eski test natijalari saqlanadi.
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

# 2-kitob natijalari, savol va variantlar aralash tartibi bilan saqlanadi.
db.execute(
    """
    CREATE TABLE IF NOT EXISTS attempts2 (
        user_id INTEGER PRIMARY KEY,
        current_question INTEGER DEFAULT 0,
        score INTEGER DEFAULT 0,
        started_at TEXT,
        finished_at TEXT,
        completed INTEGER DEFAULT 0,
        question_order TEXT,
        option_orders TEXT
    )
    """
)

# Har bir test uchun alohida kirish huquqi.
db.execute(
    """
    CREATE TABLE IF NOT EXISTS test_access (
        user_id INTEGER NOT NULL,
        test_key TEXT NOT NULL,
        unlocked INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, test_key)
    )
    """
)

# Yangi referal uchun vaqtinchalik bog‘lanish.
# invited_user_id UNIQUE: bir odam faqat bitta test uchun bir marta referal bo‘la oladi.
db.execute(
    """
    CREATE TABLE IF NOT EXISTS test_referrals (
        invited_user_id INTEGER PRIMARY KEY,
        referrer_id INTEGER NOT NULL,
        test_key TEXT NOT NULL,
        confirmed INTEGER DEFAULT 0
    )
    """
)

db.commit()

timeout_tasks = {}


def add_user(user_id, full_name=None, username=None):
    existing = db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if existing:
        db.execute(
            "UPDATE users SET full_name=?, username=? WHERE user_id=?",
            (full_name, username, user_id),
        )
    else:
        db.execute(
            "INSERT INTO users (user_id, full_name, username) VALUES (?, ?, ?)",
            (user_id, full_name, username),
        )
    db.commit()


def get_user(user_id):
    return db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()


def mark_verified(user_id):
    db.execute("UPDATE users SET verified=1 WHERE user_id=?", (user_id,))
    db.commit()


def ensure_test_access(user_id, test_key):
    db.execute(
        "INSERT OR IGNORE INTO test_access (user_id, test_key, unlocked) VALUES (?, ?, 0)",
        (user_id, test_key),
    )
    db.commit()


def get_test_access(user_id, test_key):
    ensure_test_access(user_id, test_key)
    return db.execute(
        "SELECT * FROM test_access WHERE user_id=? AND test_key=?",
        (user_id, test_key),
    ).fetchone()


def unlock_test(user_id, test_key):
    ensure_test_access(user_id, test_key)
    db.execute(
        "UPDATE test_access SET unlocked=1 WHERE user_id=? AND test_key=?",
        (user_id, test_key),
    )
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


def test_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📘 1-kitob testi", callback_data="choose_test:t1")],
            [InlineKeyboardButton(text="📗 2-kitob testi", callback_data="choose_test:t2")],
        ]
    )


def final_channel_check_keyboard(test_key, invite_link=None):
    rows = []
    if invite_link:
        rows.append([
            InlineKeyboardButton(
                text="🔐 Yopiq kanalga kirish",
                url=invite_link
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text="✅ Kanalga kirdim — tekshirish",
            callback_data=f"verify_final:{test_key}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def actual_start_keyboard(test_key):
    if test_key == "t1":
        text = "📘 1-kitob testini boshlash"
        cb = "start_test"
    else:
        text = "📗 2-kitob testini boshlash"
        cb = "start_test2"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=cb)]
        ]
    )


async def is_member_of_required_channels(user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch["id"], user_id)
            if member.status in {ChatMemberStatus.LEFT, ChatMemberStatus.KICKED}:
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


async def send_final_channel_and_start(user_id, test_key):
    # Referal tasdiqlangach test darhol ochilmaydi.
    # Avval foydalanuvchi yopiq kanalga kiradi, so‘ng bot a’zolikni tekshiradi.
    if await is_final_channel_member(user_id):
        await bot.send_message(
            user_id,
            "🎉 Referalingiz tasdiqlandi!\n\n"
            "✅ Siz yopiq kitobxonlik kanaliga a’zosiz.\n"
            "Endi testni boshlashingiz mumkin.",
            reply_markup=actual_start_keyboard(test_key),
        )
        return

    try:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
        invite = await bot.create_chat_invite_link(
            chat_id=FINAL_CHANNEL_ID,
            expire_date=expire,
            member_limit=1,
            name=f"{test_key}_{user_id}",
        )

        await bot.send_message(
            user_id,
            "🎉 Referalingiz tasdiqlandi!\n\n"
            "1️⃣ Avval yopiq kitobxonlik kanaliga kiring.\n"
            "2️⃣ So‘ng “✅ Kanalga kirdim — tekshirish” tugmasini bosing.\n"
            "3️⃣ A’zoligingiz tasdiqlangach testni boshlash tugmasi chiqadi.\n\n"
            "⏳ Kanal havolasi 24 soat amal qiladi va 1 kishi uchun.",
            reply_markup=final_channel_check_keyboard(
                test_key,
                invite.invite_link
            ),
        )
    except Exception as e:
        print("Invite link error:", e)
        await bot.send_message(
            user_id,
            "⚠️ Yopiq kanalga taklif havolasini yaratishda xatolik yuz berdi.\n"
            "Botning yopiq kanalda administrator ekanini tekshiring."
        )


async def send_test_referral_post(chat_id, user_id, test_key):
    me = await bot.get_me()
    payload = f"{test_key}_{user_id}"
    ref_link = f"https://t.me/{me.username}?start={payload}"

    test_name = "1-kitob testi" if test_key == "t1" else "2-kitob testi"

    caption = (
        f"📚 {test_name.upper()} UCHUN 1 TA YANGI REFERAL KERAK.\n\n"
        "Shaxsiy havolangizni hali bu botdan foydalanmagan yangi odamga yuboring. "
        "U havola orqali botga kirib, 4 ta majburiy kanalga a’zo bo‘lib "
        "“✅ A’zo bo‘ldim” tugmasini bosishi kerak.\n\n"
        "⚠️ Oldin botdan foydalangan yoki avval referal sifatida ishlatilgan odam "
        "yangi referal hisoblanmaydi.\n\n"
        f"🔗 Sizning referal havolangiz:\n{ref_link}"
    )

    share_url = (
        f"https://t.me/share/url?url={quote(ref_link)}"
        f"&text={quote('Zohida Akademy — Har hafta bir kitob loyihasiga qo‘shiling!')}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Do‘stga yuborish", url=share_url)],
            [InlineKeyboardButton(
                text="🔄 Referalni tekshirish",
                callback_data=f"check_test_ref:{test_key}"
            )],
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


def create_pending_test_referral(invited_user_id, referrer_id, test_key, was_existing):
    if was_existing:
        return False
    if invited_user_id == referrer_id:
        return False
    if test_key not in {"t1", "t2"}:
        return False
    if not get_user(referrer_id):
        return False

    # Bir odam butun loyiha bo‘yicha faqat bir marta referal bo‘la oladi.
    existing = db.execute(
        "SELECT * FROM test_referrals WHERE invited_user_id=?",
        (invited_user_id,),
    ).fetchone()
    if existing:
        return False

    db.execute(
        """
        INSERT INTO test_referrals
        (invited_user_id, referrer_id, test_key, confirmed)
        VALUES (?, ?, ?, 0)
        """,
        (invited_user_id, referrer_id, test_key),
    )
    db.commit()
    return True


async def confirm_pending_test_referral(invited_user_id):
    row = db.execute(
        "SELECT * FROM test_referrals WHERE invited_user_id=?",
        (invited_user_id,),
    ).fetchone()

    if not row or row["confirmed"]:
        return False

    # Yangi odam 4 ta majburiy kanalga haqiqatan a’zo bo‘lgandagina tasdiqlanadi.
    if not await is_member_of_required_channels(invited_user_id):
        return False

    db.execute(
        "UPDATE test_referrals SET confirmed=1 WHERE invited_user_id=?",
        (invited_user_id,),
    )
    unlock_test(row["referrer_id"], row["test_key"])
    db.commit()

    await send_final_channel_and_start(row["referrer_id"], row["test_key"])
    return True


# -------------------- START / A’ZOLIK --------------------

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id

    # Referal "yangi odam" bo‘lishi uchun botda avval ro‘yxatdan o‘tmagan bo‘lishi kerak.
    was_existing = get_user(user_id) is not None

    test_key = None
    referrer_id = None

    parts = message.text.split(maxsplit=1)
    if len(parts) == 2:
        payload = parts[1].strip()
        if payload.startswith("t1_") or payload.startswith("t2_"):
            try:
                test_key, rid = payload.split("_", 1)
                referrer_id = int(rid)
            except Exception:
                test_key = None
                referrer_id = None

    add_user(user_id, message.from_user.full_name, message.from_user.username)

    if test_key and referrer_id:
        create_pending_test_referral(
            invited_user_id=user_id,
            referrer_id=referrer_id,
            test_key=test_key,
            was_existing=was_existing,
        )

    if not await is_member_of_required_channels(user_id):
        await message.answer(
            "📚 Zohida Akademy — “Har hafta bir kitob” loyihasiga xush kelibsiz!\n\n"
            "Avval quyidagi 4 ta kanalga a’zo bo‘ling. "
            "So‘ng “✅ A’zo bo‘ldim” tugmasini bosing.",
            reply_markup=required_channels_keyboard(),
        )
        return

    mark_verified(user_id)
    await confirm_pending_test_referral(user_id)

    await message.answer(
        "✅ Kanal a’zoligingiz tasdiqlandi.\n\n"
        "Endi ishlamoqchi bo‘lgan testni tanlang:",
        reply_markup=test_menu_keyboard(),
    )


@dp.callback_query(F.data == "check_channels")
async def check_channels_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    add_user(user_id, callback.from_user.full_name, callback.from_user.username)

    if not await is_member_of_required_channels(user_id):
        await callback.answer(
            "❌ Hali barcha 4 ta kanalga a’zo emassiz.",
            show_alert=True,
        )
        return

    mark_verified(user_id)
    await confirm_pending_test_referral(user_id)

    await callback.answer("✅ A’zolik tasdiqlandi!")
    await bot.send_message(
        callback.message.chat.id,
        "📚 Endi ishlamoqchi bo‘lgan testni tanlang:",
        reply_markup=test_menu_keyboard(),
    )


@dp.message(Command("tests"))
async def tests_handler(message: Message):
    if not await is_member_of_required_channels(message.from_user.id):
        await message.answer(
            "Avval 4 ta majburiy kanalga a’zo bo‘ling.",
            reply_markup=required_channels_keyboard(),
        )
        return

    await message.answer(
        "📚 Kerakli testni tanlang:",
        reply_markup=test_menu_keyboard(),
    )


# -------------------- TEST TANLASH / REFERAL --------------------

@dp.callback_query(F.data.startswith("choose_test:"))
async def choose_test_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    test_key = callback.data.split(":", 1)[1]

    if test_key not in {"t1", "t2"}:
        return

    if not await is_member_of_required_channels(user_id):
        await callback.answer(
            "Avval 4 ta majburiy kanalga a’zo bo‘ling.",
            show_alert=True,
        )
        return

    # O‘sha test allaqachon tugatilgan bo‘lsa qayta ishlanmaydi.
    if test_key == "t1":
        attempt = db.execute(
            "SELECT * FROM attempts WHERE user_id=?",
            (user_id,),
        ).fetchone()
        if attempt and attempt["completed"]:
            await callback.answer(
                "Siz 1-kitob testini avval ishlagansiz.",
                show_alert=True,
            )
            return
    else:
        attempt = db.execute(
            "SELECT * FROM attempts2 WHERE user_id=?",
            (user_id,),
        ).fetchone()
        if attempt and attempt["completed"]:
            await callback.answer(
                "Siz 2-kitob testini avval ishlagansiz.",
                show_alert=True,
            )
            return

    access = get_test_access(user_id, test_key)

    if access["unlocked"]:
        await callback.answer("✅ Bu test siz uchun ochiq.")
        await send_final_channel_and_start(user_id, test_key)
        return

    await callback.answer("🔐 Avval 1 ta yangi referal kerak.", show_alert=True)
    await send_test_referral_post(callback.message.chat.id, user_id, test_key)


@dp.callback_query(F.data.startswith("check_test_ref:"))
async def check_test_ref_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    test_key = callback.data.split(":", 1)[1]

    access = get_test_access(user_id, test_key)
    if access["unlocked"]:
        await callback.answer("✅ Referalingiz tasdiqlangan!")
        await send_final_channel_and_start(user_id, test_key)
    else:
        await callback.answer(
            "⏳ Hali yangi referalingiz tasdiqlanmadi.\n"
            "Taklif qilgan odam 4 ta kanalga a’zo bo‘lib “A’zo bo‘ldim”ni bosishi kerak.",
            show_alert=True,
        )


@dp.callback_query(F.data.startswith("verify_final:"))
async def verify_final_channel_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    test_key = callback.data.split(":", 1)[1]

    if test_key not in {"t1", "t2"}:
        return

    access = get_test_access(user_id, test_key)
    if not access["unlocked"]:
        await callback.answer(
            "Avval shu test uchun referal shartini bajaring.",
            show_alert=True,
        )
        return

    if not await is_final_channel_member(user_id):
        await callback.answer(
            "❌ Siz hali yopiq kanalga kirmagansiz.\n"
            "Avval kanalga kiring, keyin yana tekshiring.",
            show_alert=True,
        )
        return

    await callback.answer("✅ Yopiq kanal a’zoligingiz tasdiqlandi!")
    await bot.send_message(
        callback.message.chat.id,
        "✅ A’zoligingiz tasdiqlandi.\n\n"
        "Endi testni boshlashingiz mumkin.",
        reply_markup=actual_start_keyboard(test_key),
    )


# -------------------- 1-KITOB TESTI --------------------

def question_keyboard(question_index):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="A", callback_data=f"answer:{question_index}:0"),
                InlineKeyboardButton(text="B", callback_data=f"answer:{question_index}:1"),
                InlineKeyboardButton(text="C", callback_data=f"answer:{question_index}:2"),
                InlineKeyboardButton(text="D", callback_data=f"answer:{question_index}:3"),
            ]
        ]
    )


async def send_question(chat_id, question_index):
    q = QUESTIONS[question_index]
    opts = q["options"]

    question_text = (
        f"{q['q']}\n\n"
        f"A) {opts[0]}\n\n"
        f"B) {opts[1]}\n\n"
        f"C) {opts[2]}\n\n"
        f"D) {opts[3]}"
    )

    await bot.send_message(
        chat_id,
        question_text,
        reply_markup=question_keyboard(question_index),
    )


@dp.callback_query(F.data == "start_test")
async def start_test_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    access = get_test_access(user_id, "t1")
    if not access["unlocked"]:
        await callback.answer(
            "🔐 1-kitob testi uchun avval 1 ta yangi referal kerak.",
            show_alert=True,
        )
        await send_test_referral_post(callback.message.chat.id, user_id, "t1")
        return

    if not await is_final_channel_member(user_id):
        await callback.answer(
            "❌ Avval yopiq kitobxonlik kanaliga kiring.",
            show_alert=True,
        )
        await send_final_channel_and_start(user_id, "t1")
        return

    attempt = db.execute(
        "SELECT * FROM attempts WHERE user_id=?",
        (user_id,),
    ).fetchone()

    if attempt and attempt["completed"]:
        await callback.answer(
            "Siz 1-kitob testini avval ishlagansiz.",
            show_alert=True,
        )
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
        await callback.answer(
            "Bu savolga javob allaqachon qabul qilingan.",
            show_alert=True,
        )
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
            "✅ 1-kitob testi yakunlandi!\n\n"
            f"Natijangiz: {score}/{len(QUESTIONS)}\n"
            f"Foiz: {percent}%\n\n"
            "Natijangiz saqlandi.",
            reply_markup=test_menu_keyboard(),
        )
        await notify_admin_result(
            user_id, "1-kitob", score, len(QUESTIONS)
        )
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


# -------------------- 2-KITOB: 30 SAVOL, ARALASH, 20 DAQIQA --------------------

def make_test2_attempt():
    q_order = list(range(len(TEST2_QUESTIONS)))
    random.shuffle(q_order)

    option_orders = {}
    for q_idx in q_order:
        order = list(range(len(TEST2_QUESTIONS[q_idx]["options"])))
        random.shuffle(order)
        option_orders[str(q_idx)] = order

    return q_order, option_orders


def parse_dt(value):
    return datetime.fromisoformat(value) if value else None


def test2_seconds_left(attempt):
    started = parse_dt(attempt["started_at"])
    if not started:
        return 0

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    return max(
        0,
        int(TEST2_TIME_LIMIT_MINUTES * 60 - elapsed)
    )


def test2_keyboard(step, q_idx, option_order):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="A", callback_data=f"t2answer:{step}:0"),
                InlineKeyboardButton(text="B", callback_data=f"t2answer:{step}:1"),
                InlineKeyboardButton(text="C", callback_data=f"t2answer:{step}:2"),
                InlineKeyboardButton(text="D", callback_data=f"t2answer:{step}:3"),
            ]
        ]
    )


async def send_test2_question(chat_id, user_id):
    attempt = db.execute(
        "SELECT * FROM attempts2 WHERE user_id=?",
        (user_id,),
    ).fetchone()

    if not attempt or attempt["completed"]:
        return

    if test2_seconds_left(attempt) <= 0:
        await finish_test2(user_id, chat_id, timed_out=True)
        return

    q_order = json.loads(attempt["question_order"])
    option_orders = json.loads(attempt["option_orders"])
    step = attempt["current_question"]

    if step >= len(q_order):
        await finish_test2(user_id, chat_id)
        return

    q_idx = q_order[step]
    q = TEST2_QUESTIONS[q_idx]
    order = option_orders[str(q_idx)]

    seconds_left = test2_seconds_left(attempt)
    mm, ss = divmod(seconds_left, 60)

    displayed_options = [q["options"][orig_idx] for orig_idx in order]

    question_text = (
        f"📗 2-kitob testi\n"
        f"❓ Savol {step + 1}/{len(q_order)}\n"
        f"⏳ Qolgan vaqt: {mm:02d}:{ss:02d}\n\n"
        f"{q['q']}\n\n"
        f"A) {displayed_options[0]}\n\n"
        f"B) {displayed_options[1]}\n\n"
        f"C) {displayed_options[2]}\n\n"
        f"D) {displayed_options[3]}"
    )

    await bot.send_message(
        chat_id,
        question_text,
        reply_markup=test2_keyboard(step, q_idx, order),
    )


async def finish_test2(user_id, chat_id, timed_out=False):
    attempt = db.execute(
        "SELECT * FROM attempts2 WHERE user_id=?",
        (user_id,),
    ).fetchone()

    if not attempt or attempt["completed"]:
        return

    finished = datetime.now(timezone.utc)

    db.execute(
        """
        UPDATE attempts2
        SET finished_at=?, completed=1
        WHERE user_id=?
        """,
        (finished.isoformat(), user_id),
    )
    db.commit()

    q_order = json.loads(attempt["question_order"])
    total = len(q_order)
    score = attempt["score"]
    percent = round(score / total * 100) if total else 0

    started = parse_dt(attempt["started_at"])
    spent = int((finished - started).total_seconds()) if started else 0
    spent = min(spent, TEST2_TIME_LIMIT_MINUTES * 60)

    sm, ss = divmod(spent, 60)

    title = "⏰ Vaqt tugadi!" if timed_out else "✅ 2-kitob testi yakunlandi!"

    await bot.send_message(
        chat_id,
        f"{title}\n\n"
        f"Natijangiz: {score}/{total}\n"
        f"Foiz: {percent}%\n"
        f"Sarflangan vaqt: {sm:02d}:{ss:02d}\n\n"
        "Natijangiz saqlandi.",
        reply_markup=test_menu_keyboard(),
    )

    await notify_admin_result(
        user_id,
        "2-kitob",
        score,
        total,
        spent
    )

    task = timeout_tasks.pop(user_id, None)
    if task and task is not asyncio.current_task():
        task.cancel()


async def timeout_test2(user_id, chat_id, seconds):
    try:
        await asyncio.sleep(seconds)

        attempt = db.execute(
            "SELECT * FROM attempts2 WHERE user_id=?",
            (user_id,),
        ).fetchone()

        if attempt and not attempt["completed"]:
            await finish_test2(
                user_id,
                chat_id,
                timed_out=True
            )

    except asyncio.CancelledError:
        pass


@dp.callback_query(F.data == "start_test2")
async def start_test2_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    access = get_test_access(user_id, "t2")
    if not access["unlocked"]:
        await callback.answer(
            "🔐 2-kitob testi uchun avval 1 ta yangi referal kerak.",
            show_alert=True,
        )
        await send_test_referral_post(
            callback.message.chat.id,
            user_id,
            "t2"
        )
        return

    if not await is_final_channel_member(user_id):
        await callback.answer(
            "❌ Avval yopiq kitobxonlik kanaliga kiring.",
            show_alert=True,
        )
        await send_final_channel_and_start(user_id, "t2")
        return

    attempt = db.execute(
        "SELECT * FROM attempts2 WHERE user_id=?",
        (user_id,),
    ).fetchone()

    if attempt and attempt["completed"]:
        await callback.answer(
            "Siz 2-kitob testini avval ishlagansiz.",
            show_alert=True,
        )
        return

    if not attempt:
        q_order, option_orders = make_test2_attempt()
        now = datetime.now(timezone.utc).isoformat()

        db.execute(
            """
            INSERT INTO attempts2
            (user_id, current_question, score, started_at,
             completed, question_order, option_orders)
            VALUES (?, 0, 0, ?, 0, ?, ?)
            """,
            (
                user_id,
                now,
                json.dumps(q_order),
                json.dumps(option_orders),
            ),
        )
        db.commit()

        attempt = db.execute(
            "SELECT * FROM attempts2 WHERE user_id=?",
            (user_id,),
        ).fetchone()

    left = test2_seconds_left(attempt)

    if left <= 0:
        await callback.answer(
            "Test vaqti tugagan.",
            show_alert=True,
        )
        await finish_test2(
            user_id,
            callback.message.chat.id,
            timed_out=True
        )
        return

    old_task = timeout_tasks.pop(user_id, None)
    if old_task:
        old_task.cancel()

    timeout_tasks[user_id] = asyncio.create_task(
        timeout_test2(
            user_id,
            callback.message.chat.id,
            left
        )
    )

    await callback.answer()

    # Birinchi marta boshlangandagina qoidalarni ko‘rsatamiz.
    if attempt["current_question"] == 0:
        await bot.send_message(
            callback.message.chat.id,
            "📗 2-kitob testi boshlandi!\n\n"
            "🔀 30 ta savol tartibi har bir ishtirokchi uchun aralashtiriladi.\n"
            "🔀 A/B/C/D javob variantlari ham aralashtiriladi.\n"
            f"⏳ Umumiy vaqt: {TEST2_TIME_LIMIT_MINUTES} daqiqa.\n"
            "↩️ Oldingi savolga qaytib bo‘lmaydi.\n"
            "✅ Har savolga faqat bir marta javob beriladi.",
        )

    await send_test2_question(
        callback.message.chat.id,
        user_id
    )


@dp.callback_query(F.data.startswith("t2answer:"))
async def test2_answer_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    attempt = db.execute(
        "SELECT * FROM attempts2 WHERE user_id=?",
        (user_id,),
    ).fetchone()

    if not attempt or attempt["completed"]:
        await callback.answer(
            "2-kitob testi faol emas.",
            show_alert=True,
        )
        return

    if test2_seconds_left(attempt) <= 0:
        await callback.answer(
            "⏰ Vaqt tugadi.",
            show_alert=True,
        )

        try:
            await callback.message.edit_reply_markup(
                reply_markup=None
            )
        except Exception:
            pass

        await finish_test2(
            user_id,
            callback.message.chat.id,
            timed_out=True
        )
        return

    _, step_text, displayed_pos_text = callback.data.split(":")
    step = int(step_text)
    displayed_pos = int(displayed_pos_text)

    if step != attempt["current_question"]:
        await callback.answer(
            "Bu savolga javob allaqachon qabul qilingan.",
            show_alert=True,
        )
        return

    q_order = json.loads(attempt["question_order"])
    option_orders = json.loads(attempt["option_orders"])

    q_idx = q_order[step]
    original_opt_idx = option_orders[str(q_idx)][displayed_pos]
    correct = TEST2_QUESTIONS[q_idx]["correct"]

    score = attempt["score"]
    if original_opt_idx == correct:
        score += 1

    next_step = step + 1

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    db.execute(
        """
        UPDATE attempts2
        SET current_question=?, score=?
        WHERE user_id=?
        """,
        (next_step, score, user_id),
    )
    db.commit()

    await callback.answer("Javob qabul qilindi.")

    if next_step >= len(q_order):
        await finish_test2(
            user_id,
            callback.message.chat.id
        )
    else:
        await send_test2_question(
            callback.message.chat.id,
            user_id
        )


# -------------------- NATIJALAR --------------------

async def notify_admin_result(
    user_id,
    test_name,
    score,
    total,
    spent_seconds=None
):
    if user_id == ADMIN_ID:
        return

    user = get_user(user_id)
    name = (
        user["full_name"]
        if user and user["full_name"]
        else str(user_id)
    )
    username = (
        f"@{user['username']}"
        if user and user["username"]
        else "username yo‘q"
    )

    percent = round(score / total * 100) if total else 0

    extra = ""
    if spent_seconds is not None:
        mm, ss = divmod(spent_seconds, 60)
        extra = f"\nVaqt: {mm:02d}:{ss:02d}"

    try:
        await bot.send_message(
            ADMIN_ID,
            "📊 Yangi test natijasi\n\n"
            f"Test: {test_name}\n"
            f"Ishtirokchi: {name}\n"
            f"Telegram: {username}\n"
            f"ID: {user_id}\n"
            f"Natija: {score}/{total} ({percent}%){extra}",
        )
    except Exception:
        pass


@dp.message(Command("results"))
async def results_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    old_rows = db.execute(
        """
        SELECT a.user_id, a.score, a.started_at, a.finished_at,
               u.full_name, u.username
        FROM attempts a
        LEFT JOIN users u ON u.user_id=a.user_id
        WHERE a.completed=1
        ORDER BY a.score DESC, a.finished_at ASC
        """
    ).fetchall()

    new_rows = db.execute(
        """
        SELECT a.user_id, a.score, a.started_at, a.finished_at,
               a.question_order, u.full_name, u.username
        FROM attempts2 a
        LEFT JOIN users u ON u.user_id=a.user_id
        WHERE a.completed=1
        ORDER BY a.score DESC,
                 (julianday(a.finished_at)-julianday(a.started_at)) ASC
        """
    ).fetchall()

    parts = ["🏆 TEST NATIJALARI\n"]

    parts.append("\n📘 1-KITOB TESTI")
    if old_rows:
        for i, row in enumerate(old_rows, start=1):
            username = (
                f"@{row['username']}"
                if row["username"]
                else "—"
            )
            parts.append(
                f"{i}. {row['full_name'] or row['user_id']} — "
                f"{row['score']}/{len(QUESTIONS)} — {username}"
            )
    else:
        parts.append("Hozircha natija yo‘q.")

    parts.append("\n📗 2-KITOB TESTI")
    if new_rows:
        for i, row in enumerate(new_rows, start=1):
            username = (
                f"@{row['username']}"
                if row["username"]
                else "—"
            )

            total = (
                len(json.loads(row["question_order"]))
                if row["question_order"]
                else len(TEST2_QUESTIONS)
            )

            start = parse_dt(row["started_at"])
            end = parse_dt(row["finished_at"])

            spent = (
                int((end - start).total_seconds())
                if start and end
                else 0
            )
            spent = min(
                spent,
                TEST2_TIME_LIMIT_MINUTES * 60
            )

            mm, ss = divmod(spent, 60)

            parts.append(
                f"{i}. {row['full_name'] or row['user_id']} — "
                f"{row['score']}/{total} — {mm:02d}:{ss:02d} — "
                f"{username}"
            )
    else:
        parts.append("Hozircha natija yo‘q.")

    result_text = "\n".join(parts)

    for i in range(0, len(result_text), 4000):
        await message.answer(result_text[i:i + 4000])


@dp.message(Command("myresult"))
async def my_result_handler(message: Message):
    uid = message.from_user.id

    old = db.execute(
        """
        SELECT * FROM attempts
        WHERE user_id=? AND completed=1
        """,
        (uid,),
    ).fetchone()

    new = db.execute(
        """
        SELECT * FROM attempts2
        WHERE user_id=? AND completed=1
        """,
        (uid,),
    ).fetchone()

    lines = ["📊 SIZNING NATIJALARINGIZ"]

    if old:
        p = round(
            old["score"] / len(QUESTIONS) * 100
        )
        lines.append(
            f"\n📘 1-kitob: "
            f"{old['score']}/{len(QUESTIONS)} ({p}%)"
        )

    if new:
        total = (
            len(json.loads(new["question_order"]))
            if new["question_order"]
            else len(TEST2_QUESTIONS)
        )
        p = round(new["score"] / total * 100)

        start = parse_dt(new["started_at"])
        end = parse_dt(new["finished_at"])

        spent = (
            int((end - start).total_seconds())
            if start and end
            else 0
        )
        spent = min(
            spent,
            TEST2_TIME_LIMIT_MINUTES * 60
        )

        mm, ss = divmod(spent, 60)

        lines.append(
            f"\n📗 2-kitob: "
            f"{new['score']}/{total} ({p}%) — "
            f"{mm:02d}:{ss:02d}"
        )

    if not old and not new:
        lines.append(
            "\nHali yakunlangan testingiz yo‘q."
        )

    await message.answer("\n".join(lines))


# Sinov paytida faqat testga oid yangi referral-access yozuvlarini tozalash.
# 1- va 2-kitob natijalari o‘chmaydi.
@dp.message(Command("resetaccess"))
async def reset_access_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    db.execute("DELETE FROM test_referrals")
    db.execute("DELETE FROM test_access")
    db.commit()

    await message.answer(
        "✅ Testlarga kirish uchun referal ma’lumotlari tozalandi.\n"
        "Test natijalari saqlandi."
    )


async def main():
    print("ZA Kitobxonlik bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
