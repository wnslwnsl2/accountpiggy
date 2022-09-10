# 1. YAML로 expense 넣는다.
# 2. 해당 파일 이름을 input으로 받고 정산을 한다.
import expense
import expense_matrix_maker
import expense_matrix_cleaner
import yaml


def main():
    print("Staring expense cleaning")
    with open('datas/jeju_220824_220829.yaml') as f:
        data = yaml.load(f, Loader=yaml.loader.SafeLoader)
        print(data['Users'])
        print(type(data))

if __name__ == "__main__":
    main()
