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
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select Category", )
    class Meta:
        model = Task
        fields = ['title', 'description', 'unit_price', 'total_participants','cost', 'sub_category', 'tags', 'sample_image','required_proof']
        widgets = {
        'unit_price':forms.NumberInput(attrs={'max':99999, 'min':1}),
        'total_participants':forms.NumberInput(attrs={'max':999999999, 'min':1}),
        'cost':forms.NumberInput(attrs={'max':9999999999, 'min':500.00, 'readonly':True}),
        }

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sub_category"].queryset = SubCategory.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(category__id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['sub_category'].queryset = self.instance.category.subcategory_set.order_by('name')

class UserTaskForm(forms.ModelForm):
    class Meta:
        model = UserTask
        fields = ['comments','image1','image2','image3']
        
class TransactionForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=1000.00, max_value=9999999999)

class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)

class AddParticipantsForm(forms.Form):
    no_of_participants = forms.IntegerField(required=True, min_value=1, max_value=9999999999)