from django.shortcuts import render, get_object_or_404
from .models import Pool, Usertype_Ref, User, MaintenanceSchedule, Temp_Turbidity, Temp_Temperature, Temp_Ph, Final_Turbidity, Final_Temperature, Final_Ph
from monitoring.forms import AddUserForm
from django.views.generic import TemplateView
from django.db.models import Sum, Count
import math


class AddUserView(TemplateView):
    template_name = "monitoring/pool owner/add-user.html"

    def get(self,request):
        form = AddUserForm()
        return render(request, self.template_name,{'form': form})



def index(request):
    poolref = Pool.objects.all()
    temperature = Temp_Temperature.objects.all()
    turbidity = Temp_Turbidity.objects.all()
    ph = Temp_Ph.objects.all()
    
    poolCount = Pool.objects.all().count()
    tempdeviations = []
    
    #standard deviation of one pool
    itemTemperature = Temp_Temperature.objects.filter(pool=poolref.get(pk=1))
    lvltemp = itemTemperature.annotate(temperaturesum=Sum('temp_temperaturelevel'))
    lvltempCount = itemTemperature.annotate(temperatureCount=Count('temp_temperaturelevel'))
    tempSum=lvltemp.get().temperaturesum
    tempCount=lvltempCount.get().temperatureCount
    tempMean = tempSum/tempCount
    tempx = []
    for level in itemTemperature:
        reading = level.temp_temperaturelevel
        reading -=tempMean
        tempx.append(reading)
    newTempSum = 0
    for read in tempx:
        newTempSum+= read
    tempVariance = newTempSum/tempCount
    tempStandardDev = math.sqrt(tempVariance )
    content= {
        'poolCount': newTempSum,
        'pool':pool,
        'temperature':temperature,
        'turbidity':turbidity,
        'ph':ph,
    }
    return render(request, 'monitoring/pool technician/home.html', content)

def login(request):
    return render(request, 'monitoring/login.html')
def pool(request):
    return render(request, 'monitoring/pool technician/pool-stat.html')

def indexOwner(request):
    return render(request, 'monitoring/pool owner/home-owner.html')
def firstLogin(request):
    return render(request, 'monitoring/pool technician/first-login.html')
def personnel(request):
    return render(request, 'monitoring/pool owner/personnel-efficiency.html')
def search(request):
    return render(request, 'monitoring/pool owner/search-technician.html')
def profile(request):
    return render(request, 'monitoring/pool owner/technician-profile.html')
