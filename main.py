import vk_api
import sqlite3
import requests
import json

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from key import key
from config import *
from pprint import pprint
from random import randint as random

#   //    получение расписания    //

#req = requests.get('https://bot-t-s.nttek.ru/rest-api/group/15-04')
#rasp = req.json()


vk = vk_api.VkApi(token=key)
vk._auth_token()


#   //    синхронизация с бд    //

con = sqlite3.connect('vk_bot.db')
cur = con.cursor()
users = cur.execute ('SELECT * FROM users').fetchall()
for i in users:
    cache_dict[i[0]] = [i[0], i[1], i[2], i[3], i[4]]
con.close()


def send_message (user_id, message, keyboard_array = None, color = VkKeyboardColor.PRIMARY):
    keyboard = VkKeyboard()
    attr = {
        "user_id": user_id,
        "message": message,
        "random_id": random(-1000, 1000),
        }
    if keyboard_array not in [None, False]:
        line = 1
        for i in keyboard_array:
            if i != 'Назад':
                try:
                    keyboard.add_button (i, color)
                except:
                    keyboard.add_line()
                    line += 1
            else:
                if line > 1 or len(keyboard_array) > 2:
                    keyboard.add_line()
                keyboard.add_button (i, VkKeyboardColor.NEGATIVE)
        attr['keyboard'] = keyboard.get_keyboard()
    elif keyboard_array == False:
        attr['keyboard'] = keyboard.get_empty_keyboard()
    vk.method ("messages.send", attr)

def back_to_menu (user_id, position):
    if position == 'Profile':
        Trigger['Profile'] = False
    elif position == 'Rasp':
        Trigger['Rasp'] = False
    elif position == 'Admin':
        Trigger['Admin'] = False
    Trigger['Main'] = True
    send_message(user_id, 'Главное меню', menu_key)
             


for event in VkLongPoll(vk).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        id = event.user_id
        text = event.text.lower()

        print (id, text)

        if id not in cache_dict:
            Trigger['Reg'] = False
            Trigger['Send'] = False
            cache_dict[id] = 1

        if Trigger['Reg']:
            if Trigger['Profile']:
                if text == 'сбросить профиль':
                    con = sqlite3.connect('vk_bot.db')
                    cur = con.cursor()
                    cur.execute(f"DELETE FROM users WHERE id = {id}")
                    con.commit()
                    con.close()

                    cache_dict[id] = 1
                    Trigger['Send'] = True
                    Trigger['Reg'] = False
                    Trigger['Main'] = True
                    Trigger['Profile'] = False

                    send_message(id, 'Выберите свою роль', role)
                elif text == 'назад':
                    back_to_menu(id, 'Profile')
            elif Trigger['Rasp']:
                if text == 'по группам':
                    pass
                    #req = requests.get('https://bot-t-s.nttek.ru/rest-api/group/15-04')
                    #rasp = req.json()
                elif text == 'по преподавателям':
                    pass
                    #req = requests.get('https://bot-t-s.nttek.ru/rest-api/teacher/15-04')
                    #rasp = req.json()
                elif text == 'назад':
                    back_to_menu(id, 'Rasp')
            elif Trigger['Main']:
                if text == "расписание":
                    send_message(id, 'Выберите тип расписания', rasp)
                    Trigger['Rasp'] = True
                elif text == "профиль":
                    if cache_dict[id][2] == None:
                        #   студент
                        msg = '''
                        Ваш профиль:

                        Роль: {}
                        Группа: {}'''.format(cache_dict[id][1], cache_dict[id][3])
                    else:
                        #   преподаватель
                        msg = '''
                        Ваш профиль:

                        Роль: {}
                        Фамилия: {}'''.format(cache_dict[id][1], cache_dict[id][2])

                    if cache_dict[id][4] == 1:
                        msg += "\n\nАдмин"
                    send_message(id, msg, ['Сбросить профиль', 'Назад'])
                    Trigger['Profile'] = True
                    Trigger['Main'] = False
                elif text == "админ":
                    pass
        else:
            if cache_dict[id] == 1:
                if text.capitalize() not in role:
                    if Trigger['Send'] == False:
                        Trigger['Send'] == True
                        send_message(id, 'Выберите свою роль', role)
                    else:
                        send_message(id, 'Некорректный выбор')
                else:
                    user_role = text.capitalize()
                    cache_dict[id] = 2
                    if user_role == role[0]:
                        last_name = None
                        send_message(id, 'Выберите свой корпус', corpus)
                    else:
                        Trigger['Send'] = True
                        group = None
                        send_message(id, 'Введите свою фамилию', False)
            elif cache_dict[id] == 2:
                if user_role == role[0]:
                    if text not in corpus:
                        send_message(id, 'Некорректный выбор')
                    else:
                        user_corpus = int(text)
                        cache_dict[id] = 3
                        send_message(id, 'Выберите ваш курс', course)
                else:
                    if Trigger['Send']:
                        last_name = text.capitalize()
                        send_message(id, 'Ваша фамилия: {}. Все верно?'.format(last_name), ['Да', 'Нет'])
                        Trigger['Send'] = False
                    else:
                        if text == 'да':
                            cache_dict[id] = 5
                            msg = '''
                            Вы хотете завершить регистрацию с этими данными?

                            Роль: {}
                            Фамилия: {}'''.format(user_role, last_name)
                            send_message (id, msg, ['Да', 'Нет'])
                        elif text == 'нет':
                            Trigger['Send'] = True
                            send_message(id, 'Введите свою фамилию', False)
            elif cache_dict[id] == 3:
                if text not in course:
                    send_message (id, 'Некорректный выбор')
                else:
                    if user_corpus == 1:
                        if text == '1':
                            group = group_one_one
                        elif text == '2':
                            group = group_one_two
                        elif text == '3':
                            group = group_one_three
                        elif text == '4':
                            group = group_one_four
                    else:
                        if text == '1':
                            group = group_two_one
                        elif text == '2':
                            group = group_two_two
                        elif text == '3':
                            group = group_two_three
                        elif text == '4':
                            group = group_two_four
                    cache_dict[id] = 4
                    send_message (id, "Выберите свою группу", group)
            elif cache_dict[id] == 4:
                if text.upper() not in group:
                    send_message (id, 'Некорректный выбор')
                else:
                    group = text.upper()
                    cache_dict[id] = 5
                    msg = '''
                    Вы хотете завершить регистрацию с этими данными?

                    Роль: {}
                    Группа: {}'''.format(user_role, group)
                    send_message (id, msg, ['Да', 'Нет'])
            elif cache_dict[id] == 5:
                if text == "да":
                    if id in [177157427]:
                        admin = 1
                    else:
                        admin = 0
                    cache_dict[id] = [id, user_role, last_name, group, admin]
                    con = sqlite3.connect('vk_bot.db')
                    cur = con.cursor()
                    sql = "INSERT INTO 'users' VALUES (?,?,?,?,?)"
                    cur.execute(sql, (id, user_role, last_name, group, admin))
                    con.commit()
                    con.close()
                    Trigger['Reg'] = True
                    send_message(id, 'гатова', menu_key)
                elif text == 'нет':
                    cache_dict[id] = 1
                    send_message(id, 'Выберите свою роль', role)

