# ВК бот с расписанием для колледжа

### Бот находится в разработке
------------------------------

Для запуска бота необходимо создать файл `key.py` c вашим токеном в той же директории, что и файл `main.py`. 
Токен можно получить в настройках вашего сообщества.
```py
key = '<YOUR ACCESS TOKEN>'
```

Бот асинхронный, написан на <a href='https://github.com/vkbottle/vkbottle'>vkbottle</a>

Задуманный функционал:
- Регистрация пользователей
- Расписание для групп и преподавателей
- Быстрый просмотр своего расписания

База данных
-------

Поля       |    Описание           |   Принадлежность  |
-----------|-----------------------|-------------------|
id         |  id вконтакте         | Все               |
role       |  Роль                 | Все               |
last_name  |  Фамилия              | Преподаватели     |
corpus     |  Корпус               | Студенты          |
group      |  Группа               | Студенты          |
admin      |  Права администратора | Все               |
