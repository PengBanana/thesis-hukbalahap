from django.shortcuts import render
from .models import Pool

def index(request):
    pool = Pool.objects.all()
    content= {
        'pool':pool
    }
    return render(request, 'monitoring/pool technician/home.html', content)

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
