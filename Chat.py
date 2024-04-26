import telebot
from telebot import types

import pymysql

bot = telebot.TeleBot('token')

conn = pymysql.connect(
    host='',
    port=,
    user='',
    password='',
    db=''
)

cursor = conn.cursor()


def chat(msg):
    user = msg.from_user

    query = f"SELECT * FROM Users WHERE id = '{user.id}'"
    cursor.execute(query)
    room_id = cursor.fetchone()

    print(room_id)

    query = f"SELECT timeset FROM Rooms WHERE id = '{room_id[0]}'"
    cursor.execute(query)
    room_time = cursor.fetchone()

    if room_time[0] == 'Wait':
        query = f"SELECT players FROM Rooms WHERE id = '{room_id[0]}'"
        cursor.execute(query)
        players = cursor.fetchone()

        players = players[0].split('/')

        #player_name =

        for i in players:
            query = f"SELECT id FROM Users WHERE name = '{i}'"
            cursor.execute(query)
            player_id = cursor.fetchone()
            #if player_id != user.id:



bot.polling(none_stop=True, interval=0)