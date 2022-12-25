from datetime import datetime


class Expense():
    def __init__(self, users, creditor, cost, purpose, date) -> None:
        self.users = users
        self.creditor = creditor
        self.cost = cost
        self.purpose = purpose
        try:
            self.date = datetime.strptime(date, '%Y.%m.%d %H:%M')
        except:
            self.date = datetime.strptime(date, '%Y/%m/%d %H:%M')

    def __str__(self) -> str:
        return f'{self.date},{self.creditor},{self.get_user_string()},{self.cost},{self.purpose}'

    def get_user_string(self):
        temp_str = ""
        for user in self.users:
            temp_str += f'{user}|'
        return temp_str
