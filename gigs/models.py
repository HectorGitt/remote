from django.db import models

# Create your models here.

#django user model
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    Male = 'M'
    Female = 'F'
    GENDER = [ (Male,'Male'), (Female, 'Female')]
    gender = models.CharField(choices=GENDER, max_length=1)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.username
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    percentage_fee = models.IntegerField()

    def __str__(self):
        return self.name

class Task(models.Model):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected')
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    unit_price = models.PositiveIntegerField(default=1)
    total_participants = models.PositiveIntegerField(default=1)
    cost = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.CharField(max_length=100)
    sample_image = models.ImageField(upload_to='media/', blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return self.title 
    
class UserTask(models.Model):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.user.username + ' - ' + self.task.title



