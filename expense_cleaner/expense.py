class Expense():
    def __init__(self, users, expend_user_index, cost, purpose, datetime) -> None:
        self.users = users
        self.expend_user_index = expend_user_index
        self.cost = cost
        self.purpose = purpose
        self.datetime = datetime
