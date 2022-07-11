import sqlite3

from vkbottle import Keyboard, EMPTY_KEYBOARD, KeyboardButtonColor, Text
from requests import get
from copy import deepcopy
from vk_api import vk_api

from key import key
from config import *



def group_list(corpus: str, course: str) -> list:
#   // list of group by specified parameters
    data_list = get('https://bot-t-s.nttek.ru/rest-api/available').json()
    rasp = get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    group_list = [i for i in rasp[corpus] if i[0] == course]
    return group_list      

def course_chain (user_group: str) -> list:
#   // course chain for function 'Change course'
    chain = []
    data_list = get('https://bot-t-s.nttek.ru/rest-api/available').json()
    rasp = get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    for i in rasp:
        for j in rasp[i]:
            if j[1:] == user_group[1:]:
                chain.append(j)
    chain.remove(user_group)
    return chain

def get_keyboard (buttons: list | tuple, one_time: bool = False):
    keyboard = Keyboard(one_time=one_time, inline=False)
    if len(buttons) < 9:
        max_button = 4
    else:
        max_button = 3

    count = 0
    for button in buttons:
        if button == 'Назад':
            keyboard.row()
            keyboard.add(Text(button), KeyboardButtonColor.NEGATIVE)
        elif count != max_button:
            keyboard.add(Text(button), KeyboardButtonColor.PRIMARY)
            count += 1
        else:
            keyboard.row()
            count = 0
            keyboard.add(Text(button), KeyboardButtonColor.PRIMARY)
            count += 1
    return keyboard.get_json()

def data_base(sql:str, value: tuple = ()):
#   // sending database queries
    con = sqlite3.connect('vk_bot.db')
    cur = con.cursor()
    if 'SELECT' in sql:
        if value:
            query = cur.execute(sql, value).fetchall()
        else:
            query = cur.execute(sql).fetchall()
        con.close()
        return query
    else:
        if value:
            cur.execute(sql, value)
        else:
            cur.execute(sql)
        con.commit()
        con.close()

def begin(user_id: int):
    cache_dict[user_id] = [1, []] # [step:int, memory:list]
    user_trigger[user_id] = deepcopy(trigger_list)
    user_trigger[user_id]['Reg'] = False
    user_trigger[user_id]['AfterRestart'] = True

def users_to_msg(start_msg:str, array_to_message:list|tuple, cache_dict:dict = {}) -> str:
    vk = vk_api.VkApi(token=key)
    vk._auth_token()
    for user in array_to_message:
        usr_info = vk.method('users.get', {'user_id': user[0]})[0]
        if not cache_dict:
            start_msg += f'vk.com/id{user[0]} - {usr_info["first_name"]} {usr_info["last_name"]}\n'
        else:
            start_msg += f'vk.com/id{user[0]} - {cache_dict[user[0]][2]} - {usr_info["first_name"]} {usr_info["last_name"]}\n'
    return start_msg
