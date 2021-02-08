from expense_matrix_cleaner import expense_matrix_cleaner
from accounts.models import User
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
import datetime

class Room(models.Model):
    name = models.CharField(verbose_name='여행이름',max_length=30)
    #togotags
    start_date = models.DateField(verbose_name='여행시작날짜')
    end_date = models.DateField(verbose_name='여행종료 날짜',null=True,blank=True)

    def __str__(self):
        return self.name

    def get_description(self):
        return '{}'.format(self.name)

    def get_next_index(self):
        indexed_Users = self.users.all()
        # 빈거 확인하는 알고리즘
        # 1) 전체 어레이 만들고 sort
        if len(indexed_Users)==0:
            return 0
        if len(indexed_Users)==1:
            return 1

        index_array = sorted([indexed_user.index for indexed_user in indexed_Users])
        stack = []

        for i in range(len(index_array)-1):
            stack.append(index_array[i])
            if stack[-1]!=index_array[i+1]-1:
                return stack[-1]+1
        return len(indexed_Users)

class IndexedUser(models.Model):
    user = models.ForeignKey(User,default=None,on_delete=models.SET_NULL,blank=True,null=True,related_name="indexed_set")
    room = models.ForeignKey(Room,on_delete=models.CASCADE,related_name="users")
    index = models.IntegerField(default=0,validators=[MinValueValidator(0)])
    is_admin = models.BooleanField(default=False)
    nickname = models.CharField(default = 'nickname',max_length=30)

    def is_dummy(self):
        return self.user.email == User.objects.dummyemail

    def __str__(self):
        return '{}({})'.format(self.nickname,self.user.name)

class UserMatrixMapper:
    def __init__(self,users,all_expense_entries):
        self.user_list_arranged_by_expendmoney = self.get_user_list_arranged_by_expendmoney(users,all_expense_entries)
        self.all_expense_entries = all_expense_entries

    # 알고리즘을 위하여 user를 쓴 돈 순으로 정렬한다.
    def get_user_list_arranged_by_expendmoney(self, users,all_expense_entries):
        # 돈을 받을 자: 돈 쓴자
        # temp_tuple_dict = expense.receiver를 key로 하고, value를 총 쓴돈으로하는 dict
        temp_tuple_dict = {user:0 for user in users}

        # 돈을 가장 적게 사용한 순(본인이 본인한테 보내는 것 제외)을 user를 정렬하기
        # 1) 총 쓴 돈을 dict에 모두 저장한다.
        for entry in all_expense_entries:
            if entry.sender != entry.receiver: #본인이 본인한테 보내는 것 제외
                temp_tuple_dict[entry.receiver]+=entry.value

        # 돈을 가장 적게 사용한 순으로 user를 정렬한다.
        users = [user for (user,value) in sorted(temp_tuple_dict.items(),key=lambda x:x[1])]
        return users

    def map_to_matindex(self,user):
        return self.user_list_arranged_by_expendmoney.index(user)

    def map_to_user(self,mat_index):
        return self.user_list_arranged_by_expendmoney[mat_index]

    def get_initial_matrix(self):
        n = len(self.user_list_arranged_by_expendmoney)
        mat = [[0 for col in range(n)] for row in range(n)]

        for entry in self.all_expense_entries:
            sender_idx = self.map_to_matindex(entry.sender)
            receiver_idx = self.map_to_matindex(entry.receiver)
            mat[sender_idx][receiver_idx]+=entry.value
        return mat

    def save_cleaned_entries(self,matrix,cleaned_mat):
        n = len(cleaned_mat)

        for row in range(n):
            for col in range(n):
                if cleaned_mat[row][col]!=0:
                    sender = self.map_to_user(row)
                    receiver = self.map_to_user(col)
                    ExpenseMatrixEntry.objects.get_or_create(matrix=matrix,sender=sender,receiver=receiver,value=cleaned_mat[row][col],is_cleaned_data=True)

    def printMat(self,mat):
        n = len(mat)
        b = '-' * n
        print(b)
        for row in range(n):
            s = ''
            for col in range(n):
                s+='{}\t'.format(mat[row][col])
            print(s)
        print(b)

class ExpenseMatrix(models.Model):
    room = models.OneToOneField(Room,on_delete=models.CASCADE)

    # expenses : 정산 데이터
    # user 목록
    def cleanup(self,room):
        # 1) 모든 메트릭스를 지운다.
        ExpenseMatrixEntry.objects.filter(matrix=self).delete()

        # 2) 초기 entry 데이터를 만든다.
        expenses = Expense.objects.filter(room=room).all()
        for expense in expenses:
            self.set_expense(expense)

        # 3) 행렬을 만든다.
        users=IndexedUser.objects.filter(room=room).all()
        all_expense_entries = ExpenseMatrixEntry.objects.filter(matrix=self,is_cleaned_data=False).all()
        mapper = UserMatrixMapper(users,all_expense_entries)
        mat = mapper.get_initial_matrix()
        mapper.printMat(mat)

        mat_cleaner = expense_matrix_cleaner.ExpenseMatrixCleaner(mat)
        cleaned_mat = mat_cleaner.get_cleaned_matrix()
        mapper.save_cleaned_entries(self,cleaned_mat)
        mapper.printMat(cleaned_mat)

    def set_expense(self,expense):
        nbbangNumber = len(expense.users.all())
        for sender in expense.users.all():
            entry,dummy = ExpenseMatrixEntry.objects.get_or_create(matrix=self,sender=sender,receiver=expense.expend_user,is_cleaned_data=False)
            entry.value += expense.cost//nbbangNumber
            entry.save()

class ExpenseMatrixEntry(models.Model):
    matrix = models.ForeignKey(ExpenseMatrix,verbose_name='정산 행렬',on_delete=models.CASCADE)
    sender = models.ForeignKey(IndexedUser,verbose_name='보내야 하는 사람',on_delete=models.CASCADE,related_name='senders')
    receiver = models.ForeignKey(IndexedUser,verbose_name='받을 사람',on_delete=models.CASCADE,related_name='receivers')
    value = models.IntegerField(verbose_name='금액',default=0,validators=[MinValueValidator(0)])
    is_cleaned_data = models.BooleanField(default=False)

    def __str__(self):
        return '{}가 {}한테 {}원'.format(self.sender,self.receiver,self.value)

class ExpenseManager(models.Manager):
    # form
    # room
    def CreateExpense(self,form,room,indexed_user):
        expense = form.save(commit=False)
        expense.expend_user = indexed_user
        expense.room = room
        expense.save()
        form.save_m2m()

    # room과 관련된 expense queryset을 return 한다.
    def expenses_in_room(self,room):
        return super().get_queryset().filter(room=room)

class Expense(models.Model):
    purpose_categories=(
        ('no', 'not selected'),
        ('et', 'etc'),
        ('sl', 'sleeping'),
        ('tr', 'transportaion'),
        ('fo', 'food'),
        ('dr', 'drink'),
    )
    users = models.ManyToManyField(IndexedUser,related_name="participated_expense_set")
    # TODO user가 사라졌어 > 그럼 Expense가 없어져야 하는게 아니라, expend_user가 dummy가 되던가 해야된다.
    # TODO 해당 user가 없어진다고 해도 Expense 자체는 없어지면 안된다.
    expend_user = models.ForeignKey(IndexedUser,verbose_name='돈쓴자',related_name="expend_expense_set",on_delete=models.CASCADE)
    room = models.ForeignKey(Room,related_name="expense_set",on_delete=models.CASCADE)
    cost = models.IntegerField(verbose_name='금액',default=0,validators=[MinValueValidator(0)])
    purpose = models.CharField(verbose_name='용도',max_length=30,null=True,blank=True)
    purpose_category = models.CharField(verbose_name='카테고리',max_length=2,choices=purpose_categories)
    datetime = models.DateTimeField(verbose_name='쓴시간',default=datetime.datetime.now)

    objects = ExpenseManager()

    def __str__(self):
        return self.purpose