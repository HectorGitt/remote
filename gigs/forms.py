from django import forms

from .models import User, Category, Task
from django.contrib.auth.forms import UserCreationForm

class UserForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Required. 30 characters or fewer. Letters only.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required. 30 characters or fewer. Letters only.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name','email', 'password1', 'password2', 'gender']