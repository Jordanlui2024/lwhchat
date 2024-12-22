from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm

# Create your views here.
def homePage(request):
    return render(request, 'core/homePage.html', {"page":"home"})    


def loginPage(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homePage')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
           messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
                     
    return render(request, 'core/homePage.html', {'form': form, "page":"login"})   

def signupPage(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('homePage')
        else:
            print(form.errors)    
    else:
        form = SignUpForm()
            
    return render(request, 'core/homePage.html', {"form":form, "page":"signup"})

# @login_required
# def profilePage(request):
    