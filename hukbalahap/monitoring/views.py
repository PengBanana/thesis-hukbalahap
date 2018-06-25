from django.shortcuts import render, get_object_or_404
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
    #get values from form
    p = request.POST['password']
    rp = request.POST['repassword']
    u = request.POST['uname']
    f =request.POST['fName']
    l = request.POST['lName']
    uType = get_object_or_404(Usertype_Ref, usertype='admin')
    #check if password match
    if p == rp: 
    #check if user exist
        try:
            go = User.objects.get(u)
        except User.DoesNotExist:
            go = None
        if go == None:
            #usertype should be pool technician needs fully populated database
            addUser = User(username = u, password = p, lastname = l, firstname = f, usertype_ref = uType)
            addUser.save()
            #register success display success message
            return render(request, 'monitoring/register_success.html')
        #add errors to string and output errors
        else:
            error = 2
            context= {
                'error': error
            }
            return render(request, 'monitoring/pool owner/add-user.html', context)
    else:
        error = 1
        context= {
            'error': error
        }
        return render(request, 'monitoring/pool owner/add-user.html', context)

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
