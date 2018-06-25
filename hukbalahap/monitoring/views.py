from django.shortcuts import render
from .models import Pool, Usertype_Ref, User, MaintenanceSchedule, Temp_Turbidity, Temp_Temperature, Temp_Ph, Final_Turbidity, Final_Temperature, Final_Ph

def index(request):
    pool = Pool.objects.all()
    temperature = Temp_Temperature.objects.all()
    turbidity = Temp_Turbidity.objects.all()
    ph = Temp_Ph.objects.all()
    content= {
        'pool':pool,
        'temperature':temperature,
        'turbidity':turbidity,
        'ph':ph,
    }
    return render(request, 'monitoring/pool technician/home.html', content)

def register_user(request):
    #check if password match
    #check if user exist
    #add errors to string and output errors
    request.POST['fName']
    request.POST['lName']
    addUser = User(username = request.POST['uname'], password = request.POST['password'], lastname = request.POST['lName'], firstname = request.POST['lName'])
    addUser.save()
    user = User.objects.all()
    retval = get_object_or_404(User, user_password='peng')
    content= {
        'user':user,
        'alvin': retval
    }
    #success page
    return render(request, 'monitoring/personnel.html', content)


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
def personnel(request):
    return render(request, 'monitoring/pool owner/personnel-efficiency.html')
