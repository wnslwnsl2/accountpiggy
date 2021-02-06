from django.shortcuts import render,redirect
from .forms import CreateAccountForm
from . import forms
from django.contrib.auth import logout,login,authenticate
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Account

# Create your views here.
def register_page(request):
    if 'next' in request.GET:
        next = request.GET['next']
    else:
        next = '/'

    if request.method == 'POST':
        form = CreateAccountForm(request.POST)

        if form.is_valid():
            user = form.save()

            Account.objects.create(
                bank=form.cleaned_data['bank'],
                number=form.cleaned_data['account_number'],
                user=user
            )

            user = authenticate(request, username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
                return redirect(next)
    else:
        form = CreateAccountForm()

    context={
        'form':form,
        'next':next,
    }

    return render(request,'accounts/register.html',context)

def login_page(request):
    if 'next' in request.GET:
        next = request.GET['next']
    else:
        next = '/'

    if request.method=='POST':
        form = forms.LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)

            if user is not None:
                login(request,user)
                return HttpResponseRedirect(next)
            else:
                messages.info(request,'Username OR password is incorrect')
    else:
        form = forms.LoginForm()

    context = {
        'form':form,
        'next':next
    }
    return render(request, 'accounts/login.html', context)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/accounts/login')