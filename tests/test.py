from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait



role = ('Студент', 'Преподаватель')
corpus = ('Корпус 1', 'Корпус 2')
course = ('1', '2', '3', '4')

def get_sequence():
    #создание всевозможных вариантов регистрации
    sequence = []
    for i in role:
        if i != 'Преподаватель':
            for j in corpus:
                for t in course:
                    sequence.append([i, j, t])
        else:
            sequence.append([i, 'Зубенко', 'Да', 'Да'])
    return sequence


class vk_test:
    def __init__(self, username, password):
        self.username = username
        self.user_pass = password
        self.login_url = 'https://vk.com'
        self.bot_id = '-207742975'
        self.driver = webdriver.Chrome(executable_path='tests\chromedriver.exe')
    
    def find(self, element:str, func:str, by = By.XPATH, sometext = ''):
        self.driver.implicitly_wait(5)
        match func:
            case 'click':
                try:
                    self.driver.find_element(by, element).click()
                except NoSuchElementException:
                    print(f'Элемент не найден, ожидаем появляения')
                    WebDriverWait(self.driver, timeout=10).until(self.driver.find_element(by, element).click())
                    
            case 'send_keys':
                try:
                    self.driver.find_element(by, element).send_keys(sometext)
                except NoSuchElementException:
                    print(f'Элемент не найден, ожидаем появляения')
                    WebDriverWait(self.driver, timeout=10).until(self.driver.find_element(by, element).send_keys(sometext))
    
    def send_message(self, text):
        sleep(3)
        self.find('//*[@id="im_editable0"]', 'send_keys', sometext=text)
        try:
            self.find('//*[@id="content"]/div/div/div[3]/div[2]/div[4]/div[2]/div[4]/div[1]/button/span[2]', 'click')
        except:
            #   captcha
            sleep(30)
            self.find('//*[@id="content"]/div/div/div[3]/div[2]/div[4]/div[2]/div[4]/div[1]/button/span[2]', 'click')

    def get_profile(self):
        sequence = get_sequence()
        sequence = [sequence[0], sequence[-1]]
        sequence[0].extend(['1Ф8', 'Да'])
        #   если регистрация в боте уже есть
        self.send_message('bebra')
        self.send_message('Профиль')
        self.send_message('Сбросить профиль')
        return sequence

    def exit(self):
        self.driver.quit()
    
    def login(self):
        self.find('//*[@id="index_email"]', 'send_keys', sometext=Keys.CONTROL + "a")
        self.find('//*[@id="index_email"]', 'send_keys', sometext=Keys.DELETE)
        self.find('//*[@id="index_email"]', 'send_keys', sometext=self.username)
        self.find('//*[@id="index_login"]/div/form/button/span', 'click')
    
    def password(self):
        self.find('/html/body/div/div/div/div[2]/div/form/div[1]/div[3]/div[2]/div[1]/div/input', 'send_keys', sometext=Keys.CONTROL + "a")
        self.find('/html/body/div/div/div/div[2]/div/form/div[1]/div[3]/div[2]/div[1]/div/input', 'send_keys', sometext=Keys.DELETE)
        self.find('/html/body/div/div/div/div[2]/div/form/div[1]/div[3]/div[2]/div[1]/div/input', 'send_keys', sometext=self.user_pass)
        self.find('/html/body/div/div/div/div[2]/div/form/div[2]/button', 'click')

    def verify_code(self):
        self.find(
            '/html/body/div/div/div/div[2]/form/div[5]/div/div/input', 
            'send_keys', 
            sometext=Keys.CONTROL + "a")
        self.find(
            '/html/body/div/div/div/div[2]/form/div[5]/div/div/input', 
            'send_keys', 
            sometext=Keys.DELETE)
        self.find(
            '/html/body/div/div/div/div[2]/form/div[5]/div/div/input', 
            'send_keys', 
            sometext=input('Введите код из приложения-генератора кодов: '))
        self.find('/html/body/div/div/div/div[2]/form/div[6]/div/button[1]/div', 'click')



    def log_in(self, step):
        if not step:
            self.driver.get(self.login_url)
            self.login()
            self.password()
            self.verify_code()
        else:
            match step:
                case 'login':
                    self.login()
                    self.password()
                    self.verify_code()
                case 'password':
                    self.password()
                    self.verify_code()
                case 'verify_code':
                    self.verify_code()
        url = self.driver.current_url
        if 'feed' not in url:
            match url[0]:
                case 'vk.com':
                    return [False, 'login']
                case 'id.vk.com':
                    try:
                        assert "пароль" in self.driver.page_source
                        return [False, 'password']
                    except AssertionError:
                        return [False, 'verify_code']
        else:
            return [True]
    
    def find_dialog(self):
        self.find('l_msg', 'click', By.ID)
        sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, f"li[data-list-id='{self.bot_id}']").click()
        url = self.driver.current_url.split('/')
        if url[-1] == 'im?sel=-207742975':
            return True
        else:
            return False
    
    def registration(self):   
        sequence = get_sequence()
        self.find('//*[@id="_im_keyboard_container"]/div/div/div[1]/div[1]/div/div[1]/div/div[1]/div[1]/button/span', 'click')
        self.send_message('Профиль')
        self.send_message('Сбросить профиль')
        for buttons in sequence:
            if buttons[0] != 'Преподаватель':
                for button in buttons:
                    self.send_message(button)
                sleep(3)
                self.find('button[type="text"]', 'click', By.CSS_SELECTOR)
                sequence_2 = ['Да', 'Профиль', 'Сбросить профиль', '-------------------Проверено-------------------']
                for text in sequence_2:
                    self.send_message(text)
                sleep(5)
            else:
                sequence_2 = [*buttons, 'Профиль', 'Сбросить профиль', '-------------------Проверено-------------------']
                for text in sequence_2:
                    self.send_message(text)
                sleep(5)
    
    def change_profile(self):
        sequence = self.get_profile()
        for role in sequence:
            for text in role:
                self.send_message(text)
            self.send_message('Профиль')
            if role[0] == 'Студент':
                self.send_message('Изменить курс')
            else:
                self.send_message('Изменить фамилию')
                self.send_message('Бебров')
            sleep(3)
            self.find(
                '//*[@id="_im_keyboard_container"]/div/div/div[1]/div[1]/div/div[1]/div/div[1]/div[1]/button/span',
                'click')
            self.send_message('Профиль')
            self.send_message('Сбросить профиль')
    
    def admin_commands(self):
        sequence = self.get_profile()
        commands = [
            '/admin users',
            '/admin user 177157427', '/admin user 1', '/admin user sellways',
            '/admin userbygroup 1Ф8', '/admin userbygroup 2ИС3', '/admin userbygroup 54',
            '/admin teacherbysurname Зубенко', '/admin teacherbysurname зубенко', '/admin teacherbysurname 54',
            '/admin allteacher',
            '/admin addadmin 177157427', '/admin addadmin be', '/admin addadmin 999999999999',
            '/admin deleteadmin 177157427', '/admin deleteadmin be', '/admin deleteadmin 999999999999',
            '/admin alladmin',
        ]
        for role in sequence:
            for text in role:
                self.send_message(text)
            for text in commands:
                self.send_message(text)
                self.send_message('----------------------')
            self.send_message('Профиль')
            self.send_message('Сбросить профиль')
            



if __name__ == '__main__':
    choice = input(
        '''Выберите тип проверки бота:
        1 - проверка регистрации
        2 - проверка изменения вторичных полей профиля
        3 - проверка команд админа
        4 - полная проверка
        ''')
    if choice in ['1', '2', '3', '4']:
        bot = vk_test(input('Введите свой логин: '), input('Введите свой пароль: '))
        login = bot.log_in(False)
        if login[0]:
            print('Выполнен вход в аккаунт')
            if bot.find_dialog():
                print('Найден диалог')
            else:
                bot.find_dialog()
            match choice:
                case '1':
                    bot.registration()
                case '2':
                    bot.change_profile()
                case '3':
                    bot.admin_commands()
                case '4':
                    bot.registration()
                    bot.change_profile()
                    bot.admin_commands()
        else:
            bot.log_in(login[1])
        bot.exit()