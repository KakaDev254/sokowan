from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm # <-- Imported CustomLoginForm
from store.models import Order

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to Sokowan!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        # Use the custom login form
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        # Use the custom login form for GET requests too
        form = CustomLoginForm()
        
    # Note: Removed the manual form.fields[...].widget.attrs.update() lines 
    # because those styles are now handled inside CustomLoginForm in forms.py

    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def order_history(request):
    # Fetch orders tied to this user, ordered by newest first
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'users/order_history.html', {'orders': orders})