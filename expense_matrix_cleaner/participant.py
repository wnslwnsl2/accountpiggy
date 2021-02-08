# 서로 상쇄되서 캔슬링할 Item
class TransferItem:
    def __init__(self,sender,fromidx,toidx):
        # 보내야 하는 돈이 옮겨지는 사람
        self.sender = sender
        # from에서 to로 보내야 하는 돈이 옮겨짐
        self.fromidx = fromidx
        self.toidx = toidx

        # 실제로 보내야 하는 돈을 옮기는 method
    def transfer(self,value):
        self.sender.setSend(self.fromidx, self.sender.getSend(self.fromidx) - value)
        self.sender.setSend(self.toidx, self.sender.getSend(self.toidx) + value)

# 정산 참가자들에 대해 보내고 받아야하는 목록을 저장하는 객체
class Participant:
    def __init__(self,idx,refMatrixRow,refMatrixCol):
        # 본인의 index
        self.idx = idx
        ### refMatrixRow, refMatrixCol
        # 1) ref : Matrix에 수정사항을 반영하기 위하여 본인이 해당되는 데이터를 참조해서 받아옴
        # 2) Row : 보내야할 목록들
        # 3) Col : 받아야할 목록득
        self.refMatrixRow = refMatrixRow
        self.refMatrixCol = refMatrixCol

        #보내야 하는 금액
    def getSend(self,idx):
        return self.refMatrixRow[idx]

        #보내야 하는 금액 설정
    def setSend(self,idx,value):
        if value<=0.000001:
            value = 0
        self.refMatrixRow[idx] = value

        #받아야 하는 금액
    def getRecv(self,idx):
        return self.refMatrixCol[idx]

    def __str__(self):
        return "Sender:{}".format(self.idx)