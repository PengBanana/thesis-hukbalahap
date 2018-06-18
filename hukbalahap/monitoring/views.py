from django.shortcuts import render

def index(request):
    return render(request, 'monitoring/pool technician/home.html')

def pool(request):
    return render(request, 'monitoring/pool technician/pool-stat.html')

def login(request):
    return render(request, 'monitoring/login.html')
def indexOwner(request):
    return render(request, 'monitoring/pool owner/home-owner.html')
def firstLogin(request):
    return render(request, 'monitoring/pool technician/first-login.html')
def addUser(request):
    return render(request, 'monitoring/pool owner/add-user.html')
