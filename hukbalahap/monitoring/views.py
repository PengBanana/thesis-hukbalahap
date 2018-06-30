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
    poolref = Pool.objects.all().order_by('pk')
    #poolCount = Pool.objects.all().count()
    #temperature levels
    tempDeviations = []
    #standard deviation of multiple pools stored in array
    for poolitem in Pool.objects.all().order_by('pk'):
        #temperatureList = poolitem.liveTemperature.values_list('temp_temperaturelevel', flat=True)
        temperatureList = Temp_Temperature.objects.filter(pool=poolref.get(pk=poolitem.pk))
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
        turbidityList = Temp_Turbidity.objects.filter(pool=poolref.get(pk=poolitem.pk))
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
            turbidityStandardDev = math.sqrt(tempVariance)
            turbidityDeviations.append(tempStandardDev)
        except:
            turbiditySum = 0
            turbidityCount = 0
            turbidityDeviations.append('No Readings')
    ph = []
    content= {
        'debug_check': tempDeviations,
        'pool':poolref,
        'temperature':tempDeviations,
        'turbidity':turbidityDeviations,
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
