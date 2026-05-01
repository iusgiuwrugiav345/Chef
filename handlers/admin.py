from aiogram import types

from bot import bot, dp
from configurebot import cfg
from handlers.db import (
    db_profile_access,
    db_profile_exist,
    db_profile_exist_usr,
    db_profile_get_usrname,
    db_profile_updateone,
)


errormessage = cfg["error_message"]
lvl1name = cfg["1lvl_adm_name"]
lvl2name = cfg["2lvl_adm_name"]
lvl3name = cfg["3lvl_adm_name"]
devid = cfg["dev_id"]
support_chat_id = cfg["teh_chat_id"]


def extract_arg(arg):
    return arg.split()[1:]


def is_owner(uid):
    return bool(devid) and uid == devid


def has_access(uid, level):
    return is_owner(uid) or db_profile_access(uid) >= level


async def notify_dev(cid, error):
    if not devid:
        return

    try:
        await bot.send_message(
            devid,
            f"Admin error in chat *{cid}*\nStatus: `{error}`",
            parse_mode="Markdown",
        )
    except Exception:
        pass


async def admin_ot(message: types.Message):
    try:
        uid = message.from_user.id
        allow_reply = is_owner(uid) or (support_chat_id and message.chat.id == support_chat_id)
        if not allow_reply and not has_access(uid, 1):
            await message.reply(
                "У вас нет доступа к этой команде. Нужен уровень доступа 1 или выше.",
                parse_mode="Markdown",
            )
            return

        args = extract_arg(message.text)
        if len(args) < 2:
            await message.reply(
                "Укажите аргументы команды.\nПример: `/ответ 516712732 Ваш ответ`",
                parse_mode="Markdown",
            )
            return

        chatid = int(args[0])
        answer = " ".join(args[1:]).strip()
        await message.reply("Вы успешно ответили на вопрос.")
        await bot.send_message(
            chatid,
            f"Новое уведомление!\nОтвет от техподдержки:\n\n`{answer}`",
            parse_mode="Markdown",
        )
    except Exception as error:
        await message.answer(errormessage, parse_mode="Markdown")
        await notify_dev(message.chat.id, error)


async def admin_giveaccess(message: types.Message):
    try:
        uidown = message.from_user.id
        if not has_access(uidown, 3):
            await message.reply(
                "У вас нет доступа к этой команде. Нужен уровень доступа 3.",
                parse_mode="Markdown",
            )
            return

        args = extract_arg(message.text)
        if len(args) != 2:
            await message.reply(
                "Укажите аргументы команды.\nПример: `/доступ 516712372 1`",
                parse_mode="Markdown",
            )
            return

        uid = int(args[0])
        access = int(args[1])
        if not db_profile_exist(uid):
            await message.reply("Этого пользователя не существует!", parse_mode="Markdown")
            return

        if access == 0:
            outmsg = "Вы успешно сняли все доступы с этого человека!"
        elif access == 1:
            outmsg = f"Вы успешно выдали доступ *{lvl1name}* данному человеку!"
        elif access == 2:
            outmsg = f"Вы успешно выдали доступ *{lvl2name}* данному человеку!"
        elif access == 3:
            outmsg = f"Вы успешно выдали доступ *{lvl3name}* данному человеку!"
        else:
            await message.reply(
                "Максимальный уровень доступа: *3*",
                parse_mode="Markdown",
            )
            return

        db_profile_updateone({"_id": uid}, {"$set": {"access": access}})
        await message.reply(outmsg, parse_mode="Markdown")
    except Exception as error:
        await message.answer(errormessage, parse_mode="Markdown")
        await notify_dev(message.chat.id, error)


async def admin_ban(message: types.Message):
    try:
        uidown = message.from_user.id
        if not has_access(uidown, 2):
            await message.reply(
                "У вас нет доступа к этой команде. Нужен уровень доступа 2.",
                parse_mode="Markdown",
            )
            return

        args = extract_arg(message.text)
        if len(args) != 2:
            await message.reply(
                "Укажите аргументы команды.\nПример: `/бан 51623722 Причина`",
                parse_mode="Markdown",
            )
            return

        uid = int(args[0])
        reason = args[1]
        if not db_profile_exist(uid):
            await message.reply("Этого пользователя не существует!", parse_mode="Markdown")
            return

        db_profile_updateone({"_id": uid}, {"$set": {"ban": 1}})
        await message.reply(
            f"Вы успешно забанили этого пользователя.\nПричина: `{reason}`",
            parse_mode="Markdown",
        )
        await bot.send_message(
            uid,
            f"Администратор *заблокировал* вас в боте.\nПричина: `{reason}`",
            parse_mode="Markdown",
        )
    except Exception as error:
        await message.answer(errormessage, parse_mode="Markdown")
        await notify_dev(message.chat.id, error)


async def admin_unban(message: types.Message):
    try:
        uidown = message.from_user.id
        if not has_access(uidown, 2):
            await message.reply(
                "У вас нет доступа к этой команде. Нужен уровень доступа 2.",
                parse_mode="Markdown",
            )
            return

        args = extract_arg(message.text)
        if len(args) != 1:
            await message.reply(
                "Укажите аргументы команды.\nПример: `/разбан 516272834`",
                parse_mode="Markdown",
            )
            return

        uid = int(args[0])
        if not db_profile_exist(uid):
            await message.reply("Этого пользователя не существует!", parse_mode="Markdown")
            return

        db_profile_updateone({"_id": uid}, {"$set": {"ban": 0}})
        await message.reply("Вы успешно разблокировали этого пользователя", parse_mode="Markdown")
        await bot.send_message(
            uid,
            "Администратор *разблокировал* вас в боте!",
            parse_mode="Markdown",
        )
    except Exception as error:
        await message.answer(errormessage, parse_mode="Markdown")
        await notify_dev(message.chat.id, error)


async def admin_id(message: types.Message):
    try:
        args = extract_arg(message.text)
        if len(args) != 1:
            await message.reply(
                "Укажите аргументы команды.\nПример: `/айди username`",
                parse_mode="Markdown",
            )
            return

        username = args[0]
        if not db_profile_exist_usr(username):
            await message.reply("Этого пользователя не существует!", parse_mode="Markdown")
            return

        uid = db_profile_get_usrname(username, "_id")
        await message.reply(f"ID: `{uid}`", parse_mode="Markdown")
    except Exception as error:
        await message.answer(errormessage, parse_mode="Markdown")
        await notify_dev(message.chat.id, error)


def register_handler_admin():
    dp.register_message_handler(admin_ot, commands=["ответ", "ot", "answer"])
    dp.register_message_handler(admin_giveaccess, commands=["доступ", "access"])
    dp.register_message_handler(admin_ban, commands=["бан", "ban"])
    dp.register_message_handler(admin_unban, commands=["разбан", "unban"])
    dp.register_message_handler(admin_id, commands=["айди", "id"])
