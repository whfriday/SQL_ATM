"""Логика работы банкомата"""

from sql_query import SQL_ATM


class ATM:

    def atm_logic(self):
        SQL_ATM.create_table()
        SQL_ATM.insert_users((1234, 1111, 10000))
        SQL_ATM.insert_users((2345, 2222, 10000))
        number_card = input("Введите, пожалуйста, номер карты: ")

        while True:
            if SQL_ATM.input_card(number_card):
                if SQL_ATM.input_code(number_card):
                    
                    SQL_ATM.input_operation(number_card)
                    break
                else:
                    break
            else:
                break


start = ATM()
start.atm_logic()

