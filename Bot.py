import telebot
from telebot import types

import pymysql

import random
import requests

import threading

bot = telebot.TeleBot('token')

keyboardReg = telebot.types.ReplyKeyboardMarkup(True, True)
keyboardReg.row('Регистрация', 'Поддержать')

keyboardStart = telebot.types.ReplyKeyboardMarkup(True, True)
keyboardStart.row('Найти комнату', 'Информация', 'Поддержать')

keyboardCreate = telebot.types.ReplyKeyboardMarkup(True, True)
keyboardCreate.row('Создать', 'Отмена')

keyboardDonate = types.InlineKeyboardMarkup()
url_button = types.InlineKeyboardButton(text="Перейти на сайт поддержки", url="http://telegrammafia.tk")
keyboardDonate.add(url_button)

keyboardChange = telebot.types.ReplyKeyboardMarkup(True, True)
keyboardChange.row('Да', 'Нет')

keyboardEmpty = telebot.types.ReplyKeyboardMarkup(True, True)
keyboardEmpty.row('')

conn = pymysql.connect(
    host='',
    port=,
    user='',
    password='',
    db='',
    max_allowed_packet='1024M'
)

cursor = conn.cursor()


def connection_mysql():
    global conn, cursor
    conn = pymysql.connect(
        host='',
        port=,
        user='',
        password='',
        db='',
        max_allowed_packet='1024M'
    )

    cursor = conn.cursor()


def registration(msg):
    user = msg.from_user
    if len(msg.text.split('/')) > 1:
        msg = bot.send_message(user.id, 'Недопустимые символы. Введите имя ещё раз.')
        bot.register_next_step_handler(msg, registration)
    else:
        query = f"SELECT * FROM Users WHERE name = '{msg.text}'"
        cursor.execute(query)
        row = cursor.fetchone()
        if row is None:
            query = f"INSERT INTO Users(id, name, games, won, lost, role, voted) VALUES('{user.id}', '{msg.text}', {0}, {0}, {0}, '', '{0}')"
            cursor.execute(query)
            conn.commit()
            bot.send_message(user.id, 'Регистрация прошла успешно.', reply_markup=keyboardStart)
        else:
            msg = bot.send_message(user.id, 'Это имя уже занято. Попробуйте ещё.')
            bot.register_next_step_handler(msg, registration)


def create_room_step1(msg):
    user = msg.from_user
    try:
        if (int(msg.text) < 5) and (int(msg.text) >= 1):
            query = (f"INSERT INTO Rooms(id, don, slut, doctors, mafia, status, population, population_min)"
                     f" VALUES({0}, {0}, {0}, {0}, {int(msg.text)}, 'Create', {0}, {user.id})")
            cursor.execute(query)
            conn.commit()

            msg = bot.send_message(user.id, 'Будет ли роль дона мафии участвовать в игре?', reply_markup=keyboardChange)
            bot.register_next_step_handler(msg, create_room_step2)
        else:
            msg = bot.send_message(user.id, 'Число не удовлетворяет условию. Введите ещё раз.')
            bot.register_next_step_handler(msg, create_room_step1)
    except:
            msg = bot.send_message(user.id, 'Сообщение не удовлетворяет условию. Введите ещё раз.')
            bot.register_next_step_handler(msg, create_room_step1)


def create_room_step2(msg):
    user = msg.from_user
    if msg.text == 'Да':
        query = f"UPDATE Rooms SET don = '{1}' WHERE population_min = '{user.id}'"
        cursor.execute(query)
        conn.commit()

        msg = bot.send_message(user.id, 'Будет ли роль "ночной бабочки" участвовать в игре?',
                               reply_markup=keyboardChange)
        bot.register_next_step_handler(msg, create_room_step3)
    elif msg.text == 'Нет':
        msg = bot.send_message(user.id, 'Будет ли роль "ночной бабочки" участвовать в игре?',
                               reply_markup=keyboardChange)
        bot.register_next_step_handler(msg, create_room_step3)
    else:
        msg = bot.send_message(user.id, 'Я вас не понимаю. Попробуйте ещё раз', reply_markup=keyboardChange)
        bot.register_next_step_handler(msg, create_room_step2)


def create_room_step3(msg):
    user = msg.from_user
    if msg.text == 'Да':
        query = f"UPDATE Rooms SET slut = '{1}' WHERE population_min = '{user.id}'"
        cursor.execute(query)
        conn.commit()

        msg = bot.send_message(user.id, 'Сколько докторов будет в игре? (от 1 до 2)')
        bot.register_next_step_handler(msg, create_room_finish)
    elif msg.text == 'Нет':
        msg = bot.send_message(user.id, 'Сколько докторов будет в игре? (от 1 до 2)')
        bot.register_next_step_handler(msg, create_room_finish)
    else:
        msg = bot.send_message(user.id, 'Я вас не понимаю. Попробуйте ещё раз', reply_markup=keyboardChange)
        bot.register_next_step_handler(msg, create_room_step3)


def create_room_finish(msg):
    user = msg.from_user
    try:
        if (int(msg.text) < 3) and (int(msg.text) >= 1):
            query = f"UPDATE Rooms SET doctors = '{int(msg.text)}' WHERE population_min = '{user.id}'"
            cursor.execute(query)
            conn.commit()

            while True:
                room_id = random.randint(1, 1000000)
                query = f"SELECT * FROM Rooms WHERE id = '{room_id}'"
                cursor.execute(query)
                had = cursor.fetchone()
                if had is None:
                    break

            bot.send_message(user.id, f'Комната успешно созданна. ID: {room_id}')

            query = f"UPDATE Users SET room_id = '{room_id}' WHERE id = '{user.id}'"
            cursor.execute(query)
            conn.commit()

            query = f"UPDATE Rooms SET id = '{room_id}' WHERE population_min = '{user.id}'"
            cursor.execute(query)
            conn.commit()

            query = f"UPDATE Rooms SET status = 'Wait' WHERE id = '{room_id}'"
            cursor.execute(query)
            conn.commit()

            query = f"SELECT * FROM Rooms WHERE id = '{room_id}'"
            cursor.execute(query)
            room = cursor.fetchone()

            query = f"UPDATE Rooms SET population = '{1}' WHERE id = '{room_id}'"
            cursor.execute(query)
            conn.commit()

            if room[2] + room[3] > room[4]:
                pop_min = room[2] + room[3] + 1
            else:
                pop_min = room[4] * 2 + 1

            query = f"UPDATE Rooms SET population_min = '{pop_min}' WHERE id = '{room_id}'"
            cursor.execute(query)
            conn.commit()

        else:
            msg = bot.send_message(user.id, 'Число не удовлетворяет условию. Введите ещё раз.')
            bot.register_next_step_handler(msg, create_room_finish)
    except:
        msg = bot.send_message(user.id, 'Сообщение не удовлетворяет условию. Введите ещё раз.')
        bot.register_next_step_handler(msg, create_room_finish)


def room_connect(msg, room_id):
    user = msg.from_user
    try:
        query = f"SELECT population, population_min, status FROM Rooms WHERE id = '{room_id}'"
        cursor.execute(query)
        room = cursor.fetchone()

        query = f"SELECT name FROM Users WHERE id = '{user.id}'"
        cursor.execute(query)
        player_name = cursor.fetchone()

        query = f"UPDATE Users SET room_id = '{room_id}' WHERE id = '{user.id}'"
        cursor.execute(query)
        conn.commit()

        query = f"SELECT id FROM Users WHERE room_id = '{room_id}'"
        cursor.execute(query)
        players_id = cursor.fetchall()

        for i in players_id:
            bot.send_message(i[0], f'В комнату вошёл {player_name[0]} \n'
                                   f'Игроков {room[0] + 1}/12')

        bot.send_message(user.id, f'ID: {room_id}', reply_markup=keyboardEmpty)

        if room[1] <= room[0] + 1:
            if room[2] != 'Timer':
                t = threading.Timer(30.0, timer_start_room, args=(1, room_id, ))
                t.start()

                query = f"UPDATE Rooms SET status = 'Timer' WHERE id = '{room_id}'"
                cursor.execute(query)
                conn.commit()

                for i in players_id:
                    bot.send_message(i[0], 'Игра начнётся через 60 секунд.')

        query = f"UPDATE Rooms SET population = '{room[0] + 1}' WHERE id = '{room_id}'"
        cursor.execute(query)
        conn.commit()
    except:
        print("Error mySQL")


def chat(msg):
    user = msg.from_user

    query = f"SELECT name, room_id, role FROM Users WHERE id = '{user.id}'"
    cursor.execute(query)
    player = cursor.fetchone()

    room_id = player[1]

    query = f"SELECT status FROM Rooms WHERE id = '{room_id}'"
    cursor.execute(query)
    room = cursor.fetchone()

    if (room[0] == 'Wait') or (room[0] == 'Timer'):
        if msg.text != '/leave':
            query = f"SELECT id FROM Users WHERE room_id = '{room_id}'"
            cursor.execute(query)
            players_id = cursor.fetchall()
            for i in players_id:
                if int(i[0]) != int(user.id):
                    bot.send_message(i[0], f"{player[0]}: {msg.text}")

        else:
            bot.send_message(user.id, "Вы вышли из комнаты.", reply_markup=keyboardStart)

            query = f"SELECT population, population_min, status FROM Rooms WHERE id = '{room_id}'"
            cursor.execute(query)
            room = cursor.fetchone()

            query = f"UPDATE Users SET room_id = '0' WHERE id = '{user.id}'"
            cursor.execute(query)
            conn.commit()

            if room[0] - 1 != 0:
                query = f"UPDATE Rooms SET population = '{room[0] - 1}' WHERE id = '{room_id}'"
                cursor.execute(query)
                conn.commit()

                query = f"SELECT id FROM Users WHERE room_id = '{room_id}'"
                cursor.execute(query)
                players_id = cursor.fetchall()
                for i in players_id:
                    bot.send_message(i[0], f"{player[0]} покинул комнату \n"
                                           f"Игроков {room[0] - 1}/12")

                if room[0] - 1 < room[1]:
                    if room[2] == 'Timer':
                        for i in players_id:
                            bot.send_message(i[0], f"Начало игры отменено.")
                        query = f"UPDATE Rooms SET status = 'Wait' WHERE id = {room_id}"
                        cursor.execute(query)
                        conn.commit()

            else:
                query = f"DELETE FROM Rooms WHERE id = '{room_id}'"
                cursor.execute(query)
                conn.commit()

    elif room[0] == 'Day':
        query = f"SELECT id FROM Users WHERE room_id = '{room_id}'"
        cursor.execute(query)
        players_id = cursor.fetchall()
        for i in players_id:
            if int(i[0]) != int(user.id):
                bot.send_message(i[0], f'{player[0]}: {msg.text}')

    elif room[0] == 'Night':
        if (player[2] == 'Mafia') or (player[2] == 'Don'):
            query = f"SELECT id FROM Users WHERE (role = 'Mafia') OR (role = 'Don') AND (room_id = '{room_id}')"
            cursor.execute(query)
            players_id = cursor.fetchall()

            for i in players_id:
                if int(i[0]) != int(user.id):
                    bot.send_message(i[0], f'{player[0]}: {msg.text}')

        else:
            bot.send_message(user.id, 'Вы не можете писать ночью.')


def add_roles(room_id):
    connection_mysql()

    query = f"SELECT id FROM Users WHERE room_id = '{room_id}'"
    cursor.execute(query)
    players_id = cursor.fetchall()

    query = f"SELECT * FROM Rooms WHERE id = '{room_id}'"
    cursor.execute(query)
    room = cursor.fetchone()

    players_id = list(players_id)

    for doctor in range(room[3]):
        user_id = random.choice(players_id)
        players_id.remove(user_id)

        query = f"UPDATE Users SET role = 'Doctor' WHERE id = '{user_id[0]}'"
        cursor.execute(query)
        conn.commit()

        bot.send_message(user_id[0], 'Ваша роль: доктор')
        r = requests.get('https://i.ibb.co/1KW3n2R/image.png')
        url = r.url
        bot.send_photo(user_id[0], photo=url)

    for mafia in range(room[4]):
        user_id = random.choice(players_id)
        players_id.remove(user_id)

        if mafia == 0:
            if int(room[1]) == 1:
                query = f"UPDATE Users SET role = 'Don' WHERE id = '{user_id[0]}'"
                cursor.execute(query)
                conn.commit()

                bot.send_message(user_id[0], 'Ваша роль: дон мафии')

                r = requests.get('https://i.ibb.co/5KHb7Gf/image.png')
                url = r.url
                bot.send_photo(user_id[0], photo=url)
            else:
                query = f"UPDATE Users SET role = 'Mafia' WHERE id = '{user_id[0]}'"
                cursor.execute(query)
                conn.commit()

                bot.send_message(user_id[0], 'Ваша роль: мафия')

                r = requests.get('https://i.ibb.co/z5mr9h9/image.png')
                url = r.url
                bot.send_photo(user_id[0], photo=url)
        else:
            query = f"UPDATE Users SET role = 'Mafia' WHERE id = '{user_id[0]}'"
            cursor.execute(query)
            conn.commit()

            bot.send_message(user_id[0], 'Ваша роль: мафия')

            r = requests.get('https://i.ibb.co/z5mr9h9/image.png')
            url = r.url
            bot.send_photo(user_id[0], photo=url)

    if room[2] != 0:
        user_id = random.choice(players_id)
        players_id.remove(user_id)

        query = f"UPDATE Users SET role = 'Slut' WHERE id = '{user_id[0]}'"
        cursor.execute(query)
        conn.commit()

        bot.send_message(user_id[0], 'Ваша роль: проститука')

        r = requests.get('https://i.ibb.co/zmbkgcW/image.png')
        url = r.url
        bot.send_photo(user_id[0], photo=url)

    # Коммисар
    user_id = random.choice(players_id)
    players_id.remove(user_id)

    query = f"UPDATE Users SET role = 'Commissar' WHERE id = '{user_id[0]}'"
    cursor.execute(query)
    conn.commit()

    bot.send_message(user_id[0], 'Ваша роль: шериф')

    r = requests.get('https://i.ibb.co/9v0Y78j/image.png')
    url = r.url
    bot.send_photo(user_id[0], photo=url)

    if len(players_id) != 0:
        for peaceful in players_id:
            query = f"UPDATE Users SET role = 'Peaceful' WHERE id = '{peaceful[0]}'"
            cursor.execute(query)
            conn.commit()

            bot.send_message(peaceful[0], 'Ваша роль: мирный житель')

            r = requests.get('https://i.ibb.co/p2bm3HM/image.png')
            url = r.url
            bot.send_photo(user_id[0], photo=url)

    for i in players_id:
        bot.send_message(i[0], 'Ночь. Мафия в чате.')


def timer_start_room(timer, room_id):
    query = f"SELECT id FROM Users WHERE room_id = '{room_id}'"
    cursor.execute(query)
    players_id = cursor.fetchall()

    query = f"SELECT status FROM Rooms WHERE id = '{room_id}'"
    cursor.execute(query)
    room = cursor.fetchone()

    if room[0] == 'Timer':
        if timer == 1:
            for i in players_id:
                bot.send_message(i[0], 'До начала игры осталось 30 секунд.')
            t = threading.Timer(20.0, timer_start_room, args=(2, room_id))
            t.start()
        elif timer == 2:
            for i in players_id:
                bot.send_message(i[0], 'До начала игры осталось 10 секунд.')
            t = threading.Timer(5.0, timer_start_room, args=(3, room_id))
            t.start()
        elif timer == 3:
            for i in players_id:
                bot.send_message(i[0], 'До начала игры осталось 5 секунд.')
            t = threading.Timer(1.0, timer_start_room, args=(4, room_id))
            t.start()
        elif timer == 4:
            for i in players_id:
                bot.send_message(i[0], 'До начала игры осталось 4 секунды.')
            t = threading.Timer(1.0, timer_start_room, args=(5, room_id))
            t.start()
        elif timer == 5:
            for i in players_id:
                bot.send_message(i[0], 'До начала игры осталось 3 секунды.')
            t = threading.Timer(1.0, timer_start_room, args=(6, room_id))
            t.start()
        elif timer == 6:
            for i in players_id:
                bot.send_message(i[0], 'До начала игры осталось 2 секунды.')
            t = threading.Timer(1.0, timer_start_room, args=(7, room_id))
            t.start()
        elif timer == 7:
            for i in players_id:
                bot.send_message(i[0], 'До начала игры осталось 1 секунды.')
            t = threading.Timer(1.0, timer_start_room, args=(8, room_id))
            t.start()
        elif timer == 8:
            for i in players_id:
                bot.send_message(i[0], 'Игра началась.')
            add_roles(room_id)

            query = f"UPDATE Rooms SET status = 'Night' WHERE id = '{room_id}'"
            cursor.execute(query)
            conn.commit()


def timer_day(room_id):
    query = f"SELECT id FROM Users WHERE room_id = '{room_id}'"
    cursor.execute(query)
    players_id = cursor.fetchall()


def timer_night(room_id):
    query = f"SELECT id FROM Users WHERE room_id = '{room_id}'"
    cursor.execute(query)
    players_id = cursor.fetchall()
    print(1)


@bot.message_handler(content_types=['text'])
def get_text_messages(msg):
    connection_mysql()
    user = msg.from_user

    query = f"SELECT room_id FROM Users WHERE id = '{user.id}'"
    cursor.execute(query)
    room_check = cursor.fetchone()
    if room_check is None:
        if msg.text == 'Регистрация':
            query = f'SELECT id FROM Users WHERE id = "{user.id}"'
            cursor.execute(query)

            row = cursor.fetchone()
            if row is not None:
                bot.send_message(user.id, 'Вы уже зарегистрированы.', reply_markup=keyboardStart)
            else:
                msg = bot.send_message(user.id, 'Придумайте себе игровое имя.')
                bot.register_next_step_handler(msg, registration)
        else:
            bot.send_message(user.id, 'Для начала вам необходимо зарегистрироваться.', reply_markup=keyboardReg)
    elif room_check[0] == 0:
        if msg.text == 'Найти комнату':
            query = f"SELECT * FROM Rooms WHERE (status = 'Timer') AND (population < 12)"
            cursor.execute(query)
            room = cursor.fetchone()

            if room is not None:
                room_connect(msg, room[0])
            else:
                query = f"SELECT * FROM Rooms WHERE (status = 'Wait') AND (population < 12)"
                cursor.execute(query)
                room = cursor.fetchone()
                if room is not None:
                    room_connect(msg, room[0])
                else:
                    bot.send_message(user.id, 'В данный момент нет свободных комнат.', reply_markup=keyboardCreate)

        elif msg.text == 'Поддержать':
            bot.send_message(user.id, 'Вы хотите нас поддержать?', reply_markup=keyboardDonate)

        elif msg.text == 'Регистрация':
            bot.send_message(user.id, 'Вы уже зарегестрированны.', reply_markup=keyboardStart)

        elif msg.text == 'Создать':
            msg = bot.send_message(user.id, 'Введите кол-во мафий. От 1 до 4')
            bot.register_next_step_handler(msg, create_room_step1)

        elif '/connect' in msg.text:
            room_id = (msg.text.split())[-1]

            query = f"SELECT status, population FROM Rooms WHERE id = '{room_id}'"
            cursor.execute(query)
            room = cursor.fetchone()

            if room is None:
                bot.send_message(user.id, 'Такой комнаты не существует.')
            elif room[0] != 'Wait' and room[0] != 'Timer':
                bot.send_message(user.id, 'В этой комнате уже идёт игра.')
            elif room[1] == 12:
                bot.send_message(user.id, 'В этой комнате нет места.')
            else:
                room_connect(msg, room_id)
    else:
        chat(msg)


bot.polling(none_stop=True, interval=0)