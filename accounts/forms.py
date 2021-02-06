from django import forms
from .models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class CreateAccountForm(forms.ModelForm):
    password1 = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('email','name')

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        if len(password1) < 6:
            raise forms.ValidationError("비밀번호는 6자리 이상입니다.")

        password2 = self.cleaned_data['password2']

        if password1!= password2:
            raise forms.ValidationError("비밀번호가 일치 하지 않습니다.")

        return password2

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
