
#   //  тригеры для логики  //

Trigger = {
    #   регистрация
    'Reg': True,
    'Send': False,
    #   меню
    'Main': True,
    'Profile': False,
    'Admin': False,
    'Spam': False,
    'Change': False,
    #   расписание
    'Rasp': False,
    'Data': False,
    'Mine_Rasp': False,
    'Teacher': False
}

admin_list = [
    177157427,
    501057196
]

cache_dict = {}

#   //    инофрмация о пользователе   //

#   id          //  id вконтакте         //  Все
#   role        //  Роль                 //  Все
#   last_name   //  Фамилия              //  Преподаватели
#   corpus      //  Корпус               //  Студенты
#   group       //  Группа               //  Студенты
#   admin       //  Права администратора //  Все


#   //    ключи    //

role = ('Студент', 'Преподаватель')
corpus = ('Корпус 1', 'Корпус 2')
course = ('1', '2', '3', '4')
menu_key = ("Расписание", "Своё расписание", "Профиль", "Админ")
admin_key = ('Нюхнуть бебры', 'Рассылка', 'Пукнуть сливой', 'Назад')
rasp_key = ('По группам', 'По преподавателям', 'Назад')
profile = ('Сбросить профиль', 'Изменить курс', 'Назад')