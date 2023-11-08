from django import forms
from django.contrib.auth import authenticate

from accounts.models import User, Setting


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


# class RegistrationForm(forms.ModelForm):
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ('username', 'first_name', 'middle_name', 'last_name', 'email', 'contact_no', 'role', 'password')

#     def cleaned_password(self):
#         password = self.cleaned_data.get('password')
#         password2 = self.cleaned_data.get('password2')
#         if password != password2:
#             return None
#         return password


class SignupForm(forms.ModelForm):
    password = forms.CharField(min_length=8, label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=8, label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'middle_name', 'last_name', 'email', 'password')

    def cleaned_password(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            return None
        return password


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Setting
        fields = ('value',)
