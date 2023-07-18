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
    path('support/', views.ContactView.as_view(), name='support'),
    path('switch_role/', views.toggle_role, name='switch_role'),
] + static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)
