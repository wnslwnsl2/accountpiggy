# 1. YAML로 expense 넣는다.
# 2. 해당 파일 이름을 input으로 받고 정산을 한다.
from datetime import datetime
import expense
import expense_matrix_maker
import expense_matrix_cleaner
import yaml


class TestingExpenseCleaner():
    def __init__(self) -> None:
        self.users = None
        self.expenses = []
        self.mat = []
        pass

    def SetUsers(self, users):
        self.users = users

    def SetExpenses(self, expenses_yaml_list):
        for e in expenses_yaml_list:
            temp_ex = expense.Expense(
                e["Users"], e["ExpendUser"], e["Cost"], e["Purpose"], e["DateTime"])
            self.expenses.append(temp_ex)
            print(temp_ex)
    
    def SetMatrix(self):
        pass

def main():
    tec = TestingExpenseCleaner()

    print("Staring expense cleaning")
    with open('datas/jeju_220824_220829.yaml') as f:
        data = yaml.load(f, Loader=yaml.loader.SafeLoader)
        tec.SetUsers(data['Users'])
        tec.SetExpenses(data['Expenses'])


if __name__ == "__main__":
    main()
