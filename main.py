from vkbottle.bot import Bot, Message
from time import sleep
from copy import deepcopy

from config import *
from modules import *
from keyboards import *
from key import key



bot = Bot(token=key)
    
    
    #  // на счет задержки подключения к апи
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
admin = data_base('SELECT * FROM admin')
for i in admin:
    admin_list.append(i[0])



#    //    check for registration    //


@bot.on.message(func=lambda message: message.from_id not in cache_dict)
async def start(message: Message):
    id = message.from_id
    begin(id)
    await message.answer(
        "Здравствуйте, для начала необходимо пройти небольшую регистарцию")
    await message.answer(
        "Выберите вашу роль", 
        keyboard=kb_role)



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
        keyboard=kb_menu)



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
            user_trigger[id]['Menu'] = False
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



#    //    admin menu    //


@bot.on.message(func=lambda message:
    (user_trigger[message.from_id]['Menu']) &
    (message.from_id in admin_list) &
    ('/admin' in message.text))
async def admin_menu(message: Message):
    id = message.from_id
    command = message.text.split(' ')
    match command[1]:
        case 'users':
            await message.answer(f'Сейчас зарегестрировано {len(cache_dict)} пользователей')
        case 'user':
            if len(command) > 2:
                try:
                    needed_id = int(command[2])
                    if needed_id in cache_dict and len(cache_dict[needed_id]) > 2:
                        msg = 'Пользователь зарегестрирован'
                    else:
                        msg = 'Пользователь не зарегистрирован'
                    await message.answer(msg)
                except ValueError:
                    await message.answer('id состоит из цифр так то')
        case 'userbygroup':
            if len(command) > 2:
                group = command[2].upper()
                usr_id = data_base(
                    "SELECT id FROM users WHERE `group`=?", (group, ))
                if usr_id:
                    msg = f'Список пользователей с группой {group}:\n\n'
                    msg = users_to_msg(msg, usr_id)
                else:
                    msg = 'Пользователей с этой группой не найдено'
                await message.answer(msg)
        case 'teacherbysurname':
            if len(command) > 2:
                surname = command[2].capitalize()
                teacher = data_base(
                    'SELECT id FROM users WHERE `surname`=?', 
                    (surname, ))
                if teacher:
                    msg = f'Список преподавателей с фамилией {surname}:\n\n'
                    msg = users_to_msg(msg, teacher)
                else:
                    msg = 'Преподавателей с такой фамилией не найдено'
                await message.answer(msg)
        case 'allteacher':
            teacher = data_base(
                    "SELECT id FROM users WHERE `role`='Преподаватель'")
            if teacher:
                msg = f'Список преподавателей:\n\n'
                msg = users_to_msg(msg, teacher, cache_dict)
            else:
                msg = 'Пользователей с ролью преподавателя не найдено'
            await message.answer(msg)
        case 'addadmin':
            if id == 177157427:
                if len(command) > 2:
                    try:
                        needed_id = int(command[2])
                        s = data_base("SELECT * FROM admin WHERE `id`=?", (needed_id,))
                        if not s:
                            admin_list.append(needed_id)
                            data_base('INSERT INTO admin VALUES(?)', (needed_id, ))
                            await message.answer(
                                f'Пользователь с id {needed_id} добавлен к администраторам')
                        else:
                            await message.answer(
                                f'Пользователь с id {needed_id} уже является администратором')
                    except ValueError:
                        await message.answer('id состоит из цифр так то')
        case 'deleteadmin':
            if id == 177157427:
                if len(command) > 2:
                    try:
                        needed_id = int(command[2])
                        if needed_id != 177157427:
                            s = data_base("SELECT id FROM admin WHERE `id`=?", (needed_id,))
                            if s:
                                admin_list.remove(needed_id)
                                data_base(
                                    "DELETE from admin WHERE id = ?", 
                                    (needed_id,))
                                await message.answer(
                                    f'Пользователь с id {needed_id} был удален из администраторов')
                            else:
                                await message.answer(
                                    f'Пользователь с id {needed_id} не является администратором')
                    except ValueError:
                        await message.answer('id состоит из цифр так то')
        case 'alladmin':
            admins = data_base('SELECT * FROM admin')
            msg = users_to_msg('Список администраторов:\n\n', admins)
            await message.answer(msg)

#  //  profile

@bot.on.message(func=lambda message:
    (user_trigger[message.from_id]['Profile']))
async def menu_profile (message: Message):
    id = message.from_id
    match message.text.capitalize():
        case 'Сбросить профиль':
            data_base(
                "DELETE from users WHERE id = ?", 
                (id,))
            begin(id)
            await message.answer(
                "Выберите вашу роль", 
                keyboard=kb_role)
        case 'Изменить курс':
            if cache_dict[id][1] == 'Студент':
                user_trigger[id]['Profile'] = False
                chain = course_chain(cache_dict[id][4])
                if chain:
                    user_trigger[id]['Change_course'] = True
                    cache_dict[id].append(chain)
                    await message.answer(
                        'Выберите номер нового курса',
                        keyboard=get_keyboard(chain))
                else:
                    user_trigger[id]['Menu'] = True
                    await message.answer(
                        'К сожалению, для вас пока нет других доступных курсов',
                        keyboard=kb_menu) 
        case 'Изменить фамилию':
            if cache_dict[id][1] == 'Преподаватель':
                user_trigger[id]['Profile'] = False
                user_trigger[id]['Change_surname'] = True
                await message.answer(
                    'Введите новую фамилию',
                    keyboard=EMPTY_KEYBOARD)
        case 'Назад':
            user_trigger[id]['Profile'] = False
            await message.answer('Главное меню', keyboard=kb_menu)

@bot.on.message(func=lambda message:
    (user_trigger[message.from_id]['Change_course']))
async def change_course(message: Message):
    id = message.from_id
    if message.text.upper() in cache_dict[id][5]:
        cache_dict[id][4] = message.text.upper()
        del cache_dict[id][5]
        data_base(
            "UPDATE users SET 'group' = ? WHERE id = ?",
            (message.text.upper(), id))
        user_trigger[id]['Change_course'] = False
        user_trigger[id]['Menu'] = True
        await message.answer('Ваш курс был успешно изменен', keyboard=kb_menu)

@bot.on.message(func=lambda message:
    (user_trigger[message.from_id]['Change_surname']))
async def change_surname(message: Message):
    id = message.from_id
    text = message.text.capitalize()
    if not user_trigger[id]['Send']:
        cache_dict[id].append(text)
        user_trigger[id]['Send'] = True
        await message.answer(
            f'Ваша фамилия {text}. Все верно?', 
            keyboard=kb_proof)
    else:
        match text:
            case 'Да':
                user_trigger[id]['Send'] = False
                user_trigger[id]['Change_surname'] = False
                user_trigger[id]['Menu'] = True
                cache_dict[id][2] = cache_dict[id][5]
                del cache_dict[id][5]
                data_base(
                    "UPDATE users SET 'surname' = ? WHERE id = ?",
                    (cache_dict[id][2], id))
                await message.answer(
                    'Ваша фамилия была успешно изменена',
                    keyboard=kb_menu)
            case 'Нет':
                del cache_dict[id][5]
                user_trigger[id]['Send'] = False
                await message.answer(
                    'Введите свою фамилию ещё раз',
                    keyboard=EMPTY_KEYBOARD)
        

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
            keyboard = kb_corpus
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
                keyboard=kb_course)
    else:
        #   teacher
        if not user_trigger[id]['Send']:
            cache_dict[id][1].append(text)
            user_trigger[id]['Send'] = True
            await message.answer(
                f'Ваша фамилия {text}. Все верно?', 
                keyboard=kb_proof)
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
                    await message.answer(user_msg)
                case 'Нет':
                    del cache_dict[id][1][1]
                    user_trigger[id]['Send'] = False
                    user_msg = 'Введите свою фамилию ещё раз'
                    await message.answer(user_msg, keyboard=EMPTY_KEYBOARD)
            


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
        await message.answer(msg, keyboard=kb_proof)


@bot.on.message(func=lambda message: cache_dict[message.from_id][0] == 5)
async def reg_confirm (message: Message):
   id = message.from_id
   match message.text.capitalize():
        case "Да":
            cache_dict[id][1].insert(0, id)
            match cache_dict[id][1][1]:
                case 'Студент':
                    cache_dict[id][1].insert(2, None)
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
            user_trigger[id]['Menu'] = True
            await message.answer(
                'Главное меню', 
                keyboard=kb_menu)
        case "Нет":
            cache_dict[id] = [1, []]
            await message.answer(
                "Выберите вашу роль", 
                keyboard=kb_role)


bot.run_forever()