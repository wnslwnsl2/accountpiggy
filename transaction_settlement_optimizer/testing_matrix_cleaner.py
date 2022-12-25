# 1. YAML로 expense 넣는다.
# 2. 해당 파일 이름을 input으로 받고 정산을 한다.
from datetime import datetime
import expense
import expense_matrix_cleaner
import yaml


class User():
    def __init__(self, name, idx) -> None:
        self.name = name
        self.idx = idx
        self.initial_linked_expense = 0

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'name:{self.name} idx:{self.idx} linked_expense:{self.initial_linked_expense}'


class TestingExpenseCleaner():
    def __init__(self) -> None:
        self.users = {}
        self.expenses = []
        pass

    """
    Set user
    - idx to User
    - name to User
    """

    def SetUsers(self, users):
        self.n = len(users)
        self.mat = [[0 for col in range(self.n)] for row in range(self.n)]
        self.user_array = users
        self.users = {user: User(user, idx) for idx, user in enumerate(users)}

    """
    Set expenses
    """

    def SetExpenses(self, expenses_yaml_list):
        for e in expenses_yaml_list:
            temp_ex = expense.Expense(
                e["Users"], e["ExpendUser"], e["Cost"], e["Purpose"], e["DateTime"])
            self.expenses.append(temp_ex)

            nbbang_number = len(temp_ex.users)
            nbbang_cost = temp_ex.cost // nbbang_number

            creditor_idx = self.users[temp_ex.creditor].idx

            for debtor in temp_ex.users:
                debtor_idx = self.users[debtor].idx
                self.mat[debtor_idx][creditor_idx] += nbbang_cost
            print(temp_ex)

    def print_mat(self, mat):
        line_width = 10
        header = '\t'
        for user in self.users:
            header += f'{user}\t'
        header += f'1/N\t'
        print(header)

        for row in range(len(mat)):
            row_str = f'{self.user_array[row]}\t'
            debt_sum=0
            for debt_money in mat[row]:
                debt_sum+=debt_money
                row_str += f'{debt_money}\t'
            row_str += f'{debt_sum}\t'
            print(row_str)
        
        temp_sum=[ 0 for i in range(len(self.users))]

        for row in range(len(mat)):
            for col in range(len(mat)):
                temp_sum[col]+=mat[row][col]
        
        last_str="쓴돈\t"
        for row in range(len(mat)):
            last_str += f'{temp_sum[row]}\t'
        print(last_str)


def main():
    tec = TestingExpenseCleaner()

    with open('datas/jeju_220824_220829.yaml') as f:
        data = yaml.load(f, Loader=yaml.loader.SafeLoader)
        tec.SetUsers(data['Users'])
        tec.SetExpenses(data['Expenses'])

    print("\n\n")
    print("Before optimize expenses")
    tec.print_mat(tec.mat)

    print("\n\n")
    print("After optimize expenses")
    cleaner = expense_matrix_cleaner.ExpenseMatrixCleaner(tec.mat)
    tec.print_mat(cleaner.get_cleaned_matrix())


if __name__ == "__main__":
    main()
