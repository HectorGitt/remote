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
    path('jobs/', views.jobs, name='jobs'),
    path('post_job/', views.post_job, name='post_job'),
    path('post_job_new/', views.post_job_new, name='post_job_new'),
    path('profile/', views.profile, name='profile'),
] + static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)
