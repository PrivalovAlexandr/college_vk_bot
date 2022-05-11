import requests
import sqlite3
from datetime import date
from pprint import pprint

data_list = ['1-09']
#req = requests.get('https://bot-t-s.nttek.ru/rest-api/group/7-05')
#rasp = req.json()

def check_rasp():
    req = requests.get('https://bot-t-s.nttek.ru/rest-api/available')
    data_list = req.json()
    if '1-09' in data_list:
        req = requests.get('https://bot-t-s.nttek.ru/rest-api/group/1-09')
        rasp = req.json()
        con = sqlite3.connect('vk_bot.db')
        cur = con.cursor()
        try:
            last_backup = cur.execute("SELECT * FROM 'group_backup'").fetchone()[0]    
            if last_backup != str(date.timetuple(date.today())[0]):
                cur.execute("DELETE FROM 'group_backup'")
                sql = "INSERT INTO 'group_backup' VALUES(?)"
                cur.execute(sql, (str(date.timetuple(date.today())[0]),))
                for i in rasp:
                    for j in rasp[i]:
                        cur.execute(sql, (j,))
        except TypeError:
            sql = "INSERT INTO 'group_backup' VALUES(?)"
            cur.execute(sql, (str(date.timetuple(date.today())[0]),))
            for i in rasp:
                for j in rasp[i]:
                    cur.execute(sql, (j,))
        con.commit()
        con.close()
    return data_list

def course_chain (user_group: str):
#   // цепочки курсов для кнопки Next course 
    group_list = []
    chain = []
    if data_list:
        req = requests.get(f'https://bot-t-s.nttek.ru/rest-api/group/{data_list[0]}')
        rasp = req.json()
        for i in rasp:
            for j in rasp[i]:
                group_list.append(j)
    else:
        con = sqlite3.connect('vk_bot.db')
        cur = con.cursor()
        group = cur.execute("SELECT * FROM 'group_backup'").fetchall()[1:]
        for i in group:
            group_list.append(i[0])
    for i in group_list:
        if i[1:] == user_group[1:]:
            chain.append(i)
    return chain

#def group_list(corpus: str, course: str):
#   // список групп по заданному корпусу и курсу
#    group_list = []
#    for i in rasp[corpus]:
#        if i[0] == course:
#            group_list.append(i)
#    return group_list


#pprint(course_chain(rasp))
#print(group_list("Корпус 1", "2")) 

