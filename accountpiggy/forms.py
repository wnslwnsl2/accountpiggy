from .models import Room,Expense
from accounts.models import User
from django import forms
import datetime

class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('name','max_number_of_members','start_date','end_date')
        widgets={
            'start_date':forms.DateInput(attrs={'default':datetime.date.today(),'class':'form-control', 'type':'date'}),
            'end_date':forms.DateInput(attrs={'default':datetime.date.today(),'class':'form-control', 'type':'date'}),
        }

class ExpenseCreateForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        label="멤버들",
        widget=forms.CheckboxSelectMultiple,
        queryset=User.objects.all()
    )
    # purpose_category = forms.MultipleChoiceField(
    #     choices=Expense.purpose_categories,
    #     widget=forms.RadioSelect)

    class Meta:
        model = Expense
        fields = ('users','cost','purpose','purpose_category','datetime',)
    #
    # def __init__(self,*args,**kwargs):
    #     super(ExpenseCreateForm, self).__init__(*args, **kwargs)
    #     room = kwargs.pop('room')
    #     self.fields['users'].queryset = room.users.all()
    #
    #     # spend_user = kwargs.pop('spend_user')
    #     # choices = room.users
    #     # self.fields['users'].queryset = choices