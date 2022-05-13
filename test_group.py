import requests
import sqlite3
from datetime import date
from pprint import pprint

data_list = requests.get('https://bot-t-s.nttek.ru/rest-api/available').json()
rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()

def create_msg (group_rasp: dict):
    some_list = [[],[]]
    for i in group_rasp:
        text = f"{group_rasp[i][0]} ({group_rasp[i][1]})"
        some_list[0].append([i + ' | ', f' | {group_rasp[i][2]} \n'])
        some_list[1].append(text)
    msg = ''
    count = 0
    for j in some_list[1]:
        msg += j.center(len(max(some_list[1], key=len))).join(some_list[0][count])
        count += 1
    return msg

def course_chain (user_group: str):
#   // цепочки курсов для кнопки Next course 
    chain = []
    rasp = requests.get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}').json()
    for i in rasp:
        for j in rasp[i]:
            if j[1:] == user_group[1:]:
                chain.append(j)
    return chain