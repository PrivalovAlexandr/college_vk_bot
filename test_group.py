import requests
from pprint import pprint

data_list = ['7-05']
req = requests.get('https://bot-t-s.nttek.ru/rest-api/group/7-05')
rasp = req.json()

def course_chain ():
#   // цепочки курсов для кнопки Next course 
    group = {}
    for i in rasp.keys():
       for j in rasp[i]:
           if j[1:] not in group:
               group[j[1:]] = [j]
           else:
               if j not in group[j[1:]]:
                   group[j[1:]].append(j)
                   group[j[1:]].sort()
    return group


def group_list(corpus: str, course: str):
#   // список групп по заданному корпусу и курсу
    group_list = []
    for i in rasp[corpus]:
        if i[0] == course:
            group_list.append(i)
    return group_list


pprint(course_chain())
print(group_list("Корпус 1", "2"))        