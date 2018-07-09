from django.shortcuts import render, get_object_or_404
from .models import Pool, Usertype_Ref, User,Type, Temp_Turbidity, Temp_Temperature, Temp_Ph, Final_Turbidity, Final_Temperature, Final_Ph, MaintenanceSchedule
from .forms import SignUpForm, SignUpType, Pool, MaintenanceSchedule,EditDetailsForm,ChangePasswordForm
from django.views.generic import TemplateView
from django.db.models import Q
from django.db.models import Sum, Count
import math

def index(request):
    poolref = Pool.objects.all().order_by('pk')
    #poolCount = Pool.objects.all().count()
    #temperature levels
    tempDeviations = []
    #standard deviation of multiple pools stored in array
    for poolitem in Pool.objects.all().order_by('pk'):
        #temperatureList = poolitem.liveTemperature.values_list('temp_temperaturelevel', flat=True)
        temperatureList = Temp_Temperature.objects.all().filter(pool=poolref.get(pk=poolitem.pk))
        sumTemperature = temperatureList.annotate(sumTemp=Sum('temp_temperaturelevel'))
        countTemperature = temperatureList.annotate(temperatureCount=Count('temp_temperaturelevel'))
        #sumOfTemp=sumTemperature.get(pk=1)
        try:
            tempSum = sumTemperature.get().sumTemp
            tempCount = countTemperature.get().temperatureCount
        except:
            tempSum = 0
            tempCount = 0
        if(tempCount>0):
            tempMean = tempSum/tempCount
            tempx = []
            for level in temperatureList:
                reading = level.temp_temperaturelevel
                reading -=tempMean
                tempx.append(reading)
            newTempSum = 0
            for read in tempx:
                newTempSum+= read
            tempVariance = newTempSum/tempCount
            tempStandardDev = math.sqrt(tempVariance)
            tempDeviations.append(tempStandardDev)
        else:
            tempDeviations.append('No Readings')

    #turbidity levels
    turbidityDeviations = []
    #standard deviation of turbidity
    for poolitem in Pool.objects.all().order_by('pk'):
        turbidityList = Temp_Turbidity.objects.all().filter(pool=poolref.get(pk=poolitem.pk))
        sumTurbidity = turbidityList.annotate(sumTur=Sum('temp_turbiditylevel'))
        countTurbidity = turbidityList.annotate(countTur=Count('temp_turbiditylevel'))
        try:
            turbiditySum = sumTurbidity.get().sumTur
            turbidityCount = countTurbidity.get().countTur
            turbidityMean = turbiditySum/turbidityCount
            turbidityx = []
            for level in turbidityList:
                reading = level.temp_turbiditylevel
                reading -=turbidityMean
                turbidityx.append(reading)
            newTurbiditySum = 0
            for read in turbidityx:
                newTurbiditySum+= read
            turbidityVariance = newTurbiditySum/turbidityCount
            turbidityStandardDev = math.sqrt(turbidityVariance)
            turbidityDeviations.append(turbidityStandardDev)
        except:
            turbiditySum = 0
            turbidityCount = 0
            turbidityDeviations.append('No Readings')
    phDeviations = []
    #standard deviation of ph
    for poolitem in Pool.objects.all().order_by('pk'):
        phList = Temp_Ph.objects.all().filter(pool=poolref.get(pk=poolitem.pk))
        sumPh = phList.annotate(phSum=Sum('temp_phlevel'))
        countPh = phList.annotate(phCount=Count('temp_phlevel'))
        try:
            phSum = sumPh.get().phSum
            phCount = countPh.get().phCount
            phMean = phSum/phCount
            phx = []
            for level in phList:
                reading = level.temp_phlevel
                reading -=phMean
                phx.append(reading)
            newPhSum = 0
            for read in phx:
                newPhSum+= read
            phVariance = newPhSum/phCount
            phStandardDev = math.sqrt(phVariance)
            phDeviations.append(phStandardDev)
        except:
            phSum = 0
            phCount = 0
            phDeviations.append('No Readings')
        chlorineLevels=['Cannot Compute', 'Cannot Compute', 'Cannot Compute', 'Cannot Compute']
    content= {
        'debug_check': '',
        'pool':poolref,
        'temperature':tempDeviations,
        'turbidity':turbidityDeviations,
        'ph':phDeviations,
        'chlorine':chlorineLevels,
    }
    return render(request, 'monitoring/pool technician/home.html', content)

def poolDetails_view(request, poolitem_id):
    poolref = Pool.objects.get(id=poolitem_id)
    ph = Final_Ph.objects.all().filter(pool=poolref)
    turbidity = Final_Turbidity.objects.all().filter(pool=poolref)
    temperature = Final_Temperature.objects.all().filter(pool=poolref)
    content= {
        'debug_check':'debug off',
        'pool':poolref.pool_location,
        'ph':ph,
        'turbidity':turbidity,
        'temperature':temperature,
    }
    return render(request, 'monitoring/pool technician/pool-stat.html', content)

def addUser(request):
    if request.method == 'POST':
        print('request POST')
        form = SignUpForm(request.POST)
        form2= SignUpType(request.POST)
        print(form2.errors)
        if form.is_valid() and form2.is_valid():
            print('forms valid')
            form.save()
            print(form2.cleaned_data.get('type'))
            print('form1 saved')
            #user.refresh_from_db()  # load the profile instance created by the signal
            #user.save()
            #raw_password = form.cleaned_data.get('password1')
            #newusertype = Usertype_Ref.objects.get(usertype=form2.cleaned_data.get('type'))
            print(form.cleaned_data.get('username'))
            #newuser = User.objects.get(username=form.cleaned_data.get('username'))
            #newtype = Type(user=newuser, type=newusertype)
            #newtype.save()
            print('newtype saved')
            return render(request, 'monitoring/pool owner/add-user.html')
            #user = authenticate(username=user.username, password=raw_password)
            #login(request, user)
            #return redirect('home')
    else:
        form = SignUpForm()
        form2= SignUpType()
    return render(request, 'monitoring/pool owner/add-user.html',locals())


def setMaintenance(request):
    if request.method == 'POST':
        print('request POST')
        form = Pool(request.POST)
        form2= MaintenanceSchedule(request.POST)
        print(form2.errors)
        if form.is_valid() and form2.is_valid():
            print('forms valid')
            form.save()
            print(form.cleaned_data.get('pool_location'))
            print(form2.cleaned_data.get('timeStart'))
            print(form2.cleaned_data.get('timeEnd'))
            return redirect('setMaintenance')

    else:
        form = Pool()
        form2= MaintenanceSchedule()
    return render(request, 'monitoring/pool technician/set-maintenance-schedule.html',locals())


def finishMaintenance(request):
    if request.method == 'POST':
        print('yuuuuuuuuuuuuuuuuuuuuuuhhhh')
        form = MaintenanceSchedule(request.POST)

        if form.is_valid():
            print('forms valid')
            form.save()
            print(form.cleaned_data.get('timeAccomplished'))
            print(form.cleaned_data.get('act_chlorine'))
            return redirect('finishMaintenance')

    else:
        form= MaintenanceSchedule()
    return render(request, 'monitoring/pool technician/finish-maintenance-schedule.html',locals())

def searchPT(request):
    item = request.POST['item']

    allUsers = User.objects.all()
    filtered = allUsers.filter (Q(first_name__icontains=item) | Q(last_name__icontains=item)  | Q(username__icontains=item))
    debugger = filtered
    if not filtered:
        print('no searches')
        return render(request, 'monitoring/pool owner/result-not-found.html')
    else:
        content={
            'searchedItem': item,
            'items':filtered,
        }
    return render(request, 'monitoring/pool owner/search-technician.html', content,)
def profile(request,item_id):
    user = User.objects.get(id=item_id)

    if (request.method == 'POST' ) & ('password' in request.POST):
        form2 = ChangePasswordForm(request.user, request.POST)
        #if form2.is_valid():

            #alert = 'Password Successfully Changed.'

    elif (request.method == 'POST' ) & ('editDetails' in request.POST):
        print("possssst")
        form1 =EditDetailsForm(request.POST)
        if form1.is_valid():
            print('uuuuuup')
            fname = request.POST.get('first_name')
            lname = request.POST.get('last_name')
            user.first_name=fname
            user.last_name=lname
            user.save()


            #alert = 'Details Successfully Changed.'


    else:
        print('naq walang nangyari')
        form1 = EditDetailsForm()
        form2 = ChangePasswordForm(request.user)
    content = {
        'item_id': user,
        'form1': form1,
        'form2': form2,

    }
    return render(request, 'monitoring/pool owner/technician-profile.html', content)


def notFound(request):
    return render(request, 'monitoring/pool owner/result-not-found.html')


def login(request):
    return render(request, 'monitoring/login.html')
def pool(request):
    return render(request, 'monitoring/pool technician/pool-stat.html')

def indexOwner(request):
    return render(request, 'monitoring/pool owner/home-owner.html')
def firstLogin(request):
    return render(request, 'monitoring/pool technician/first-login.html')
def personnel(request):
    return render(request, 'monitoring/pool owner/personnel-efficiency.html')\
