from datetime import datetime


class Expense():
    def __init__(self, users, spender, cost, purpose, date) -> None:
        self.users = users
        self.spender = spender
        self.cost = cost
        self.purpose = purpose
        self.date = datetime.strptime(date, '%Y-%m-%d %H:%M')

    def __str__(self) -> str:
        return f'Users: {self.users} Spender: {self.spender} Cost: {self.cost} Purpose: {self.purpose}'
