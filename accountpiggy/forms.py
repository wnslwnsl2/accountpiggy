from .models import Room,Expense,Member
from accounts.models import User
from django import forms
import datetime

class NameForm(forms.Form):
    name = forms.CharField(max_length=100)

class CleanedPageUserSelectForm(forms.Form):
    selectedUser = forms.ModelChoiceField(
        label='정산할 유저',
        widget=forms.RadioSelect,
        queryset=Member.objects.all(),
    )

class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ('name','start_date','end_date')
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control','placeholder':'방 이름을 입력해 주세요.'}),
            'start_date':forms.DateInput(attrs={'value':datetime.date.today(),'class':'form-control', 'type':'date'}),
            'end_date':forms.DateInput(attrs={'value':datetime.date.today(),'class':'form-control', 'type':'date'}),
        }

class ExpenseCreateForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        label="멤버들",
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class':'form-check-input',
                'type':'checkbox'
            }
        ),
        queryset=Member.objects.all(),
    )
    expend_user = forms.ModelChoiceField(
        queryset=Member.objects.all(),
    )
    purpose = forms.CharField(
        label="목적",
        widget = forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder':'사용 목적을 입력해 주세요.'
                }
            )
    )
    cost = forms.CharField(
        label="비용",
        widget=forms.NumberInput(
            attrs={
                'value':0,
                'class':'form-control',
                'min':0
            }
        )
    )
    purpose_category = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=Expense.purpose_categories
    )
    datetime = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'value': datetime.date.today(),
                'class':'form-control',
                'type':'date'
            }
        ),
    )

    class Meta:
        model = Expense
        fields = ('expend_user','users','cost','purpose','purpose_category','datetime',)