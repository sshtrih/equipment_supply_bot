BOT_TOKEN = '5782975625:AAFh6w-_RUFAApDgQ-hEFD7NMYo1E-DfV1o'

completed_task_data = '<b>Задание №{task_name}</b>\n<u>{task_id}</u>\n\n' \
                      '<b>Дата создания</b>\n<u>{date_of_creation}</u>\n\n' \
                      '<b>Срок завершения</b>\n<u>{term_of_execution}</u>\n\n' \
                      '<b>Контракт</b>\n<u>{contract}</u>\n\n' \
                      '<b>Контактное лицо</b>\n<u>{contact_person}</u>\n\n' \
                      '<b>Автор</b>\n<u>{author}</u>\n\n' \
                      '<b>Дата выполнения выполнено</b>\n<u>{completion_date}</u>\n\n' \
                      '<b>Приоритет</b>\n<u>{priority}</u>'

unfulfilled_task_data = '<b>Задание №{task_name}</b>\n<u>{task_id}</u>\n\n' \
                        '<b>Дата создания</b>\n<u>{date_of_creation}</u>\n\n' \
                        '<b>Срок завершения</b>\n<u>{term_of_execution}</u>\n\n' \
                        '<b>Контракт</b>\n<u>{contract}</u>\n\n' \
                        '<b>Контактное лицо</b>\n<u>{contact_person}</u>\n\n' \
                        '<b>Автор</b>\n<u>{author}</u>\n\n' \
                        '<b>Приоритет</b>\n<u>{priority}</u>'

find_dict = {'Название организации': 'organization.title', 'ИНН': 'organization.inn',
             'Номер телефона': 'organization.phone_number', 'Электронная почта': 'organization.email_address',
             'Область': 'address.area', 'Город': 'address.locality', 'Район': 'address.district',
             'Улица': 'address.street', 'Номер дома и квартиры': 'street_address', 'Почтовый адрес': 'postal_code',
             'Контактное лицо': 'contact_person.name', 'Телефон контактного лица': 'contact_person.phone_number',
             'Электронная почта контактного лица': 'contact_person.email_address'}

client_data = '<b>{title}</b> (<strong>{inn}</strong>) \n<u>{phone_number}</u>\n<u>{email_address}</u>\n' \
              '<b>Активный клиент</b> - <u>{client_status}</u>\n\n' \
              '<b>Адрес</b>\n<u>{area}, {locality}, {district}, {street},'\
              ' {street_address}</u> (<b>{postal_code}</b>) \n\n<b>Контактное лицо</b>\n{name}\n'\
              '<u>{phone_number_person}</u>\n<u>{email_address_person}</u>'

employee_data = ''