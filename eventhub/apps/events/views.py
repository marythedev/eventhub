from django.shortcuts import render

def home(request):
    return render(request, 'events/home.html')

def register(request):
    if request.method == "POST":
        print("User registered")
    return render(request, 'events/register.html')

def login(request):
    if request.method == 'POST':
        print("User logged in")
    return render(request, 'events/login.html')

def account(request):
    if request.method == 'POST':
        print("Account updated")
    return render(request, 'events/account.html')

def events(request):
    return render(request, 'events/events.html')

def purchase(request):
    if request.method == 'POST':
        print("Purchase successful")
    return render(request, 'events/purchase.html/')

def pay(request):
    if request.method == 'POST':
        print("Paid for the order")
    return render(request, 'events/payment.html/')

def orders(request):
    return render(request, 'events/order.html/')