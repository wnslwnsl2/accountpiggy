import datetime
from expense_matrix_cleaner import expense_matrix_cleaner
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import random

"""
방
=

사용자가 여행에 대해 정보를 올리고 내리는 기본적인 공간

name:
    방이름
start_date:
    여행 시작 일
end_date:
    여행 종료 일
"""
class Room(models.Model):
    name = models.CharField(verbose_name='여행이름',max_length=30)
    start_date = models.DateField(verbose_name='여행시작날짜')
    end_date = models.DateField(verbose_name='여행종료 날짜',null=True,blank=True)

    def __str__(self):
        return self.name

    def get_description(self):
        return '{}'.format(self.name)

    def accept_user(self,user,is_admin=False):
        #TODO 더미 일 경우에 대해 따로 진행해줘야함
        if user in self:
            if user.email != 'dummydummy@dummydummy.dummy':
                raise EOFError("accept_user")

        member = Member.objects.create(
            user=user,
            nickname=user.name,
            room=self,
            is_admin=is_admin
        )
        member.save()
        return member


    def __contains__(self, user):
        return Member.objects.filter(room=self,user=user).exists()

    def get_member_instance_of_user(self,user):
        return Member.objects.get(user=user,room=self)

    def str_start_date(self):
        return '{}년{}월{}일'.format(
            self.start_date.year,
            self.start_date.month,
            self.start_date.day)

    def str_end_date(self):
        return '{}년{}월{}일'.format(
            self.end_date.year,
            self.end_date.month,
            self.end_date.day)
"""
Member
======

user > member > room
user는 member로서 room에 참가한다.
nickname, index, is_admin과 같은 방에 따라 다른 정보를 보관함
"""
class Member(models.Model):
    user = models.ForeignKey("accounts.User",default=None,on_delete=models.SET_NULL,blank=True,null=True,related_name="member_set")
    room = models.ForeignKey(Room,on_delete=models.CASCADE,related_name="members")
    is_admin = models.BooleanField(default=False)
    nickname = models.CharField(default = 'nickname',max_length=30)

    def __str__(self):
        return '{}({})'.format(self.nickname,self.user.name)
    def change_nickname(self,nickname):
        self.nickname = nickname
        self.save()

"""
UserMatrixMapper
================
정산에 필한 정보들을 갖고 관리한다.
"""
class UserMatrixMapper:
    def __init__(self,users,all_expense_entries):
        self.user_list_arranged_by_expendmoney = self.get_user_list_arranged_by_expendmoney(users,all_expense_entries)
        self.all_expense_entries = all_expense_entries

    # 알고리즘을 위하여 user를 쓴 돈 순으로 정렬한다.
    def get_user_list_arranged_by_expendmoney(self, users,all_expense_entries):
        # 돈을 받을 자: 돈 쓴자
        # temp_tuple_dict = expense.receiver를 key로 하고, value를 총 쓴돈으로하는 dict
        temp_tuple_dict = {
            user:0 for user in users
        }

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



"""
Matrix
======
방마다 정산 메트릴스를 onetoone으로 갖는다.
"""
class ExpenseMatrix(models.Model):
    room = models.OneToOneField(Room,related_name="matrix",on_delete=models.CASCADE)
    needed_to_clean_up = models.BooleanField(default=True)

    def cleanup(self,room):
        if self.needed_to_clean_up:
            # 1) 모든 matrix를 초기화 한다.
            ExpenseMatrixEntry.objects.filter(matrix=self).delete()

            # 2) 초기 entry 데이터를 만든다.
            # expenses > entry 데이터
            expenses = Expense.objects.filter(room=room).all()
            for expense in expenses:
                self.__set_expense(expense)

            # 3) entry - matrix mapper를 만든다.
            users = Member.objects.filter(room=room).all()
            all_expense_entries = ExpenseMatrixEntry.objects.filter(matrix=self,is_cleaned_data=False).all()
            mapper = UserMatrixMapper(users,all_expense_entries)
            mat = mapper.get_initial_matrix()
            mapper.printMat(mat)

            # 4) 알고리즘을 돌린다.
            mat_cleaner = expense_matrix_cleaner.ExpenseMatrixCleaner(mat)
            cleaned_mat = mat_cleaner.get_cleaned_matrix()

            # 5) 정산된 행렬로 다시 Entry를 만들어 준다.
            mapper.save_cleaned_entries(self,cleaned_mat)
            mapper.printMat(cleaned_mat)
            self.needed_to_clean_up = False
            self.save()

    """
        expense로 Entry를 만든다.
    """
    def __set_expense(self,expense):
        nbbangNumber = len(expense.users.all())
        for sender in expense.users.all():
            entry,dummy = ExpenseMatrixEntry.objects.get_or_create(matrix=self,sender=sender,receiver=expense.expend_user,is_cleaned_data=False)
            entry.value += expense.cost//nbbangNumber
            entry.save()

    def get_send_item_list(self,user):
        return ExpenseMatrixEntry.objects.filter(
            matrix=self,
            sender=user,
            is_cleaned_data=True,).exclude(receiver=user).all()

    def get_recv_item_list(self,user):
        return ExpenseMatrixEntry.objects.filter(
            matrix=self,
            receiver=user,
            is_cleaned_data=True,).exclude(sender=user).all()

    def get_self_expense(self,user):
        try:
            entry = ExpenseMatrixEntry.objects.get(
                matrix=self,
                sender=user,
                receiver=user,
                is_cleaned_data=True,
            )
            return entry.value
        except:
            return 0
        
    def get_total_members_expense(self):
        all_entries = ExpenseMatrixEntry.objects.filter(matrix=self,is_cleaned_data=True).all()
        if len(all_entries) == 0:
            return 0

        ret = 0
        for entry in all_entries:
            ret += entry.value
        return ret

class ExpenseMatrixEntry(models.Model):
    """
    Matrix의 한 요소를 표현하는 모델
    sender = row 에 해당
    receiver = col 에 해당
    is_cleaned_date = 정산 후의 데이터인지 전의 데이터인지
    """
    matrix = models.ForeignKey(ExpenseMatrix,verbose_name='정산 행렬',on_delete=models.CASCADE)
    sender = models.ForeignKey(Member, verbose_name='보내야 하는 사람', on_delete=models.CASCADE, related_name='senders')
    receiver = models.ForeignKey(Member, verbose_name='받을 사람', on_delete=models.CASCADE, related_name='receivers')
    value = models.IntegerField(verbose_name='금액',default=0,validators=[MinValueValidator(0)])
    # 0: none
    # 1: sender_act
    # 2: check_again
    # 3: end
    state = models.IntegerField(verbose_name='정산 상태',default=0)
    is_cleaned_data = models.BooleanField(default=False)

    def __str__(self):
        return '{}가 {}한테 {}원'.format(self.sender,self.receiver,self.value)

class ExpenseManager(models.Manager):
    # 변경사항을 저장하거나 새로 만든다
    def create_or_save(self,expense_id,form,room,indexed_user):
        naivedate = form.cleaned_data['date']
        naivedatetime = datetime.datetime(
            naivedate.year,
            naivedate.month,
            naivedate.day,
            int(form.cleaned_data['hour']),
            int(form.cleaned_data['minute']),
            00
        )

        if Expense.objects.filter(id=expense_id).exists():
            expense = Expense.objects.get(id=expense_id)
            expense.expend_user = indexed_user
            expense.users.set(form.cleaned_data['users'].all())
            expense.cost = form.cleaned_data['cost']
            expense.purpose = form.cleaned_data['purpose']
            expense.purpose_category = form.cleaned_data['purpose_category']
            expense.datetime = timezone.make_aware(naivedatetime)
        else:
            expense = Expense.objects.create(
                expend_user = indexed_user,
                cost = form.cleaned_data['cost'],
                purpose = form.cleaned_data['purpose'],
                purpose_category = form.cleaned_data['purpose_category'],
                datetime = timezone.make_aware(naivedatetime),
                room=room,
            )
            expense.users.set(form.cleaned_data['users'].all())
        expense.save()
        room.matrix.needed_to_clean_up = True
        room.matrix.save()
        return expense


    # room과 관련된 expense queryset을 return 한다.
    def expenses_in_room(self,room):
        return super().get_queryset().filter(room=room)


class ExpensesInDay:
    def __init__(self,date):
        self.date = date
        self.expense_list = []

    def add_expense(self,expense):
        self.expense_list.append(expense)


class Expense(models.Model):
    """
    지출 내역 모델
    """
    purpose_categories=[
        ('fo', '식사'),
        ('sl', '숙소'),
        ('dr', '(기호식품) ex)술/커피'),
        ('tr', '교통'),
        ('et', '기타'),
    ]
    users = models.ManyToManyField(Member, related_name="participated_expense_set")
    expend_user = models.ForeignKey(Member, verbose_name='돈쓴자', related_name="expend_expense_set", on_delete=models.CASCADE)
    room = models.ForeignKey(Room,related_name="expense_set",on_delete=models.CASCADE)
    cost = models.IntegerField(verbose_name='금액',default=0,validators=[MinValueValidator(0)])
    purpose = models.CharField(verbose_name='용도',max_length=30,null=True,blank=True)
    purpose_category = models.CharField(verbose_name='카테고리',max_length=2,choices=purpose_categories)

    datetime = models.DateTimeField(verbose_name='쓴시간')

    objects = ExpenseManager()

    def __str__(self):
        return self.purpose

    def number_of_participants(self):
        return len(self.users.all())

    def divided_cost(self):
        return self.cost//self.number_of_participants()

class EnteringQAManager(models.Manager):
    nouns = [
        '요이','기린','사자','호랑이','거북이','치타','고구마','감자',
    ]
    adjectives =[
        '잠자는','달리는','즐거운','행동하는','성난','배부른','예민한',
    ]

    def get_noun_noun_code(self):
        first = random.randrange(0,len(self.nouns))
        second = random.randrange(0,len(self.nouns))
        if second==first:
            if second==0:
                second = second+1
            else:
                second = second-1
        return (self.nouns[first],self.nouns[second])

    def get_adjective_noun_code(self):
        noun = random.randrange(0,len(self.nouns))
        adjective = random.randrange(0,len(self.adjectives))
        return (self.adjectives[adjective],self.nouns[noun])

    def create(self,*args,**kwargs):
        q,a = self.get_adjective_noun_code()
        kwargs['Q']=q
        kwargs['A']=a
        return super(EnteringQAManager,self).create(*args,**kwargs)



class EnteringQA(models.Model):
    Q = models.CharField(verbose_name="질문",max_length=10,default='요이')
    A = models.CharField(verbose_name="답변",max_length=10,default='탱구리')
    room = models.OneToOneField(Room,on_delete=models.CASCADE,related_name='QA')

    objects = EnteringQAManager()

    def match_code(self,answer):
        return answer == self.A