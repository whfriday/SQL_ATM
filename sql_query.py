"""Методы, с помощью которых отправляются sql-запросы"""

import sqlite3, csv, datetime

now_date = datetime.datetime.now().strftime("%H:%M-%d.%m.%Y")

class  SQL_ATM:

    
    @staticmethod
    def create_table():
        """Создание таблицы Users_data"""

        with sqlite3.connect("atm.db") as db:   #конструкция with позволяет не прописывать команду commit, выполняя её автоматически
            cur = db.cursor()   #переменная для управления БД
            cur.executescript("""CREATE TABLE IF NOT EXISTS Users_data(
                        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Number_card INTEGER NOT NULL UNIQUE,
                        Pin_code INTEGER NOT NULL,
                        Balance INTEGER NOT NULL);""")    
            print("Создание таблицы Users_data")
            

    @staticmethod
    def insert_users(users_data):
        """Создание нового пользователя"""

        with sqlite3.connect("atm.db") as db:   
            cur = db.cursor()
            cur.execute("""CREATE UNIQUE INDEX IF NOT EXISTS card_num ON Users_data (Number_card, Pin_code, Balance);""") #уникальный индекс, чтобы исключить дубликаты 
            cur.execute("""INSERT OR IGNORE INTO Users_data (Number_card, Pin_code, Balance) VALUES(?, ?, ?);""", users_data)
            print("Создание нового пользователя")


    @staticmethod
    def input_card(number_card):
            """Ввод и проверка карты"""
            try:
                with sqlite3.connect("atm.db") as db:   
                    cur = db.cursor() 
                    cur.execute(f"""SELECT Number_card FROM Users_data WHERE Number_card = {number_card}""")
                    result_card = cur.fetchone()
                    if result_card == None:
                        print("Введён неизвестный номер карты")
                        return False
                    else:
                        print(f"Введён номер карты: {number_card}")
                        return True
            except:
                print("Введён неизвестный номер карты")
    
    @staticmethod
    def input_code(number_card):
        """Ввод и проверка пин-кода"""

        pin_code = input("Введите, пожалуйста, пин-код карты: ")

        with sqlite3.connect("atm.db") as db:   
            cur = db.cursor() 
            cur.execute(f"""SELECT Pin_code FROM Users_data WHERE Number_card = {number_card}""")
            result_code = cur.fetchone()
            input_pin = result_code[0]
            try:
                if input_pin == int(pin_code):
                    print("Введён верный пин-код")
                    return True
                else:
                    print("Введён некорректный пин-код")
                    return False
            except:
                print("Введён некорректный пин-код")
                return False
            

    @staticmethod
    def info_balance(number_card):
        """Вывод на экран баланса карты"""

        with sqlite3.connect("atm.db") as db:   
            cur = db.cursor() 
            cur.execute(f"""SELECT Balance FROM Users_data WHERE Number_card = {number_card}""")
            result_info_balance = cur.fetchone()
            balance_card = result_info_balance[0]
            print(f"Баланс вашей карты: {balance_card}")


    @staticmethod
    def withdraw_money(number_card):
        """Снятие денежных средств с баланса карты"""

        amount = input("Введите, пожалуйста, сумму, которую желаете снять: ")
        with sqlite3.connect("atm.db") as db:   
            cur = db.cursor() 
            cur.execute(f"""SELECT Balance FROM Users_data WHERE Number_card = {number_card}""")
            result_info_balance = cur.fetchone()
            balance_card = result_info_balance[0]
            try:
                if int(amount) <= 0:
                    print("Введите корректную сумму!")
                    return False
                elif int(amount) > balance_card:
                    print("На вашей карте недостаточно денежных средств.")
                    return False
                else:
                    cur.execute(f"""UPDATE Users_data SET Balance = Balance - {int(amount)} WHERE Number_card = {number_card};""")
                    db.commit()
                    print("Заберите денежные средства в лотке для выдачи")
                    SQL_ATM.info_balance(number_card)
                    SQL_ATM.report_operation_1(now_date, number_card, "1", amount, "")
                    return True
            except:
                print("Попытка выполнить некорректное действие")
                return False
            
    
    @staticmethod
    def deposition_money(number_card):
        """Внесение денежных средств"""

        amount = input("Введите, пожалуйста, сумму, которую желаете внести: ")
        with sqlite3.connect("atm.db") as db:   
            cur = db.cursor() 
        try:
            if int(amount) <= 0:
                    print("Введите корректную сумму!")
                    return False
            cur.execute(f"""UPDATE Users_data SET Balance = Balance + {int(amount)} WHERE Number_card = {number_card};""")
            db.commit()
            print("Денежные средства поступили на ваш счёт!")
            SQL_ATM.info_balance(number_card)
            SQL_ATM.report_operation_1(now_date, number_card, "2", amount, "")
        except:
            print("Попытка выполнить некорректное действие")
            return False
        
    @staticmethod
    def transfer_money(number_card):
        """Перевод денежных средств"""

        payee_number_card = input("Введите, пожалуйста, номер карты получателя: ")
        amount = input("Введите, пожалуйста, сумму, которую желаете перевести: ")
        
        with sqlite3.connect("atm.db") as db:   
            cur = db.cursor()
        try:
            if int(amount) <= 0:
                    print("Введите корректную сумму!")
                    return False

            #ошибка перевода самому себе
            if number_card == payee_number_card:
                print("Вы не можете переводить средства самому себе!")
                return False
        
            cur.execute(f"""SELECT Balance FROM Users_data WHERE Number_card = {number_card}""")
            result_info_balance = cur.fetchone()
            balance_card = result_info_balance[0]
            
            if int(amount) > balance_card:
                print("На вашей карте недостаточно денежных средств.")
                return False
            
        # Проверка существования в БД получателя
            cur.execute(f"""SELECT Number_card FROM Users_data WHERE Number_card = {payee_number_card}""")
            payee_card_result = cur.fetchone()
            if payee_card_result == None:
                print("Проверьте корректность карты получателя")
                return False
            
            else:
                cur.executescript(f"""UPDATE Users_data SET Balance = Balance - {int(amount)} WHERE Number_card = {number_card};
                                UPDATE Users_data SET Balance = Balance + {int(amount)} WHERE Number_card = {payee_number_card};""")
                db.commit()
                print("Денежные средства успешно отправлены получателю!")
                SQL_ATM.info_balance(number_card)
                SQL_ATM.report_operation_1(now_date, number_card, "3", amount, payee_number_card)
                SQL_ATM.report_operation_2(now_date, payee_number_card, "3", amount, number_card)
        except:
            print("Попытка выполнить некорректное действие")
            return False
                
        
    @staticmethod
    def input_operation(number_card):
        """Выбор операции"""
        while True:
            operation = input("Введите, пожалуйста, операцию, которую хотите совершить: \n"
                            "1. Узнать баланс \n"
                            "2. Снять денежные средства\n"
                            "3. Внести денежные средства\n"
                            "4. Завершить работу\n"
                            "5. Перевести денежные средства\n")
            if operation == "1":
                SQL_ATM.info_balance(number_card)
            elif operation == "2":
                SQL_ATM.withdraw_money(number_card)
            elif operation == "3":
                SQL_ATM.deposition_money(number_card)
            elif operation == "4":
                print("Спасибо за Ваш визит, всего доброго!")
                return False
            elif operation == "5":
                SQL_ATM.transfer_money(number_card)
            else:
                print("Данная операция недоступна, приносим свои извинения. Попробуйте другую операцию!")

    @staticmethod
    def report_operation_1(now_date, number_card, type_operation, amount, payee):
        """Отчёт об операциях"""
        user_data = [
            (now_date, number_card, type_operation, amount, payee)
        ]
        with open("report_1.csv", "a", newline='') as file: 
            writer = csv.writer(file, delimiter=";")    
            writer.writerows(
                user_data
            )
        print("Данные внесены в отчёт")

    @staticmethod
    def report_operation_2(now_date, payee, type_operation, amount, sender):
        """Отчёт о переводах между клиентами"""
        user_data = [
            (now_date, payee, type_operation, amount, sender)
        ]
        with open("report_2.csv", "a", newline='') as file: 
            writer = csv.writer(file, delimiter=";")    
            writer.writerows(user_data)
        print("Данные р переводе внесены в отчёт")


    """type_operation
    1 - Снятие
    2 - Пополнение
    3 - Перевод"""
