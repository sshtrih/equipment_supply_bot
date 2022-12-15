import string
import telebot
import psycopg2
import re

import pandas as pd

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from psycopg2 import sql
from keyboa import Keyboa

from res import completed_task_data, unfulfilled_task_data, BOT_TOKEN, find_dict, client_data

bot = telebot.TeleBot(BOT_TOKEN)


class Person:

    def __init__(self):
        self.employee_id = None
        self.markup = None
        self.status = None
        self.new_task_attributes = ['Название задания', 'Срок выполнения', 'Контракт', 'Контактное лицо',
                                    'Приоритет от 1 до 3']
        self.task_status = None
        self.update_task_par = {}
        self.employees = None
        self.unfulfilled_name = None
        self.unfulfilled_tasks = None
        self.completed_tasks = None
        self.completed_tasks_name = None
        self.connection = None
        self.role = None
        self.clients = None
        self.message_id = None
        self.password = None
        self.login = None
        self.confirm_password = None
        self.find_query = sql.SQL('''SELECT * FROM Organization JOIN address ON organization.address_id = address.id 
                        JOIN contact_person ON contact_person.organization_id = Organization.organization_id WHERE ''') \
            .format()
        self.connection = psycopg2.connect(user="postgres",
                                           password="200330020550",
                                           host="127.0.0.1",
                                           port="5432",
                                           database="Equipment supply")

        self.cursor = self.connection.cursor()

    def create_user(self):
        query_create = sql.SQL("CREATE USER {username} WITH PASSWORD {password};").format(
            username=sql.Identifier(self.login),
            password=sql.Placeholder()
        )
        self.cursor.execute(query_create, [self.password])
        self.connection.commit()

        query_grant = sql.SQL("GRANT {role} TO {username};").format(
            role=sql.Identifier(self.role),
            username=sql.Identifier(self.login)
        )

        self.cursor.execute(query_grant)
        self.connection.commit()

    def unfulfilled_task(self):
        self.cursor.execute("SELECT * FROM task WHERE completion_status = false")
        self.unfulfilled_tasks = self.cursor.fetchall()
        self.unfulfilled_name = [i[8] for i in self.unfulfilled_tasks]

    def completed_task(self):
        self.cursor.execute("SELECT * FROM task WHERE completion_status = true")
        self.completed_tasks = self.cursor.fetchall()
        self.completed_tasks_name = [i[8] for i in self.completed_tasks]

    def authorization(self):
        try:
            query = sql.SQL("SET ROLE {username};").format(
                username=sql.Identifier(self.login)
            )

            self.cursor.execute(query)
            self.connection.commit()

            self.cursor.execute("SELECT post FROM Employee WHERE login = current_user;")
            post, = self.cursor.fetchone()
            if post == 'Менеджер':
                self.role = 'managers'
            else:
                self.role = 'ordinary_employees'
            return True
        except Exception as e:
            self.connection.commit()
            return False

    def update_task(self):
        for key, value in dict(list(self.update_task_par.items())[1:]).items():
            query = sql.SQL('UPDATE TASK SET {field_name}=%s WHERE task_id=%s;').format(
                field_name=sql.Identifier(key)
            )
            print(self.cursor.execute(query, (value, str(self.update_task_par['task_id']))))

        self.connection.commit()

    def find_client(self):
        self.cursor.execute(self.find_query)
        self.clients = self.cursor.fetchall()

    def create_task(self, employee_id):

        self.cursor.execute("INSERT INTO TASK (task_name, term_of_execution, contract_sn, contact_person_id, priority )"
                            "VALUES (%s, %s, %s, %s, %s) RETURNING task_id", [i for i in self.new_task_attributes])
        task_id, = self.cursor.fetchall()
        print(task_id)

        self.cursor.execute("INSERT INTO TASK_EMPLOYEE VALUES (%s, %s)", (task_id, employee_id))
        self.connection.commit()

    def get_employees(self):

        self.cursor.execute("SELECT * FROM employee")
        self.employees = self.cursor.fetchall()


person = Person()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Привет, наш бот создан только для сотрудников компании.\n'
                                           'Для продолжения необходимо авторизоваться:\n\n'
                                           '/sign_in - Войти в систему\n/sign_up - Зарегистрироваться')


@bot.message_handler(commands=['sign_in', 'sign_up'])
def new_request(message):
    if message.text == '/sign_in':
        mess = 'Введите ваш логин'
        person.status = 'authorization'
    else:
        mess = 'Мы очень рады новому сотруднику!\nПожалуйста, придумайте логин для входа'
        person.status = 'registration'
    bot.send_message(message.chat.id, mess)
    bot.register_next_step_handler(message, login)


def login(message):
    person.login = message.text
    input_password(message)


@bot.message_handler(commands=['find_client'])
def find_client(message):
    mess = 'Введите поле, по которому хотите найти клиента\n' \
           '`Название организации`\n`ИНН`\n`Номер телефона`\n`Электронная почта`\n' \
           '`Область`\n`Город`\n`Район`\n`Улица`\n' \
           '`Номер дома и квартиры`\n`Почтовый адрес`\n' \
           '`Контактное лицо`\n`Телефон контактного лица`\n`Электронная почта контактного лица`'
    bot.send_message(message.from_user.id, mess, parse_mode='markdown')
    bot.register_next_step_handler(message, find)


def find(message, else_field=''):
    if message.text == 'Найти':
        person.find_client()
        for i in person.clients:
            mess = client_data.format(title=i[1], inn=i[0], phone_number=i[2], email_address=i[4],
                                      client_status=i[5], area=i[8], locality=i[9], district=i[10],
                                      street=i[11], street_address=i[12], postal_code=i[13], name=i[16],
                                      phone_number_person=i[17], email_address_person=i[18])
            bot.send_message(message.from_user.id, mess, parse_mode='html')
    else:
        field_name, field_data = message.text.split('=')
        person.find_query += sql.SQL("{else_field} {field_name} = {field_data}").format(
            else_field=sql.SQL(else_field),
            field_name=sql.SQL(find_dict[field_name]),
            field_data=sql.Literal(field_data)
        )
        bot.register_next_step_handler(message, find, 'AND')


@bot.message_handler(commands=['report'])
def create_report(message):
    person.get_employees()
    keyboard_employee = Keyboa(items=[i[1] for i in person.employees]).keyboard
    bot.send_message(message.from_user.id, 'Выберите сотрудника', reply_markup=keyboard_employee)


@bot.message_handler(commands=['new_task'])
def create_task(message, key=0):
    if message.text == '/new_task':
        bot.send_message(message.from_user.id, person.new_task_attributes[key])
        bot.register_next_step_handler(message, create_task, key + 1)
    else:
        if key == len(person.new_task_attributes):
            person.new_task_attributes[key - 1] = message.text
            bot.register_next_step_handler(message, create_task, key + 1)
        elif key > len(person.new_task_attributes):
            create_report(message)
        else:
            bot.send_message(message.from_user.id, person.new_task_attributes[key])
            person.new_task_attributes[key - 1] = message.text
            bot.register_next_step_handler(message, create_task, key + 1)


@bot.message_handler(commands=['completed_task', 'unfulfilled_task'])
def show_tasks_list(message, n=0, edit_flag=False):
    if person.role is not None:
        try:
            person.task_status = message.text[1:]
        except AttributeError:
            pass

        if person.task_status == 'completed_task':
            person.completed_task()
            all_task = [{i[8]: f't{i[9]}'} for i in person.completed_tasks]
        else:
            person.unfulfilled_task()
            all_task = [{i[8]: f'ut{i[9]}'} for i in person.unfulfilled_tasks]
        if len(all_task) <= 10:
            keyboard = Keyboa(all_task[n:n + 10]).keyboard
        else:
            if n + 10 > len(all_task):
                items = [{'⏪ Назад': f'back-{n - 10}'}]
            elif n < 10:
                items = [{'Вперёд ⏩': f'next-{n + 10}'}]
            else:
                items = [{'⏪ Назад': f'back-{n - 10}'}, {'Вперёд ⏩': f'next-{n + 10}'}]

            keyboard_flipping = Keyboa(items=items, items_in_row=2).keyboard
            keyboard_task = Keyboa(all_task[n:n + 10]).keyboard
            keyboard = Keyboa.combine(keyboards=(keyboard_task, keyboard_flipping))
        if not edit_flag:
            person.message_task = bot.send_message(message.from_user.id, 'Задания', reply_markup=keyboard).id
        else:
            bot.edit_message_text(text='Задания', chat_id=message.from_user.id,
                                  message_id=person.message_task,
                                  reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, 'У вас нет привилегий')


def role(message):
    button_manager = KeyboardButton('Менеджер')
    button_clerk = KeyboardButton('Рядовой сотрудник')
    markup = ReplyKeyboardMarkup().row(button_manager, button_clerk)
    bot.send_message(message.from_user.id, 'Выберите должность: ',
                     reply_markup=markup)


def show_task(message, task_id):
    if task_id.startswith('t'):
        task_id = int(task_id[1:])
        task = list(filter(lambda x: x[9] == task_id, person.completed_tasks))[0]
        mess = completed_task_data.format(task_name=task[9], task_id=task[8], date_of_creation=task[0],
                                          term_of_execution=task[1], contract=task[2], contact_person=task[4],
                                          author=task[5], completion_date=task[6], priority=task[7])
        bot.send_message(message.from_user.id, mess, parse_mode='html')
    else:
        task_id = int(task_id[2:])
        inline_kb1 = InlineKeyboardMarkup()
        task = list(filter(lambda x: x[9] == task_id, person.unfulfilled_tasks))[0]
        mess = unfulfilled_task_data.format(task_name=task[9], task_id=task[8], date_of_creation=task[0],
                                            term_of_execution=task[1], contract=task[2], contact_person=task[4],
                                            author=task[5], priority=task[7])
        btn_complete = InlineKeyboardButton('Выполнить', callback_data=f'complete{task_id}')
        inline_kb1.add(btn_complete)

        if person.role == 'managers':
            btn_change = InlineKeyboardButton('Изменить', callback_data=f'change{task_id}')
            inline_kb1.add(btn_change)
        bot.send_message(message.from_user.id, mess, parse_mode='html', reply_markup=inline_kb1)


def input_password(message, case='lower', edit_flag=False):
    keyboard_erase_finish = Keyboa(items=[{'✅': 'finish'}, {'⬅': 'erase'}], items_in_row=2).keyboard
    if case == 'upper':
        items = [{'🔡': 'lower'}, {'🔢': 'dig'}, {'🔣': 'punc'}]
    elif case == 'lower':
        items = [{'🔠': 'upper'}, {'🔢': 'dig'}, {'🔣': 'punc'}]
    elif case == 'dig':
        items = [{'🔠': 'upper'}, {'🔡': 'lower'}, {'🔣': 'punc'}]
    else:
        items = [{'🔠': 'upper'}, {'🔡': 'lower'}, {'🔢': 'dig'}]

    keyboard_flipping = Keyboa(items=items, items_in_row=3).keyboard

    keyboard_lower = Keyboa(items=list(string.ascii_lowercase), items_in_row=5).keyboard
    keyboard_upper = Keyboa(items=list(string.ascii_uppercase), items_in_row=5).keyboard
    keyboard_dig = Keyboa(items=list(string.digits), items_in_row=5).keyboard
    keyboard_punc = Keyboa(items=list(string.punctuation), items_in_row=5).keyboard

    keyboard = Keyboa.combine(keyboards=(keyboard_erase_finish, eval(f'keyboard_{case}'), keyboard_flipping))
    mess = 'Введите пароль'
    if not edit_flag:
        res = bot.send_message(message.from_user.id, mess, reply_markup=keyboard)
        person.message_id = res.id
    else:
        bot.edit_message_text(mess, chat_id=message.from_user.id,
                              message_id=person.message_id,
                              reply_markup=keyboard)


def after_authorization(message, successful):
    if successful:
        bot.send_message(message.from_user.id, 'Авторизация прошла успешно\n\nСписок команд для продолжения:\n\n'
                                               '/completed_task - Просмотреть выполненные задачи\n/unfulfilled_task - '
                                               'Просмотреть невыполненные задачи\n/find_client - Найти клиента\n'
                                               '/report - Cоздать отчёт по сотруднику\n'
                                               '/new_task - Создать новую задачу')
    else:
        bot.send_message(message.from_user.id, 'Похоже вы неправильно ввели логин или пароль, попробуйте снова')
        person.login = None
        person.password = None
        start(message)


def complete_task(message, task_id):
    person.cursor.execute(f"UPDATE TASK SET completion_status=true, completion_date = (SELECT NOW()) "
                          f"WHERE task_id={task_id};")
    person.connection.commit()
    bot.send_message(message.from_user.id, 'Задание выполнены')


def change_task(call, task_id):
    person.update_task_par.update({'task_id': task_id})
    button1 = KeyboardButton('Срок выполнения')
    button2 = KeyboardButton('Контактное лицо')
    button3 = KeyboardButton('Приоритет')
    button4 = KeyboardButton('Название')
    button5 = KeyboardButton('Сохранить изменения')
    markup = ReplyKeyboardMarkup().row(button4, button1).row(button2, button3).add(button5)
    bot.send_message(call.from_user.id, 'Выберите поле, которое хотите изменить', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == 'Название':
        bot.send_message(message.from_user.id, 'Введите новое значений')
        bot.register_next_step_handler(message, update_name)
    elif re.match(r'\d{4}-\d{2}-\d{2} \d{4}-\d{2}-\d{2}', message.text):
        create_employee_report(message, message.text)
    elif message.text == 'Срок выполнения':
        bot.send_message(message.from_user.id, 'Введите новое значений')
        bot.register_next_step_handler(message, update_term_of_execution)
    elif message.text == 'Контакное лицо':
        pass
    elif message.text == 'Приоритет':
        bot.send_message(message.from_user.id, 'Введите новое значений')
        bot.register_next_step_handler(message, update_priority)
    elif message.text == 'Сохранить изменения':
        person.update_task()
        bot.send_message(message.from_user.id, 'Параметры изменены', reply_markup=ReplyKeyboardRemove())
    elif message.text == 'Менеджер':
        person.role = 'managers'
        person.create_user()
        bot.send_message(message.from_user.id, 'Пользователь успешно создан', reply_markup=ReplyKeyboardRemove())
    elif message.text == 'Рядовой сотрудник':
        person.role = 'ordinary_employees'
        person.create_user()
        bot.send_message(message.from_user.id, 'Пользователь успешно создан', reply_markup=ReplyKeyboardRemove())


def select_reports_date(message, employee_id):
    bot.send_message(message.from_user.id, 'Введите период за которой нужно сделать отчёт по сотруднику в формате:\n'
                                           '<u>YYYY-MM-DD YYYY-MM-DD</u>', parse_mode='html')
    person.employee_id = employee_id


def create_employee_report(message, mess):
    start_date, end_date = mess.split(' ')
    person.cursor.execute("SELECT * FROM report(%s,%s,%s)",
                          (start_date, end_date, person.employee_id))
    tasks = person.cursor.fetchall()
    df = pd.DataFrame({'Всего': [tasks[0][0]], 'В срок': [tasks[0][1]],
                       'Не в срок': [tasks[0][2]],
                       'Истёкших незавершено': [tasks[0][3]],
                       'Неистёкших незавершено': [tasks[0][4]]})
    df.to_excel(r'D:\teams.xlsx', index=False)
    f = open(r'D:\teams.xlsx', "rb")
    bot.send_document(message.from_user.id, f)


def update_name(message):
    person.update_task_par.update({'task_name': str(message.text)})


def update_priority(message):
    person.update_task_par.update({'priority': str(message.text)})


def update_term_of_execution(message):
    person.update_task_par.update({'term_of_execution': str(message.text)})


def show_employee(message, name):
    employee = list(filter(lambda x: x[1] == name, person.employees))[0]
    button_report = InlineKeyboardButton('Создать отчёт по сотруднику', callback_data=f'report{employee[0]}')
    button_add_in_task = InlineKeyboardButton('Назначить задание', callback_data=f'add_task{employee[0]}')
    keyboard = InlineKeyboardMarkup().row(button_report, button_add_in_task)
    mess = f'<b>Сотрудник</b>\n<u>{employee[1]}</u>\n\n<b>Должность</b>\n<u>{employee[2]}</u>\n\n' \
           f'<b>Логин</b>\n<u>{employee[3]}</u>'
    bot.send_message(message.from_user.id, mess, parse_mode='html', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if re.match(r'add_task', call.data):
        person.create_task(call.data[8:])
    elif re.match(r'report', call.data):
        select_reports_date(call, call.data[6:])
    elif re.match(r'\w+ \w+ \w+', call.data):
        show_employee(call, call.data)
    elif re.match(r'complete\d+', call.data):
        complete_task(call, int(call.data[8:]))
    elif call.data[:4] == 'next':
        show_tasks_list(call, int(call.data[5:]), True)
    elif call.data[:4] == 'back':
        show_tasks_list(call, int(call.data[5:]), True)
    elif re.match(r'change\d+', call.data):
        change_task(call, int(call.data[6:]))
    elif re.match(r'.{1,2}\d+', call.data):
        show_task(call, call.data)
    elif call.data == 'erase':
        if person.password is not None:
            try:
                person.password = person.password[:len(person.password) - 1]
                password = '*' * len(person.password)
                bot.edit_message_text(text=f'<b>{password}</b>', chat_id=call.from_user.id,
                                      message_id=person.password_message_id, parse_mode='html')
            except:
                person.password = None
                bot.delete_message(chat_id=call.from_user.id,
                                   message_id=person.password_message_id)

    elif call.data == 'finish':
        if person.status == 'authorization':
            after_authorization(call, person.authorization())
        else:
            role(call)
    elif re.match(r'\w{3,5}', call.data):
        input_password(call, call.data, True)
    elif re.match(r'.', call.data):
        if person.password is None:
            password_message = bot.send_message(call.from_user.id, '<b>*</b>', parse_mode='html')
            person.password_message_id = password_message.id
            person.password = str(call.data)

        else:
            person.password += str(call.data)
            password = '*' * len(person.password)
            bot.edit_message_text(text=f'<b>{password}</b>', chat_id=call.from_user.id,
                                  message_id=person.password_message_id, parse_mode='html')


bot.infinity_polling()
