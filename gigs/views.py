from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    user = request.user
    return render(request, 'index.html', {'user': user})
def signup(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            print('Account created for {username}')
            return redirect('login')
    else:
        form = ProfileForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def jobs(request):
    return render(request, 'jobs.html')

@login_required
def post_job(request):
    return render(request, 'post_gig/category.html')

@login_required
def post_job_new(request):
    return render(request, 'post_gig/post_gig.html')

@login_required
def profile(request):
    return render(request, 'profile.html')