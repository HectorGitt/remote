from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import UserForm, TaskForm
from django.contrib.auth.decorators import login_required
from .models import User, Category, Task, UserTask
from django.views.generic import ListView

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

@method_decorator(login_required, name='dispatch')
class TaskListView(ListView):
    model = Task
    queryset = Task.objects.filter(status='APPROVED').order_by('-date_created')
    template_name = 'jobs.html'
    context_object_name = 'tasks'
    paginate_by = 5

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

def apply(request, slug):
    task = Task.objects.filter(slug=slug).first()
    user = User.objects.filter(username=request.user.username).first()
    if task:
        if task.owner != user:
            if task.state != 'IN_PROGRESS':
                print('Task is not in progress')
                return redirect('dashboard')
            if task.is_registered(user) is not True:
                UserTask.objects.create(user=user, task=task)
                print('Applied')
                return redirect(request.META.get('HTTP_REFERER'))
            
            else:
                print('Already applied')
                return redirect('dashboard')
        else:
            print('You cannot apply to your own task')
            return redirect('home')
    