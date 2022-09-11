import numpy as np
import participant

# TODO
# 1. Makes init receive explicit parameters.
# 
class ExpenseMatrixCleaner:
    def __init__(self,mat):
        self.n = len(mat)
        self.expense_matrix = np.asarray(mat)
        self.participants = self.__get_initial_participants(self.expense_matrix,self.n)

    # 캔슬링 진행 메서드(외부 호출)
    def get_cleaned_matrix(self):
        self.__clean()
        return self.expense_matrix

    # 사용 내역을 matrix에 n등분 하여 기록한다.
    def __get_initial_mat(self,expense_log_list,n):
        expense_matrix = np.zeros((n,n))
        for expense_log in expense_log_list:
            #print("{},{},{}".format(expense_log.spend_user_id,expense_log.participant_user_id_list,expense_log.cost))
            dividedExpense = expense_log.cost / len(expense_log.participant_user_id_list)
            for participant_user in expense_log.participant_user_id_list:
                expense_matrix[self.user_id_list.index(participant_user)][self.user_id_list.index(expense_log.spend_user_id)] += dividedExpense
        return expense_matrix

    # 확정) matrix를 만들고 나서 제일 큰 순으로 매트릭스를 다시 정렬하는 건 좋지 않다.
    def __getname_order_by_total_expense_value(self,user_id_list,expense_log_list,n):
        #지출 비용을 담을 list
        expense_list = [0 for i in range(n)]
        for expense_log in expense_log_list:
            if expense_log.spend_user_id in expense_log.participant_user_id_list:
                #자신한테 쓴 돈 제외
                expense_list[user_id_list.index(expense_log.spend_user_id)] += expense_log.cost / len(expense_log.participant_user_id_list) * (len(expense_log.participant_user_id_list)-1)
            else:
                expense_list[user_id_list.index(expense_log.spend_user_id)] += expense_log.cost

        #지출 비용을 sort할 tuple
        idx_expense_value_tuple_list = [(idx,expense_list[idx]) for idx in range(n)]
        idx_expense_value_tuple_list.sort(key=lambda x:x[1])
        #지출 비용 순으로 정렬된 names를 return
        return [user_id_list[t[0]] for t in idx_expense_value_tuple_list]

    # 참가자들에 대한 클래스를 생성한다.
    def __get_initial_participants(self,expense_matrix,n):
        participants = []
        for row in range(n):
            participants.append(Participant(row,expense_matrix[row],expense_matrix[:,row]))
        return participants

    #실제 캔슬링을 진행한다.
    def __clean(self):
        for sender in self.participants:
            for from_cand in [col for col in range(self.n) if col != sender.idx and sender.getSend(col)!=0]:
                # [from_cand 추가 기준]
                # 1) 본인 지출 항목으로부터 항목이 움직이지 않게 하기
                #   > col != sender.idx
                # 2) 보내는 값이 0이면 처리 하지 않기
                #   > sender.getSend(col)!=0
                for to_cand in [col for col in range(self.n) if col != from_cand and not (col!=sender.idx and sender.getSend(col)==0)]:
                    # [to_cand 추가 기준]
                    # 1) from_cand != to_cand > col != from_cand
                    # 2) 본인에게 보내는 경우를 제외하고 값이 0인 항으로 보낼 수 없다.
                    while(True):
                        # [while 루프]
                        # 한번의 작업이 끝나고 나서 반복적으로 to_cand가 선정 될 수 있도록 loop

                        # 처리할 필요가 없거나: 보내야 하는 값이 0
                        if sender.getSend(from_cand)==0:
                            break

                        canceler_idx = self.__get_canceler_idx(sender,from_cand,to_cand)
                        # 더 이상 처리할 수 없을 때: canceler의 값이 -1
                        if canceler_idx == -1:
                            break
                        canceler = self.participants[canceler_idx]

                        #더 작은 값으로 처리한다.
                        value = min(sender.getSend(from_cand),canceler.getSend(to_cand))
                        t1 = TransferItem(sender,from_cand,to_cand)
                        t2 = TransferItem(canceler,to_cand,from_cand)
                        self.__canceling(value,t1,t2)

    # canceling을 진행할 수 있으면 canceler idx를 return 하고,
    # 아니면 -1을 return 한다.
    def __get_canceler_idx(self,sender,from_cand,to_cand):
        # 1순위 처리: 상호 상쇄 되는 항목이 있다면 우선 처리한다.
        # to_cand가 sender.idx가 되고,
        # self.participants[from_cand].getSend(to_cand)가 0이 아니라면 연산이 가능하다
        if sender.idx == to_cand and self.participants[from_cand].getSend(to_cand)!=0:
            return from_cand

        # [canceler 선정]
        # canceler는 sender가 될 수 없다.
        for cand_canceler_idx in [row for row in range(self.n) if row!=sender.idx]:
            cand_canceler = self.participants[cand_canceler_idx]
            #
            if cand_canceler.getSend(to_cand) * cand_canceler.getSend(from_cand)!=0:
                return cand_canceler_idx
        return -1

    # 설정된 항목에 맞게 데이터를 변경한다.
    def __canceling(self,value,transferitem1,transferitem2):
        transferitem1.transfer(value)
        transferitem2.transfer(value)