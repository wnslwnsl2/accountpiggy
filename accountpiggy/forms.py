from .models import Room,Expense,IndexedUser
from accounts.models import User
from django import forms
import datetime

class CleanedPageUserSelectForm(forms.Form):
    selectedUser = forms.ModelChoiceField(
        label='정산할 유저',
        widget=forms.RadioSelect,
        queryset=IndexedUser.objects.all(),
    )

class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('name','start_date','end_date')
        widgets={
            'start_date':forms.DateInput(attrs={'default':datetime.date.today(),'class':'form-control', 'type':'date'}),
            'end_date':forms.DateInput(attrs={'default':datetime.date.today(),'class':'form-control', 'type':'date'}),
        }

class ExpenseCreateForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        label="멤버들",
        widget=forms.CheckboxSelectMultiple,
        queryset=IndexedUser.objects.all()
    )

    class Meta:
        model = Expense
        fields = ('expend_user','users','cost','purpose','purpose_category','datetime',)

class NameForm(forms.Form):
    name = forms.CharField(label='너의 이름은',max_length=100)