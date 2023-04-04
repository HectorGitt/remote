from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm, TaskForm
from django.contrib.auth.decorators import login_required
from .models import User, Category, Task

# Create your views here.
def home(request):
    user = request.user
    return render(request, 'index.html', {'user': user})
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            print('Account created for {username}')
            return redirect('login')
    else:
        form = UserForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    profile = User.objects.filter(username=request.user.username).first()
    return render(request, 'dashboard.html', {'profile': profile})

@login_required
def jobs(request):
    tasks = Task.objects.filter(status='APPROVED')
    return render(request, 'jobs.html', {'tasks': tasks})

@login_required
def post_job(request):
    return render(request, 'post_gig/category.html')

@login_required
def post_job_new(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            try:
                task.cost = task.unit_price * task.total_participants
                task.owner = User.objects.filter(username=request.user.username).first()
                task.save()
                return redirect('dashboard')
            except Exception as e:
                #push error to form and return to form
                print(e)
                return redirect('post_job_new')
            
                
                
            
        else:
            print(form.errors)
    else:
        form = TaskForm()
    return render(request, 'post_gig/post_gig.html', {'form': form})
    

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def task_details(request, slug):
    task = Task.objects.filter(slug=slug).first()
    return render(request, 'task_details.html', {'task': task})