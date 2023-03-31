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
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username
    
    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender']

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
    title = models.CharField(max_length=100)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_participants = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.CharField(max_length=100)
    sample_image = models.ImageField(upload_to='media/')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return self.title
    
    def registered_count(self):
        return ProfileTask.objects.filter(task=self).count()
    
class ProfileTask(models.Model):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected')
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.profile.user.username + ' - ' + self.task.title



