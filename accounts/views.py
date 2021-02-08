from django.shortcuts import render,redirect
from .forms import CreateAccountForm
from django.contrib.auth import logout,login,authenticate
from django.http import HttpResponseRedirect
from django.contrib import messages

# Create your views here.
def register_page(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login')
    else:
        form = CreateAccountForm()

    context={'form':form}

    return render(request,'accounts/register.html',context)

def login_page(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Username OR password is incorrect')

        context = {'username':username,
                   'password':password}
        return render(request, 'accounts/login.html', context)

    context = {}
    return render(request, 'accounts/login.html', context)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/accounts/login')