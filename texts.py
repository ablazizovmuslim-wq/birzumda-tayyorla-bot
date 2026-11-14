"""Bot matnlari: o'zbekcha (uz), ruscha (ru), inglizcha (en).

Matn ichida {e[kalit]} — premium emoji (bot.py dagi pe() orqali qo'yiladi),
{nom} — o'zgaruvchilar (summa, raqam va h.k.).
"""

LANGS = {"uz": "🇺🇿 O'zbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
DEFAULT_LANG = "uz"

# ------------------------------------------------------------------ menyu tugmalari
BTN = {
    "app":      {"uz": "✨ Buyurtmalar uchun", "ru": "✨ Для заказов", "en": "✨ For orders"},
    "order":    {"uz": "🛒 Buyurtma berish", "ru": "🛒 Заказать", "en": "🛒 Place an order"},
    "prices":   {"uz": "💰 Narxlar", "ru": "💰 Цены", "en": "💰 Prices"},
    "samples":  {"uz": "🎨 Namunalar", "ru": "🎨 Примеры", "en": "🎨 Samples"},
    "bonus":    {"uz": "🎁 Bonus va aksiyalar", "ru": "🎁 Бонусы и акции", "en": "🎁 Bonuses & promos"},
    "orders":   {"uz": "📦 Buyurtmalarim", "ru": "📦 Мои заказы", "en": "📦 My orders"},
    "contact":  {"uz": "📞 Aloqa", "ru": "📞 Связь", "en": "📞 Contact"},
    "lang":     {"uz": "🌐 Til", "ru": "🌐 Язык", "en": "🌐 Language"},
    "info":     {"uz": "📖 Ma'lumot", "ru": "📖 Информация", "en": "📖 Info"},
    "channel":  {"uz": "📢 Kanalimiz", "ru": "📢 Наш канал", "en": "📢 Our channel"},
    "subscribe": {"uz": "📢 Kanalga obuna bo'lish", "ru": "📢 Подписаться на канал", "en": "📢 Subscribe to the channel"},
    # inline tugmalar
    "back":     {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"},
    "see_samples": {"uz": "🎨 Namunalarni ko'rish", "ru": "🎨 Посмотреть примеры", "en": "🎨 See samples"},
    "skip":     {"uz": "⏭ O'tkazib yuborish", "ru": "⏭ Пропустить", "en": "⏭ Skip"},
    "files_done": {"uz": "✅ Tayyor / O'tkazish", "ru": "✅ Готово / Пропустить", "en": "✅ Done / Skip"},
    "ready":    {"uz": "✅ Tayyor", "ru": "✅ Готово", "en": "✅ Done"},
    "confirm":  {"uz": "✅ Tasdiqlash", "ru": "✅ Подтвердить", "en": "✅ Confirm"},
    "restart":  {"uz": "✏️ Qaytadan", "ru": "✏️ Заново", "en": "✏️ Start over"},
    "cancel":   {"uz": "❌ Bekor qilish", "ru": "❌ Отменить", "en": "❌ Cancel"},
    "promo":    {"uz": "🎟 Promokod", "ru": "🎟 Промокод", "en": "🎟 Promo code"},
    "promo_off": {"uz": "🎟 Promokodni o'chirish", "ru": "🎟 Убрать промокод", "en": "🎟 Remove promo code"},
    "bonus_use": {"uz": "💰 Bonus ({sum})", "ru": "💰 Бонус ({sum})", "en": "💰 Bonus ({sum})"},
    "bonus_off": {"uz": "💰 Bonusni olib tashlash", "ru": "💰 Без бонуса", "en": "💰 Don't use bonus"},
    "share":    {"uz": "📤 Do'stlarga ulashish", "ru": "📤 Поделиться с друзьями", "en": "📤 Share with friends"},
    "shop":     {"uz": "📦 Tayyor ishlar", "ru": "📦 Готовые работы", "en": "📦 Ready works"},
    "group":    {"uz": "👥 Guruh uchun", "ru": "👥 Для группы", "en": "👥 For a group"},
    "group_off": {"uz": "👥 Guruhni bekor qilish", "ru": "👥 Без группы", "en": "👥 Not a group"},
}

DEADLINES = {
    "normal": {"uz": "Oddiy muddat", "ru": "Обычный срок", "en": "Standard time"},
    "urgent": {"uz": "⚡ Shoshilinch (+{pct}%)", "ru": "⚡ Срочно (+{pct}%)", "en": "⚡ Urgent (+{pct}%)"},
}

STATUS = {
    "quote":    {"uz": "💬 Narx kelishilmoqda", "ru": "💬 Согласуем цену", "en": "💬 Agreeing on price"},
    "new":      {"uz": "🕐 To'lov kutilmoqda", "ru": "🕐 Ожидает оплаты", "en": "🕐 Awaiting payment"},
    "paid":     {"uz": "🧾 Chek tekshirilmoqda", "ru": "🧾 Проверяем чек", "en": "🧾 Checking receipt"},
    "work":     {"uz": "🛠 Tayyorlanmoqda", "ru": "🛠 В работе", "en": "🛠 In progress"},
    "done":     {"uz": "✅ Topshirildi", "ru": "✅ Сдан", "en": "✅ Delivered"},
    "rejected": {"uz": "❌ Rad etildi", "ru": "❌ Отклонён", "en": "❌ Rejected"},
}

CURRENCY = {"uz": "so'm", "ru": "сум", "en": "UZS"}
NEGOTIABLE = {"uz": "kelishiladi", "ru": "договорная", "en": "negotiable"}
FROM = {"uz": "{p}dan", "ru": "от {p}", "en": "from {p}"}

# ------------------------------------------------------------------ katalog tarjimasi
TURTLE = {"uz": "🐢 Toshbaqa o'qituvchi", "ru": "🐢 Черепаха-учитель", "en": "🐢 Turtle teacher"}
TURTLE_LONG = {"uz": "🐢 Toshbaqa o'qituvchi — slaydda gapirib, mavzuni tushuntiradi",
               "ru": "🐢 Черепаха-учитель — говорит на слайдах и объясняет тему",
               "en": "🐢 Turtle teacher — talks on the slides and explains the topic"}

CAT_TR = {
    "ru": {
        "s": {"title": "🎓 Для студентов", "services": {
            "taqdimot": {"name": "Слайды (презентация)", "packages": {
                "start": ("Start", "10–12 слайдов, современный дизайн, 3 часа"),
                "pro": ("Professional", "15–20 слайдов, анимация, диаграммы, 6 часов"),
                "premium": ("Premium", "20–25 слайдов, Morph, неон, текст речи, 12 часов")}},
            "mustaqil": {"name": "Самостоятельная работа", "desc": "В Word, с красивой обложкой"},
            "kurs": {"name": "Курсовая работа", "desc": "План, главы, заключение, список литературы"},
            "maqola": {"name": "Статья / тезисы", "desc": "Научная статья или тезисы конференции"},
            "amaliy": {"name": "Практическая / лабораторная", "desc": "По условию задания, с отчётом"},
            "referat": {"name": "Реферат", "desc": "План, текст, литература, красивая обложка"},
            "portfolio": {"name": "Портфолио", "desc": "Портфолио студента и резюме"},
            "boshqa": {"name": "Другое — напишите сами", "desc": "Напишите, что нужно, цену согласуем"},
        }},
        "t": {"title": "👩‍🏫 Для преподавателей", "services": {
            "dars": {"name": "Презентация (слайды)", "packages": {
                "start": ("Start", "12–15 слайдов, для открытого урока"),
                "pro": ("Professional", "15–20 слайдов, анимация, диаграммы, 🐢 Черепаха-учитель"),
                "premium": ("Premium", "20–25 слайдов, Morph, 🐢 Черепаха-учитель, текст речи, видео")}},
            "portfolio": {"name": "Портфолио-презентация (с фото)", "packages": {
                "start": ("Start", "15–20 слайдов, фото, достижения, сертификаты"),
                "pro": ("Professional", "20–25 слайдов, анимация, фотоколлажи, 🐢 Черепаха-учитель"),
                "premium": ("Premium", "25–30 слайдов, Morph, видео и музыка, текст речи, 🐢 Черепаха-учитель")}},
            "oum": {"name": "Учебно-методический комплекс", "desc": "Лекции, практические занятия, тесты"},
            "ishlanma": {"name": "Разработка урока", "desc": "План открытого или обычного урока"},
            "maqola": {"name": "Научная статья / тезисы", "desc": "Для журнала или конференции"},
            "test": {"name": "Тесты и задания", "desc": "Тесты, вопросы, кейсы по предмету"},
            "tadbir": {"name": "Презентация мероприятия", "desc": "Конференция, мероприятие, отчёт"},
            "boshqa": {"name": "Другое — напишите сами", "desc": "Напишите, что нужно, цену согласуем"},
        }},
    },
    "en": {
        "s": {"title": "🎓 For students", "services": {
            "taqdimot": {"name": "Slides (presentation)", "packages": {
                "start": ("Start", "10–12 slides, modern design, 3 hours"),
                "pro": ("Professional", "15–20 slides, animation, charts, 6 hours"),
                "premium": ("Premium", "20–25 slides, Morph, neon design, speech text, 12 hours")}},
            "mustaqil": {"name": "Independent work", "desc": "In Word, with a nice cover page"},
            "kurs": {"name": "Term paper", "desc": "Outline, chapters, conclusion, references"},
            "maqola": {"name": "Article / abstract", "desc": "Research article or conference abstract"},
            "amaliy": {"name": "Practical / lab work", "desc": "Based on your task, with a report"},
            "referat": {"name": "Essay (referat)", "desc": "Outline, text, references, nice cover"},
            "portfolio": {"name": "Portfolio", "desc": "Student portfolio and CV"},
            "boshqa": {"name": "Other — describe it", "desc": "Tell us what you need, we'll agree on the price"},
        }},
        "t": {"title": "👩‍🏫 For teachers", "services": {
            "dars": {"name": "Presentation (slides)", "packages": {
                "start": ("Start", "12–15 slides, for an open lesson"),
                "pro": ("Professional", "15–20 slides, animation, charts, 🐢 Turtle teacher"),
                "premium": ("Premium", "20–25 slides, Morph, 🐢 Turtle teacher, speech text, video")}},
            "portfolio": {"name": "Portfolio presentation (with photos)", "packages": {
                "start": ("Start", "15–20 slides, photos, achievements, certificates"),
                "pro": ("Professional", "20–25 slides, animation, photo collages, 🐢 Turtle teacher"),
                "premium": ("Premium", "25–30 slides, Morph, video and music, speech text, 🐢 Turtle teacher")}},
            "oum": {"name": "Teaching materials set (O'UM)", "desc": "Lectures, practical classes, tests"},
            "ishlanma": {"name": "Lesson plan", "desc": "Open lesson or everyday lesson plan"},
            "maqola": {"name": "Research article / abstract", "desc": "For a journal or conference"},
            "test": {"name": "Tests and tasks", "desc": "Subject tests, questions, case studies"},
            "tadbir": {"name": "Event presentation", "desc": "Conference, event, report"},
            "boshqa": {"name": "Other — describe it", "desc": "Tell us what you need, we'll agree on the price"},
        }},
    },
}

# ------------------------------------------------------------------ xabarlar
TX = {
    "pick_lang": {
        "uz": "{e[globe]} <b>Tilni tanlang</b> · Выберите язык · Choose language",
        "ru": "{e[globe]} <b>Выберите язык</b> · Tilni tanlang · Choose language",
        "en": "{e[globe]} <b>Choose language</b> · Tilni tanlang · Выберите язык"},
    "lang_set": {
        "uz": "{e[ok]} Til o'zgardi: <b>O'zbekcha</b>",
        "ru": "{e[ok]} Язык изменён: <b>Русский</b>",
        "en": "{e[ok]} Language changed: <b>English</b>"},
    "welcome": {
        "uz": ("Assalomu alaykum, <b>{name}</b>! {e[hi]}\n\n"
               "{e[star]} <b>{bot}</b> — o'qish va ish uchun kerakli ishlarni tez, chiroyli va o'z vaqtida tayyorlab beradi.\n\n"
               "{e[bot]} <b>Bot nima qila oladi?</b>\n"
               "{e[student]} <b>Talabalarga:</b> slayd, mustaqil ish, kurs ishi, maqola, amaliy ish, referat, portfolio\n"
               "{e[teacher]} <b>Ustozlarga:</b> taqdimot, portfolio, o'quv-uslubiy majmua, dars ishlanmasi, maqola, testlar\n"
               "{e[edit]} Ro'yxatda yo'q bo'lsa — o'zingiz yozasiz\n\n"
               "{e[heart]} <b>Siz nima olasiz?</b>\n"
               "{e[ok]} Tayyor fayl (PPTX / Word / PDF) shu chatga keladi\n"
               "{e[image]} Professional dizayn · 🐢 Toshbaqa o'qituvchi\n"
               "{e[fire]} O'z vaqtida va bepul tuzatish\n\n"
               "{e[orders]} <b>Qanday ishlaydi?</b>\n"
               "{e[n1]} «✨ Buyurtmalar uchun» → talaba yoki ustoz\n"
               "{e[n2]} Ishni tanlab, mavzuni yozasiz\n"
               "{e[n3]} To'lov qilib, chekni yuborasiz\n"
               "{e[n4]} Tayyor ish shu yerga keladi\n\n"
               "{e[contact]} Admin: {contact}\n\n"
               "Boshlash uchun menyudan tanlang {e[down]}"),
        "ru": ("Ассалому алайкум, <b>{name}</b>! {e[hi]}\n\n"
               "{e[star]} <b>{bot}</b> — быстро, красиво и вовремя готовит работы для учёбы и работы.\n\n"
               "{e[bot]} <b>Что умеет бот?</b>\n"
               "{e[student]} <b>Студентам:</b> слайды, самостоятельная, курсовая, статья, практическая, реферат, портфолио\n"
               "{e[teacher]} <b>Преподавателям:</b> презентации, портфолио, УМК, разработки уроков, статьи, тесты\n"
               "{e[edit]} Нет в списке — напишите сами\n\n"
               "{e[heart]} <b>Что вы получите?</b>\n"
               "{e[ok]} Готовый файл (PPTX / Word / PDF) прямо в чат\n"
               "{e[image]} Профессиональный дизайн · 🐢 Черепаха-учитель\n"
               "{e[fire]} Вовремя и бесплатные правки\n\n"
               "{e[orders]} <b>Как это работает?</b>\n"
               "{e[n1]} «✨ Для заказов» → студент или преподаватель\n"
               "{e[n2]} Выбираете работу и пишете тему\n"
               "{e[n3]} Оплачиваете и отправляете чек\n"
               "{e[n4]} Готовая работа приходит сюда\n\n"
               "{e[contact]} Админ: {contact}\n\n"
               "Выберите в меню {e[down]}"),
        "en": ("Hello, <b>{name}</b>! {e[hi]}\n\n"
               "{e[star]} <b>{bot}</b> makes the work you need for study and teaching — fast, beautiful and on time.\n\n"
               "{e[bot]} <b>What can the bot do?</b>\n"
               "{e[student]} <b>For students:</b> slides, independent work, term paper, article, lab work, essay, portfolio\n"
               "{e[teacher]} <b>For teachers:</b> presentations, portfolio, teaching materials, lesson plans, articles, tests\n"
               "{e[edit]} Not on the list — just describe it\n\n"
               "{e[heart]} <b>What you get</b>\n"
               "{e[ok]} A ready file (PPTX / Word / PDF) right in this chat\n"
               "{e[image]} Professional design · 🐢 Turtle teacher\n"
               "{e[fire]} On time, free revisions\n\n"
               "{e[orders]} <b>How it works</b>\n"
               "{e[n1]} «✨ For orders» → student or teacher\n"
               "{e[n2]} Pick the work and write the topic\n"
               "{e[n3]} Pay and send the receipt\n"
               "{e[n4]} The finished work arrives here\n\n"
               "{e[contact]} Admin: {contact}\n\n"
               "Choose from the menu {e[down]}")},
    "ref_welcome": {
        "uz": "{e[heart]} Siz do'stingiz taklifi bilan keldingiz!\nBirinchi buyurtmangizga <b>{sum} chegirma</b> avtomatik qo'llanadi.",
        "ru": "{e[heart]} Вы пришли по приглашению друга!\nНа первый заказ автоматически действует <b>скидка {sum}</b>.",
        "en": "{e[heart]} You came by a friend's invite!\nA <b>{sum} discount</b> is applied to your first order automatically."},
    "ref_joined": {
        "uz": "{e[heart]} Havolangiz orqali <b>{name}</b> botga qo'shildi!\nU birinchi buyurtmasini to'lagach, sizga <b>{sum}</b> bonus tushadi {e[money]}",
        "ru": "{e[heart]} По вашей ссылке в бот пришёл <b>{name}</b>!\nКогда он оплатит первый заказ, вам начислится <b>{sum}</b> бонуса {e[money]}",
        "en": "{e[heart]} <b>{name}</b> joined the bot with your link!\nWhen they pay for their first order, you get a <b>{sum}</b> bonus {e[money]}"},
    "ref_reward": {
        "uz": "{e[money]} <b>+{sum} bonus!</b>\nDo'stingiz {name} birinchi buyurtmasini to'ladi.\nBalans: <b>{bal}</b>",
        "ru": "{e[money]} <b>+{sum} бонуса!</b>\nВаш друг {name} оплатил первый заказ.\nБаланс: <b>{bal}</b>",
        "en": "{e[money]} <b>+{sum} bonus!</b>\nYour friend {name} paid for their first order.\nBalance: <b>{bal}</b>"},
    "bonus_gift": {
        "uz": "{e[heart]} Sizga <b>{sum}</b> bonus berildi!",
        "ru": "{e[heart]} Вам начислено <b>{sum}</b> бонуса!",
        "en": "{e[heart]} You received a <b>{sum}</b> bonus!"},
    "who_for": {"uz": "Kim uchun buyurtma? 👇", "ru": "Для кого заказ? 👇", "en": "Who is the order for? 👇"},
    "restart": {"uz": "Qaytadan boshlaymiz. Kim uchun buyurtma? 👇", "ru": "Начнём заново. Для кого заказ? 👇",
                "en": "Let's start over. Who is the order for? 👇"},
    "cancelled": {"uz": "Buyurtma bekor qilindi.", "ru": "Заказ отменён.", "en": "Order cancelled."},
    "cancel_cmd": {"uz": "Bekor qilindi.", "ru": "Отменено.", "en": "Cancelled."},
    "prices_footer": {
        "uz": "⚡ Shoshilinch buyurtma: <b>+{pct}%</b>\n🔁 Tuzatishlar bepul\n🐢 Toshbaqa o'qituvchi: ustozlarga Pro va Premium'da, talabalarga +{turtle}\n\nBuyurtma berish uchun tugmani bosing 👇",
        "ru": "⚡ Срочный заказ: <b>+{pct}%</b>\n🔁 Правки бесплатно\n🐢 Черепаха-учитель: преподавателям в Pro и Premium, студентам +{turtle}\n\nНажмите кнопку, чтобы заказать 👇",
        "en": "⚡ Urgent order: <b>+{pct}%</b>\n🔁 Free revisions\n🐢 Turtle teacher: included for teachers in Pro & Premium, +{turtle} for students\n\nTap the button to order 👇"},
    "samples_soon": {"uz": "Namunalar tez orada qo'shiladi 🙂", "ru": "Примеры скоро появятся 🙂", "en": "Samples coming soon 🙂"},
    "samples_intro": {
        "uz": "Mana ishlarimdan namunalar 👇\n<i>Animatsiyalar kompyuterdagi PowerPoint'da to'liq ko'rinadi.</i>",
        "ru": "Вот примеры моих работ 👇\n<i>Анимации полностью видны в PowerPoint на компьютере.</i>",
        "en": "Here are samples of my work 👇\n<i>Animations play fully in PowerPoint on a computer.</i>"},
    "no_orders": {
        "uz": "Sizda hali buyurtma yo'q. «✨ Buyurtmalar uchun» tugmasini bosing.",
        "ru": "У вас пока нет заказов. Нажмите «✨ Для заказов».",
        "en": "You have no orders yet. Tap «✨ For orders»."},
    "contact": {"uz": "Savollar bo'lsa yozing: {contact}", "ru": "По вопросам пишите: {contact}",
                "en": "Questions? Write to: {contact}"},
    "choose_service": {"uz": "<b>{title}</b>\nXizmatni tanlang 👇", "ru": "<b>{title}</b>\nВыберите услугу 👇",
                       "en": "<b>{title}</b>\nChoose a service 👇"},
    "choose_pkg": {"uz": "<b>{name}</b> — paketni tanlang:\n", "ru": "<b>{name}</b> — выберите пакет:\n",
                   "en": "<b>{name}</b> — choose a package:\n"},
    "other_ask": {
        "uz": "{e[edit]} <b>Qanday ish kerak?</b>\nIsh turini va mavzuni yozing (masalan: «Diplom ishi — Raqamli iqtisodiyot»).\n<i>Narxni admin ko'rib chiqib, sizga yuboradi.</i>",
        "ru": "{e[edit]} <b>Какая работа нужна?</b>\nНапишите вид работы и тему (например: «Дипломная — Цифровая экономика»).\n<i>Админ посмотрит и пришлёт цену.</i>",
        "en": "{e[edit]} <b>What work do you need?</b>\nWrite the type and topic (e.g. «Diploma — Digital economy»).\n<i>The admin will review it and send you a price.</i>"},
    "picked": {"uz": "Tanlandi: <b>{name}</b> — {price}\n<i>{desc}</i>", "ru": "Выбрано: <b>{name}</b> — {price}\n<i>{desc}</i>",
               "en": "Selected: <b>{name}</b> — {price}\n<i>{desc}</i>"},
    "topic_ask": {
        "uz": "{header}\n\n📝 <b>Mavzuni yozing</b> (masalan: «Sun'iy intellekt ta'limda»):",
        "ru": "{header}\n\n📝 <b>Напишите тему</b> (например: «Искусственный интеллект в образовании»):",
        "en": "{header}\n\n📝 <b>Write the topic</b> (e.g. «Artificial intelligence in education»):"},
    "topic_long": {"uz": "Mavzu juda uzun, qisqaroq yozing (300 belgigacha).", "ru": "Тема слишком длинная, сократите (до 300 символов).",
                   "en": "The topic is too long, please shorten it (up to 300 characters)."},
    "details_ask": {
        "uz": "ℹ️ <b>Qo'shimcha talablar?</b>\nMasalan: fan nomi, o'qituvchi, slayd soni, ism-familiya, rang…\nBo'lmasa — o'tkazib yuboring.",
        "ru": "ℹ️ <b>Дополнительные требования?</b>\nНапример: предмет, преподаватель, число слайдов, ФИО, цвет…\nЕсли нет — пропустите.",
        "en": "ℹ️ <b>Any extra requirements?</b>\nE.g. subject, teacher, number of slides, full name, colour…\nIf not — skip."},
    "files_ask": {
        "uz": "📸 <b>Ishga qo'yiladigan rasmlaringiz bormi?</b>\n"
              "Galereyadan tanlab yuboring — <b>bir nechtasini birdaniga</b> (albom) ham bo'ladi. Ko'pi bilan {mx} ta.\n\n"
              "💡 Rasm ostiga izoh yozing, masalan: <i>«3-slaydga»</i>, <i>«muqovaga»</i>.\n"
              "💎 Sifat yo'qolmasin desangiz — <b>📎 → Fayl</b> qilib yuboring.\n"
              "📄 Namuna, topshiriq sharti, Word/PDF ham yuborsangiz bo'ladi.\n\n"
              "Tugatgach «✅ Tayyor», rasm bo'lmasa — «O'tkazish».",
        "ru": "📸 <b>Есть фото, которые нужно вставить в работу?</b>\n"
              "Выберите в галерее и отправьте — можно <b>сразу несколько</b> (альбомом). Максимум {mx}.\n\n"
              "💡 Подпишите фото, например: <i>«на 3-й слайд»</i>, <i>«на обложку»</i>.\n"
              "💎 Чтобы не терялось качество — отправьте <b>📎 → Файл</b>.\n"
              "📄 Образец, условие задания, Word/PDF — тоже можно.\n\n"
              "Когда закончите — «✅ Готово», если фото нет — «Пропустить».",
        "en": "📸 <b>Any photos to put into the work?</b>\n"
              "Pick them in your gallery and send — <b>several at once</b> (album) is fine. Up to {mx}.\n\n"
              "💡 Add a caption, e.g. <i>«for slide 3»</i>, <i>«for the cover»</i>.\n"
              "💎 To keep full quality, send via <b>📎 → File</b>.\n"
              "📄 Samples, task conditions, Word/PDF are welcome too.\n\n"
              "When finished tap «✅ Done», no photos — «Skip»."},
    "files_max": {"uz": "Ko'pi bilan {n} ta rasm/fayl. «✅ Tayyor» ni bosing.", "ru": "Максимум {n} фото/файлов. Нажмите «✅ Готово».",
                  "en": "{n} photos/files at most. Tap «✅ Done»."},
    "files_got": {"uz": "✅ Qabul qilindi: <b>{n}</b> ta (rasm: {ph}, fayl: {dc}).\nYana yuboring yoki «✅ Tayyor» ni bosing.",
                  "ru": "✅ Принято: <b>{n}</b> (фото: {ph}, файлов: {dc}).\nОтправьте ещё или нажмите «✅ Готово».",
                  "en": "✅ Received: <b>{n}</b> (photos: {ph}, files: {dc}).\nSend more or tap «✅ Done»."},
    "files_first": {"uz": "Avval rasmni yuboring 📸 — keyin izoh yozasiz. Rasm bo'lmasa «O'tkazish».",
                    "ru": "Сначала отправьте фото 📸 — потом подпись. Если фото нет — «Пропустить».",
                    "en": "Send the photo first 📸, then the note. No photos — «Skip»."},
    "files_note_ok": {"uz": "📝 Izoh {n}-rasmga yozib qo'yildi. Yana yuboring yoki «✅ Tayyor».",
                      "ru": "📝 Подпись добавлена к фото №{n}. Отправьте ещё или «✅ Готово».",
                      "en": "📝 Note added to photo #{n}. Send more or tap «✅ Done»."},
    "deadline_ask": {"uz": "⏱ <b>Muddatni tanlang:</b>", "ru": "⏱ <b>Выберите срок:</b>", "en": "⏱ <b>Choose the deadline:</b>"},
    "confirm_title": {"uz": "{e[check]} <b>Buyurtmangizni tekshiring:</b>", "ru": "{e[check]} <b>Проверьте заказ:</b>",
                      "en": "{e[check]} <b>Check your order:</b>"},
    "f_topic": {"uz": "📝 Mavzu", "ru": "📝 Тема", "en": "📝 Topic"},
    "f_details": {"uz": "ℹ️ Qo'shimcha", "ru": "ℹ️ Доп. требования", "en": "ℹ️ Extra"},
    "f_files": {"uz": "📎 Fayllar: {n} ta", "ru": "📎 Файлы: {n}", "en": "📎 Files: {n}"},
    "f_deadline": {"uz": "⏱ Muddat", "ru": "⏱ Срок", "en": "⏱ Deadline"},
    "f_price": {"uz": "Narx", "ru": "Цена", "en": "Price"},
    "f_welcome": {"uz": "🎁 Do'st chegirmasi", "ru": "🎁 Скидка от друга", "en": "🎁 Friend discount"},
    "f_promo": {"uz": "🎟 Promokod", "ru": "🎟 Промокод", "en": "🎟 Promo code"},
    "f_bonus": {"uz": "💰 Bonusdan", "ru": "💰 Бонусами", "en": "💰 From bonus"},
    "f_total": {"uz": "Jami", "ru": "Итого", "en": "Total"},
    "f_discount": {"uz": "🏷 Chegirma", "ru": "🏷 Скидка", "en": "🏷 Discount"},
    "f_status": {"uz": "Holat", "ru": "Статус", "en": "Status"},
    "f_order": {"uz": "Buyurtma", "ru": "Заказ", "en": "Order"},
    "admin_price": {"uz": "<i>Narxni admin belgilaydi.</i>", "ru": "<i>Цену назначит админ.</i>", "en": "<i>The admin will set the price.</i>"},
    "promo_ask": {"uz": "{e[star]} Promokodni yozing:", "ru": "{e[star]} Введите промокод:", "en": "{e[star]} Enter the promo code:"},
    "promo_bad": {
        "uz": "❌ Bunday promokod yo'q yoki muddati tugagan. Boshqasini yozing yoki «Orqaga» bosing.",
        "ru": "❌ Такого промокода нет или он истёк. Введите другой или нажмите «Назад».",
        "en": "❌ This promo code doesn't exist or has expired. Try another or tap «Back»."},
    "promo_ok": {"uz": "{e[ok]} Promokod <b>{code}</b> qo'llandi: −{pct}%", "ru": "{e[ok]} Промокод <b>{code}</b> применён: −{pct}%",
                 "en": "{e[ok]} Promo code <b>{code}</b> applied: −{pct}%"},
    "wa_bad": {"uz": "Ma'lumot o'qilmadi, qaytadan urinib ko'ring.", "ru": "Не удалось прочитать данные, попробуйте ещё раз.",
               "en": "Couldn't read the data, please try again."},
    "wa_notfound": {"uz": "Xizmat yoki paket topilmadi. Qaytadan tanlang.", "ru": "Услуга или пакет не найдены. Выберите заново.",
                    "en": "Service or package not found. Please choose again."},
    "wa_notopic": {"uz": "Mavzu yozilmagan.", "ru": "Тема не указана.", "en": "No topic given."},
    "wa_ok": {"uz": "{e[app]} Mini ilovadan buyurtma qabul qilindi!", "ru": "{e[app]} Заказ из мини-приложения принят!",
              "en": "{e[app]} Order from the Mini App received!"},
    "wa_promo_ok": {"uz": "{e[ok]} Promokod <b>{code}</b> qabul qilindi.", "ru": "{e[ok]} Промокод <b>{code}</b> принят.",
                    "en": "{e[ok]} Promo code <b>{code}</b> accepted."},
    "wa_promo_bad": {"uz": "❌ Promokod «{code}» topilmadi — chegirmasiz davom etamiz.",
                     "ru": "❌ Промокод «{code}» не найден — продолжаем без скидки.",
                     "en": "❌ Promo code «{code}» not found — continuing without a discount."},
    "quote_ok": {
        "uz": "{e[ok]} <b>So'rov #{oid} qabul qilindi!</b>\n\n{e[orders]} Admin ishingizni ko'rib chiqib, <b>narx va muddatni</b> shu yerga yuboradi.\nOdatda 10–30 daqiqa ichida javob beramiz.",
        "ru": "{e[ok]} <b>Запрос #{oid} принят!</b>\n\n{e[orders]} Админ посмотрит и пришлёт сюда <b>цену и срок</b>.\nОбычно отвечаем за 10–30 минут.",
        "en": "{e[ok]} <b>Request #{oid} received!</b>\n\n{e[orders]} The admin will review it and send the <b>price and deadline</b> here.\nWe usually reply within 10–30 minutes."},
    "payment": {
        "uz": "{e[ok]} <b>Buyurtma #{oid} qabul qilindi!</b>\n\n💳 To'lov uchun karta:\n<code>{card}</code>\n👤 {owner}\n\n{e[money]} Summa: <b>{sum}</b>\n\nTo'lovdan so'ng <b>chek rasmini (skrinshot)</b> shu yerga yuboring {e[down]}",
        "ru": "{e[ok]} <b>Заказ #{oid} принят!</b>\n\n💳 Карта для оплаты:\n<code>{card}</code>\n👤 {owner}\n\n{e[money]} Сумма: <b>{sum}</b>\n\nПосле оплаты отправьте сюда <b>фото чека (скриншот)</b> {e[down]}",
        "en": "{e[ok]} <b>Order #{oid} received!</b>\n\n💳 Card for payment:\n<code>{card}</code>\n👤 {owner}\n\n{e[money]} Amount: <b>{sum}</b>\n\nAfter paying, send a <b>photo of the receipt (screenshot)</b> here {e[down]}"},
    "price_set": {"uz": "{e[money]} So'rovingiz #{oid} narxi belgilandi.\n\n", "ru": "{e[money]} Цена по запросу #{oid} назначена.\n\n",
                  "en": "{e[money]} The price for request #{oid} is set.\n\n"},
    "cheque_ok": {
        "uz": "{e[check]} Chek qabul qilindi! Tekshirib, tez orada ishni boshlaymiz. Holatini «📦 Buyurtmalarim» bo'limida ko'rasiz.",
        "ru": "{e[check]} Чек принят! Проверим и скоро начнём работу. Статус — в разделе «📦 Мои заказы».",
        "en": "{e[check]} Receipt received! We'll check it and start soon. See the status in «📦 My orders»."},
    "cheque_wrong": {"uz": "Iltimos, to'lov <b>chekining rasmini</b> yuboring 📸", "ru": "Пожалуйста, отправьте <b>фото чека</b> об оплате 📸",
                     "en": "Please send a <b>photo of the payment receipt</b> 📸"},
    "paid_ok": {"uz": "✅ <b>To'lov tasdiqlandi!</b> Buyurtma #{oid} tayyorlanmoqda 🛠\n\n"
                      "⏰ Tayyor bo'ladi: <b>{due}</b> gacha\n"
                      "📩 Tayyor bo'lishi bilan fayl <b>shu chatga avtomatik</b> keladi — hech narsa qilish shart emas.",
                "ru": "✅ <b>Оплата подтверждена!</b> Заказ #{oid} в работе 🛠\n\n"
                      "⏰ Будет готово: до <b>{due}</b>\n"
                      "📩 Как только будет готово, файл <b>сам придёт в этот чат</b> — ничего делать не нужно.",
                "en": "✅ <b>Payment confirmed!</b> Order #{oid} is in progress 🛠\n\n"
                      "⏰ Ready by: <b>{due}</b>\n"
                      "📩 As soon as it's ready, the file <b>arrives in this chat automatically</b> — nothing else to do."},
    "rejected": {"uz": "❌ Buyurtma #{oid} bo'yicha to'lov tasdiqlanmadi.\nSavol bo'lsa: {contact}",
                 "ru": "❌ Оплата по заказу #{oid} не подтверждена.\nВопросы: {contact}",
                 "en": "❌ Payment for order #{oid} was not confirmed.\nQuestions: {contact}"},
    "done": {"uz": "🎉 Buyurtma #{oid} tayyor! Rahmat 🙏\nTuzatish kerak bo'lsa yozing: {contact}",
             "ru": "🎉 Заказ #{oid} готов! Спасибо 🙏\nНужны правки — пишите: {contact}",
             "en": "🎉 Order #{oid} is ready! Thank you 🙏\nNeed changes? Write to: {contact}"},
    "file_cap": {"uz": "📦 Buyurtma #{oid} — tayyor ish", "ru": "📦 Заказ #{oid} — готовая работа", "en": "📦 Order #{oid} — your finished work"},
    "loose_file": {"uz": "Fayl qabul qilindi. Buyurtma berish uchun «✨ Buyurtmalar uchun» tugmasini bosing.",
                   "ru": "Файл получен. Чтобы заказать, нажмите «✨ Для заказов».",
                   "en": "File received. To order, tap «✨ For orders»."},
    "menu": {"uz": "Menyudan tanlang 👇", "ru": "Выберите в меню 👇", "en": "Choose from the menu 👇"},
    "privacy": {"uz": "🔒 Maxfiylik siyosati: {url}", "ru": "🔒 Политика конфиденциальности: {url}", "en": "🔒 Privacy policy: {url}"},
    "myid": {"uz": "Sizning ID: <code>{id}</code>", "ru": "Ваш ID: <code>{id}</code>", "en": "Your ID: <code>{id}</code>"},
    "bonus_menu": {
        "uz": ("{e[heart]} <b>Bonus va aksiyalar</b>\n\n{aksiya}"
               "{e[money]} Bonus balansingiz: <b>{bal}</b>\n"
               "{e[student]} Taklif qilganlar: <b>{inv}</b> (to'lov qilgan: {paid})\n\n"
               "{e[star]} <b>Qanday ishlaydi?</b>\n"
               "{e[n1]} Havolangizni do'stlarga yuboring\n"
               "{e[n2]} Do'stingiz birinchi buyurtmaga <b>{welcome}</b> chegirma oladi\n"
               "{e[n3]} U to'lov qilgach, sizga <b>{bonus}</b> bonus tushadi\n"
               "{e[n4]} Bonus bilan buyurtmaning <b>{pct}%</b> gacha qismini to'laysiz\n\n"
               "{e[globe]} Sizning havolangiz:\n<code>{link}</code>\n\n"
               "{e[edit]} Promokodingiz bo'lsa — buyurtmani tasdiqlashda kiriting."),
        "ru": ("{e[heart]} <b>Бонусы и акции</b>\n\n{aksiya}"
               "{e[money]} Ваш бонусный баланс: <b>{bal}</b>\n"
               "{e[student]} Приглашено: <b>{inv}</b> (оплатили: {paid})\n\n"
               "{e[star]} <b>Как это работает?</b>\n"
               "{e[n1]} Отправьте свою ссылку друзьям\n"
               "{e[n2]} Друг получает скидку <b>{welcome}</b> на первый заказ\n"
               "{e[n3]} Когда он оплатит, вам начислится <b>{bonus}</b> бонуса\n"
               "{e[n4]} Бонусами можно оплатить до <b>{pct}%</b> заказа\n\n"
               "{e[globe]} Ваша ссылка:\n<code>{link}</code>\n\n"
               "{e[edit]} Есть промокод — введите его при подтверждении заказа."),
        "en": ("{e[heart]} <b>Bonuses & promos</b>\n\n{aksiya}"
               "{e[money]} Your bonus balance: <b>{bal}</b>\n"
               "{e[student]} Invited: <b>{inv}</b> (paid: {paid})\n\n"
               "{e[star]} <b>How it works</b>\n"
               "{e[n1]} Send your link to friends\n"
               "{e[n2]} Your friend gets <b>{welcome}</b> off their first order\n"
               "{e[n3]} Once they pay, you get a <b>{bonus}</b> bonus\n"
               "{e[n4]} Pay up to <b>{pct}%</b> of an order with bonuses\n\n"
               "{e[globe]} Your link:\n<code>{link}</code>\n\n"
               "{e[edit]} Have a promo code? Enter it when confirming the order.")},
    "aksiya_line": {"uz": "{e[fire]} <b>Joriy aksiya:</b>\n{text}\n\n", "ru": "{e[fire]} <b>Текущая акция:</b>\n{text}\n\n",
                    "en": "{e[fire]} <b>Current promo:</b>\n{text}\n\n"},
    "share_text": {
        "uz": "Slayd, mustaqil ish, kurs ishi — tez va chiroyli! Havola orqali kirsang, birinchi buyurtmaga {sum} chegirma 🎁",
        "ru": "Слайды, самостоятельные, курсовые — быстро и красиво! По ссылке — скидка {sum} на первый заказ 🎁",
        "en": "Slides, papers, term papers — fast and beautiful! Join with my link and get {sum} off your first order 🎁"},
    "channel_msg": {
        "uz": "{e[channel]} <b>Kanalimizga obuna bo'ling!</b>\n\nYangi namunalar, {e[fire]} aksiyalar va {e[star]} promokodlar birinchi bo'lib shu yerda chiqadi.",
        "ru": "{e[channel]} <b>Подпишитесь на наш канал!</b>\n\nНовые примеры работ, {e[fire]} акции и {e[star]} промокоды — первыми именно там.",
        "en": "{e[channel]} <b>Subscribe to our channel!</b>\n\nNew samples, {e[fire]} promos and {e[star]} promo codes appear there first."},
    "channel_soon": {"uz": "Kanal tez orada ochiladi 🙂", "ru": "Канал скоро откроется 🙂", "en": "The channel is coming soon 🙂"},
    "info": {
        "uz": ("{e[bot]} <b>{bot} haqida</b>\n\n"
               "{e[student]} <b>Talabalarga</b> ({min_s}): slayd, mustaqil ish, kurs ishi, maqola, amaliy ish, referat, portfolio\n"
               "{e[teacher]} <b>Ustozlarga</b> ({min_t}): taqdimot, portfolio, o'quv-uslubiy majmua, dars ishlanmasi, maqola, test, tadbir\n"
               "{e[edit]} Ro'yxatda yo'q ish — yozasiz, narxni kelishamiz\n\n"
               "{e[image]} <b>Slayd paketlari</b>\n"
               "• <b>Start</b> — zamonaviy, toza dizayn\n"
               "• <b>Professional</b> — animatsiya, diagrammalar\n"
               "• <b>Premium</b> — Morph, neon dizayn, nutq matni\n"
               "🐢 <b>Toshbaqa o'qituvchi</b> — slaydda gapirib, mavzuni tushuntiradi\n"
               "    👩‍🏫 ustozlarga — Pro va Premium'da bepul · 🎓 talabalarga — +{turtle}\n\n"
               "{e[orders]} <b>Qanday ishlaydi?</b>\n"
               "{e[n1]} Ish va paketni tanlaysiz, mavzuni yozasiz\n"
               "{e[n2]} Kartaga to'lab, chek rasmini yuborasiz\n"
               "{e[n3]} Admin tasdiqlaydi va ishni boshlaymiz\n"
               "{e[n4]} Tayyor fayl shu chatga keladi\n\n"
               "{e[fire]} Shoshilinch: +{urgent}% · 🔁 Tuzatish bepul\n\n"
               "{e[heart]} <b>Bonus va aksiyalar</b>\n"
               "• Do'stingiz havolangiz orqali kelsa — unga <b>{welcome}</b> chegirma, sizga <b>{bonus}</b> bonus\n"
               "• Bonus bilan buyurtmaning {pct}% gacha qismini to'laysiz\n"
               "• Promokodlar va aksiyalar — kanalimizda\n\n"
               "{e[globe]} Tillar: O'zbekcha · Русский · English — /lang\n"
               "{e[channel]} Kanal: {channel}\n"
               "{e[bot]} Video yuklash boti: {yukla}\n"
               "{e[contact]} Admin: {contact}\n"
               "🔒 Maxfiylik siyosati: /privacy"),
        "ru": ("{e[bot]} <b>О боте {bot}</b>\n\n"
               "{e[student]} <b>Студентам</b> ({min_s}): слайды, самостоятельная, курсовая, статья, практическая, реферат, портфолио\n"
               "{e[teacher]} <b>Преподавателям</b> ({min_t}): презентации, портфолио, УМК, разработки уроков, статьи, тесты, мероприятия\n"
               "{e[edit]} Нет в списке — напишите, цену согласуем\n\n"
               "{e[image]} <b>Пакеты слайдов</b>\n"
               "• <b>Start</b> — современный чистый дизайн\n"
               "• <b>Professional</b> — анимация, диаграммы\n"
               "• <b>Premium</b> — Morph, неон, текст речи\n"
               "🐢 <b>Черепаха-учитель</b> — говорит на слайдах и объясняет тему\n"
               "    👩‍🏫 преподавателям — бесплатно в Pro и Premium · 🎓 студентам — +{turtle}\n\n"
               "{e[orders]} <b>Как это работает?</b>\n"
               "{e[n1]} Выбираете работу и пакет, пишете тему\n"
               "{e[n2]} Оплачиваете на карту и отправляете фото чека\n"
               "{e[n3]} Админ подтверждает, и мы начинаем\n"
               "{e[n4]} Готовый файл приходит в этот чат\n\n"
               "{e[fire]} Срочно: +{urgent}% · 🔁 Правки бесплатно\n\n"
               "{e[heart]} <b>Бонусы и акции</b>\n"
               "• Друг пришёл по вашей ссылке — ему скидка <b>{welcome}</b>, вам <b>{bonus}</b> бонуса\n"
               "• Бонусами можно оплатить до {pct}% заказа\n"
               "• Промокоды и акции — в нашем канале\n\n"
               "{e[globe]} Языки: O'zbekcha · Русский · English — /lang\n"
               "{e[channel]} Канал: {channel}\n"
               "{e[bot]} Бот для скачивания видео: {yukla}\n"
               "{e[contact]} Админ: {contact}\n"
               "🔒 Политика конфиденциальности: /privacy"),
        "en": ("{e[bot]} <b>About {bot}</b>\n\n"
               "{e[student]} <b>For students</b> ({min_s}): slides, independent work, term paper, article, lab work, essay, portfolio\n"
               "{e[teacher]} <b>For teachers</b> ({min_t}): presentations, portfolio, teaching materials, lesson plans, articles, tests, events\n"
               "{e[edit]} Not on the list — describe it and we'll agree on a price\n\n"
               "{e[image]} <b>Slide packages</b>\n"
               "• <b>Start</b> — modern, clean design\n"
               "• <b>Professional</b> — animation, charts\n"
               "• <b>Premium</b> — Morph, neon design, speech text\n"
               "🐢 <b>Turtle teacher</b> — talks on the slides and explains the topic\n"
               "    👩‍🏫 teachers — free in Pro & Premium · 🎓 students — +{turtle}\n\n"
               "{e[orders]} <b>How it works</b>\n"
               "{e[n1]} Pick the work and package, write the topic\n"
               "{e[n2]} Pay by card and send a photo of the receipt\n"
               "{e[n3]} The admin confirms and we start\n"
               "{e[n4]} The finished file arrives in this chat\n\n"
               "{e[fire]} Urgent: +{urgent}% · 🔁 Free revisions\n\n"
               "{e[heart]} <b>Bonuses & promos</b>\n"
               "• A friend joins with your link — they get <b>{welcome}</b> off, you get a <b>{bonus}</b> bonus\n"
               "• Pay up to {pct}% of an order with bonuses\n"
               "• Promo codes and offers — in our channel\n\n"
               "{e[globe]} Languages: O'zbekcha · Русский · English — /lang\n"
               "{e[channel]} Channel: {channel}\n"
               "{e[bot]} Video downloader bot: {yukla}\n"
               "{e[contact]} Admin: {contact}\n"
               "🔒 Privacy policy: /privacy")},
}

# Bot menyusidagi buyruqlar (chap pastdagi «Menu» tugmasi)
COMMANDS = {
    "uz": [("start", "Botni ishga tushirish"), ("order", "Buyurtma berish"), ("bonus", "Bonus va aksiyalar"),
           ("info", "Bot haqida ma'lumot"), ("tayyor", "Tayyor ishlar do'koni"), ("shablon", "Dizayn shablonlari"), ("channel", "Kanalimizga obuna bo'lish"), ("lang", "Tilni o'zgartirish"),
           ("privacy", "Maxfiylik siyosati")],
    "ru": [("start", "Запустить бота"), ("order", "Сделать заказ"), ("bonus", "Бонусы и акции"),
           ("info", "Информация о боте"), ("tayyor", "Магазин готовых работ"), ("shablon", "Шаблоны дизайна"), ("channel", "Подписаться на канал"), ("lang", "Сменить язык"),
           ("privacy", "Политика конфиденциальности")],
    "en": [("start", "Start the bot"), ("order", "Place an order"), ("bonus", "Bonuses & promos"),
           ("info", "About the bot"), ("tayyor", "Ready works shop"), ("shablon", "Design templates"), ("channel", "Subscribe to our channel"), ("lang", "Change language"),
           ("privacy", "Privacy policy")],
}

# Bot profili: «Bu bot nima qila oladi?» (description, 512 belgigacha) va qisqa tavsif (about, 120 belgigacha)
DESCRIPTION = {
    "uz": ("🎓 Talabalar va 👩‍🏫 ustozlar uchun tez va chiroyli tayyorlaymiz: slayd, mustaqil ish, kurs ishi, "
           "maqola, referat, portfolio, O'UM, dars ishlanmasi, testlar.\n\n"
           "📦 Start · Professional · Premium\n"
           "🐢 Toshbaqa o'qituvchi — slaydda gapirib tushuntiradi\n"
           "⚡ Shoshilinch · 🔁 Bepul tuzatish\n"
           "🎁 Do'st taklif qiling — bonus oling · 🎟 promokodlar\n"
           "🌐 O'zbekcha · Русский · English\n\n{channel_line}"
           "📥 Video yuklash: {yukla}\n"
           "💜 Admin: {contact}"),
    "ru": ("🎓 Студентам и 👩‍🏫 преподавателям быстро и красиво: слайды, самостоятельные, курсовые, "
           "статьи, рефераты, портфолио, УМК, разработки уроков, тесты.\n\n"
           "📦 Start · Professional · Premium\n"
           "🐢 Черепаха-учитель — объясняет тему голосом\n"
           "⚡ Срочно · 🔁 Бесплатные правки\n"
           "🎁 Приглашайте друзей — бонусы · 🎟 промокоды\n"
           "🌐 O'zbekcha · Русский · English\n\n{channel_line}"
           "📥 Скачать видео: {yukla}\n"
           "💜 Админ: {contact}"),
    "en": ("🎓 For students and 👩‍🏫 teachers: slides, independent work, term papers, articles, essays, "
           "portfolios, teaching materials, lesson plans, tests — fast and beautiful.\n\n"
           "📦 Start · Professional · Premium\n"
           "🐢 Turtle teacher — explains the topic out loud\n"
           "⚡ Urgent orders · 🔁 Free revisions\n"
           "🎁 Invite friends — earn bonuses · 🎟 promo codes\n"
           "🌐 O'zbekcha · Русский · English\n\n{channel_line}"
           "📥 Video downloader: {yukla}\n"
           "💜 Admin: {contact}"),
}
CHANNEL_LINE = {"uz": "📢 Kanal: {ch}\n", "ru": "📢 Канал: {ch}\n", "en": "📢 Channel: {ch}\n"}
SHORT_DESC = {
    "uz": "Slayd, mustaqil ish, kurs ishi va boshqalar — tez va chiroyli. 🐢 Toshbaqa o'qituvchi, bonuslar. 💜 {contact}",
    "ru": "Слайды, самостоятельные, курсовые и другое — быстро и красиво. 🐢 Черепаха-учитель, бонусы. 💜 {contact}",
    "en": "Slides, papers, term papers and more — fast and beautiful. 🐢 Turtle teacher, bonuses. 💜 {contact}",
}

# ------------------------------------------------------------------ batafsil so'rovnoma (texnik topshiriq)
# Har bir xizmat turi uchun savollar ketma-ketligi
BRIEF_GROUPS = {
    "slides": ["subject", "slides", "wlang", "script", "title", "plan", "must", "where", "style", "date", "extra"],
    "paper": ["subject", "pages", "wlang", "script", "title", "cover", "plan", "must", "format", "date", "extra"],
    "portfolio": ["who", "sections", "must", "where", "style", "date", "extra"],
    "teach": ["subject", "grade", "count", "wlang", "script", "cover", "plan", "must", "date", "extra"],
    "other": ["free", "date"],
}
SVC_GROUP = {"taqdimot": "slides", "dars": "slides", "tadbir": "slides",
             "mustaqil": "paper", "kurs": "paper", "maqola": "paper", "amaliy": "paper", "referat": "paper",
             "portfolio": "portfolio", "oum": "teach", "ishlanma": "teach", "test": "teach", "boshqa": "other"}

# Savol matni va tezkor javob tugmalari (opts)
BRIEF_Q = {
    "subject": {"uz": "📚 <b>Fan nomi</b> (yoki tadbir nomi)?", "ru": "📚 <b>Название предмета</b> (или мероприятия)?",
                "en": "📚 <b>Subject</b> (or event name)?"},
    "slides": {"uz": "🖼 <b>Nechta slayd</b> kerak?", "ru": "🖼 <b>Сколько слайдов</b> нужно?", "en": "🖼 <b>How many slides?</b>",
               "opts": {"uz": ["10", "15", "20", "25"], "ru": ["10", "15", "20", "25"], "en": ["10", "15", "20", "25"]}},
    "pages": {"uz": "📄 <b>Hajmi</b> — necha bet?", "ru": "📄 <b>Объём</b> — сколько страниц?", "en": "📄 <b>Length</b> — how many pages?",
              "opts": {"uz": ["10", "15", "20", "30"], "ru": ["10", "15", "20", "30"], "en": ["10", "15", "20", "30"]}},
    "wlang": {"uz": "🌐 Ish <b>qaysi tilda</b> bo'lsin?", "ru": "🌐 На <b>каком языке</b> работа?", "en": "🌐 <b>Which language</b> should the work be in?",
              "opts": {"uz": ["O'zbekcha", "Ruscha", "Inglizcha"], "ru": ["Узбекский", "Русский", "Английский"],
                       "en": ["Uzbek", "Russian", "English"]}},
    "title": {"uz": "🎓 <b>Titul (muqova) uchun</b>: F.I.Sh, guruh, OTM, o'qituvchi\n<i>Masalan: Aliyev Ali, 101-guruh, ADPI, o'qituvchi Karimova N.</i>",
              "ru": "🎓 <b>Для титульного листа</b>: ФИО, группа, вуз, преподаватель\n<i>Например: Алиев Али, группа 101, АДПИ, преподаватель Каримова Н.</i>",
              "en": "🎓 <b>For the title page</b>: full name, group, university, teacher\n<i>E.g. Ali Aliyev, group 101, ADPI, teacher N. Karimova</i>"},
    "plan": {"uz": "🗂 <b>Reja yoki bo'limlar</b> bormi? Yozing yoki tugmani bosing",
             "ru": "🗂 Есть <b>план или разделы</b>? Напишите или нажмите кнопку",
             "en": "🗂 Do you have an <b>outline or sections</b>? Write them or tap the button",
             "opts": {"uz": ["O'zingiz tuzing"], "ru": ["Составьте сами"], "en": ["You make it"]}},
    "style": {"uz": "🎨 <b>Rang yoki dizayn</b> istagi?", "ru": "🎨 Пожелания по <b>цвету и дизайну</b>?", "en": "🎨 <b>Colour or design</b> preference?",
              "opts": {"uz": ["Binafsha-qora", "Ko'k-oq", "Rasmiy / klassik", "Farqi yo'q"],
                       "ru": ["Фиолетово-чёрный", "Сине-белый", "Строгий / классика", "Неважно"],
                       "en": ["Purple & black", "Blue & white", "Formal / classic", "No preference"]}},
    "format": {"uz": "📐 <b>Rasmiylashtirish talablari</b>? (shrift, interval, adabiyotlar soni)",
               "ru": "📐 <b>Требования к оформлению</b>? (шрифт, интервал, количество источников)",
               "en": "📐 <b>Formatting requirements</b>? (font, spacing, number of references)",
               "opts": {"uz": ["Standart: Times New Roman 14, 1.5"], "ru": ["Стандарт: Times New Roman 14, 1.5"],
                        "en": ["Standard: Times New Roman 14, 1.5"]}},
    "who": {"uz": "👤 <b>Kim uchun</b>: F.I.Sh, lavozim, ish joyi?", "ru": "👤 <b>Для кого</b>: ФИО, должность, место работы?",
            "en": "👤 <b>Who is it for</b>: full name, position, workplace?"},
    "sections": {"uz": "🗂 <b>Qaysi bo'limlar</b> bo'lsin? (yutuqlar, sertifikatlar, ochiq darslar…)",
                 "ru": "🗂 <b>Какие разделы</b> нужны? (достижения, сертификаты, открытые уроки…)",
                 "en": "🗂 <b>Which sections</b>? (achievements, certificates, open lessons…)",
                 "opts": {"uz": ["Standart bo'limlar"], "ru": ["Стандартные разделы"], "en": ["Standard sections"]}},
    "grade": {"uz": "🏫 <b>Kurs / sinf</b> va yo'nalish?", "ru": "🏫 <b>Курс / класс</b> и направление?", "en": "🏫 <b>Year / grade</b> and field?"},
    "count": {"uz": "🔢 <b>Hajm</b>: necha soat yoki nechta savol?", "ru": "🔢 <b>Объём</b>: сколько часов или вопросов?",
              "en": "🔢 <b>Size</b>: how many hours or questions?"},
    "free": {"uz": "✍️ <b>Ishni batafsil yozing</b>: nima kerak, hajmi, talablar",
             "ru": "✍️ <b>Опишите подробно</b>: что нужно, объём, требования",
             "en": "✍️ <b>Describe it in detail</b>: what you need, size, requirements"},
    "date": {"uz": "📅 <b>Aniq qachongacha</b> kerak?", "ru": "📅 <b>К какому сроку</b> нужно?", "en": "📅 <b>When exactly</b> do you need it?",
             "opts": {"uz": ["Bugun", "Ertaga", "2–3 kunda", "Farqi yo'q"], "ru": ["Сегодня", "Завтра", "Через 2–3 дня", "Неважно"],
                      "en": ["Today", "Tomorrow", "In 2–3 days", "No rush"]}},
    "extra": {"uz": "💬 <b>Yana istaklar</b> bormi?", "ru": "💬 <b>Ещё пожелания</b>?", "en": "💬 <b>Anything else</b>?"},
    "script": {"uz": "🔤 O'zbekcha bo'lsa — <b>qaysi yozuvda</b>?", "ru": "🔤 Если на узбекском — <b>какой алфавит</b>?",
               "en": "🔤 If in Uzbek — <b>which script</b>?",
               "opts": {"uz": ["Lotin (o'zbekcha)", "Кирилл (ўзбекча)", "O'zbekcha emas"], "ru": ["Латиница", "Кириллица", "Не на узбекском"],
                        "en": ["Latin", "Cyrillic", "Not Uzbek"]}},
    "must": {"uz": "📌 <b>Albatta bo'lishi kerak</b> bo'lgan narsalar? (raqamlar, nomlar, sanalar, yutuqlar, iqtiboslar)\n<i>Ro'yxat qilib yozing — hech biri tushib qolmaydi.</i>",
             "ru": "📌 Что <b>обязательно должно быть</b>? (цифры, имена, даты, достижения, цитаты)\n<i>Напишите списком — ничего не потеряется.</i>",
             "en": "📌 What <b>must be included</b>? (numbers, names, dates, achievements, quotes)\n<i>Write it as a list — nothing will be missed.</i>",
             "opts": {"uz": ["Hech narsa — o'zingiz tuzing"], "ru": ["Ничего — составьте сами"], "en": ["Nothing — up to you"]}},
    "where": {"uz": "🎯 <b>Qayerda</b> taqdim etiladi?", "ru": "🎯 <b>Где</b> будете показывать?", "en": "🎯 <b>Where</b> will it be presented?",
              "opts": {"uz": ["Dars / seminar", "Tanlov", "Himoya", "Konferensiya / tadbir"], "ru": ["Урок / семинар", "Конкурс", "Защита", "Конференция"],
                       "en": ["Class / seminar", "Contest", "Defense", "Conference / event"]}},
}
BRIEF_REQUIRED = {"subject", "slides", "pages", "wlang", "title", "who", "free", "script"}
BRIEF_REQ_TX = {"uz": "❗ Bu savol <b>majburiy</b> — keyin «bu qani?» degan gap bo'lmasligi uchun. Javob yozing yoki tugmani bosing.",
                "ru": "❗ Этот вопрос <b>обязательный</b> — чтобы потом не было «а где это?». Напишите ответ или нажмите кнопку.",
                "en": "❗ This question is <b>required</b> — so nothing is missing later. Type an answer or tap a button."}
# Admin uchun texnik topshiriqdagi nomlar (o'zbekcha)
BRIEF_LABEL = {"script": "Yozuv", "must": "ALBATTA BO'LSIN", "where": "Qayerda taqdim etiladi", "subject": "Fan", "slides": "Slaydlar soni", "pages": "Hajmi (bet)", "wlang": "Ish tili",
               "title": "Titul ma'lumotlari", "plan": "Reja / bo'limlar", "style": "Dizayn shabloni", "cover": "Muqova shabloni", "format": "Rasmiylashtirish",
               "who": "Kim uchun", "sections": "Bo'limlar", "grade": "Kurs / sinf", "count": "Hajm",
               "free": "Batafsil", "date": "Qachongacha", "extra": "Qo'shimcha istaklar",
               "group": "Guruh mavzulari"}
BRIEF_TX = {
    "intro": {"uz": "{e[edit]} <b>Endi bir nechta savol</b> — ishni aynan siz xohlagandek qilishimiz uchun.\nJavob yozing yoki tugmani bosing. Bilmasangiz — «O'tkazish».",
              "ru": "{e[edit]} <b>Теперь несколько вопросов</b> — чтобы сделать работу точно как вы хотите.\nНапишите ответ или нажмите кнопку. Не знаете — «Пропустить».",
              "en": "{e[edit]} <b>Now a few questions</b> — so we make it exactly the way you want.\nType an answer or tap a button. Not sure — «Skip»."},
    "step": {"uz": "Savol {i}/{n}", "ru": "Вопрос {i}/{n}", "en": "Question {i}/{n}"},
    "skip": {"uz": "⏭ O'tkazish", "ru": "⏭ Пропустить", "en": "⏭ Skip"},
    "finish": {"uz": "✅ Qolganini o'tkazish", "ru": "✅ Остальное пропустить", "en": "✅ Skip the rest"},
    "done": {"uz": "{e[ok]} Rahmat! Hammasi yozib olindi.", "ru": "{e[ok]} Спасибо! Всё записали.", "en": "{e[ok]} Thanks! Got everything."},
    "too_long": {"uz": "Juda uzun — 500 belgigacha yozing.", "ru": "Слишком длинно — до 500 символов.", "en": "Too long — up to 500 characters."},
    "summary": {"uz": "🗒 <b>Talablaringiz:</b>", "ru": "🗒 <b>Ваши требования:</b>", "en": "🗒 <b>Your requirements:</b>"},
}
BRIEF_LABEL_TR = {
    "ru": {"script": "Алфавит", "must": "Обязательно", "where": "Где показ", "subject": "Предмет", "slides": "Слайдов", "pages": "Страниц", "wlang": "Язык работы", "title": "Титул",
           "plan": "План", "style": "Шаблон дизайна", "cover": "Шаблон обложки", "format": "Оформление", "who": "Для кого", "sections": "Разделы",
           "grade": "Курс / класс", "count": "Объём", "free": "Подробно", "date": "Срок", "extra": "Пожелания",
           "group": "Темы группы"},
    "en": {"script": "Script", "must": "Must include", "where": "Presented at", "subject": "Subject", "slides": "Slides", "pages": "Pages", "wlang": "Language", "title": "Title page",
           "plan": "Outline", "style": "Design template", "cover": "Cover template", "format": "Formatting", "who": "For", "sections": "Sections",
           "grade": "Year / grade", "count": "Size", "free": "Details", "date": "Deadline", "extra": "Extra",
           "group": "Group topics"},
}

TURTLE_ADDON_TX = {
    "btn_add": {"uz": "🐢 Toshbaqa o'qituvchi qo'shish (+{sum})", "ru": "🐢 Добавить черепаху-учителя (+{sum})",
                "en": "🐢 Add the Turtle teacher (+{sum})"},
    "btn_off": {"uz": "🐢 Toshbaqani olib tashlash", "ru": "🐢 Убрать черепаху", "en": "🐢 Remove the turtle"},
    "line_in": {"uz": "🐢 Toshbaqa o'qituvchi — paketga kiradi", "ru": "🐢 Черепаха-учитель — входит в пакет",
                "en": "🐢 Turtle teacher — included in the package"},
    "line_add": {"uz": "🐢 Toshbaqa o'qituvchi: +{sum}", "ru": "🐢 Черепаха-учитель: +{sum}", "en": "🐢 Turtle teacher: +{sum}"},
    "hint": {"uz": "<i>🐢 Xohlasangiz — Toshbaqa o'qituvchi slaydda gapirib, mavzuni tushuntiradi (+{sum}).</i>",
             "ru": "<i>🐢 По желанию — черепаха-учитель голосом объяснит тему на слайдах (+{sum}).</i>",
             "en": "<i>🐢 Optional — the Turtle teacher explains the topic out loud on the slides (+{sum}).</i>"},
}

# ------------------------------------------------------------------ namunalar karuseli
SAMPLE_PKG = {
    1: {"uz": "Zamonaviy, toza dizayn · ikonkalar · tushunarli tuzilma",
        "ru": "Современный чистый дизайн · иконки · понятная структура",
        "en": "Modern, clean design · icons · clear structure"},
    2: {"uz": "Animatsiya · diagrammalar · reja va bosqichlar · infografika",
        "ru": "Анимация · диаграммы · план и этапы · инфографика",
        "en": "Animation · charts · outline and steps · infographics"},
    3: {"uz": "Neon nur · Morph o'tishlari · nutq matni · eng chiroyli dizayn",
        "ru": "Неоновое свечение · Morph-переходы · текст речи · самый красивый дизайн",
        "en": "Neon glow · Morph transitions · speech text · our most beautiful design"},
}
SAMPLE_TX = {
    "title": {"uz": "{e[samples]} <b>Namunalar — {pkg}</b>", "ru": "{e[samples]} <b>Примеры — {pkg}</b>",
              "en": "{e[samples]} <b>Samples — {pkg}</b>"},
    "prices": {"uz": "{e[student]} Talabalar: <b>{s}</b>\n{e[teacher]} Ustozlar: <b>{t}</b>",
               "ru": "{e[student]} Студентам: <b>{s}</b>\n{e[teacher]} Преподавателям: <b>{t}</b>",
               "en": "{e[student]} Students: <b>{s}</b>\n{e[teacher]} Teachers: <b>{t}</b>"},
    "turtle_in": {"uz": "🐢 Ustozlarga Toshbaqa o'qituvchi bilan · talabalarga +{sum}",
                  "ru": "🐢 Преподавателям с черепахой-учителем · студентам +{sum}",
                  "en": "🐢 Teachers get the Turtle teacher · students +{sum}"},
    "turtle_add": {"uz": "🐢 Toshbaqa o'qituvchi — talabalarga +{sum}", "ru": "🐢 Черепаха-учитель — студентам +{sum}",
                   "en": "🐢 Turtle teacher — students +{sum}"},
    "slide": {"uz": "Slayd {i} / {n} · ◀️ ▶️ bilan varaqlang", "ru": "Слайд {i} / {n} · листайте ◀️ ▶️",
              "en": "Slide {i} / {n} · flip with ◀️ ▶️"},
    "download": {"uz": "📥 PPTX faylni olish", "ru": "📥 Скачать PPTX", "en": "📥 Get the PPTX"},
    "pptx_cap": {"uz": "{pkg} namunasi 🎨\n<i>Animatsiyalar kompyuterdagi PowerPoint'da to'liq ko'rinadi.</i>",
                 "ru": "Пример {pkg} 🎨\n<i>Анимации полностью видны в PowerPoint на компьютере.</i>",
                 "en": "{pkg} sample 🎨\n<i>Animations play fully in PowerPoint on a computer.</i>"},
}

# ------------------------------------------------------------------ yangi funksiyalar: sharh, guruh, do'kon, sodiqlik...
FX = {
    "auto_wait": {"uz": "✅ <b>To'lov tasdiqlandi!</b> Buyurtma #{oid} 🛠\n\n⚡ Ishingiz <b>hozir tayyorlanmoqda</b> — bir necha daqiqada shu chatga keladi 📩",
                  "ru": "✅ <b>Оплата подтверждена!</b> Заказ #{oid} 🛠\n\n⚡ Работа <b>уже готовится</b> — через несколько минут придёт в этот чат 📩",
                  "en": "✅ <b>Payment confirmed!</b> Order #{oid} 🛠\n\n⚡ Your work is <b>being prepared now</b> — it will arrive in this chat in a few minutes 📩"},
    "auto_manual": {"uz": "🛠 Buyurtma #{oid} ustida ishlayapmiz — sifatli chiqishi uchun biroz ko'proq vaqt kerak.\n⏰ Tayyor bo'ladi: <b>{due}</b> gacha. Fayl shu chatga keladi 📩",
                    "ru": "🛠 Работаем над заказом #{oid} — чтобы всё было качественно, нужно чуть больше времени.\n⏰ Будет готово: до <b>{due}</b>. Файл придёт в этот чат 📩",
                    "en": "🛠 We're working on order #{oid} — it needs a bit more time to be done right.\n⏰ Ready by: <b>{due}</b>. The file will arrive in this chat 📩"},
    "rv_ask": {"uz": "{e[star]} <b>Ishimiz yoqdimi?</b>\nBuyurtma #{oid} ni baholang:",
               "ru": "{e[star]} <b>Понравилась работа?</b>\nОцените заказ #{oid}:",
               "en": "{e[star]} <b>Did you like it?</b>\nRate order #{oid}:"},
    "rv_comment": {"uz": "Rahmat! ✍️ Qisqacha fikringizni yozing yoki «O'tkazish» ni bosing.",
                   "ru": "Спасибо! ✍️ Напишите короткий отзыв или нажмите «Пропустить».",
                   "en": "Thanks! ✍️ Write a short review or tap «Skip»."},
    "rv_consent": {"uz": "Fikringizni kanalimizda <b>ismingiz bilan</b> (familiyasiz) e'lon qilsak bo'ladimi?",
                   "ru": "Можно опубликовать ваш отзыв в нашем канале <b>с вашим именем</b> (без фамилии)?",
                   "en": "May we post your review in our channel <b>with your first name</b>?"},
    "rv_yes": {"uz": "✅ Ha, mumkin", "ru": "✅ Да, можно", "en": "✅ Yes"},
    "rv_no": {"uz": "❌ Yo'q", "ru": "❌ Нет", "en": "❌ No"},
    "rv_thanks": {"uz": "💜 Rahmat! Fikringiz biz uchun juda muhim.", "ru": "💜 Спасибо! Ваш отзыв очень важен для нас.",
                  "en": "💜 Thank you! Your feedback means a lot."},
    "rv_low": {"uz": "😔 Uzr! Admin siz bilan bog'lanadi — kamchiliklarni bepul tuzatamiz.",
               "ru": "😔 Извините! Админ свяжется с вами — бесплатно всё исправим.",
               "en": "😔 Sorry! The admin will contact you — we'll fix everything for free."},
    "shop_title": {"uz": "📦 <b>Tayyor ishlar</b>\nArzon va tez: to'lov tasdiqlangach fayl darhol keladi. Tanlang 👇",
                   "ru": "📦 <b>Готовые работы</b>\nДёшево и быстро: файл приходит сразу после подтверждения оплаты. Выберите 👇",
                   "en": "📦 <b>Ready works</b>\nCheap and fast: the file arrives right after the payment is confirmed. Choose 👇"},
    "shop_empty": {"uz": "Hozircha tayyor ishlar yo'q — tez orada qo'shiladi 🙂", "ru": "Пока готовых работ нет — скоро появятся 🙂",
                   "en": "No ready works yet — coming soon 🙂"},
    "shop_item": {"uz": "📦 <b>{title}</b>\n{e[money]} Narx: <b>{price}</b>\n\n<i>To'lov tasdiqlangach, fayl shu chatga avtomatik keladi.</i>",
                  "ru": "📦 <b>{title}</b>\n{e[money]} Цена: <b>{price}</b>\n\n<i>После подтверждения оплаты файл автоматически придёт в этот чат.</i>",
                  "en": "📦 <b>{title}</b>\n{e[money]} Price: <b>{price}</b>\n\n<i>Once the payment is confirmed, the file arrives here automatically.</i>"},
    "shop_buy": {"uz": "💳 Sotib olish", "ru": "💳 Купить", "en": "💳 Buy"},
    "shop_prev": {"uz": "👀 Namunasini ko'rish", "ru": "👀 Посмотреть пример", "en": "👀 See a preview"},
    "shop_back": {"uz": "⬅️ Ro'yxatga", "ru": "⬅️ К списку", "en": "⬅️ Back to list"},
    "shop_paid": {"uz": "✅ To'lov tasdiqlandi! Mana faylingiz 👇", "ru": "✅ Оплата подтверждена! Вот ваш файл 👇",
                  "en": "✅ Payment confirmed! Here is your file 👇"},
    "grp_ask": {"uz": "👥 <b>Necha kishi uchun?</b>\nBir xil ish turi, har biriga o'z mavzusi.\n{n1} ta ishdan — <b>−{p1}%</b>, {n2} tadan — <b>−{p2}%</b> 🎉",
                "ru": "👥 <b>На сколько человек?</b>\nОдин вид работы, у каждого своя тема.\nОт {n1} работ — <b>−{p1}%</b>, от {n2} — <b>−{p2}%</b> 🎉",
                "en": "👥 <b>How many people?</b>\nSame type of work, each with its own topic.\nFrom {n1} works — <b>−{p1}%</b>, from {n2} — <b>−{p2}%</b> 🎉"},
    "grp_other": {"uz": "✍️ Boshqa son", "ru": "✍️ Другое число", "en": "✍️ Other number"},
    "grp_custom": {"uz": "Sonini yozing (2–50):", "ru": "Напишите число (2–50):", "en": "Type the number (2–50):"},
    "grp_topics": {"uz": "📝 Har bir ishning mavzusini <b>yangi qatordan</b> yozing.\nYoki «O'tkazish» — mavzularni keyin admin bilan kelishasiz.",
                   "ru": "📝 Напишите тему каждой работы <b>с новой строки</b>.\nИли «Пропустить» — темы согласуете с админом позже.",
                   "en": "📝 Write each topic <b>on a new line</b>.\nOr «Skip» — agree on the topics with the admin later."},
    "grp_line": {"uz": "👥 Guruh: {n} ta × {unit}", "ru": "👥 Группа: {n} × {unit}", "en": "👥 Group: {n} × {unit}"},
    "grp_off": {"uz": "👥 Guruh chegirmasi ({pct}%)", "ru": "👥 Скидка группе ({pct}%)", "en": "👥 Group discount ({pct}%)"},
    "grp_bonus": {"uz": "🎁 Guruhni yig'ganingiz uchun +{sum} bonus!", "ru": "🎁 За сбор группы +{sum} бонуса!",
                  "en": "🎁 +{sum} bonus for organising the group!"},
    "loy_off": {"uz": "🏆 Sodiqlik chegirmasi ({pct}%)", "ru": "🏆 Скидка за лояльность ({pct}%)", "en": "🏆 Loyalty discount ({pct}%)"},
    "loy_menu": {"uz": "🏆 <b>Darajangiz: {lvl}</b> · buyurtmalar: {n} ta\n{next}\n",
                 "ru": "🏆 <b>Ваш уровень: {lvl}</b> · заказов: {n}\n{next}\n",
                 "en": "🏆 <b>Your level: {lvl}</b> · orders: {n}\n{next}\n"},
    "loy_next": {"uz": "Har 5-buyurtma — <b>50% chegirma</b>! Keyingisigacha: {k} ta",
                 "ru": "Каждый 5-й заказ — <b>скидка 50%</b>! До следующей: {k}",
                 "en": "Every 5th order — <b>50% off</b>! Orders to go: {k}"},
    "loy_now": {"uz": "🎉 Keyingi buyurtmangiz — <b>50% chegirma</b> bilan!", "ru": "🎉 Ваш следующий заказ — <b>со скидкой 50%</b>!",
                "en": "🎉 Your next order is <b>50% off</b>!"},
    "loy_rules": {"uz": "🥉 Bronza · 🥈 Kumush (5+ buyurtma) −5% · 🥇 Oltin (10+) −10%",
                  "ru": "🥉 Бронза · 🥈 Серебро (5+ заказов) −5% · 🥇 Золото (10+) −10%",
                  "en": "🥉 Bronze · 🥈 Silver (5+ orders) −5% · 🥇 Gold (10+) −10%"},
    "lvl": {"uz": ["🥉 Bronza", "🥈 Kumush", "🥇 Oltin"], "ru": ["🥉 Бронза", "🥈 Серебро", "🥇 Золото"],
            "en": ["🥉 Bronze", "🥈 Silver", "🥇 Gold"]},
    "prev_msg": {"uz": "👀 <b>Buyurtma #{oid} — oldindan ko'rish</b>\nBu ishingizdan bir qism. To'liq fayl to'lovdan so'ng yuboriladi.",
                 "ru": "👀 <b>Заказ #{oid} — предпросмотр</b>\nЭто часть вашей работы. Полный файл — после оплаты.",
                 "en": "👀 <b>Order #{oid} — preview</b>\nThis is part of your work. The full file comes after payment."},
    "prev_ok": {"uz": "👀 Namuna yoqdimi? Unda to'lovni amalga oshiring 👇", "ru": "👀 Понравилось? Тогда оплатите 👇",
                "en": "👀 Like it? Then complete the payment 👇"},
    "pay_remind": {"uz": "⏰ Buyurtma #{oid} to'lovi kutilmoqda.\nTo'lov qilib, chek rasmini yuboring — ishni darhol boshlaymiz.",
                   "ru": "⏰ Ожидаем оплату заказа #{oid}.\nОплатите и пришлите фото чека — сразу начнём работу.",
                   "en": "⏰ Order #{oid} is awaiting payment.\nPay and send a photo of the receipt — we'll start right away."},
    "post_btn": {"uz": "✨ Buyurtma berish", "ru": "✨ Заказать", "en": "✨ Order now"},
}


# ------------------------------------------------------------------ 🎨 dizayn shablonlari (8 ta)
TPL = {
    1: {"uz": "Binafsha Neon", "ru": "Фиолетовый неон", "en": "Purple Neon"},
    2: {"uz": "Ko'k Kosmos", "ru": "Синий космос", "en": "Blue Cosmos"},
    3: {"uz": "Yashil Zumrad", "ru": "Изумрудный", "en": "Emerald"},
    4: {"uz": "Oq Premium", "ru": "Белый премиум", "en": "White Premium"},
    5: {"uz": "Qizil Olov", "ru": "Красный огонь", "en": "Red Fire"},
    6: {"uz": "Oltin Lyuks", "ru": "Золотой люкс", "en": "Gold Luxe"},
    7: {"uz": "Pastel Orzu", "ru": "Пастельная мечта", "en": "Pastel Dream"},
    8: {"uz": "Aurora Gradient", "ru": "Аврора", "en": "Aurora Gradient"},
}
TPL_ANY = {"uz": "🤷 Farqi yo'q", "ru": "🤷 Неважно", "en": "🤷 No preference"}
TPL_TX = {
    "album_style": {"uz": "🎨 <b>Slayd dizayn shablonlari</b> — 8 ta uslub. Pastdagi tugmalardan raqamini tanlang 👇",
                    "ru": "🎨 <b>Шаблоны дизайна слайдов</b> — 8 стилей. Выберите номер кнопкой ниже 👇",
                    "en": "🎨 <b>Slide design templates</b> — 8 styles. Pick a number with the buttons below 👇"},
    "album_cover": {"uz": "📄 <b>Muqova shablonlari</b> — 8 ta uslub. Pastdagi tugmalardan raqamini tanlang 👇",
                    "ru": "📄 <b>Шаблоны обложки</b> — 8 стилей. Выберите номер кнопкой ниже 👇",
                    "en": "📄 <b>Cover templates</b> — 8 styles. Pick a number with the buttons below 👇"},
    "gallery": {"uz": "🎨 <b>Dizayn shablonlari</b>\nBuyurtma berishda o'zingizga yoqqanini tanlaysiz.",
                "ru": "🎨 <b>Шаблоны дизайна</b>\nВыберете понравившийся при оформлении заказа.",
                "en": "🎨 <b>Design templates</b>\nYou pick the one you like when ordering."},
    "btn": {"uz": "🎨 Dizayn shablonlari", "ru": "🎨 Шаблоны дизайна", "en": "🎨 Design templates"},
}


def tpl_label(n: int, lang: str) -> str:
    return f"№{n} {TPL[n].get(lang) or TPL[n]['uz']}"


# so'rovnomada: rasm albomi + raqamli tugmalar
BRIEF_Q["style"] = {
    "uz": "🎨 <b>Dizayn shablonini tanlang</b> (yuqoridagi rasmlardan):",
    "ru": "🎨 <b>Выберите шаблон дизайна</b> (на картинках выше):",
    "en": "🎨 <b>Choose a design template</b> (pictures above):",
    "opts": {lg: [tpl_label(n, lg) for n in TPL] + [TPL_ANY[lg]] for lg in ("uz", "ru", "en")},
}
BRIEF_Q["cover"] = {
    "uz": "📄 <b>Muqova shablonini tanlang</b> (yuqoridagi rasmlardan):",
    "ru": "📄 <b>Выберите шаблон обложки</b> (на картинках выше):",
    "en": "📄 <b>Choose a cover template</b> (pictures above):",
    "opts": BRIEF_Q["style"]["opts"],
}
