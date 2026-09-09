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

# Eski test jadvali o‘z holicha qoladi.
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

# 2-kitob uchun alohida jadval. Savol va variantlar tartibi har foydalanuvchi uchun saqlanadi.
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

# 2-kitob uchun referal alohida hisoblanadi.
db.execute(
    """
    CREATE TABLE IF NOT EXISTS book2_access (
        user_id INTEGER PRIMARY KEY,
        referral_count INTEGER DEFAULT 0,
        unlocked INTEGER DEFAULT 0
    )
    """
)

db.execute(
    """
    CREATE TABLE IF NOT EXISTS book2_referrals (
        invited_user_id INTEGER PRIMARY KEY,
        referrer_id INTEGER NOT NULL,
        confirmed INTEGER DEFAULT 0
    )
    """
)
db.commit()

timeout_tasks = {}


def add_user(user_id, full_name=None, username=None, referrer_id=None):
    existing = db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if existing:
        db.execute(
            "UPDATE users SET full_name=?, username=? WHERE user_id=?",
            (full_name, username, user_id),
        )
    else:
        db.execute(
            "INSERT INTO users (user_id, full_name, username, referrer_id) VALUES (?, ?, ?, ?)",
            (user_id, full_name, username, referrer_id),
        )
    db.commit()


def get_user(user_id):
    return db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()


def mark_verified(user_id):
    db.execute("UPDATE users SET verified=1 WHERE user_id=?", (user_id,))
    db.commit()


def add_referral(referrer_id):
    db.execute("UPDATE users SET referral_count=referral_count+1 WHERE user_id=?", (referrer_id,))
    db.commit()


def mark_reward_given(user_id):
    db.execute("UPDATE users SET reward_given=1 WHERE user_id=?", (user_id,))
    db.commit()


def grant_existing_access(user_id):
    # Asosiy kanalga oldindan kirgan foydalanuvchi qayta referal qilmaydi.
    db.execute(
        "UPDATE users SET verified=1, reward_given=1 WHERE user_id=?",
        (user_id,),
    )
    db.commit()



def ensure_book2_access(user_id):
    db.execute(
        "INSERT OR IGNORE INTO book2_access (user_id, referral_count, unlocked) VALUES (?, 0, 0)",
        (user_id,),
    )
    db.commit()


def get_book2_access(user_id):
    ensure_book2_access(user_id)
    return db.execute("SELECT * FROM book2_access WHERE user_id=?", (user_id,)).fetchone()


def create_book2_pending_referral(invited_user_id, referrer_id, invited_was_existing):
    # 2-kitob uchun faqat botdan avval foydalanmagan YANGI odam sanaladi.
    if invited_was_existing or invited_user_id == referrer_id:
        return False

    existing = db.execute(
        "SELECT * FROM book2_referrals WHERE invited_user_id=?",
        (invited_user_id,),
    ).fetchone()
    if existing:
        return False

    db.execute(
        "INSERT INTO book2_referrals (invited_user_id, referrer_id, confirmed) VALUES (?, ?, 0)",
        (invited_user_id, referrer_id),
    )
    db.commit()
    return True


async def confirm_book2_referral(invited_user_id):
    row = db.execute(
        "SELECT * FROM book2_referrals WHERE invited_user_id=?",
        (invited_user_id,),
    ).fetchone()
    if not row or row["confirmed"]:
        return

    referrer_id = row["referrer_id"]
    ensure_book2_access(referrer_id)

    db.execute(
        "UPDATE book2_referrals SET confirmed=1 WHERE invited_user_id=?",
        (invited_user_id,),
    )
    db.execute(
        "UPDATE book2_access SET referral_count=referral_count+1 WHERE user_id=?",
        (referrer_id,),
    )

    access = db.execute(
        "SELECT * FROM book2_access WHERE user_id=?",
        (referrer_id,),
    ).fetchone()

    if access["referral_count"] >= 1:
        db.execute(
            "UPDATE book2_access SET unlocked=1 WHERE user_id=?",
            (referrer_id,),
        )
    db.commit()

    access = get_book2_access(referrer_id)
    try:
        if access["unlocked"]:
            start_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="📗 2-kitob testini boshlash",
                        callback_data="start_test2"
                    )]
                ]
            )
            await bot.send_message(
                referrer_id,
                "🎉 2-kitob uchun yangi referalingiz tasdiqlandi!\n\n"
                "📗 Endi 2-kitob testini boshlashingiz mumkin.",
                reply_markup=start_keyboard,
            )
    except Exception:
        pass


async def send_book2_referral_post(chat_id, user_id):
    ensure_book2_access(user_id)
    me = await bot.get_me()
    ref_link = f"https://t.me/{me.username}?start=b2_{user_id}"

    caption = (
        "📗 2-KITOB TESTINI OCHISH UCHUN 1 TA YANGI REFERAL KERAK.\n\n"
        "Quyidagi shaxsiy havolangizni hali botimizdan foydalanmagan 1 nafar do‘stingizga yuboring. "
        "U havola orqali botga kirib, 4 ta majburiy kanalga a’zo bo‘lib a’zoligini tasdiqlashi kerak.\n\n"
        "✅ Oldingi kitob uchun qilgan referalingiz bu safar hisoblanmaydi.\n"
        "✅ 2-kitob uchun yangi referal alohida sanaladi.\n\n"
        f"🔗 Sizning 2-kitob referal havolangiz:\n{ref_link}"
    )

    share_url = (
        f"https://t.me/share/url?url={quote(ref_link)}"
        f"&text={quote('Zohida Akademy — Har hafta bir kitob loyihasiga qo‘shiling!')}"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Do‘stga yuborish", url=share_url)],
            [InlineKeyboardButton(text="🔄 2-kitob referalini tekshirish", callback_data="check_referral2")],
        ]
    )

    photo_path = os.path.join(os.path.dirname(__file__), REFERRAL_PHOTO)
    if os.path.exists(photo_path):
        await bot.send_photo(chat_id, FSInputFile(photo_path), caption=caption, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id, caption, reply_markup=keyboard)


def required_channels_keyboard():
    rows = [[InlineKeyboardButton(text=ch["name"], url=ch["link"])] for ch in CHANNELS]
    rows.append([InlineKeyboardButton(text="✅ A’zo bo‘ldim", callback_data="check_channels")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def test_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📘 1-kitob testi", callback_data="start_test")],
            [InlineKeyboardButton(text="📗 2-kitob testi", callback_data="start_test2")],
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


async def give_access(user_id, chat_id):
    user = get_user(user_id)
    if not user:
        return

    if user["reward_given"]:
        await bot.send_message(
            chat_id,
            "✅ Sizda asosiy kanalga kirish huquqi mavjud.\n\n"
            "Quyidan kerakli kitob testini tanlang:",
            reply_markup=test_menu_keyboard(),
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
        reply_markup=test_menu_keyboard(),
    )


async def send_referral_post(chat_id, user_id):
    me = await bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user_id}"

    caption = (
        "📚 HAR HAFTA KITOB O‘QING VA SOVRINLARNI QO‘LGA KIRITING!\n\n"
        "Blogim obunachilari uchun kitobxonlik loyihasi! 🥳\n\n"
        "Birgalikda har hafta kitob o‘qiymiz va o‘qilgan asar bo‘yicha test ishlaymiz. "
        "Eng yuqori natija ko‘rsatgan ishtirokchilar sovrinlarni qo‘lga kiritadi! 🏆\n\n"
        "👇 Konkursda ishtirok etish uchun quyidagi havola orqali qo‘shiling:\n"
        f"{ref_link}"
    )

    share_url = (
        f"https://t.me/share/url?url={quote(ref_link)}"
        f"&text={quote('Kitobxonlik loyihasiga qo‘shiling!')}"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Do‘stga yuborish", url=share_url)],
            [InlineKeyboardButton(text="🔄 Referalni tekshirish", callback_data="check_referral")],
        ]
    )

    photo_path = os.path.join(os.path.dirname(__file__), REFERRAL_PHOTO)
    if os.path.exists(photo_path):
        await bot.send_photo(chat_id, FSInputFile(photo_path), caption=caption, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id, caption, reply_markup=keyboard)


async def after_verification(user_id, chat_id):
    # Agar foydalanuvchi asosiy kanalga avvaldan a’zo bo‘lsa,
    # yangi deploy yoki DB holatidan qat’i nazar qayta referal talab qilinmaydi.
    if await is_final_channel_member(user_id):
        grant_existing_access(user_id)
        await bot.send_message(
            chat_id,
            "✅ Siz loyiha ishtirokchisisiz.\n\nKerakli testni tanlang:",
            reply_markup=test_menu_keyboard(),
        )
        return

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
    book2_referrer_id = None

    invited_was_existing = get_user(user_id) is not None
    invited_was_final_member = await is_final_channel_member(user_id)

    parts = message.text.split(maxsplit=1)
    if len(parts) == 2:
        payload = parts[1].strip()

        if payload.startswith("b2_"):
            try:
                possible_referrer = int(payload[3:])
                if possible_referrer != user_id and get_user(possible_referrer):
                    book2_referrer_id = possible_referrer
            except ValueError:
                pass
        else:
            try:
                possible_referrer = int(payload)
                if possible_referrer != user_id:
                    referrer_id = possible_referrer
            except ValueError:
                pass

    add_user(user_id, message.from_user.full_name, message.from_user.username, referrer_id)

    if book2_referrer_id and not invited_was_existing and not invited_was_final_member:
        create_book2_pending_referral(
            invited_user_id=user_id,
            referrer_id=book2_referrer_id,
            invited_was_existing=False,
        )

    if invited_was_final_member:
        grant_existing_access(user_id)
        db.execute("DELETE FROM book2_referrals WHERE invited_user_id=? AND confirmed=0", (user_id,))
        db.commit()

        await message.answer(
            "📚 Xush kelibsiz! Siz asosiy kanal a’zosisiz.\n\n"
            "📘 1-kitob testi avvalgi tartibda ishlaydi.\n"
            "📗 2-kitob testi uchun 1 ta yangi referal talab qilinadi.\n\n"
            "Kerakli testni tanlang:",
            reply_markup=test_menu_keyboard(),
        )
        return

    if not await is_member_of_required_channels(user_id):
        await message.answer(
            "Assalomu alaykum! Konkursda qatnashish uchun avval quyidagi 4 ta kanalga a’zo bo‘ling.",
            reply_markup=required_channels_keyboard(),
        )
        return

    user = get_user(user_id)
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
                    f"🎉 Yangi referal tasdiqlandi!\nReferallaringiz: {ref_user['referral_count']}/{REFERRAL_TARGET}",
                )
            except Exception:
                pass

    await confirm_book2_referral(user_id)
    await after_verification(user_id, message.chat.id)


@dp.callback_query(F.data == "check_channels")
async def check_channels_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    add_user(user_id, callback.from_user.full_name, callback.from_user.username, None)

    if await is_final_channel_member(user_id):
        grant_existing_access(user_id)
        db.execute("DELETE FROM book2_referrals WHERE invited_user_id=? AND confirmed=0", (user_id,))
        db.commit()

        await callback.answer("✅ Siz avvaldan loyiha ishtirokchisisiz!")
        await bot.send_message(
            callback.message.chat.id,
            "Kerakli testni tanlang:",
            reply_markup=test_menu_keyboard(),
        )
        return

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
                    f"🎉 Yangi referal tasdiqlandi!\nReferallaringiz: {ref_user['referral_count']}/{REFERRAL_TARGET}",
                )
            except Exception:
                pass

    await confirm_book2_referral(user_id)

    await callback.answer("✅ A’zolik tasdiqlandi!")
    await after_verification(user_id, callback.message.chat.id)


@dp.callback_query(F.data == "check_referral")
async def check_referral_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    if await is_final_channel_member(user_id):
        grant_existing_access(user_id)
        await callback.answer("✅ Sizda kirish huquqi bor!")
        await bot.send_message(
            callback.message.chat.id,
            "Kerakli testni tanlang:",
            reply_markup=test_menu_keyboard(),
        )
        return

    user = get_user(user_id)
    if not user:
        await callback.answer("Avval /start bosing.", show_alert=True)
        return

    if user["referral_count"] >= REFERRAL_TARGET:
        await callback.answer("✅ Referal sharti bajarildi!")
        await give_access(user_id, callback.message.chat.id)
    else:
        await callback.answer(
            f"Hozircha {user['referral_count']}/{REFERRAL_TARGET} ta referal.",
            show_alert=True,
        )


@dp.callback_query(F.data == "check_referral2")
async def check_referral2_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    access = get_book2_access(user_id)

    if access["unlocked"]:
        await callback.answer("✅ 2-kitob testi ochildi!")
        start_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="📗 2-kitob testini boshlash",
                    callback_data="start_test2"
                )]
            ]
        )
        await bot.send_message(
            callback.message.chat.id,
            "📗 2-kitob uchun referal sharti bajarildi.\n\n"
            "Quyidagi tugmani bosib testni boshlang.",
            reply_markup=start_keyboard,
        )
    else:
        await callback.answer(
            f"📗 2-kitob referali: {access['referral_count']}/1\n"
            "Hali 1 ta yangi odamning a’zoligi tasdiqlanishi kerak.",
            show_alert=True,
        )


# -------------------- 1-KITOB TESTI (ESKI TEST) --------------------

def question_keyboard(question_index):
    labels = ["A", "B", "C", "D"]
    rows = []
    for i, option in enumerate(QUESTIONS[question_index]["options"]):
        rows.append(
            [InlineKeyboardButton(
                text=f"{labels[i]}) {option}",
                callback_data=f"answer:{question_index}:{i}",
            )]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_question(chat_id, question_index):
    q = QUESTIONS[question_index]
    await bot.send_message(chat_id, q["q"], reply_markup=question_keyboard(question_index))


@dp.callback_query(F.data == "start_test")
async def start_test_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    if not await is_final_channel_member(user_id):
        await callback.answer("Avval kitobxonlik kanaliga kiring.", show_alert=True)
        return

    grant_existing_access(user_id)

    attempt = db.execute("SELECT * FROM attempts WHERE user_id=?", (user_id,)).fetchone()
    if attempt and attempt["completed"]:
        await callback.answer("Siz 1-kitob testini avval ishlagansiz.", show_alert=True)
        return

    if not attempt:
        db.execute(
            "INSERT INTO attempts (user_id, current_question, score, started_at, completed) VALUES (?, 0, 0, ?, 0)",
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
    attempt = db.execute("SELECT * FROM attempts WHERE user_id=?", (user_id,)).fetchone()

    if not attempt or attempt["completed"]:
        await callback.answer("Test faol emas.", show_alert=True)
        return

    _, q_index_text, answer_text = callback.data.split(":")
    q_index = int(q_index_text)
    selected = int(answer_text)

    if q_index != attempt["current_question"]:
        await callback.answer("Bu savolga javob allaqachon qabul qilingan.", show_alert=True)
        return

    score = attempt["score"] + (1 if selected == QUESTIONS[q_index]["correct"] else 0)
    next_question = q_index + 1

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    if next_question >= len(QUESTIONS):
        finished = datetime.now(timezone.utc)
        db.execute(
            "UPDATE attempts SET current_question=?, score=?, finished_at=?, completed=1 WHERE user_id=?",
            (next_question, score, finished.isoformat(), user_id),
        )
        db.commit()

        percent = round(score / len(QUESTIONS) * 100)
        await callback.answer("Javob qabul qilindi.")
        await bot.send_message(
            callback.message.chat.id,
            f"✅ 1-kitob testi yakunlandi!\n\nNatijangiz: {score}/{len(QUESTIONS)}\nFoiz: {percent}%\n\nNatijangiz saqlandi.",
            reply_markup=test_menu_keyboard(),
        )
        await notify_admin_result(user_id, "1-kitob", score, len(QUESTIONS))
        return

    db.execute(
        "UPDATE attempts SET current_question=?, score=? WHERE user_id=?",
        (next_question, score, user_id),
    )
    db.commit()

    await callback.answer("Javob qabul qilindi.")
    await send_question(callback.message.chat.id, next_question)


# -------------------- 2-KITOB TESTI: ARALASH + 20 DAQIQA --------------------

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
    return max(0, int(TEST2_TIME_LIMIT_MINUTES * 60 - elapsed))


def test2_keyboard(step, q_idx, option_order):
    labels = ["A", "B", "C", "D"]
    rows = []
    for displayed_pos, original_opt_idx in enumerate(option_order):
        option_text = TEST2_QUESTIONS[q_idx]["options"][original_opt_idx]
        rows.append(
            [InlineKeyboardButton(
                text=f"{labels[displayed_pos]}) {option_text}",
                callback_data=f"t2answer:{step}:{displayed_pos}",
            )]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_test2_question(chat_id, user_id):
    attempt = db.execute("SELECT * FROM attempts2 WHERE user_id=?", (user_id,)).fetchone()
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
    seconds_left = test2_seconds_left(attempt)
    mm, ss = divmod(seconds_left, 60)

    await bot.send_message(
        chat_id,
        f"📗 2-kitob testi\n"
        f"❓ Savol {step + 1}/{len(q_order)}\n"
        f"⏳ Qolgan vaqt: {mm:02d}:{ss:02d}\n\n"
        f"{q['q']}",
        reply_markup=test2_keyboard(step, q_idx, option_orders[str(q_idx)]),
    )


async def finish_test2(user_id, chat_id, timed_out=False):
    attempt = db.execute("SELECT * FROM attempts2 WHERE user_id=?", (user_id,)).fetchone()
    if not attempt or attempt["completed"]:
        return

    finished = datetime.now(timezone.utc)
    db.execute(
        "UPDATE attempts2 SET finished_at=?, completed=1 WHERE user_id=?",
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
    await notify_admin_result(user_id, "2-kitob", score, total, spent)

    task = timeout_tasks.pop(user_id, None)
    if task and task is not asyncio.current_task():
        task.cancel()


async def timeout_test2(user_id, chat_id, seconds):
    try:
        await asyncio.sleep(seconds)
        attempt = db.execute("SELECT * FROM attempts2 WHERE user_id=?", (user_id,)).fetchone()
        if attempt and not attempt["completed"]:
            await finish_test2(user_id, chat_id, timed_out=True)
    except asyncio.CancelledError:
        pass


@dp.callback_query(F.data == "start_test2")
async def start_test2_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    if not await is_final_channel_member(user_id):
        await callback.answer("Avval kitobxonlik kanaliga kiring.", show_alert=True)
        return

    grant_existing_access(user_id)

    attempt = db.execute("SELECT * FROM attempts2 WHERE user_id=?", (user_id,)).fetchone()

    if attempt and attempt["completed"]:
        await callback.answer("Siz 2-kitob testini avval ishlagansiz.", show_alert=True)
        return

    access = get_book2_access(user_id)
    if not access["unlocked"]:
        await callback.answer("📗 2-kitob uchun 1 ta yangi referal kerak.", show_alert=True)
        await send_book2_referral_post(callback.message.chat.id, user_id)
        return

    if not attempt:
        q_order, option_orders = make_test2_attempt()
        now = datetime.now(timezone.utc).isoformat()
        db.execute(
            """
            INSERT INTO attempts2
            (user_id, current_question, score, started_at, completed, question_order, option_orders)
            VALUES (?, 0, 0, ?, 0, ?, ?)
            """,
            (user_id, now, json.dumps(q_order), json.dumps(option_orders)),
        )
        db.commit()
        attempt = db.execute("SELECT * FROM attempts2 WHERE user_id=?", (user_id,)).fetchone()

    left = test2_seconds_left(attempt)
    if left <= 0:
        await callback.answer("Test vaqti tugagan.", show_alert=True)
        await finish_test2(user_id, callback.message.chat.id, timed_out=True)
        return

    old_task = timeout_tasks.pop(user_id, None)
    if old_task:
        old_task.cancel()
    timeout_tasks[user_id] = asyncio.create_task(timeout_test2(user_id, callback.message.chat.id, left))

    await callback.answer()
    await bot.send_message(
        callback.message.chat.id,
        "📗 2-kitob testi boshlandi!\n\n"
        "🔀 30 ta savolning tartibi har bir ishtirokchi uchun aralashtiriladi.\n"
        "🔀 A/B/C/D javob variantlari ham har savolda aralashtiriladi.\n"
        f"⏳ Umumiy vaqt: {TEST2_TIME_LIMIT_MINUTES} daqiqa.\n"
        "↩️ Oldingi savolga qaytib bo‘lmaydi.\n"
        "✅ Har savolga faqat bir marta javob beriladi.",
    )
    await send_test2_question(callback.message.chat.id, user_id)


@dp.callback_query(F.data.startswith("t2answer:"))
async def test2_answer_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    attempt = db.execute("SELECT * FROM attempts2 WHERE user_id=?", (user_id,)).fetchone()

    if not attempt or attempt["completed"]:
        await callback.answer("2-kitob testi faol emas.", show_alert=True)
        return

    if test2_seconds_left(attempt) <= 0:
        await callback.answer("⏰ Vaqt tugadi.", show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await finish_test2(user_id, callback.message.chat.id, timed_out=True)
        return

    _, step_text, displayed_pos_text = callback.data.split(":")
    step = int(step_text)
    displayed_pos = int(displayed_pos_text)

    if step != attempt["current_question"]:
        await callback.answer("Bu savolga javob allaqachon qabul qilingan.", show_alert=True)
        return

    q_order = json.loads(attempt["question_order"])
    option_orders = json.loads(attempt["option_orders"])

    q_idx = q_order[step]
    original_opt_idx = option_orders[str(q_idx)][displayed_pos]
    correct = TEST2_QUESTIONS[q_idx]["correct"]

    score = attempt["score"] + (1 if original_opt_idx == correct else 0)
    next_step = step + 1

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    db.execute(
        "UPDATE attempts2 SET current_question=?, score=? WHERE user_id=?",
        (next_step, score, user_id),
    )
    db.commit()

    await callback.answer("Javob qabul qilindi.")

    if next_step >= len(q_order):
        await finish_test2(user_id, callback.message.chat.id)
    else:
        await send_test2_question(callback.message.chat.id, user_id)


async def notify_admin_result(user_id, test_name, score, total, spent_seconds=None):
    if user_id == ADMIN_ID:
        return

    user = get_user(user_id)
    name = user["full_name"] if user and user["full_name"] else str(user_id)
    username = f"@{user['username']}" if user and user["username"] else "username yo‘q"
    percent = round(score / total * 100) if total else 0

    extra = ""
    if spent_seconds is not None:
        mm, ss = divmod(spent_seconds, 60)
        extra = f"\nVaqt: {mm:02d}:{ss:02d}"

    try:
        await bot.send_message(
            ADMIN_ID,
            f"📊 Yangi test natijasi\n\n"
            f"Test: {test_name}\n"
            f"Ishtirokchi: {name}\n"
            f"Telegram: {username}\n"
            f"ID: {user_id}\n"
            f"Natija: {score}/{total} ({percent}%){extra}",
        )
    except Exception:
        pass


@dp.message(Command("tests"))
async def tests_handler(message: Message):
    if await is_final_channel_member(message.from_user.id):
        grant_existing_access(message.from_user.id)
        await message.answer("📚 Kerakli testni tanlang:", reply_markup=test_menu_keyboard())
    else:
        await message.answer("Avval /start orqali loyiha shartlarini bajaring.")


@dp.message(Command("resetbook2"))
async def reset_book2_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    db.execute("DELETE FROM book2_referrals")
    db.execute("DELETE FROM book2_access")
    db.execute("DELETE FROM attempts2")
    db.commit()

    await message.answer(
        "✅ 2-kitob bo‘yicha referal va test ma’lumotlari tozalandi.\n"
        "1-kitob natijalari va foydalanuvchilar bazasi saqlandi."
    )


@dp.message(Command("results"))
async def results_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    old_rows = db.execute(
        """
        SELECT a.user_id, a.score, a.started_at, a.finished_at, u.full_name, u.username
        FROM attempts a
        LEFT JOIN users u ON u.user_id=a.user_id
        WHERE a.completed=1
        ORDER BY a.score DESC, a.finished_at ASC
        """
    ).fetchall()

    new_rows = db.execute(
        """
        SELECT a.user_id, a.score, a.started_at, a.finished_at, a.question_order, u.full_name, u.username
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
            username = f"@{row['username']}" if row["username"] else "—"
            parts.append(f"{i}. {row['full_name'] or row['user_id']} — {row['score']}/{len(QUESTIONS)} — {username}")
    else:
        parts.append("Hozircha natija yo‘q.")

    parts.append("\n📗 2-KITOB TESTI")
    if new_rows:
        for i, row in enumerate(new_rows, start=1):
            username = f"@{row['username']}" if row["username"] else "—"
            total = len(json.loads(row["question_order"])) if row["question_order"] else len(TEST2_QUESTIONS)
            start = parse_dt(row["started_at"])
            end = parse_dt(row["finished_at"])
            spent = int((end - start).total_seconds()) if start and end else 0
            spent = min(spent, TEST2_TIME_LIMIT_MINUTES * 60)
            mm, ss = divmod(spent, 60)
            parts.append(f"{i}. {row['full_name'] or row['user_id']} — {row['score']}/{total} — {mm:02d}:{ss:02d} — {username}")
    else:
        parts.append("Hozircha natija yo‘q.")

    text = "\n".join(parts)
    for i in range(0, len(text), 4000):
        await message.answer(text[i:i+4000])


@dp.message(Command("myresult"))
async def my_result_handler(message: Message):
    uid = message.from_user.id
    old = db.execute("SELECT * FROM attempts WHERE user_id=? AND completed=1", (uid,)).fetchone()
    new = db.execute("SELECT * FROM attempts2 WHERE user_id=? AND completed=1", (uid,)).fetchone()

    lines = ["📊 SIZNING NATIJALARINGIZ"]
    if old:
        p = round(old["score"] / len(QUESTIONS) * 100)
        lines.append(f"\n📘 1-kitob: {old['score']}/{len(QUESTIONS)} ({p}%)")
    if new:
        total = len(json.loads(new["question_order"])) if new["question_order"] else len(TEST2_QUESTIONS)
        p = round(new["score"] / total * 100)
        start = parse_dt(new["started_at"])
        end = parse_dt(new["finished_at"])
        spent = int((end - start).total_seconds()) if start and end else 0
        spent = min(spent, TEST2_TIME_LIMIT_MINUTES * 60)
        mm, ss = divmod(spent, 60)
        lines.append(f"\n📗 2-kitob: {new['score']}/{total} ({p}%) — {mm:02d}:{ss:02d}")

    if not old and not new:
        lines.append("\nHali yakunlangan testingiz yo‘q.")

    await message.answer("\n".join(lines))


async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
