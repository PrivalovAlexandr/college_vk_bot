import requests
from pprint import pprint

req = requests.get('https://bot-t-s.nttek.ru/rest-api/group/7-05')
rasp = req.json()
group_one_one = []
group_one_two = []
group_one_three = []
group_one_four = []
group_two_one = []
group_two_two = []
group_two_three = []
group_two_four = []
group = {}
for i in rasp.keys():
    for j in rasp[i]:
        if j[1:] not in group:
            group[j[1:]] = [j]
        else:
            if j not in group[j[1:]]:
                group[j[1:]].append(j)
for i in rasp.keys():
    for j in rasp[i]:
        if j[0] == '1':
            if i == 'Корпус 1':
                group_one_one.append(j)
            else:
                group_two_one.append(j)
        elif j[0] == '2':
            if i == 'Корпус 1':
                group_one_two.append(j)
            else:
                group_two_two.append(j)
        elif j[0] == '3':
            if i == 'Корпус 1':
                group_one_three.append(j)
            else:
                group_two_three.append(j)
        elif j[0] == '4':
            if i == 'Корпус 1':
                group_one_four.append(j)
            else:
                group_two_four.append(j)
pprint(group)
print(group_one_one, group_one_two, group_one_three, group_one_four, '\n', group_two_one, group_two_two, group_two_three, group_two_four)
        