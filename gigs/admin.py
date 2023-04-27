from django.contrib import admin
from .models import User, Category, Task, UserTask, SubCategory

# Register your models here.

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Task)
admin.site.register(UserTask)
admin.site.register(SubCategory)


