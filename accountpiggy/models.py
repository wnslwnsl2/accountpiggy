from accounts.models import User
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
import datetime

class Room(models.Model):
    name = models.CharField(verbose_name='여행이름',max_length=30)
    max_number_of_members = models.IntegerField(verbose_name='여행 인원수',default=1,validators=[MaxValueValidator(200),MinValueValidator(1)])

    #togotags
    start_date = models.DateField(verbose_name='여행시작날짜')
    end_date = models.DateField(verbose_name='여행종료 날짜',null=True,blank=True)
    users = models.ManyToManyField(User,related_name="participating_room_list")

    def isAdminUser(self,checkingUser):
        return self.users.all().index(checkingUser) == 0

    def isMember(self,checkingUser):
        return checkingUser in self.users.all()

    def __str__(self):
        return self.name

    def get_description(self):
        users = self.users.all()
        return '{}({}) ({}/{})'.format(self.name,users[0].name,len(users),self.max_number_of_members)

class ExpenseManager(models.Manager):
    def CreateExpense(self,form,room,spend_user):
        expense = form.save(commit=False)
        expense.expend_user = spend_user
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
    users = models.ManyToManyField(User,related_name="participated_expense_set")
    # TODO user가 사라졌어 > 그럼 Expense가 없어져야 하는게 아니라, expend_user가 dummy가 되던가 해야된다.
    # TODO 해당 user가 없어진다고 해도 Expense 자체는 없어지면 안된다.
    expend_user = models.ForeignKey(User,related_name="expend_expense_set",on_delete=models.CASCADE)
    room = models.ForeignKey(Room,related_name="expense_set",on_delete=models.CASCADE)
    cost = models.IntegerField(default=0,validators=[MinValueValidator(0)])
    purpose = models.CharField(max_length=30,null=True,blank=True)
    purpose_category = models.CharField(max_length=2,choices=purpose_categories)
    datetime = models.DateTimeField(default=datetime.datetime.now)

    manager = ExpenseManager()

    def __str__(self):
        return self.purpose