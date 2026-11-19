"""
@MyBirzumda_bot — mybirzumda.uz saytiga kirish boti (SITE_LOGIN_BOT_TOKEN).

Sayt «Kirish» → t.me/MyBirzumda_bot?start=login_X → bot darhol kiritadi (tasdiq shart emas).
Himoya: xabar ostida «🚫 Bu men emasman» — shu akkauntning saytdagi barcha sessiyalari bekor bo'ladi.
Tayyorla bilan bitta jarayonda ishlaydi, shuning uchun site_api.PENDING ni ko'radi.
"""
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

import site_api

SITE = os.getenv("SITE_URL", "https://mybirzumda.uz")
TX = {
    "uz": {"ok": "✅ <b>Siz akkauntga kirdingiz!</b>\nSaytga qayting — kabinet o'zi ochiladi.",
           "back": "🌐 Saytga qaytish", "notme": "🚫 Bu men emasman",
           "old": "⌛ Havola eskirgan. Saytda «Kirish»ni qaytadan bosing.",
           "revoked": "🔒 Saytdagi barcha kirishlar bekor qilindi. Akkauntingiz xavfsiz.",
           "hello": "👋 Bu — <b>mybirzumda.uz</b> saytiga kirish boti.\nSaytda «Kirish» tugmasini bosing — shu yerga qaytasiz va akkaunt ochiladi."},
    "ru": {"ok": "✅ <b>Вы вошли в аккаунт!</b>\nВернитесь на сайт — кабинет откроется сам.",
           "back": "🌐 Вернуться на сайт", "notme": "🚫 Это не я",
           "old": "⌛ Ссылка устарела. Нажмите «Войти» на сайте ещё раз.",
           "revoked": "🔒 Все входы на сайт отменены. Аккаунт в безопасности.",
           "hello": "👋 Это бот входа на сайт <b>mybirzumda.uz</b>.\nНажмите на сайте «Войти» — вы вернётесь сюда, и аккаунт откроется."},
    "en": {"ok": "✅ <b>You're logged in!</b>\nGo back to the site — your account opens by itself.",
           "back": "🌐 Back to the site", "notme": "🚫 This wasn't me",
           "old": "⌛ This link has expired. Tap «Log in» on the site again.",
           "revoked": "🔒 All site logins have been cancelled. Your account is safe.",
           "hello": "👋 This is the login bot for <b>mybirzumda.uz</b>.\nTap «Log in» on the site and your account opens here."},
}
router = Router()


def _lang(code, fallback="uz"):
    code = (code or "")[:2]
    return code if code in TX else fallback


@router.message(CommandStart())
async def start(m: Message, command: CommandObject):
    arg = (command.args or "").strip()
    if not arg.startswith("login_"):
        await m.answer(TX[_lang(m.from_user.language_code)]["hello"])
        return
    v = site_api.quick_pending(arg[6:])
    q = TX[_lang(v["lang"] if v else m.from_user.language_code)]
    if not v or not site_api.quick_confirm(arg[6:], m.from_user):
        await m.answer(q["old"])
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=q["back"], url=SITE + "/cabinet.html")],
        [InlineKeyboardButton(text=q["notme"], callback_data=f"rv:{m.from_user.id}:{v['lang']}")]])
    await m.answer(q["ok"], reply_markup=kb)


@router.callback_query(F.data.startswith("rv:"))
async def revoke(c: CallbackQuery):
    _, uid, lang = c.data.split(":")
    if int(uid) != c.from_user.id:
        await c.answer()
        return
    site_api.quick_revoke(c.from_user.id)
    q = TX[_lang(lang)]
    await c.answer("🔒")
    await c.message.edit_text(q["revoked"])


def build():
    token = next((t.strip() for t in os.getenv("SITE_LOGIN_BOT_TOKEN", "").split(",") if t.strip()), "")
    if not token:
        return None, None
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    return bot, dp
