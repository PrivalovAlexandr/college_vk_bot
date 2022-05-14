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


def data_base(sql:str, value: tuple = ()):
    con = sqlite3.connect('vk_bot.db')
    cur = con.cursor()
    if value:
        cur.execute(sql, value)
    else:
        if 'SELECT' in sql:
            query = cur.execute(sql).fetchall()
            con.close()
            return query
        else:
            cur.execute(sql)
    con.commit()
    con.close()

#   //    синхронизация с бд    //

users = data_base('SELECT * FROM users')
for i in users:
    cache_dict[i[0]] = [i[0], i[1], i[2], i[3], i[4], i[5]]

def send_message (user_id: int, message: str, keyboard_array = None, color = VkKeyboardColor.PRIMARY):
    keyboard = VkKeyboard()
    attr = {
        "user_id": user_id,
        "message": message,
        "random_id": random(-1000, 1000),
        }
    if keyboard_array not in [None, False]:
        line = 1
        button = 1
        if len(keyboard_array) > 8:
            max_button = 4
        else:
            max_button = 5
        for i in keyboard_array:
            if i != 'Назад':
                if button < max_button:
                    keyboard.add_button (i, color)
                else:
                    keyboard.add_line()
                    keyboard.add_button (i, color)
                    button = 0
                    line += 1
            else:
                keyboard.add_line()
                keyboard.add_button (i, VkKeyboardColor.NEGATIVE)
            button += 1
        attr['keyboard'] = keyboard.get_keyboard()
    elif keyboard_array == False:
        attr['keyboard'] = keyboard.get_empty_keyboard()
    vk.method ("messages.send", attr)

def back_to_menu (user_id: int, position: str, menu: str = 'Main'):
    Trigger[position] = False
    Trigger[menu] = True
    if menu == 'Main':
        send_message(user_id, 'Главное меню', menu_key)
    else:
        send_message(user_id, 'Админ меню', admin_key)

def group_list(corpus: str, course: str):
#   // список групп по заданному корпусу и курсу
    data_list = requests.get('https://bot-t-s.nttek.ru/rest-api/available').json()
    rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    group_list = []
    for i in rasp[corpus]:
        if i[0] == course:
            group_list.append(i)
    return group_list             


for event in VkLongPoll(vk).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        id = event.user_id
        text = event.text.capitalize()

        print (id, text)

        if id not in cache_dict:
            Trigger['Reg'] = False
            cache_dict[id] = 1

        if Trigger['Reg']:
            if Trigger['Profile']:
                if text == 'Сбросить профиль':
                    data_base(f"DELETE FROM users WHERE id = {id}")
                    cache_dict[id] = 1
                    Trigger['Send'] = True
                    Trigger['Reg'] = False
                    Trigger['Main'] = True
                    Trigger['Profile'] = False

                    send_message(id, 'Выберите свою роль', role)
                elif text == 'Cледующий курс':
                    send_message(id, 'совсем ебнутый?')
                elif text == 'Назад':
                    back_to_menu(id, 'Profile')
            elif Trigger['Rasp']:
                if text == 'По группам':
                    pass
                    #req = requests.get('https://bot-t-s.nttek.ru/rest-api/group/15-04')
                    #rasp = req.json()
                elif text == 'По преподавателям':
                    pass
                    #req = requests.get('https://bot-t-s.nttek.ru/rest-api/teacher/15-04')
                    #rasp = req.json()
                elif text == 'Назад':
                    back_to_menu(id, 'Rasp')
            elif Trigger['Spam']:
                if Trigger ['Send'] == False:
                    Trigger['Send'] = True
                    msg = text
                    send_message(id, f'Вы подтверждаете рассылку данного сообщения?\n\n{msg}', ['Да', 'Нет', 'Назад'])
                else:
                    if text == 'Да':
                        Trigger ['Send'] = False
                        Trigger ['Spam'] = False
                        Trigger ['Admin'] = True
                        for i in cache_dict:
                            send_message(i, msg)
                        send_message(id, 'Рассылка завершена', admin_key)
                    elif text == 'Нет':
                        Trigger ['Send'] = False
                        send_message(id, 'Отправьте сообщения заново', False)
                    elif text == 'Назад':
                        Trigger ['Send'] = False
                        back_to_menu(id, 'Spam', 'Admin')
            elif Trigger['Admin']:
                if text == 'Нюхнуть бебры':
                    send_message(id, 'Вы занюхнули настолько терпкую бебру, что двинули кони...')
                elif text == 'Рассылка':
                    Trigger['Admin'] = False
                    Trigger['Spam'] = True
                    send_message(id, 'Отправьте сообщения для предпросмотра. Отправку сообщения нужно будет подтвердить', False)
                elif text == 'Пукнуть сливой':
                    send_message(id, 'Вы так сильно пукнули сливой, что все остальные в помещении двинули кони')
                elif text == 'Назад':
                    back_to_menu(id, 'Admin')
            elif Trigger['Main']:
                if text == "Расписание":
                    send_message(id, 'Выберите тип расписания', rasp)
                    Trigger['Rasp'] = True
                elif text == "Профиль":
                    if cache_dict[id][2] == None:
                        #   студент
                        msg = '''
                        Ваш профиль:

                        Роль: {}
                        Группа: {}'''.format(cache_dict[id][1], cache_dict[id][4])
                    else:
                        #   преподаватель
                        msg = '''
                        Ваш профиль:

                        Роль: {}
                        Фамилия: {}'''.format(cache_dict[id][1], cache_dict[id][2])

                    if cache_dict[id][5] == 1:
                        msg += "\n\nАдмин"
                    send_message(id, msg, profile)
                    Trigger['Profile'] = True
                    Trigger['Main'] = False
                elif text == "Админ":
                    if cache_dict[id][5] == 1:
                        Trigger['Admin'] = True
                        Trigger['Main'] = False
                        send_message(id, 'Админ меню', admin_key)
                    else:
                        send_message(id, 'У вас нет прав администратора')
        else:
            if cache_dict[id] == 1:
                if text not in role:
                    if Trigger['Send'] == False:
                        Trigger['Send'] == True
                        send_message(id, 'Выберите свою роль', role)
                    else:
                        send_message(id, 'Некорректный выбор')
                else:
                    Trigger['Send'] = False
                    user_role = text
                    cache_dict[id] = 2
                    if user_role == role[0]:
                        last_name = None
                        send_message(id, 'Выберите свой корпус', corpus)
                    else:
                        group = None
                        send_message(id, 'Введите свою фамилию', False)
            elif cache_dict[id] == 2:
                if user_role == role[0]:
                    if text not in corpus:
                        send_message(id, 'Некорректный выбор')
                    else:
                        user_corpus = text
                        cache_dict[id] = 3
                        send_message(id, 'Выберите ваш курс', course)
                else:
                    if Trigger['Send'] == False:
                        last_name = text
                        Trigger['Send'] = True
                        send_message(id, 'Ваша фамилия: {}. Все верно?'.format(last_name), ['Да', 'Нет'])
                    else:
                        if text == 'Да':
                            Trigger['Send'] = False
                            cache_dict[id] = 5
                            msg = '''
                            Вы хотете завершить регистрацию с этими данными?

                            Роль: {}
                            Фамилия: {}'''.format(user_role, last_name)
                            send_message (id, msg, ['Да', 'Нет'])
                        elif text == 'Нет':
                            Trigger['Send'] = False
                            send_message(id, 'Введите свою фамилию', False)
            elif cache_dict[id] == 3:
                if text not in course:
                    send_message (id, 'Некорректный выбор')
                else:
                    group = group_list(user_corpus, text)
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
                if text == "Да":
                    if id in admin_list:
                        admin = 1
                    else:
                        admin = 0
                    cache_dict[id] = [id, user_role, last_name, user_corpus, group, admin]
                    sql = "INSERT INTO 'users' VALUES (?,?,?,?,?,?)"
                    data_base(sql, (id, user_role, last_name, user_corpus, group, admin))
                    Trigger['Reg'] = True
                    send_message(id, 'гатова', menu_key)
                elif text == 'Нет':
                    cache_dict[id] = 1
                    send_message(id, 'Выберите свою роль', role)
