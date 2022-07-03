from vkbottle.bot import Bot, Message
from time import sleep
from copy import deepcopy

from config import *
from modules import *
from key import key

bot = Bot(token=key)
    
    
    #  // на счет задержки пожключения к апи
    #кароче, вставим где получение дат расписания залупку
    #чтобы чекал наличие там первого сентября, если есть, то
    #пора обновлять в бд списочек, его выгружать перед каждым
    #запуском бота в переменную. да короче да
    
    #  // настройка получения расписания
    #сделать кнопку настроек пользователя в профиле
    #им дать выбор какое расписание получать, на неделю или по дням
    
    #  // упрощение регистрации
    #можно упростить регистрации, вырезать оттуда корпус и курс, пусть
    #они сами вводят название группы, а мы уже чекаем по первому попавшемуся
    #расписанию, они же доступны всегда, так что берем самое последнее (свежачок)
    #если есть, пропускаем, в профиле кста можно будет для красивого вида добавить
    #инфу о их корпусе и курсе, но это уже зависит от модуля


#   //    db sync    //


users = data_base('SELECT * FROM users')
for i in users:
    cache_dict[i[0]] = list(i)
    user_trigger[i[0]] = deepcopy(trigger_list)



#    //    check for registration    //


@bot.on.message(func=lambda message: message.from_id not in cache_dict)
async def start(message: Message):
    id = message.from_id
    begin(id)
    await message.answer(
        "Здравствуйте, для начала необходимо пройти небольшую регистарцию")
    await message.answer(
        "Выберите вашу роль", 
        keyboard=get_keyboard(role))



#    //    main menu    //


@bot.on.message(func=lambda message:
    (user_trigger[message.from_id]['Reg']) &
    (user_trigger[message.from_id]['AfterRestart'] is False))
async def after_restarting(message: Message):
    #    return to main menu after restarting
    user_trigger[message.from_id]['Menu'] = True
    user_trigger[message.from_id]['AfterRestart'] = True
    await message.answer(
        'Бот был перезагружен, добро пожаловать в главное меню', 
        keyboard=get_keyboard(menu_key, False))



@bot.on.message(func=lambda message:
    (user_trigger[message.from_id]['Menu']) &
    (message.text.capitalize() in menu_key))
async def main_menu(message: Message):
    match message.text.capitalize():
        case 'Расписание':
            await message.answer('технические чоколадки')
        case 'Своё расписание':
            await message.answer('технические чоколадки')
        case 'Профиль':
            id = message.from_id
            user_trigger[id]['Profile'] = True
            msg = 'Ваш профиль:\n\n'
            for i in cache_dict[id][1:]:
                if (i != None):
                    if ('Корпус' not in i):
                        msg += f"{i}\n"
            match cache_dict[id][1]:
                case 'Студент':
                    profile_key = profile_stud
                case 'Преподаватель':
                    profile_key = profile_teach
            await message.answer(msg, keyboard=get_keyboard(profile_key))
        case 'Архив расписаний':
            await message.answer('технические чоколадки')


@bot.on.message(func=lambda message:
    (user_trigger[message.from_id]['Profile']))
async def menu_profile(message:Message):
    id = message.from_id
    match cache_dict[id][1]:
        case "Студент":
            if message.text.capitalize() in profile_stud:
                match message.text.capitalize():
                    case "Сбросить профиль":
                        data_base(
                            "DELETE from users WHERE id = ?", 
                            (id,))
                        begin(id)
                        await message.answer(
                            "Выберите вашу роль", 
                            keyboard=get_keyboard(role))
        case "Преподаватель":
            if message.text.capitalize() in profile_teach:
                match message.text.capitalize():
                    case "Сбросить  профиль":
                        begin(id)
                        await message.answer(
                            "Выберите вашу роль", 
                            keyboard=get_keyboard(role))

#    //    registration    //


@bot.on.message(func=lambda message: 
    (cache_dict[message.from_id][0] == 1) &
    (message.text.capitalize() in role))
async def reg_role(message: Message):
    text = message.text.capitalize()
    cache_dict[message.from_id][1].append(text)
    match text:
        case 'Студент':
            msg = 'Выберите корпус'
            keyboard = get_keyboard(corpus)
        case 'Преподаватель':
            msg = 'Введите свою фамилию'
            keyboard = EMPTY_KEYBOARD
    cache_dict[message.from_id][0] = 2
    await message.answer(msg, keyboard=keyboard)


@bot.on.message(func=lambda message: cache_dict[message.from_id][0] == 2)
async def reg_corpus (message: Message):
    id = message.from_id
    text = message.text.capitalize()
    if cache_dict[id][1][0] == 'Студент':
        if text in corpus:
            cache_dict[id][0] = 3
            cache_dict[id][1].append(text)
            await message.answer(
                'Выберите курс', 
                keyboard=get_keyboard(course))
    else:
        #   teacher
        if not user_trigger[id]['Send']:
            cache_dict[id][1].append(text)
            user_trigger[id]['Send'] = True
            await message.answer(
                f'Ваша фамилия {text}. Все верно?', 
                keyboard=get_keyboard(('Да', 'Нет')))
        else:
            match text:
                case 'Да':
                    user_trigger[id]['Send'] = False
                    cache_dict[id][0] = 5
                    user_msg = ''
                    for i in cache_dict[id][1]:
                        user_msg += f'{i}\n'
                    await message.answer(
                        'Вы хотите завершить регистарцию с этими данными?')
                    keyboard = get_keyboard(('Да', 'Нет'))
                case 'Нет':
                    del cache_dict[id][1][1]
                    user_trigger[id]['Send'] = False
                    user_msg = 'Введите свою фамилию ещё раз'
                    keyboard = EMPTY_KEYBOARD
            await message.answer(user_msg, keyboard=keyboard)


@bot.on.message(func=lambda message: 
        (cache_dict[message.from_id][0] == 3) &
        (message.text in course))
async def reg_course (message: Message):
    id = message.from_id
    cache_dict[id][1].extend(
        [message.text,
        group_list(cache_dict[id][1][-1], message.text)]
    )
    cache_dict[id][0] = 4
    await message.answer(
        "Выберите группу", 
        keyboard=get_keyboard(cache_dict[id][1][-1]))


@bot.on.message(func=lambda message:
    (cache_dict[message.from_id][0] == 4))
async def reg_group (message: Message):
    if message.text.upper() in cache_dict[message.from_id][1][-1]:
        id = message.from_id
        del cache_dict[id][1][3]
        cache_dict[id][1][-1] = message.text.upper()
        cache_dict[id][0] = 5
        msg = ''
        for i in cache_dict[id][1]:
            msg += f"{i}\n"
        await message.answer('Вы хотите завершить регистрацию с этими данными?')
        await message.answer(msg, keyboard=get_keyboard(('Да', 'Нет')))


@bot.on.message(func=lambda message: cache_dict[message.from_id][0] == 5)
async def reg_confirm (message: Message):
   id = message.from_id
   match message.text.capitalize():
        case "Да":
            cache_dict[id][1].insert(0, id)
            match cache_dict[id][1][1]:
                case 'Студент':
                    cache_dict[id][1].insert(3, None)
                case 'Преподаватель':
                    cache_dict[id][1].extend([None, None])
            try:
                data_base(
                    'INSERT INTO users VALUES(?, ?, ?, ?, ?)', 
                    tuple(cache_dict[id][1])
                )
            except:
                #   if db is locked
                sleep(1.5)
                data_base(
                    'INSERT INTO users VALUES(?, ?, ?, ?, ?)', 
                    tuple(cache_dict[id][1])
                )
            cache_dict[id] = cache_dict[id][1]
            user_trigger[id]['Reg'] = True
            await message.answer(
                'Главное меню', 
                keyboard=get_keyboard(menu_key, False))
        case "Нет":
            cache_dict[id] = [1, []]
            await message.answer(
                "Выберите вашу роль", 
                keyboard=get_keyboard(role))

bot.run_forever()