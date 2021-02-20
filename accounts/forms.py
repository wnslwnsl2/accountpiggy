import re
from django import forms
from .models import User,Account
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class LoginForm(forms.Form):
    email = forms.EmailField(
        label='이메일',
        widget=forms.EmailInput(
            attrs={
                'class':'form-control',
                'placeholder':'이메일을 입력해 주세요.',
            }
        )
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': '비밀번호를 입력해 주세요.',
            }
        )
    )

class CreateAccountForm(forms.ModelForm):
    password1 = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': '비밀번호를 입력해 주세요.',
            }
        )
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': '비밀번호를 입력해 주세요.',
            }
        )
    )
    bank = forms.CharField(
        label="은행",
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'은행',
            }
        )
    )
    account_number = forms.CharField(
        label="계좌번호",
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'계좌번호',
            }
        )
    )

    class Meta:
        model = User
        fields = ('email','name')
        widgets = {
            'email':forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '사용하실 이메일을 입력해 주세요.',
                }
            ),
            'name':forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '이름을 입력해 주세요.',
                }
            )
        }

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        if len(password1) < 6:
            raise forms.ValidationError("비밀번호는 6자리 이상입니다.")

        password2 = self.cleaned_data['password2']

        if password1!= password2:
            raise forms.ValidationError("비밀번호가 일치 하지 않습니다.")

        return password2

    # def clean_account_number(self):
    #     account_number = self.cleaned_data['account_number']
    #     if not re.search(r'^(\d{1,})(-(\d{1,})){1,}$',account_number):
    #         raise forms.ValidationError("계좌번호를 다시 입력해 주세요")
    #     return account_number


    def save(self,commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'name','is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
