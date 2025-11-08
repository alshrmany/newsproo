from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(
        label='اسم المستخدم',widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'أدخل اسم المستخدم'}))
    password = forms.CharField(label='كلمة المرور',widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'أدخل كلمة المرور'}))

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True,label='البريد الإلكتروني',widget=forms.EmailInput(attrs={'class': 'form-control','placeholder': 'example@email.com'}))
    first_name = forms.CharField(max_length=30,required=True,label='الاسم الأول',widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'الاسم الأول'}))
    last_name = forms.CharField(max_length=30,required=True,label='اسم العائلة',widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'اسم العائلة'}))

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تخصيص حقول الـ UserCreationForm
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'اسم المستخدم'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'كلمة المرور'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'تأكيد كلمة المرور'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user