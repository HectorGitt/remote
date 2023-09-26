from django.contrib import admin
from .models import User, Category, Task, UserTask, SubCategory, Transaction
from .methods import methods
# Register your models here.


admin.site.register(Category)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'wallet_balance', 'earnings', 'is_staff']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_created' 
    list_display = ['title', 'owner', 'sub_category', 'status', 'date_created']
    list_filter = ['sub_category', 'status']

@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display =['user', 'task', 'status', 'date_created']
    list_filter = ['task', 'status', 'user']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin, methods):
    list_display = ['user', 'amount', 'transaction_type', 'approve','reject']
    list_filter = ['transaction_type', 'status']

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']