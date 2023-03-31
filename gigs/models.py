from django.db import models

# Create your models here.

#django user model
from django.contrib.auth.models import User

# Create your models here.
class Profile(User):
    Male = 'M'
    Female = 'F'
    GENDER = [ (Male,'Male'), (Female, 'Female')]
    gender = models.CharField(choices=GENDER, max_length=1)

    def __str__(self):
        return self.user.username
    
    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender']

class Category(models.Model):
    name = models.CharField(max_length=100)
    percentage_fee = models.IntegerField()

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_participants = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.CharField(max_length=100)
    sample_image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title



