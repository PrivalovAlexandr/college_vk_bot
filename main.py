from time import sleep
import vk_api
import sqlite3
import requests
import json

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from key import key
from config import *
from random import randint as random

#   //    получение расписания    //

#data_list = requests.get('https://bot-t-s.nttek.ru/rest-api/available').json()
#rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()


vk = vk_api.VkApi(token=key)
vk._auth_token()


def data_base(sql:str, value: tuple = ()):
#   // отправка запросов к базе данных
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
    i = list(i)
    cache_dict[i[0]] = i

def send_message (user_id: int, message: str, keyboard_array = None):
#   // отправка сообщения пользователю
    attr = {
        "user_id": user_id,
        "message": message,
        "random_id": random(-1000, 1000),
        }
    #   добавление клавиатуры
    keyboard = VkKeyboard()
    if keyboard_array not in [None, False]:
        button = 0
        if len(keyboard_array) > 8:
            max_button = 3
        elif 'Своё расписание' in keyboard_array:
            max_button = 2
        else:
            max_button = 4
        for i in keyboard_array:
            if i != 'Назад':
                if button < max_button:
                    keyboard.add_button (i, VkKeyboardColor.PRIMARY)
                else:
                    keyboard.add_line()
                    keyboard.add_button (i, VkKeyboardColor.PRIMARY)
                    button = 0
            else:
                keyboard.add_line()
                keyboard.add_button (i, VkKeyboardColor.NEGATIVE)
            button += 1
        attr['keyboard'] = keyboard.get_keyboard()
    elif keyboard_array == False:
        attr['keyboard'] = keyboard.get_empty_keyboard()
    vk.method ("messages.send", attr)
    return (message, keyboard_array)

def next_menu (user_id: int, position: str, next: str, msg: str = None, keyboard = None):
#   // возвращение в основные меню из меню функций
    Trigger[position] = False
    Trigger[next] = True
    if next == 'Main':
        _text = 'Главное меню'
        keyboard = menu_key
    elif next == 'Admin':
        _text = 'Админ меню'
        keyboard = admin_key
    if msg != None:
        _text = msg
    return send_message(user_id, _text, keyboard)
    
def group_list(corpus: str, course: str):
#   // список групп по заданному корпусу и курсу
    data_list = requests.get('https://bot-t-s.nttek.ru/rest-api/available').json()
    rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    group_list = [i for i in rasp[corpus] if i[0] == course]
    return group_list             

def course_chain (user_group: str):
#   // цепочки курсов
    chain = []
    data_list = requests.get('https://bot-t-s.nttek.ru/rest-api/available').json()
    rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    for i in rasp:
        for j in rasp[i]:
            if j[1:] == user_group[1:]:
                chain.append(j)
    chain.remove(user_group)
    return chain

def create_msg (group_rasp: dict):
    msg = ''
    for i in group_rasp:
        msg += ' | '.join([i, ' '.join([group_rasp[i][0], f"({group_rasp[i][1]})"]), group_rasp[i][2] + '\n'])
    return msg

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
                    data_base("DELETE FROM users WHERE id = ?", (id,))
                    cache_dict[id] = 1
                    Trigger['Send'] = True
                    Trigger['Reg'] = False
                    _text = next_menu(id, 'Profile', 'Main', 'Выберите роль', role)
                elif text == 'Изменить курс':
                    chain = course_chain(cache_dict[id][4])
                    if chain:
                        _text = next_menu(id, 'Profile', 'Change', 'Выберите группу', chain + ['Назад'])
                    else:
                        _text = send_message(id, 'Для вашей специальности пока что нет других курсов')
                elif text == 'Назад':
                    _text = next_menu(id, 'Profile', 'Main')
            elif Trigger['Change']:
                if text.upper() in chain:
                    cache_dict[id][4] = text.upper()
                    data_base("UPDATE users SET 'group' = ? WHERE id = ?", (text.upper(), id))
                    _text = next_menu(id, 'Change', 'Main', 'Ваша группа была успешно изменена')
                elif text == 'Назад':
                    _text = next_menu(id, 'Change', 'Main')
            elif Trigger['Rasp']:
                if text in rasp_key[:2]:
                    if text == rasp_key[0]:
                        rasp_type = 'group'
                    else:
                        rasp_type = 'teacher'
                    data_list = requests.get('https://bot-t-s.nttek.ru/rest-api/available').json()
                    _text = next_menu(id, 'Rasp', 'Data', 'Выберите дату расписания', data_list + ['Назад'])
                elif text == 'Назад':
                    _text = next_menu(id, 'Rasp', 'Main')
            elif Trigger['Data']:
                if text in data_list:
                    if text != 'Назад':
                        if not Trigger['Mine_Rasp']:
                            data = text
                            Trigger['Data'] = False
                            if rasp_type == 'group':
                                backup_info = cache_dict[id]
                                user_role = "Студент"
                                cache_dict[id] = 2
                                _text = next_menu(id, 'Reg', 'Rasp', 'Выберите корпус', corpus)
                            else:
                                Trigger['Teacher'] = True
                                _text = send_message(id, 'Введите фамилию преподавателя', False)
                        else:
                            if cache_dict[id][1] == 'Студент':
                                rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/group/{text}').json()
                                msg = create_msg(rasp[cache_dict[id][3]][cache_dict[id][4]])
                            else:
                                rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/teacher/{text}').json()
                                try:
                                    msg = create_msg(rasp[cache_dict[id][2]])
                                except KeyError:
                                    msg = 'В этот день у вас нет пар'
                            _text = next_menu(id, 'Data', 'Main', msg)
                elif text == 'Назад':
                    if Trigger['Mine_Rasp']:
                        Trigger['Mine_Rasp'] = False
                    _text = next_menu(id, 'Data', 'Main')
            elif Trigger['Teacher']:
                rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/teacher/{data}').json()
                try:
                    msg = create_msg(rasp[text])
                except KeyError:
                    msg = 'В этот день у преподавателя нет пар'
                _text = next_menu(id, 'Teacher', 'Main', msg)
            elif Trigger['Spam']:
                if Trigger ['Send'] == False:
                    Trigger['Send'] = True
                    msg = text
                    _text = send_message(id, f'Вы подтверждаете рассылку данного сообщения?\n\n{msg}', ['Да', 'Нет', 'Назад'])
                else:
                    if text in ('Да', 'Нет', 'Назад'):
                        Trigger ['Send'] = False
                        if text == 'Да':
                            for i in cache_dict:
                                _text = send_message(i, msg)
                            _text = next_menu(id, 'Spam', 'Admin', 'Рассылка завершена')
                        elif text == 'Нет':
                            _text = send_message(id, 'Отправьте сообщения заново', False)
                        elif text == 'Назад':
                            next_menu(id, 'Spam', 'Admin')
            elif Trigger['Admin']:
                if text == 'Нюхнуть бебры':
                    _text = send_message(id, 'Вы занюхнули настолько терпкую бебру, что двинули кони...')
                elif text == 'Рассылка':
                    _text = next_menu(id, 'Admin', 'Spam','Отправьте сообщения для предпросмотра. Отправку сообщения нужно будет подтвердить', False)
                elif text == 'Пукнуть сливой':
                    _text = send_message(id, 'Вы так сильно пукнули сливой, что все остальные в помещении двинули кони')
                elif text == 'Назад':
                    _text = next_menu(id, 'Admin', 'Main')
            elif Trigger['Main']:
                if text == "Расписание":
                    _text = next_menu(id, 'Main', 'Rasp','Выберите тип расписания', rasp_key)
                elif text == "Своё расписание":
                    data_list = requests.get('https://bot-t-s.nttek.ru/rest-api/available').json()
                    Trigger['Mine_Rasp'] = True
                    _text = next_menu(id, 'Main', 'Data', 'Выберите дату расписания', data_list + ['Назад'])
                elif text == "Профиль":
                    if cache_dict[id][2] == None:
                        #   студент
                        msg = f'Ваш профиль:\n\nРоль: {cache_dict[id][1]}\nГруппа: {cache_dict[id][4]}'
                    else:
                        #   преподаватель
                        msg = f'Ваш профиль:\n\nРоль: {cache_dict[id][1]}\nФамилия: {cache_dict[id][2]}'

                    if cache_dict[id][5] == 1:
                        msg += "\n\nАдмин"
                    _text = next_menu(id, 'Main', 'Profile', msg, profile)
                elif text == "Админ":
                    if cache_dict[id][5] == 1:
                        _text = next_menu(id, 'Main', 'Admin')
                    else:
                        _text = send_message(id, 'У вас нет прав администратора')
        else:
            if cache_dict[id] == 1:
                if text not in role:
                    if Trigger['Send'] == False:
                        Trigger['Send'] == True
                        _text = send_message(id, 'Выберите роль', role)
                    else:
                        _text = send_message(id, 'Некорректный выбор')
                else:
                    Trigger['Send'] = False
                    user_role = text
                    cache_dict[id] = 2
                    if user_role == role[0]:
                        last_name = None
                        _text = send_message(id, 'Выберите корпус', corpus)
                    else:
                        user_corpus = None
                        group = None
                        _text = send_message(id, 'Введите свою фамилию', False)
            elif cache_dict[id] == 2:
                if user_role == role[0]:
                    if text not in corpus:
                        _text = send_message(id, 'Некорректный выбор')
                    else:
                        user_corpus = text
                        cache_dict[id] = 3
                        _text = send_message(id, 'Выберите курс', course)
                else:
                    if Trigger['Send'] == False:
                        last_name = text
                        Trigger['Send'] = True
                        _text = send_message(id, f'Ваша фамилия: {last_name}. Все верно?', ['Да', 'Нет'])
                    else:
                        if text == 'Да':
                            Trigger['Send'] = False
                            cache_dict[id] = 5
                            msg = f'Вы хотете завершить регистрацию с этими данными?\n\nРоль: {user_role}\nФамилия: {last_name}'
                            _text = send_message (id, msg, ['Да', 'Нет'])
                        elif text == 'Нет':
                            Trigger['Send'] = False
                            _text = send_message(id, 'Введите свою фамилию', False)
            elif cache_dict[id] == 3:
                if text not in course:
                    _text = send_message (id, 'Некорректный выбор')
                else:
                    group = group_list(user_corpus, text)
                    cache_dict[id] = 4
                    _text = send_message (id, "Выберите группу", group)
            elif cache_dict[id] == 4:
                if text.upper() not in group:
                    _text = send_message (id, 'Некорректный выбор')
                else:
                    group = text.upper()
                    cache_dict[id] = 5
                    if Trigger['Rasp']:
                        Trigger['Reg'] = True
                        cache_dict[id] = backup_info
                        rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/group/{data}').json()
                        msg = create_msg(rasp[user_corpus][group])
                        _text = next_menu(id, 'Rasp', 'Main', msg)
                    else:
                        msg = f'Вы хотете завершить регистрацию с этими данными?\n\nРоль: {user_role}\nГруппа: {group}'
                        _text = send_message (id, msg, ('Да', 'Нет'))
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
                    _text = send_message(id, 'гатова', menu_key)
                elif text == 'Нет':
                    cache_dict[id] = 1
                    _text = send_message(id, 'Выберите роль', role)
        try:
            if vk.method("messages.getConversations", {"offset": 0, "count": 1, "filter": "unanswered"})['count'] != 0:
                if text in _text[1]:
                    send_message(id, _text[0], _text[1])
        except:
            pass