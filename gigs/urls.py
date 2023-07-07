from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.TaskListView.as_view(), name='tasks'),
    path('tasks/category/<int:id>/', views.TaskByCategoryListView.as_view(), name='tasks_category'),
    path('post_job/', views.post_job, name='post_job'),
    path('post_job_new/', views.post_job_new, name='post_job_new'),
    path('api/load_subcategories/<int:id>/', views.load_subcategories, name='subcategories'),
    path('posted_tasks/', views.PostedTaskListView.as_view(), name='posted_tasks'),
    path('profile/', views.profile, name='profile'),
    path('task/<slug:slug>/', views.task_details, name='task'),
    path('task/<slug:slug>/apply/', views.apply, name='apply'),
    path('task/<slug:slug>/pause/', views.pause_task, name='pause_task'),
    path('task/<slug:slug>/resume/', views.resume_task, name='resume_task'),
    path('task/<slug:slug>/end/', views.end_task, name='end_task'),
    path('task/<slug:slug>/applications/', views.TaskApplicationListView.as_view(), name='task_applications'),
    path('deposit/', views.DepositView.as_view(), name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('process_withdrawal/', views.ProcessWithdrawalView.as_view(), name='process_withdrawal'),
    path('user_update/bank_details/', views.BankDetailsView.as_view(), name='bank_details'),
    path('pay/', views.PayView.as_view(), name='pay'),
    path('transfer_earnings/', views.TransferEarningsView.as_view(), name='transfer_earnings'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('deposits/', views.DepositListView.as_view(), name='deposit_list'),
    path('withdrawals/', views.WithdrawalListView.as_view(), name='withdrawal_list'),
    path('receipts/', views.ReceiptListView.as_view(), name='receipt_list'),
    path('user_update/', views.UserUpdate.as_view(), name='user_update'),
    path('pay/verify_transaction/<int:id>/', views.verify_payment_transaction, name='verify_transaction'),
    path('support/', views.ContactView.as_view(), name='support'),
    path('switch_role/', views.toggle_role, name='switch_role'),
] + static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)
