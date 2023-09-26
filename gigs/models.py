from django.db import models

# Create your models here.

#django user model
from django.contrib.auth.models import AbstractUser
from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from datetime import datetime
import uuid


# Create your models here.
class User(AbstractUser):
    Male = 'M'
    Female = 'F'
    Client = 'CLIENT'
    Worker = 'WORKER'
    GENDER = [ (Male,'Male'), (Female, 'Female')]
    ROLE = [ (Client, 'Client'), (Worker, 'Worker')]
    gender = models.CharField(choices=GENDER, max_length=1)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    role = models.CharField(choices=ROLE, max_length=10, default=Client)

    def __str__(self):
        return self.username
    
    def is_client(self):
        return self.role == self.Client
    
class BankAccount(models.Model):
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_account')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + " - " + self.bank_name
    
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    percentage_fee = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)

    def __str__(self):
        return self.name + " - " + self.category.name

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super(ActiveManager, self).get_queryset().filter(status=self.model.APPROVED, state=self.model.IN_PROGRESS)

class Task(models.Model):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected')
    ]

    IN_PROGRESS = 'IN_PROGRESS'
    ENDED = 'ENDED'
    PAUSED = 'PAUSED'

    STATE_CHOICES = [
        (IN_PROGRESS, 'In Progress'),
        (ENDED, 'Ended'),
        (PAUSED, 'Paused')
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='title', unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    required_proof = models.TextField(null=True, blank=False)
    unit_price = models.PositiveIntegerField(default=1)
    total_participants = models.PositiveIntegerField(default=1)
    cost = models.PositiveIntegerField(default=0)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    tags = models.CharField(max_length=100)
    sample_image = models.ImageField(upload_to='media/', blank=True, null=True)
    #admin acceptance status
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)
    #user status
    state = models.CharField(max_length=100, choices=STATE_CHOICES, default=IN_PROGRESS)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    rejection_reason = models.TextField(null=True, blank=True)
    active = ActiveManager()
    objects = models.Manager()

    def __str__(self):
        return self.title
    
    def registered_count(self):
        return UserTask.objects.filter(task=self, status__in=('APPROVED', 'PENDING') ).count()
    
    def is_registered(self, user):
        return UserTask.objects.filter(task=self, user=user).exists()
    
    def is_approved(self):
        return self.status == self.APPROVED
    
    def is_rejected(self):
        return self.status == self.REJECTED
    
    def get_url(self):
        return '/task/' + self.slug + '/'
    
    class Meta:
        ordering = ['-id']
    __original_status = None

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self.__original_status = self.status

    def clean(self, *args, **kwargs):
        
        if not self.rejection_reason and self.status == self.REJECTED:
            raise ValidationError(("Task cannot be rejected without a reason"), code='invalid')
        
        

    def save(self, *args, **kwargs):
        if self.status != self.__original_status:
            if self.status == self.APPROVED:
                #send email to owner
                pass
            elif self.status == self.REJECTED:
                #send email to owner
                #Refund users
                refund_user(self.owner, self.slug)
                


                pass
            else:
                pass
        super(Task, self).save(*args, **kwargs)
        self.__original_status = self.status


    
    

    
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
    comments = models.TextField(null=True)
    image1 = models.ImageField(upload_to='media/', blank=True, null=True)
    image2 = models.ImageField(upload_to='media/', blank=True, null=True)
    image3 = models.ImageField(upload_to='media/', blank=True, null=True)

    def __str__(self):
        return self.user.username + ' - ' + self.task.title
    
    def get_url(self):
        return f'/applications/{self.id}/'


class TaskOrder(models.Model):
    DEBIT = 'DEBIT'
    REFUND = 'REFUND'
    ORDER_CHOICES = [
        (DEBIT, 'Debit'),
        (REFUND, 'Refund')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    order_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_type = models.CharField(max_length=100, choices=ORDER_CHOICES, default=DEBIT)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class UserReceipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'

    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    DENIED = 'DENIED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied')
    ]
    TRANSACTION_CHOICES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_type = models.CharField(max_length=100, choices=TRANSACTION_CHOICES, default=DEPOSIT)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + ' - ' + self.transaction_type + ' - ' + str(self.amount)

def refund_user(username, task_slug):
    profile = User.objects.filter(username=username).first()
    task = Task.objects.filter(slug=task_slug).first()
    if TaskOrder.objects.filter(user=profile, task=task, order_type='REFUND').first() is None and TaskOrder.objects.filter(user=profile, task=task, order_type='DEBIT').count() == 1:
        print('1')
        task_order = TaskOrder.objects.create(user=profile, task=task, order_price=task.cost, order_type='REFUND')
        print('hi')
        if task_order:
            profile.wallet_balance += task.cost
            print('2')
            profile.save()
        