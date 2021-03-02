from .models import Room,Expense,Member,ExpenseMatrix,EnteringQA
from accounts.models import User
from django import forms
import datetime
from django.utils import timezone


class NameForm(forms.Form):
    name = forms.CharField(max_length=100)

class CleanedPageUserSelectForm(forms.Form):
    selectedUser = forms.ModelChoiceField(
        label='정산할 유저',
        widget=forms.RadioSelect,
        queryset=Member.objects.all(),
    )

class RoomSaveForm(forms.ModelForm):
    def save_or_create(self,room_id):
        if Room.objects.filter(id=room_id).exists():
            room = Room.objects.get(id=room_id)
            room.name = self.cleaned_data['name']
            room.start_date = self.cleaned_data['start_date']
            room.end_date = self.cleaned_data['end_date']
            created = False
        else:
            room = self.save()
            ExpenseMatrix.objects.create(room=room)
            EnteringQA.objects.create(room=room)
            created = True
        return room,created

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
                'class':'form-control',
                'min':0
            }
        )
    )
    purpose_category = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=Expense.purpose_categories
    )
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'value': timezone.localtime(timezone.now()).date(),
                'class':'form-control',
                'type':'date'
            }
        ),
    )
    hour = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class':'form-control',
                'type':'number',
                'min':0,
                'max':23
            }
        )
    )
    minute = forms.ChoiceField(
        choices=(('00', '00'), ('30', '30')),
        widget=forms.Select(
            attrs={
                'class':'form-control',
                'type':'number',
            }
        )
    )

    class Meta:
        model = Expense
        fields = ('expend_user','users','cost','purpose','purpose_category')

    def __init__(self,*args,**kwargs):
        super(ExpenseCreateForm,self).__init__(*args,**kwargs)
        now = timezone.localtime(timezone.now())
        minute = now.minute//30*30
        hour = now.hour
        self.initial['hour'] = hour
        self.initial['minute'] = minute