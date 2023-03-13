from django.db import models

# Create your models here.

#django user model
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    Male = 'M'
    Female = 'F'
    GENDER = [ (Male,'Male'), (Female, 'Female')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(choices=GENDER, max_length=1)

    def __str__(self):
        return self.user.username
