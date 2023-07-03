
import logging
import time
import asyncio
import random
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.utils.exceptions import UserIsAnAdministratorOfTheChat, ChatNotFound, BadRequest, InvalidUserId
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import AdminFilter, BoundFilter, ChatTypeFilter, IDFilter
from aiogram.types import ParseMode, ChatType, ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from datetime import datetime, timedelta



# Инициализация бота
API_TOKEN = '5409271816:AAGSzzdSpAakrI3hho2N5ZeYL5_7Nja_kc4'  # Замените на свой токен бота
logging.basicConfig(level=logging.INFO)

# Использование хранилища в памяти
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)

# Инициализация диспетчера
dp = Dispatcher(bot, storage=storage)


ALLOWED_ADMINS = [5336334572, 5000817754]
OWNER = [5336334572]

CHATS = [-1001864234225, -1001983398772]


# КОМАНДА БАН
@dp.message_handler(IDFilter(user_id=ALLOWED_ADMINS), commands=['ban','бан', 'gban'], commands_prefix='/', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def ban(message: types.Message):
    try:
        # Получение аргументов команды /ban
        args = message.get_args().split()
        if len(args) < 2:
            await message.reply(f"Недостаточно аргументов. Используйте: /ban, gban, бан <user_id> <причина>;<ссылка>")
            return

        user_id = args[0]
        reason, link = ' '.join(args[1:]).split(';')

        # Отправка сообщения о бане в канал
        channel_id = -1001957728897
        try:
            text = f'<b>ID: {user_id}\nПричина: {reason}\n<a href="{link}">Доказательства</a></b>\n<b><a href="tg://user?id={user_id}">Профиль</a></b>'
            await bot.send_message(chat_id=channel_id, text=text, parse_mode='html')
        except BadRequest as e:
            logging.error(f"Error in chat {message.chat.id}: {e}")
            await bot.send_message(message.chat.id, f"Error: {e}")
            return

        # Отправка сообщения о бане в чаты из списка CHATS
        for chat_id in CHATS:
            try:
                await bot.kick_chat_member(chat_id=chat_id, user_id=user_id)
                text = f'<b><a href="tg://user?id={user_id}">Пользователь</a> забанен!</b> <b>Причину и всех, кого забанили можно посмотреть в канале</b> - <b>t.me/bezscamasuka</b>'
                await bot.send_message(chat_id=chat_id, text=text, parse_mode='html')
            except BadRequest as e:
                # Ловим ошибку BadRequest и отправляем сообщение об ошибке в чат
                logging.error(f"Error in chat {message.chat.id}: {e}")
                await message.reply(text=f"Ошибка: {e}")
                await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                return

    except Exception as e:
        logging.exception(e)
        await bot.send_message(f"Произошла ошибка: {e}")
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


#КОМАНДА БАН БЕЗ ПОСТА

@dp.message_handler(IDFilter(user_id=ALLOWED_ADMINS), AdminFilter(is_chat_admin=True), commands=['pban', 'local', 'локал'],
                        commands_prefix='/', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def pban(message: types.Message):

     # Получение аргументов команды /pban
        args = message.get_args().split()
        if len(args) < 1:
            await message.reply('Недостаточно аргументов. Используйте: /pban, local, локал <user_id>')
            return

        user_id = args[0]

        # Бан пользователя
        for chat_id in CHATS:
            try:
                await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            except BadRequest as e:
                logging.error(f"Error in chat {message.chat.id}: {e}")
                await bot.send_message(message.chat.id, f"Error: {e}")

        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)



# Команда РАЗБАН
@dp.message_handler(IDFilter(user_id=ALLOWED_ADMINS), AdminFilter(is_chat_admin=True), commands=['unban', 'анбан','разбан'],
                     commands_prefix='/', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def unban(message: types.Message):

    # Получение аргументов команды /UNBAN
    args = message.get_args().split()
    if len(args) < 1:
        await message.reply('Недостаточно аргументов. Используйте: /unban, анбан, разбан <user_id>')
        return

    user_id = args[0]

    # Разбан пользователя
    for chat_id in CHATS:
        try:
            await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
        except ChatNotFound:
            print(f'Чат {chat_id} не найден')
        except UserNotFound:
            print(f'Пользователь {user_id} не найден')

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

# Команда МУТ
@dp.message_handler(AdminFilter(is_chat_admin=True), commands=['mute', 'ротяру', 'мут'],
                        commands_prefix='/', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def mute(message: types.Message):
    args = message.text.split()
    if len(args) > 1:
        user_id = int(args[1])
    else:
        await message.reply('Ошибка! Укажите айди пользователя для мута.')
        return

    # Определение длительности мута (по умолчанию 1 день)
    till_date = "1d"
    if len(args) > 2:
        till_date = args[2]

    if till_date[-1] == "m":
        ban_for = int(till_date[:-1]) * 60
    elif till_date[-1] == "h":
        ban_for = int(till_date[:-1]) * 3600
    elif till_date[-1] == "d":
        ban_for = int(till_date[:-1]) * 86400
    else:
        ban_for = 15 * 60

    now_time = int(time.time())
    await bot.restrict_chat_member(chat_id=message.chat.id, user_id=user_id,
                                       permissions=types.ChatPermissions(can_send_messages=False,
                                                                         can_send_media_messages=False,
                                                                         can_send_other_messages=False),
                                       until_date=now_time + ban_for)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# Команда размут
@dp.message_handler(AdminFilter(is_chat_admin=True), commands_prefix='/', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['unmute', 'размут', 'анмут'])
async def un_mute_user(message: types.Message):
    try:
        user_id = int(message.text.split()[1]) # Извлекаем ID пользователя из аргументов команды
        await bot.restrict_chat_member(chat_id=message.chat.id, user_id=user_id,
                                       permissions=types.ChatPermissions(can_send_messages=True,
                                                                         can_send_media_messages=True,
                                                                         can_send_other_messages=True), )
    except (IndexError, ValueError):
        await bot.send_message(chat_id=message.chat.id, text="Пожалуйста, укажите конкретное ID пользователя.")
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# Команда АДМ
@dp.message_handler(IDFilter(user_id=ALLOWED_ADMINS), commands=['adm', 'адм', 'админ', 'выдать'],
                        commands_prefix='/', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def adm(message: types.Message):
    chat_id = message.chat.id  # Define chat_id
    user_id = message.from_user.id  # Define user_id
    chat_member = await bot.get_chat_member(chat_id, user_id)
    if chat_member.is_chat_admin:
        # Получаем ID пользователя, которому нужно выдать права администратора
        user_id = message.get_args()
        try:
            # Выдаем права администратора пользователю
            await bot.promote_chat_member(chat_id=chat_id, user_id=user_id, can_change_info=False,
                                          can_delete_messages=True, can_invite_users=True,
                                          can_restrict_members=False, can_pin_messages=True,
                                          can_promote_members=False)
            # Отправляем сообщение о успешной выдаче прав администратора
            await bot.send_message(chat_id=chat_id,
                                   text=f'Пользователь{message.from_user.full_name} теперь админ.')
        except Exception as e:
            # Отправляем сообщение об ошибке, если не удалось выдать права администратора
            await bot.send_message(chat_id=chat_id, text=f'Произошла ошибка при выдаче админки: {e}')
    else:
        # Отправляем сообщение, если пользователь не является администратором чата
        await bot.send_message(chat_id=chat_id,
                               text='У вас нет прав, чтобы назначать админов.')
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)



    # Команда УБРАТЬ АДМ
@dp.message_handler(IDFilter(user_id=ALLOWED_ADMINS), AdminFilter(is_chat_admin=True), commands_prefix='/', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['unadm', 'deadm', 'снять'])

async def remove_admin(message: types.Message):
    chat_id = message.chat.id
    user_id = message.get_args()

    # Проверяем, является ли пользователь администратором группы
    chat_member = await bot.get_chat_member(chat_id, user_id)
    if chat_member.status == "administrator":
        # Снимаем права администратора у пользователя
        await bot.promote_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False
        )
        await bot.send_message(chat_id, "Администратор успешно снят с должности.")
    else:
        await bot.send_message(chat_id, "Указанный пользователь не является администратором группы.")
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


#КОМАНДА ХАНИМУН
class ChatFilter(BoundFilter):
    def __init__(self, chat_id):
        self.chat_id = chat_id

    async def check(self, message: types.Message) -> bool:
        return message.chat.id == self.chat_id

@dp.message_handler(AdminFilter(is_chat_admin=True), commands_prefix='/', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['honeymoon'])
async def honeymoon_user(message: types.Message):
    # получаем текст сообщения
    text = message.get_args()  # отрезаем "/honeymoon "

    # разбиваем текст на составляющие
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Неверный формат команды. Пример: /honeymoon <user_id> <причина>;<ссылка>")
        return

    user_id = parts[0]  # id пользователя
    reason_link = parts[1]  # причина и ссылка
    if ';' not in reason_link:
        await message.reply("Неверный формат команды. Пример: /honeymoon <user_id> <причина>;<ссылка>")
        return

    reason, link = reason_link.split(';', maxsplit=1)

    # формируем новый текст сообщения
    new_text =f"{user_id} {reason};{link}\n<b>НУЖНО ЗАБАНИТЬ ЧУШКУ!</b>\n<b>Негр от:</b> <b>{message.from_user.full_name}</b>\n<b>Старшие админы: @yapupsek</b>\n  <b>Пример команды:</b>\n<code>/ban {user_id} {reason};{link}</code>"

    # отправляем новый текст в другой чат (здесь указываем ID чата, куда отправляем)
    await bot.send_message(chat_id='-1001653561778', text=new_text, parse_mode=types.ParseMode.HTML)

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

# Фильтр для проверки админских прав
class AdminFilter(AdminFilter):
    async def get_admin_ids(self, chat_id):
        admins = await bot.get_chat_administrators(chat_id=chat_id)
        return [admin.user.id for admin in admins]


#КОМАНДА ЗАКРЫТЬ ЧАТ
@dp.message_handler(IDFilter(user_id=ALLOWED_ADMINS), AdminFilter(is_chat_admin=True), commands_prefix= '/', commands=['off', 'офф', 'закрыть', 'close', 'disable'])
async def disable_write(message: types.Message):
    # Получаем информацию о чате
    chat_info = await bot.get_chat(message.chat.id)

    # Получаем объект ChatPermissions
    permissions = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False,
    )

    # Забираем права на отправку сообщений у всех участников
    try:
        await bot.set_chat_permissions(chat_id=message.chat.id, permissions=permissions)
    except Exception as e:
        print(f"Ошибка при отключении отправки сообщений в чате: {e}")
        await message.reply("Произошла ошибка при отключении отправки сообщений в чате.")
        return

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)



#РАЗРЕШИТЬ ПИСАТЬ
@dp.message_handler(IDFilter(user_id=ALLOWED_ADMINS), AdminFilter(is_chat_admin=True), commands_prefix='/', chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['on'])
async def enable_write(message: types.Message):
    # Получаем информацию о чате
    chat_info = await bot.get_chat(message.chat.id)

    # Получаем объект ChatPermissions
    permissions = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=False,
        can_add_web_page_previews=False,
        can_invite_users=True,
        can_pin_messages=False,
    )

    # Забираем права на отправку сообщений у всех участников
    try:
        await bot.set_chat_permissions(chat_id=message.chat.id, permissions=permissions)
    except Exception as e:
        print(f"Ошибка при включении отправки сообщений в чате: {e}")
        await bot.send_message("Произошла ошибка при включении отправки сообщений в чате.")
        return

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

user_captcha_status = {}
active_users = []

# Handler for new chat members
@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def handle_new_chat_members(message: types.Message):
    for user in message.new_chat_members:
        user_id = user.id
        if user_id not in user_captcha_status:
            user_captcha_status[user_id] = False
            await send_captcha(message.chat.id, user_id)

# Handler for messages from users
@dp.message_handler(lambda message: message.from_user.id in active_users, content_types=types.ContentType.ANY)
async def handle_message_with_captcha(message: types.Message):
    user_id = message.from_user.id
    if user_captcha_status[user_id]:
        # If the user has passed the captcha, allow message sending
        return
    else:
        # If the user has not passed the captcha, delete their messages
        await message.delete()

# Handler for captcha button clicks
@dp.callback_query_handler(lambda query: query.data.startswith('captcha_'))
async def handle_captcha_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    captcha_data = query.data.split('_')
    captcha_code = captcha_data[1]

    if user_id in user_captcha_status and not user_captcha_status[user_id] and captcha_code == captcha_data[1]:
        user_captcha_status[user_id] = True
        await query.answer('Вы успешно прошли капчу.')
        active_users.remove(user_id)
    else:
        await query.answer('Ошибка при прохождении капчи.')

# Generate a random captcha code
def generate_captcha_code():
    captcha_code = ''.join(random.choices('0123456789ABCDEF', k=6))
    return captcha_code

# Send captcha to the user in the chat
async def send_captcha(chat_id, user_id):
    captcha_code = generate_captcha_code()
    keyboard = types.InlineKeyboardMarkup()
    button_text = 'Пройти капчу'
    callback_data = f'captcha_{captcha_code}_{user_id}'
    button = types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
    keyboard.add(button)
    await bot.send_message(chat_id, 'Для продолжения общения пройдите капчу:', reply_markup=keyboard)
    active_users.append(user_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

