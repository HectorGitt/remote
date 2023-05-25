from typing import Any, Dict
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import UserForm, TaskForm, UserTaskForm,TransactionForm, ContactForm
from django.contrib.auth.decorators import login_required
from .models import User, Category,SubCategory, Task, UserTask, UserReceipt, TaskOrder, Transaction, BankAccount
from django.views.generic import ListView, DetailView, UpdateView, CreateView, TemplateView, FormView
import requests
from django.conf import settings
from .methods import send_mail
from decimal import Decimal

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
    is_client = profile.is_client()
    # get latest 5 tasks posted by user
    if is_client:
        tasks = Task.objects.filter(owner=profile).order_by('-date_created')
        task_count = tasks.count()
        approved_count = Task.objects.filter(owner=profile, status='APPROVED').count()
        rejected_count = Task.objects.filter(owner=profile, status='REJECTED').count()
        pending_count = Task.objects.filter(owner=profile, status='PENDING').count()
        applications = UserTask.objects.filter(task__owner=profile).order_by('-date_created')
    else:
        tasks = Task.objects.filter(status='APPROVED').order_by('-date_created')    
        task_count = UserTask.objects.filter(user=profile).count()
        approved_count = UserTask.objects.filter(user=profile, status='APPROVED').count()
        rejected_count = UserTask.objects.filter(user=profile, status='REJECTED').count()
        pending_count = UserTask.objects.filter(user=profile, status='PENDING').count()
        applications = UserTask.objects.filter(user=profile).order_by('-date_created')
    context = {'profile': profile, 'posted_tasks': tasks[:5], 'applications': applications,
                'task_count': task_count,
                'approved_count': approved_count,
                'rejected_count': rejected_count,
                'pending_count': pending_count,
                'is_client': is_client
            }
    return render(request, 'dashboard.html', context)

@method_decorator(login_required, name='dispatch')
class TaskListView(ListView):
    model = Task
    template_name = 'jobs.html'
    queryset = Task.active.order_by('-id')
    context_object_name = 'tasks'
    paginate_by = 5

    def get_context_data(self):
        context = super().get_context_data()
        context['categories'] = Category.objects.all()
        return context

    
    
        
    
class TaskByCategoryListView(ListView):
    template_name = 'jobs.html'
    context_object_name = 'tasks'
    paginate_by = 5
    
    def get_queryset(self):
        category_id = self.kwargs['id']
        return Task.active.filter(sub_category__category__id=category_id).order_by('-id')
    
    def get_context_data(self):
        context = super().get_context_data()
        context['categories'] = Category.objects.all()
        return context


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
                sub_category = SubCategory.objects.filter(id=request.POST.get('sub_category')).first()
                if sub_category.min_price > task.unit_price:
                    messages.error(request, f'Minimum Price per User must be greater than {sub_category.min_price}')
                    return render(request, 'post_gig/post_gig.html', {'form': form})
                cost = task.unit_price * task.total_participants
                task.cost = cost + Decimal(cost * 0.15)
                owner = User.objects.filter(username=request.user.username).first()
                if owner.wallet_balance < task.cost:
                    messages.error(request, f'Wallet balance is low')
                    return render(request, 'post_gig/post_gig.html', {'form': form})
                owner.wallet_balance -= task.cost
                owner.save()
                task.owner = owner
                task.save()
                task_order = TaskOrder.objects.create(task=task, user=owner, order_price=task.cost)
                task_order.save()
                message = f'Job ({task.title})   Posted successfully by {owner.username} with sub category: {task.sub_category} and unit_price: N{task.unit_price} for {task.total_participants} participant. Waiting for comfirmation'
                send_mail('RemoteGig: New Job Posted','',message, [settings.EMAIL_HOST_USER, 'abdulazeezolamidae@gmail.com'])
                messages.success(request, f'Job ({task.title}) Posted successfully')
                return redirect('dashboard')
            except Exception as e:
                #push error to form and return to form
                print(e)
                return render(request, 'post_gig/post_gig.html', {'form': form})
            
                
                
            
        else:
            print(form.errors)
    else:
        form = TaskForm(initial={'category': 1})
    return render(request, 'post_gig/post_gig.html', {'form': form})

def load_subcategories(request, id):
    category_id = int(id)
    subcategories = SubCategory.objects.filter(category__id=category_id).order_by('name')
    return JsonResponse(list(subcategories.values('id', 'name', 'min_price')), safe=False)


    

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def task_details(request, slug):
    task = Task.objects.filter(slug=slug).first()
    user = User.objects.filter(username=request.user.username).first()
    is_owner = (task.owner == user)
    if task.status != 'APPROVED' and not is_owner:
        return redirect('dashboard')
    form = UserTaskForm()
    return render(request, 'client/task_details.html', {'task': task, 'is_owner': is_owner, 'form': form})

def apply(request, slug):
    task = Task.objects.filter(slug=slug).first()
    user = User.objects.filter(username=request.user.username).first()
    if task and request.method =='POST':
        form = UserTaskForm(request.POST, request.FILES)
        if task.owner != user:
            if not form.is_valid():
                return redirect('dashboard')
            if task.state != 'IN_PROGRESS':
                print('Task is not in progress')
                messages.info(request, 'Task is not in progress')
                return redirect('dashboard')
            if task.total_participants <= task.registered_count():
                print(task.total_participants, task.registered_count())
                print('Task is no longer available')
                messages.info(request, 'Task is no longer available')
                return redirect(request.META.get('HTTP_REFERER'))
            if task.is_registered(user) is not True:
                user_task = form.save(commit=False)
                user_task.user = user
                user_task.task = task
                print('Applied')
                messages.success(request, 'Task Application Successful')
                user_task.save()
                return redirect(request.META.get('HTTP_REFERER')) 
            else:
                print('Already applied')
                messages.warning(request, 'Task Already Applied')
                return redirect('dashboard')
        else:
            print('You cannot apply to your own task')
            messages.warning(request, 'You cannot apply to your own task')
            return redirect('home')

class PostedTaskListView(ListView):
    model = Task
    template_name = 'jobs.html'
    paginate_by = 5
    context_object_name = 'tasks'
    

    def get_queryset(self):
        profile = User.objects.filter(username=self.request.user.username).first()
        return Task.objects.filter(owner=profile).order_by('-date_created')

def end_task(request, slug):
    task = Task.objects.filter(slug=slug).first()
    user = User.objects.filter(username=request.user.username).first()
    if task:
        if task.owner == user:
            if task.state != 'ENDED':
                task.state = 'ENDED'
                task.save()
                print('Task Terminated')
                messages.info(request, 'Task Terminated')
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                print('Task Already Terminated')
                messages.error(request, 'Task Terminated')
                return redirect('dashboard')
        else:
            print('You dont have the permission')
            messages.info(request, 'You dont have the permission')
            return redirect('home')
    else:
        print('403 Error')
        return redirect('home')

def pause_task(request, slug):
    task = Task.objects.filter(slug=slug).first()
    user = User.objects.filter(username=request.user.username).first()
    if task:
        if task.owner == user:
            if task.state != 'PAUSED':
                task.state = 'PAUSED'
                task.save()
                print('Task Paused')
                messages.info(request, 'Task Paused')
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                print('Task Already Paused')
                messages.warning(request, 'Task Already Paused')
                return redirect('dashboard')
        else:
            print('You dont have the permission')
            messages.warning(request, 'You dont have the required permission')
            return redirect('home')
    else:
        print('403 Error')
        return redirect('home')

def resume_task(request, slug):
    task = Task.objects.filter(slug=slug).first()
    user = User.objects.filter(username=request.user.username).first()
    if task:
        if task.owner == user:
            if task.state != 'IN_PROGRESS':
                task.state = 'IN_PROGRESS'
                task.save()
                print('Task Resumed')
                messages.success(request, 'Task Resumed')
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                print('Task Already In Progress')
                messages.warning(request, 'Task Already In Progress')
                return redirect('dashboard')
        else:
            print('You dont have the permission')
            messages.warning(request, 'You dont have the required permission')
            return redirect('home')
    else:
        print('403 Error')
        return redirect('home')

class WalletView(TemplateView):
    template_name = 'earner/wallet.html'
    context_object_name = 'receipts'
    paginate_by = 5
    
    def get_context_data(self, **kwargs):
        profile = User.objects.filter(username=self.request.user.username).first()
        deposits = Transaction.objects.filter(user=profile, transaction_type='DEPOSIT').order_by('-date_created')
        deposit_count = Transaction.objects.filter(user=profile, transaction_type='DEPOSIT', status='APPROVED').count()
        withdrawals = Transaction.objects.filter(user=profile, transaction_type='WITHDRAWAL').order_by('-date_created')
        withdrawal_count = Transaction.objects.filter(user=profile, transaction_type='WITHDRAWAL', status='APPROVED').count()
        receipts = UserReceipt.objects.filter(user=profile).order_by('-date_created')[0:5]
        receipt_count = UserReceipt.objects.filter(user=profile).order_by('-date_created').count()
        context = super().get_context_data(**kwargs)
        context['deposits'] = deposits
        context['deposit_count'] = deposit_count
        context['withdrawals'] = withdrawals
        context['withdrawal_count'] = withdrawal_count
        context['receipts'] = receipts
        context['receipt_count'] = receipt_count
        return context
    
class ClientApplication(DetailView):
    model = UserTask
    template_name = 'client/application_details.html'
    context_object_name = 'user_task'
    def get(self, request, *args, **kwargs):
        user_task = UserTask.objects.filter(id=self.kwargs['pk']).first()
        if user_task:
            if user_task.task.owner == request.user:
                return super().get(request, *args, **kwargs)
            else:
                return redirect('home')
        else:
            return redirect('home')

def approve_app(request, id):
    user_task = UserTask.objects.filter(id=id).first()
    user = user_task.user
    if user_task.task.owner != request.user:
        return redirect('home')
    if user_task.status != 'APPROVED':
        user_task.status = 'APPROVED'
        receipt = UserReceipt(user=user, task=user_task.task, unit_price=user_task.task.unit_price)
        receipt.save()
        user_task.save()
        user.earnings += user_task.task.unit_price
        user.save()
        messages.success(request, 'Application Approved')
        return redirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect('dashboard')

def reject_app(request, id):
    user_task = UserTask.objects.filter(id=id).first()
    if user_task.task.owner != request.user:
        return redirect('home')
    if user_task.status != 'REJECTED':
        user_task.status = 'REJECTED'
        
        user_task.save()
        messages.success(request, 'Application Rejected')
        return redirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect('dashboard')

class ApplicationListView(ListView):
    template_name = 'client/list_applications.html'
    context_object_name = 'applications'
    paginate_by = 5
    
    def get_queryset(self):
        profile = User.objects.filter(username=self.request.user.username).first()
        if profile.role == 'CLIENT':
            return UserTask.objects.filter(task__owner=profile).order_by('-date_created')
        return UserTask.objects.filter(user=profile).order_by('-date_created')
class TaskApplicationListView(ListView):
    template_name = 'client/task_applications.html'
    context_object_name = 'applications'
    paginate_by = 5
    
    def get_queryset(self):
        profile = User.objects.filter(username=self.request.user.username).first()
        task = Task.objects.filter(slug=self.kwargs['slug']).first()
        return UserTask.objects.filter(task__owner=profile, task=task).order_by('-date_created')
    
def approve_all_apps(request, slug):
    task = Task.objects.filter(slug=slug).first()
    if task.owner != request.user:
        return redirect('home')
    user_tasks = UserTask.objects.filter(task=task)
    for user_task in user_tasks:
        if user_task.status == 'PENDING':
            user_task.status = 'APPROVED'
            user_task.save()
            user_task.user.earnings += user_task.task.unit_price
            user_task.user.save()
            receipt = UserReceipt(user=user_task.user, task=user_task.task, unit_price=user_task.task.unit_price)
            receipt.save()
    messages.success(request, 'All Pending Application Approved')
    return redirect(request.META.get('HTTP_REFERER'))

    
class UserUpdate(UpdateView):
    model = User
    template_name = 'user_update_form.html'
    fields = ['first_name', 'last_name', 'email', 'gender', 'role']

    def get_object(self):
        return User.objects.filter(username=self.request.user.username).first()
    
class DepositView(FormView):
    form_class = TransactionForm
    template_name = 'client/deposit.html'
    fields = ['amount']
    success_url = reverse_lazy('pay')
    def form_valid(self, form):
        user = User.objects.filter(username=self.request.user.username).first()
        transaction = Transaction(user=user, amount=form.cleaned_data['amount'], transaction_type='DEPOSIT')
        transaction.save()
        return super().form_valid(form)
    
class PayView(TemplateView):
    template_name = 'client/pay.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transaction"] = Transaction.objects.filter(user=self.request.user).last()
        return context
def verify_payment_transaction(request, id):
    transaction = Transaction.objects.filter(id=id).first()
    request = requests.get('https://api.paystack.co/transaction/verify/'+str(id), headers={'Authorization': 'Bearer '+str(settings.PAYSTACK_SECRET_KEY)})
    if request.status_code == 200:
        data = request.json()['data']
        print(data)
        if data['status'] == 'success' and transaction.status == 'PENDING':
            transaction.status = 'APPROVED'
            transaction.save()
            user = transaction.user
            user.wallet_balance += transaction.amount
            user.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failed'})
    else:
        return JsonResponse({'status': 'failed'})
    
def withdraw(request):
    return render(request, 'earner/withdraw.html')

class WithdrawalListView(ListView):
    model = Transaction
    paginate_by = 20
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self) -> QuerySet[Any]:
        profile = User.objects.filter(username=self.request.user.username).first()
        return Transaction.objects.filter(transaction_type='WITHDRAWAL', user=profile).order_by('-id')
    
class DepositListView(ListView):
    model = Transaction
    paginate_by = 20
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self) -> QuerySet[Any]:
        profile = User.objects.filter(username=self.request.user.username).first()
        return Transaction.objects.filter(transaction_type='DEPOSIT', user=profile).order_by('-id')
    

class ProcessWithdrawalView(CreateView):
    model = Transaction
    template_name = 'earner/process_withdrawal.html'
    fields = ['amount']
    success_url = reverse_lazy('dashboard')

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        initial["amount"] = Decimal(self.request.GET.get('amount'))
        return initial
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bank_account"] = BankAccount.objects.filter(user=self.request.user).first()
        context["amount"] = self.request.GET.get('amount')
        return context
    def form_valid(self, form):
        user = User.objects.filter(username=self.request.user.username).first()
        form.instance.user = user    
        amount = form.cleaned_data['amount']
        if user.earnings < amount:
            messages.error(self.request, 'You dont have as much earnings')
            return redirect('withdraw')
        user.earnings -= amount
        transaction = Transaction.objects.create(user=user, amount=amount, status='PENDING', transaction_type='WITHDRAWAL')
        transaction.save()
        user.save()
        message = 'Withdrawal request of N'+ f'{transaction.amount:,}'+' was made by '+user.first_name+' '+user.last_name+' to Bank Name: '+user.bank_account.first().bank_name+'; and Account Number: '+user.bank_account.first().account_number + '; on ' + str(transaction.date_created.strftime('%d %b %Y %H:%M'))
        print(message)
        send_mail('RemoteGig Withdrawal Request', '', message, [settings.EMAIL_HOST_USER, 'abdulazeezolamidae@gmail.com'])
        messages.success(self.request, 'Withdrawal Successful, Wait for Processing')
        return super().form_valid(form)
        
class TransferEarningsView(FormView):
    template_name = 'earner/transfer_earnings.html'
    form_class = TransactionForm
    success_url = reverse_lazy('wallet')
    def form_valid(self, form):
        user = User.objects.filter(username=self.request.user.username).first()
        amount = form.cleaned_data['amount']
        if user.earnings < amount:
            messages.error(self.request, 'You dont have as much earnings')
            return redirect('transfer_earnings')
        user.earnings -= amount
        user.wallet_balance += amount
        user.save()
        messages.success(self.request, 'Transfer Successful')
        return super().form_valid(form)
class TransactionListView(ListView):
    model = Transaction
    paginate_by = 40
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self) -> QuerySet[Any]:
        profile = User.objects.filter(username=self.request.user.username).first()
        return Transaction.objects.filter(user=profile).order_by('-id')
    
class ReceiptListView(ListView):
    model = Transaction
    paginate_by = 40
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self) -> QuerySet[Any]:
        profile = User.objects.filter(username=self.request.user.username).first()
        return UserReceipt.objects.filter(user=profile).order_by('-id')

class BankDetailsView(CreateView):
    model = BankAccount
    template_name = 'earner/bank_details.html'
    fields = ['account_number', 'bank_name', 'name']
    success_url = reverse_lazy('bank_details')
    def form_valid(self, form):
        user = User.objects.filter(username=self.request.user.username).first()
        form.instance.user = user
        #make sure user has not added bank account before
        if BankAccount.objects.filter(user=user).exists():
            messages.error(self.request, 'You cant change your bank details for now...')
            return redirect('bank_details')
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bank_account"] = BankAccount.objects.filter(user=self.request.user).first()
        return context
    
class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('support')
    def form_valid(self, form):
        print(form.cleaned_data['subject'])
        print(form.cleaned_data['message'])
        print(form.cleaned_data['email'])
        subject = f"RemoteGig - {form.cleaned_data['subject']}"
        message = '<h2>From - ' + form.cleaned_data['name'] + '</h2><br/>' + form.cleaned_data['message']
        send_mail(
            subject,
            '',
            message,
            ['adeniyi.olaitanhector@yahoo.com', 'abdulazeezolamidae@gmail.com'],
        )
        messages.success(self.request, 'Message Sent')
        return super().form_valid(form)
def toggle_role(request):
    user = User.objects.filter(username=request.user.username).first()
    if user.role == User.Client:
        user.role = User.Worker
    else:
        user.role = User.Client
    user.save()
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('dashboard')


