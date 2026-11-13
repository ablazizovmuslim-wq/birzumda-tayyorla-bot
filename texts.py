"""Bot matnlari: o'zbekcha (uz), ruscha (ru), inglizcha (en).

Matn ichida {e[kalit]} — premium emoji (bot.py dagi pe() orqali qo'yiladi),
{nom} — o'zgaruvchilar (summa, raqam va h.k.).
"""

LANGS = {"uz": "🇺🇿 O'zbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
DEFAULT_LANG = "uz"

# ------------------------------------------------------------------ menyu tugmalari
BTN = {
    "app":      {"uz": "✨ Mini ilova", "ru": "✨ Мини-приложение", "en": "✨ Mini App"},
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
                "start": ("Start", "10–12 слайдов, современный дизайн, 1 день"),
                "pro": ("Professional", "15–20 слайдов, анимация, диаграммы, 🐢 Черепаха-учитель, 1–2 дня"),
                "premium": ("Premium", "20–25 слайдов, Morph, неон, 🐢 Черепаха-учитель, текст речи, 2–3 дня")}},
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
            "portfolio": {"name": "Портфолио", "desc": "Аттестация и конкурс «Лучший тьютор»"},
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
                "start": ("Start", "10–12 slides, modern design, 1 day"),
                "pro": ("Professional", "15–20 slides, animation, charts, 🐢 Turtle teacher, 1–2 days"),
                "premium": ("Premium", "20–25 slides, Morph, neon design, 🐢 Turtle teacher, speech text, 2–3 days")}},
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
            "portfolio": {"name": "Portfolio", "desc": "Attestation and «Best tutor» contest"},
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
               "{e[image]} Professional dizayn · 🐢 Toshbaqa o'qituvchi (Pro va Premium)\n"
               "{e[fire]} O'z vaqtida va bepul tuzatish\n\n"
               "{e[orders]} <b>Qanday ishlaydi?</b>\n"
               "{e[n1]} «Buyurtma berish» → talaba yoki ustoz\n"
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
               "{e[image]} Профессиональный дизайн · 🐢 Черепаха-учитель (Pro и Premium)\n"
               "{e[fire]} Вовремя и бесплатные правки\n\n"
               "{e[orders]} <b>Как это работает?</b>\n"
               "{e[n1]} «Заказать» → студент или преподаватель\n"
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
               "{e[image]} Professional design · 🐢 Turtle teacher (Pro and Premium)\n"
               "{e[fire]} On time, free revisions\n\n"
               "{e[orders]} <b>How it works</b>\n"
               "{e[n1]} «Place an order» → student or teacher\n"
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
        "uz": "⚡ Shoshilinch buyurtma: <b>+{pct}%</b>\n🔁 Tuzatishlar bepul\n🐢 Pro va Premium paketlarda — Toshbaqa o'qituvchi\n\nBuyurtma berish uchun tugmani bosing 👇",
        "ru": "⚡ Срочный заказ: <b>+{pct}%</b>\n🔁 Правки бесплатно\n🐢 В пакетах Pro и Premium — Черепаха-учитель\n\nНажмите кнопку, чтобы заказать 👇",
        "en": "⚡ Urgent order: <b>+{pct}%</b>\n🔁 Free revisions\n🐢 Pro and Premium include the Turtle teacher\n\nTap the button to order 👇"},
    "samples_soon": {"uz": "Namunalar tez orada qo'shiladi 🙂", "ru": "Примеры скоро появятся 🙂", "en": "Samples coming soon 🙂"},
    "samples_intro": {
        "uz": "Mana ishlarimdan namunalar 👇\n<i>Animatsiyalar kompyuterdagi PowerPoint'da to'liq ko'rinadi.</i>",
        "ru": "Вот примеры моих работ 👇\n<i>Анимации полностью видны в PowerPoint на компьютере.</i>",
        "en": "Here are samples of my work 👇\n<i>Animations play fully in PowerPoint on a computer.</i>"},
    "no_orders": {
        "uz": "Sizda hali buyurtma yo'q. «🛒 Buyurtma berish» tugmasini bosing.",
        "ru": "У вас пока нет заказов. Нажмите «🛒 Заказать».",
        "en": "You have no orders yet. Tap «🛒 Place an order»."},
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
        "uz": "📎 <b>Fayl yoki rasm bormi?</b> (namuna, topshiriq sharti, rasmlar)\nYuboring, tugatgach «✅ Tayyor» tugmasini bosing. Bo'lmasa — o'tkazib yuboring.",
        "ru": "📎 <b>Есть файлы или фото?</b> (образец, условие задания, картинки)\nОтправьте и нажмите «✅ Готово». Если нет — пропустите.",
        "en": "📎 <b>Any files or photos?</b> (sample, task, images)\nSend them, then tap «✅ Done». If not — skip."},
    "files_max": {"uz": "Ko'pi bilan 10 ta fayl. «✅ Tayyor» ni bosing.", "ru": "Максимум 10 файлов. Нажмите «✅ Готово».",
                  "en": "10 files at most. Tap «✅ Done»."},
    "files_got": {"uz": "Qabul qilindi ({n} ta). Yana yuboring yoki «✅ Tayyor» ni bosing.",
                  "ru": "Принято ({n}). Отправьте ещё или нажмите «✅ Готово».",
                  "en": "Received ({n}). Send more or tap «✅ Done»."},
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
    "paid_ok": {"uz": "✅ To'lov tasdiqlandi! Buyurtma #{oid} tayyorlanmoqda 🛠", "ru": "✅ Оплата подтверждена! Заказ #{oid} в работе 🛠",
                "en": "✅ Payment confirmed! Order #{oid} is in progress 🛠"},
    "rejected": {"uz": "❌ Buyurtma #{oid} bo'yicha to'lov tasdiqlanmadi.\nSavol bo'lsa: {contact}",
                 "ru": "❌ Оплата по заказу #{oid} не подтверждена.\nВопросы: {contact}",
                 "en": "❌ Payment for order #{oid} was not confirmed.\nQuestions: {contact}"},
    "done": {"uz": "🎉 Buyurtma #{oid} tayyor! Rahmat 🙏\nTuzatish kerak bo'lsa yozing: {contact}",
             "ru": "🎉 Заказ #{oid} готов! Спасибо 🙏\nНужны правки — пишите: {contact}",
             "en": "🎉 Order #{oid} is ready! Thank you 🙏\nNeed changes? Write to: {contact}"},
    "file_cap": {"uz": "📦 Buyurtma #{oid}", "ru": "📦 Заказ #{oid}", "en": "📦 Order #{oid}"},
    "loose_file": {"uz": "Fayl qabul qilindi. Buyurtma berish uchun «🛒 Buyurtma berish» tugmasini bosing.",
                   "ru": "Файл получен. Чтобы заказать, нажмите «🛒 Заказать».",
                   "en": "File received. To order, tap «🛒 Place an order»."},
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
               "• <b>Professional</b> — animatsiya, diagrammalar, 🐢\n"
               "• <b>Premium</b> — Morph, neon dizayn, nutq matni, 🐢\n"
               "🐢 <b>Toshbaqa o'qituvchi</b> — slaydda gapirib, mavzuni tushuntiradi (Pro va Premium)\n\n"
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
               "• <b>Professional</b> — анимация, диаграммы, 🐢\n"
               "• <b>Premium</b> — Morph, неон, текст речи, 🐢\n"
               "🐢 <b>Черепаха-учитель</b> — говорит на слайдах и объясняет тему (Pro и Premium)\n\n"
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
               "• <b>Professional</b> — animation, charts, 🐢\n"
               "• <b>Premium</b> — Morph, neon design, speech text, 🐢\n"
               "🐢 <b>Turtle teacher</b> — talks on the slides and explains the topic (Pro and Premium)\n\n"
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
           ("info", "Bot haqida ma'lumot"), ("channel", "Kanalimizga obuna bo'lish"), ("lang", "Tilni o'zgartirish"),
           ("privacy", "Maxfiylik siyosati")],
    "ru": [("start", "Запустить бота"), ("order", "Сделать заказ"), ("bonus", "Бонусы и акции"),
           ("info", "Информация о боте"), ("channel", "Подписаться на канал"), ("lang", "Сменить язык"),
           ("privacy", "Политика конфиденциальности")],
    "en": [("start", "Start the bot"), ("order", "Place an order"), ("bonus", "Bonuses & promos"),
           ("info", "About the bot"), ("channel", "Subscribe to our channel"), ("lang", "Change language"),
           ("privacy", "Privacy policy")],
}

# Bot profili: «Bu bot nima qila oladi?» (description, 512 belgigacha) va qisqa tavsif (about, 120 belgigacha)
DESCRIPTION = {
    "uz": ("🎓 Talabalar va 👩‍🏫 ustozlar uchun tez va chiroyli tayyorlaymiz: slayd, mustaqil ish, kurs ishi, "
           "maqola, referat, portfolio, O'UM, dars ishlanmasi, testlar.\n\n"
           "📦 Start · Professional · Premium\n"
           "🐢 Toshbaqa o'qituvchi — slaydda gapirib tushuntiradi (Pro, Premium)\n"
           "⚡ Shoshilinch · 🔁 Bepul tuzatish\n"
           "🎁 Do'st taklif qiling — bonus oling · 🎟 promokodlar\n"
           "🌐 O'zbekcha · Русский · English\n\n{channel_line}"
           "📥 Video yuklash: {yukla}\n"
           "💜 Admin: {contact}"),
    "ru": ("🎓 Студентам и 👩‍🏫 преподавателям быстро и красиво: слайды, самостоятельные, курсовые, "
           "статьи, рефераты, портфолио, УМК, разработки уроков, тесты.\n\n"
           "📦 Start · Professional · Premium\n"
           "🐢 Черепаха-учитель — объясняет тему голосом (Pro, Premium)\n"
           "⚡ Срочно · 🔁 Бесплатные правки\n"
           "🎁 Приглашайте друзей — бонусы · 🎟 промокоды\n"
           "🌐 O'zbekcha · Русский · English\n\n{channel_line}"
           "📥 Скачать видео: {yukla}\n"
           "💜 Админ: {contact}"),
    "en": ("🎓 For students and 👩‍🏫 teachers: slides, independent work, term papers, articles, essays, "
           "portfolios, teaching materials, lesson plans, tests — fast and beautiful.\n\n"
           "📦 Start · Professional · Premium\n"
           "🐢 Turtle teacher — explains the topic out loud (Pro, Premium)\n"
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
