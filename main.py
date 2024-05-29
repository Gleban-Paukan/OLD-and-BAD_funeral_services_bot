import telebot
import qrcode
from telebot import types
from datetime import datetime
from fast_bitrix24 import Bitrix
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from requests.exceptions import ConnectionError, ReadTimeout
import os, sys

bot = telebot.TeleBot('')
start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
start_markup.add(
    types.KeyboardButton('Описание Партнерской программы')
)
start_markup.add(
    types.KeyboardButton('Виды аккаунтов в Партнерской программе')
)
start_markup.add(
    types.KeyboardButton('В чем различие аккаунтов?')
)
start_markup.add(
    types.KeyboardButton('Выбрать Верифицированный аккаунт')
)
start_markup.add(
    types.KeyboardButton('Поддержка')
)
ref_id = {}
bot.parse_mode = 'html'

phone_id = {}
FIO_id = {}
mail_id = {}
time_id = {}


@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        if message.chat.type == 'private':
            with open('users_id.txt', 'r') as users_id:
                user_set = set()
                for i in users_id:
                    user_set.add(i.replace('\n', ''))
            if str(message.chat.id) not in user_set:
                with open('users_id.txt', 'a') as users_id:
                    users_id.write(str(message.chat.id) + '\n')
                with open('users_id.txt', 'r') as users_id:
                    user_set = set()
                    for i in users_id:
                        user_set.add(i.replace('\n', ''))
                with open('ref_got.txt', 'a') as non_set_ref:
                    non_set_ref.write(str(message.chat.id) + ' ' + '0' + '\n')
                with open('time_id.txt', 'a') as non_set_sub:
                    non_set_sub.write(str(message.chat.id) + ' ' + str((datetime.now()).strftime('%Y-%m-%d')) + '\n')
                if " " in message.text:
                    referrer_candidate = message.text.split()[1]
                    if str(message.chat.id) != referrer_candidate:
                        referer = referrer_candidate
                        with open('ref_id.txt', 'a') as non_set_ref:
                            non_set_ref.write(str(message.chat.id) + ' ' + referer + '\n')
                        ref_id[str(message.chat.id)] = referer
            bot.send_message(message.chat.id,
                             'Здравствуйте, <b>{0.first_name}</b>'.format(message.from_user, bot.get_me()),
                             reply_markup=define_markup(message))
    except Exception as er:
        print(er)


@bot.message_handler(content_types=['text'])
def main_handler(message):
    try:
        with open('verif_id.txt', 'r', encoding="cp1251") as users_ver:
            user_ver = set()
            for i in users_ver:
                user_ver.add(i.replace('\n', ''))
        with open('ref_id.txt', encoding="cp1251") as file:
            for line in file:
                key, *value = line.split()
                ref_id[key] = value[0]
        with open('user_phone.txt', encoding="cp1251") as file:
            for line in file:
                key, *value = line.split()
                phone_id[key] = value[0]
        with open('users_FIO.txt', encoding="cp1251") as file:
            for line in file:
                key, *value = line.split()
                FIO_id[key] = value[0]
        with open('users_mail.txt', encoding="cp1251") as file:
            for line in file:
                key, *value = line.split()
                mail_id[key] = value[0]
        if message.chat.type == 'private':
            if message.text == 'Выбрать Верифицированный аккаунт':
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(types.InlineKeyboardButton('✅ Ознакомился и согласен', callback_data='agree_verif'))
                with open('codes.txt', 'rb') as file:
                    bot.send_message(message.chat.id, 'Для продолжения необходио согласиться договором-офертой',
                                     reply_markup=markup)
            elif message.text == 'Профиль':
                if str(message.chat.id) in user_ver:
                    with open('codes.txt', 'r') as file:
                        codes = []
                        for i in file:
                            codes.append(i.replace('\n', ''))

                    bot.send_message(message.chat.id,

                                     f'''
Ващ профиль партнёра:

ФИО: <b>{FIO_id[str(message.chat.id)].replace('_', ' ')}</b>
e-mail: <b>{mail_id[str(message.chat.id)]}</b>
Телефон: <b>{phone_id[str(message.chat.id)]}</b>

Ваша партнерская ссылка: http://LINK_IS_PRIVATE/?utm_source={len(user_ver) + 2}&utm_medium=cart&utm_content={codes[len(user_ver) - 1]}
Ваш промокод: <code> {codes[len(user_ver) - 1]} </code>
                    '''
                                     )
                    bot.send_message(message.chat.id, 'Ваш QR-код:')
                    img = qrcode.make(
                        f'http://LINK_IS_PRIVATE/?utm_source={len(user_ver) + 2}&utm_medium=cart&utm_content={codes[len(user_ver) - 1]}')
                    type(img)  # qrcode.image.pil.PilImage
                    img.save("qr.png")
                    with open('qr.png', 'rb') as file:
                        bot.send_photo(message.chat.id, file, reply_markup=define_markup(message))
                else:
                    bot.send_message(message.chat.id, 'Вы ещё не создали профиль.')
            elif message.text == 'Поддержка':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton('⛔️ Закрыть обращение')
                item2 = types.KeyboardButton('🌀 Главное меню')
                markup.add(item1, item2)
                bot.send_message(message.chat.id,
                                 'Напишите ваше обращение ниже. Мы ответим в течении суток.\n\n⛔️ Для закрытия обращения, нажмите кнопку «<b>Закрыть обращение</b>»',
                                 reply_markup=markup)
                bot.register_next_step_handler(message, peresil)
        else:
            if '/send' in str(message.text):
                id = str(message.text)[
                     len('/send') + 1:len('/send') + 1 + (str(message.text)[len('/send') + 1:].find(' '))]
                bot.send_message(int(id), str(message.text)[
                                          len('/send') + 2 + (str(message.text)[len('/send') + 1:].find(' ')):])
            else:
                if message.reply_to_message.forward_from != None:
                    bot.send_message(message.reply_to_message.forward_from.id, message.text)
                else:
                    bot.send_message(message.chat.id, 'У пользователя анонимка')
    except Exception as er:
        print(er)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        with open('verif_id.txt', 'r', encoding="cp1251") as users_ver:
            user_ver = set()
            for i in users_ver:
                user_ver.add(i.replace('\n', ''))
        with open('ref_id.txt', encoding="cp1251") as file:
            for line in file:
                key, *value = line.split()
                ref_id[key] = value[0]
        with open('user_phone.txt', encoding="cp1251") as file:
            for line in file:
                key, *value = line.split()
                phone_id[key] = value[0]
        with open('users_FIO.txt', encoding="cp1251") as file:
            for line in file:
                key, *value = line.split()
                FIO_id[key] = value[0]
        with open('users_mail.txt', encoding="cp1251") as file:
            for line in file:
                key, *value = line.split()
                mail_id[key] = value[0]
        with open('time_id.txt', encoding="cp1251") as file:
            for line in file:
                key, *value = line.split()
                time_id[key] = value[0]
        if call.message:
            if call.data == 'agree_verif':
                msg = bot.send_message(call.message.chat.id, 'Введите: <b>ФИО</b>.')
                bot.register_next_step_handler(msg, FIO_remember)
            elif call.data == 'verif_2':
                with open('verif_id.txt', 'a') as users_mail:
                    users_mail.write(str(call.message.chat.id) + '\n')
                with open('verif_id.txt', 'r', encoding="cp1251") as users_ver:
                    user_ver = set()
                    for i in users_ver:
                        user_ver.add(i.replace('\n', ''))
                with open('codes.txt', 'r') as file:
                    codes = []
                    for i in file:
                        codes.append(i.replace('\n', ''))

                bot.send_message(call.message.chat.id,

                                 f'''
Ваш профиль создан.

ФИО: <b>{FIO_id[str(call.message.chat.id)].replace('_', ' ')}</b>
e-mail: <b>{mail_id[str(call.message.chat.id)]}</b>
Телефон: <b>{phone_id[str(call.message.chat.id)]}</b>

Ваша партнерская ссылка: http://LINK_IS_PRIVATE/?utm_source={len(user_ver) + 2}&utm_medium=cart&utm_content={codes[len(user_ver) - 1]}
Ваш промокод: <code> {codes[len(user_ver) - 1]} </code>
'''
                                 )
                value = [[FIO_id[str(call.message.chat.id)].replace('_', ' '), mail_id[str(call.message.chat.id)],
                          phone_id[str(call.message.chat.id)], time_id[str(call.message.chat.id)]]]
                google_sheets_registration(value)
                bot.send_message(call.message.chat.id, 'Ваш QR-код:')
                img = qrcode.make(
                    f'http://LINK_IS_PRIVATE/?utm_source={len(user_ver) + 2}&utm_medium=cart&utm_content={codes[len(user_ver) - 1]}')
                type(img)  # qrcode.image.pil.PilImage
                img.save("qr.png")
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

                markup.add(
                    types.KeyboardButton('Описание Партнерской программы')
                )
                markup.add(
                    types.KeyboardButton('Виды аккаунтов в Партнерской программе')
                )
                markup.add(
                    types.KeyboardButton('В чем различие аккаунтов?')
                )
                markup.add(
                    types.KeyboardButton('Профиль')
                )
                markup.add(
                    types.KeyboardButton('Поддержка')
                )
                with open('qr.png', 'rb') as file:
                    bot.send_photo(call.message.chat.id, file, reply_markup=markup)
                with open('users_code.txt', 'a') as users_mail:
                    users_mail.write(str(call.message.chat.id) + ' ' + codes[len(user_ver) - 1] + '\n')
                b = Bitrix('https://LINK_IS_PRIVATE/rest/28/gnkpy90z0o8icq4v/')
                data = FIO_id[str(call.message.chat.id)].replace('_', ' ').split()
                q = (b.call('crm.contact.add', items={"fields": {
                    "NAME": data[1],
                    "SECOND_NAME": data[2],
                    "LAST_NAME": data[0],
                    "OPENED": "Y",
                    "ASSIGNED_BY_ID": 1,
                    "TYPE_ID": "PARTNER",
                    "PHONE": [{"VALUE": phone_id[str(call.message.chat.id)], "VALUE_TYPE": "WORK"}],
                    'COMMENTS': str(call.message.chat.id),
                    'SOURCE_DESCRIPTION': 'Телеграм-бот.',
                    'EMAIL': mail_id[str(call.message.chat.id)]
                }}))
                with open('users_bx.txt', 'a') as users_mail:
                    users_mail.write(str(call.message.chat.id) + ' ' + str(q) + '\n')
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    except Exception as er:
        print(er)


def google_sheets_registration(values):
    sheet = get_service_sacc().spreadsheets()

    sheet_id = ""

    sheet.values().append(
        spreadsheetId=sheet_id,
        range="Партнёры",
        valueInputOption="RAW",
        body={'values': values}).execute()


def peresil(message):
    markup = define_markup(message)
    if message.text == '🌀 Главное меню':
        bot.send_message(message.chat.id, '❇️ Вы перешли в <b>Главное меню</b>', reply_markup=markup)
    elif message.text != '⛔️ Закрыть обращение':
        bot.forward_message(-1001708903938, message.chat.id, message.message_id)
        if type(message.chat.username) != str:
            user_name = 'Пользователь его не указал'
        else:
            user_name = message.chat.username
        bot.send_message(-1001708903938, f'ID пользователя <code>{message.chat.id}</code>, username: @{user_name}')
        bot.send_message(message.chat.id, 'Ваше обращение открыто. Ожидайте ответа модератора.')
        bot.register_next_step_handler(message, peresil_1)
    else:
        bot.send_message(message.chat.id, 'Ваше обращение закрыто.', reply_markup=markup)


def peresil_1(message):
    markup = define_markup(message)
    if message.text == '🌀 Главное меню':
        bot.send_message(message.chat.id, '❇️ Вы перешли в <b>Главное меню</b>', reply_markup=markup)
    elif message.text != '⛔️ Закрыть обращение':
        bot.forward_message(-1001708903938, message.chat.id, message.message_id)
        bot.register_next_step_handler(message, peresil_1)
    else:
        bot.send_message(message.chat.id, 'Ваше обращение закрыто.', reply_markup=markup)
        bot.send_message(-1001708903938,
                         f'Обращение пользователя <ins><i>{message.from_user.first_name}</i></ins> закрыто.')


def define_markup(message):
    with open('verif_id.txt', 'r', encoding="cp1251") as users_ver:
        user_ver = set()
        for i in users_ver:
            user_ver.add(i.replace('\n', ''))
    if str(message.chat.id) in user_ver:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        markup.add(
            types.KeyboardButton('Описание Партнерской программы')
        )
        markup.add(
            types.KeyboardButton('Виды аккаунтов в Партнерской программе')
        )
        markup.add(
            types.KeyboardButton('В чем различие аккаунтов?')
        )
        markup.add(
            types.KeyboardButton('Профиль')
        )
        markup.add(
            types.KeyboardButton('Поддержка')
        )
    else:
        markup = start_markup
    return markup


def FIO_remember(message):
    if message.text == '🌀 Главное меню':
        bot.send_message(message.chat.id, 'Вы перешли в <b>Главное меню</b>', reply_markup=start_markup)
    else:
        if '\n' not in message.text and str(message.text).count(' ') == 2:
            with open('users_FIO.txt', 'a') as users_mail:
                users_mail.write(str(message.chat.id) + ' ' + str(message.text).replace(' ', '_') + '\n')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('🔙 Назад'))
            msg = bot.send_message(message.chat.id, 'Введите: <b>e-mail</b>.', reply_markup=markup)
            bot.register_next_step_handler(msg, e_mail_remember)
        else:
            bot.send_message(message.chat.id, 'Вы неверно указали ваши ФИО, попробуйте ещё раз.')
            bot.register_next_step_handler(message, FIO_remember)


def e_mail_remember(message):
    if message.text == '🔙 Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item0 = types.KeyboardButton('🌀 Главное меню')
        markup.add(item0)
        msg = bot.send_message(message.chat.id,
                               'Введите: <b>ФИО</b>',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, FIO_remember)
    elif message.text == '🌀 Главное меню':
        bot.send_message(message.chat.id, 'Вы перешли в <b>Главное меню</b>', reply_markup=start_markup)
    else:
        if (' ' or '\n') not in message.text and (('@' and '.') in message.text):
            with open('users_mail.txt', 'a') as users_mail:
                users_mail.write(str(message.chat.id) + ' ' + str(message.text) + '\n')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('🌀 Главное меню'), types.KeyboardButton('🔙 Назад'))
            bot.send_message(message.chat.id,
                             'Введите ваш: <b>Номер телефона</b>.',
                             reply_markup=markup)
            bot.register_next_step_handler(message, phone_remember)
        else:
            bot.send_message(message.chat.id, 'Вы неверно указали email, попробуйте ещё раз.')
            bot.register_next_step_handler(message, e_mail_remember)


def phone_remember(message):
    if message.text == '🔙 Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('🌀 Главное меню'), types.KeyboardButton('🔙 Назад'))
        msg = bot.send_message(message.chat.id,
                               'Введите: <b>e-mail</b>.',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, phone_remember)
    elif message.text == '🌀 Главное меню':
        bot.send_message(message.chat.id, 'Вы перешли в <b>Главное меню</b>', reply_markup=start_markup)
    else:
        if '\n' not in message.text and ' ' not in message.text and str(message.text).isdigit():
            with open('user_phone.txt', 'a') as users_mail:
                users_mail.write(str(message.chat.id) + ' ' + str(message.text) + '\n')
            markup = types.InlineKeyboardMarkup(row_width=1)
            item6 = types.InlineKeyboardButton('Я согласен ✅', callback_data='verif_2')
            markup.add(item6)
            bot.send_message(message.chat.id, 'Подтвердите согласие', reply_markup=markup)
        else:
            bot.send_message(message.chat.id,
                             'Вы неверно указали номер телефона, попробуйте ещё раз в формате <b>7xxxxxxxxxx</b>.')
            bot.register_next_step_handler(message, phone_remember)


def get_service_sacc():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


bot.polling()
