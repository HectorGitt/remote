from django import forms

from .models import User, Category, Task, SubCategory, UserTask
from django.contrib.auth.forms import UserCreationForm

class UserForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Required. 30 characters or fewer. Letters only.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required. 30 characters or fewer. Letters only.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name','email', 'password1', 'password2', 'gender']
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'unit_price', 'total_participants','cost', 'category', 'tags', 'sample_image']
        widgets = {
        'unit_price':forms.NumberInput(attrs={'max':99999, 'min':1}),
        'total_participants':forms.NumberInput(attrs={'max':999999999, 'min':1}),
        'cost':forms.NumberInput(attrs={'max':9999999999, 'min':500.00, 'readonly':True}),
        }

class UserTaskForm(forms.ModelForm):
    class Meta:
        model = UserTask
        fields = ['image1','image2','image3']

    