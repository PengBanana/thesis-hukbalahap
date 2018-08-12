from django.shortcuts import render, get_object_or_404,redirect
from .models import Pool, Usertype_Ref, User,Type, Temp_Turbidity, Temp_Temperature, Temp_Ph, Final_Turbidity, Final_Temperature, Final_Ph, Status, Status_Ref, MaintenanceSchedule, Notification_Table
from .forms import SignUpForm, SignUpType, Pool,EditDetailsForm,ChangePasswordForm
from django.views.generic import TemplateView
from django.db.models import Q
from django.db.models import Sum, Count
import math, decimal, datetime
from django.contrib.auth import login as auth_login, authenticate, update_session_auth_hash,logout
from django.contrib.auth.views import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext

<<<<<<< HEAD
=======

#start of import by migs and  francis
import threading, time, spidev,numpy as np, Adafruit_GPIO.SPI as SPI, Adafruit_MCP3008, os, sqlite3
from time import sleep
import sqlite3

#end of import
#Sensor Reading Start
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
turbidityChannel = 1
phChannel = 0
sleepTime = 2
ctr = 0
arrayLength = 60
printInterval = .800
samplingInterval = 20

def sensor():
    for i in os.listdir('/sys/bus/w1/devices'):
        if i != 'w1_bus_master1':
            ds18b20 = i
    return ds18b20

def voltArray(arrayLength, mcp, channel):
    voltArray = np.zeros(arrayLength,float)
    i = 0
    while i < arrayLength:
        data = mcp.read_adc(channel)
        voltArray[i] = data
        i = i + 1
        sleep(.800)
    return voltArray

def averageVolt(voltArray, number):
    minm = 0
    maxm = 0
    avg = 0
    amount = 0

    if voltArray[0] < voltArray[1]:
        minm = voltArray[0]
        maxm = voltArray[1]
    else:
        minm = voltArray[1]
        maxm = voltArray[0]
    for x in range(2,voltArray.size):
        if voltArray[x] < minm:
            amount = amount + minm
            minm = voltArray[x]
        else:
            if voltArray[x] > maxm:
                amount = amount + maxm
                maxm = voltArray[x]
            else:
                amount = amount + voltArray[x]
    avg = amount/ (number-2)
    #print ("na average na")
    return avg

def getTurbidity(voltage):
    turbValue = (-1120.4*voltage*voltage) + (5742.3*voltage) - 4352.9
    if turbValue < 0:
        return 0
    else:
        return turbValue

def read(ds18b20):
    location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
    tfile = open(location)
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    celsius = temperature / 1000
    return celsius

#temp_pH queries
def insert_to_temp_pH():
    #reads pH value voltage and translates to actual pH value
    phVoltage = voltArray(arrayLength, mcp, phChannel)
    finalPhVoltage = averageVolt(phVoltage, arrayLength)*5.0/1024
    phValue = round((1.5 * finalPhVoltage),2)
    Temp_Ph.objects.create(pool_id='1', temp_phlevel=phValue, temp_phdatetime=datetime.datetime.now())
    print("Temp_Ph Value Added: Enrique Razon Building, " + str(phValue) + ", " + str(datetime.datetime.now()))

def del_insert_to_temp_pH():
    phVoltage = voltArray(arrayLength, mcp, phChannel)
    finalPhVoltage = averageVolt(phVoltage, arrayLength)*5.0/1024
    phValue = round((1.5 * finalPhVoltage),2)
    print("Deleted: " + str(Temp_Ph.objects.all()[0]))
    Temp_Ph.objects.all()[0].delete()
    Temp_Ph.objects.create(pool_id='1', temp_phlevel=phValue, temp_phdatetime=datetime.datetime.now())
    print("Temp_Ph Value Added: Enrique Razon Building, " + str(phValue) + ", " + str(datetime.datetime.now()))

def batchCount10pH():
    pHList = Temp_Ph.objects.all().filter(pool_id = '1')
    tempSum=0
    tempCount=0
    for item in pHList:
        tempSum+=item.temp_phlevel
        tempCount+=1
    if(tempCount>0):
        tempMean = tempSum/tempCount
        tempx = []
        for level in pHList:
            reading = level.temp_phlevel
            reading -=tempMean
            tempx.append(reading)
        newTempSum = 0
        for read in tempx:
            newTempSum+= read
        phVariance = newTempSum/tempCount
        pHStandardDev = math.sqrt(phVariance)
        pHStandardDev= decimal.Decimal(pHStandardDev)+tempMean
        Final_Ph.objects.create(pool_id='1', final_phlevel=pHStandardDev, final_phdatetime=datetime.datetime.now())
        print("Final_Ph Value Added: Enrique Razon Building, " + str(pHStandardDev) + ", " + str(datetime.datetime.now()))

def count_temp_ph():
    rc = Temp_Ph.objects.count()
    return rc

#temp_turbidity queries
def insert_to_temp_turbidity():
    #reads turbidity voltage
    turbVoltage = voltArray(arrayLength, mcp, turbidityChannel)
    finalTurbVoltage = averageVolt(turbVoltage, arrayLength)*5.0/1024
    turbValue = round((getTurbidity(finalTurbVoltage)),2)
    Temp_Turbidity.objects.create(pool_id='1', temp_turbiditylevel=turbValue, temp_turbiditydatetime=datetime.datetime.now())
    print("Temp_Turbidity Value Added: Enrique Razon Building, " + str(turbValue) + ", " + str(datetime.datetime.now()))

def del_insert_to_temp_turbidity():
    turbVoltage = voltArray(arrayLength, mcp, turbidityChannel)
    finalTurbVoltage = averageVolt(turbVoltage, arrayLength)*5.0/1024
    turbValue = round((getTurbidity(finalTurbVoltage)),2)
    print("Deleted: " + str(Temp_Turbidity.objects.all()[0]))
    Temp_Turbidity.objects.all()[0].delete()
    Temp_Turbidity.objects.create(pool_id='1', temp_turbiditylevel=turbValue, temp_turbiditydatetime=datetime.datetime.now())
    print("Temp_Turbidity Value Added: Enrique Razon Building, " + str(turbValue) + ", " + str(datetime.datetime.now()))

def batchCount10Turbidity():
    turbidityList = Temp_Turbidity.objects.all().filter(pool_id = '1')
    tempSum=0
    tempCount=0
    for item in turbidityList:
        tempSum+=item.temp_turbiditylevel
        tempCount+=1
    if(tempCount>0):
        tempMean = tempSum/tempCount
        tempx = []
        for level in turbidityList:
            reading = level.temp_turbiditylevel
            reading -=tempMean
            tempx.append(reading)
        newTempSum = 0
        for read in tempx:
            newTempSum+= read
        turbidityVariance = newTempSum/tempCount
        turbidityStandardDev = math.sqrt(turbidityVariance)
        turbidityStandardDev = decimal.Decimal(turbidityStandardDev)+tempMean
        Final_Turbidity.objects.create(pool_id='1', final_turbiditylevel=turbidityStandardDev, final_turbiditydatetime=datetime.datetime.now())
        print("Final_Turbidity Value Added: Enrique Razon Building, " + str(turbidityStandardDev) + ", " + str(datetime.datetime.now()))

def count_temp_turbidity():
    rc = Temp_Turbidity.objects.count()
    return rc

#temp_temperature queries
def insert_to_temp_temperature():
    #reads temperature sensor
    serialNum = sensor()
    tempData = read(serialNum)
    Temp_Temperature.objects.create(pool_id='1', temp_temperaturelevel=tempData, temp_temperaturedatetime=datetime.datetime.now())
    print("Temp_Temperature Value Added: Enrique Razon Building, " + str(tempData) + ", " + str(datetime.datetime.now()))

def del_insert_to_temp_temperature():
    serialNum = sensor()
    tempData = read(serialNum)
    print("Deleted: " + str(Temp_Temperature.objects.all()[0]))
    Temp_Temperature.objects.all()[0].delete()
    Temp_Temperature.objects.create(pool_id='1', temp_temperaturelevel=tempData, temp_temperaturedatetime=datetime.datetime.now())
    print("Temp_Temperature Value Added: Enrique Razon Building, " + str(tempData) + ", " + str(datetime.datetime.now()))

def batchCount10Temp():
    temperatureList = Temp_Temperature.objects.all().filter(pool_id = '1')
    tempSum=0
    tempCount=0
    for item in temperatureList:
        tempSum+=item.temp_temperaturelevel
        tempCount+=1
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
        tempStandardDev= decimal.Decimal(tempStandardDev)+tempMean
        Final_Temperature.objects.create(pool_id='1', final_temperaturelevel=tempStandardDev, final_temperaturedatetime=datetime.datetime.now())
        print("Final_Temperature Value Added: Enrique Razon Building, " + str(tempStandardDev) + ", " + str(datetime.datetime.now()))

def count_temp_temperature():
    rc = Temp_Temperature.objects.count()
    return rc

class sensorReading(threading.Thread):

    def run(self):
        pH_batchCount = 0
        turb_batchCount = 0
        temp_batchCount = 0
        while True:
            #query code below
            pH_rowCount = count_temp_ph()
            print("Preliminary Row Count for pH: " + str(pH_rowCount))
            print("Preliminary Batch Count for pH: " + str(pH_batchCount))
            turb_rowCount = count_temp_turbidity()
            print("Preliminary Row Count for Turbidity: " + str(turb_rowCount))
            print("Preliminary Batch Count for Turbidity: " + str(turb_batchCount))
            temp_rowCount = count_temp_temperature()
            print("Preliminary Row Count for Temperature: " + str(temp_rowCount))
            print("Preliminary Batch Count for Temperature: " + str(temp_batchCount))

            #while row and batch NOT 10
            if(pH_rowCount < 10 and pH_batchCount != 10):
                insert_to_temp_pH()
                pH_batchCount += 1
            if(turb_rowCount < 10 and turb_batchCount != 10):
                insert_to_temp_turbidity()
                turb_batchCount += 1
            if(temp_rowCount < 10 and pH_batchCount != 10):
                insert_to_temp_temperature()
                temp_batchCount += 1

            #if rowcount IS 10 and batch NOT 10
            if(pH_rowCount >= 10 and pH_batchCount != 10):
                del_insert_to_temp_pH()
                pH_batchCount += 1
            if(turb_rowCount >= 10 and turb_batchCount != 10):
                del_insert_to_temp_turbidity()
                turb_batchCount += 1
            if(temp_rowCount >= 10 and temp_batchCount != 10):
                del_insert_to_temp_temperature()
                temp_batchCount += 1

            #if row and batch is 10
            if(pH_rowCount >= 10 and pH_batchCount == 10):
                del_insert_to_temp_pH()
                batchCount10pH()
                pH_batchCount = 1
            if(turb_rowCount >= 10 and turb_batchCount == 10):
                del_insert_to_temp_turbidity()
                batchCount10Turbidity()
                turb_batchCount = 1
            if(temp_rowCount >= 10 and temp_batchCount == 10):
                del_insert_to_temp_temperature()
                batchCount10Temp()
                temp_batchCount = 1

            #if rowcount NOT 10 and batch IS 10
            if(pH_rowCount < 10 and pH_batchCount == 10):
                insert_to_temp_pH()
                batchCount10pH()
                pH_batchCount = 1
            if(turb_rowCount < 10 and turb_batchCount == 10):
                insert_to_temp_turbidity()
                batchCount10Turbidity()
                turb_batchCount = 1
            if(temp_rowCount < 10 and temp_batchCount == 10):
                insert_to_temp_temperature()
                batchCount10Temp()
                temp_batchCount = 1

        sleep(180)

sensorRead = sensorReading()
sensorRead.start()

#Sensor Reading end

>>>>>>> 272f9fc85f1de49337d7e3d3996d919cb03e730b
def login(request):
    msg = None
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        userx = authenticate(username=username, password=password)

        if userx is not None:
            userStat =Status.objects.get(id=userx.pk)
            notDeactivated =  Status_Ref.objects.get(pk=1)
            if userx.is_active and userStat.status == notDeactivated:
                auth_login(request, userx)
                usertype = Type.objects.get(user=userx)
                adminType= Usertype_Ref.objects.get(pk=1)
                if usertype.type == adminType:
                    return redirect('/monitoring/index/')

                else:
                    return redirect('/monitoring/index/')


            else:
                msg = 'username or password not correct'
        else:
            messages.error(request,'username or password not correct')
            msg = 'username or password not correct'
            content ={
                'msg' : msg,
            }
            return render(request,'registration/login.html',content)

    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'msg' : msg})


def logout_view(request):
    logout(request)
    return render(request,'registration/logout.html')

@login_required(login_url="/monitoring/login")
def index(request):
    notifications = getNotification(request)
    usertype = Type.objects.get(user=request.user)
    adminType= Usertype_Ref.objects.get(pk=1)
    #notification code
    notifications = getNotification(request)
    if not usertype.type == adminType:
        poolref = Pool.objects.all().order_by('pk')
        #temperature levels
        tempDeviations = []
        tempColors = []
        for poolitem in Pool.objects.all().order_by('pk'):
            temperatureList = Temp_Temperature.objects.all().filter(pool=poolref.get(pk=poolitem.pk))
            tempSum=0
            tempCount=0
            for item in temperatureList:
                tempSum+=item.temp_temperaturelevel
                tempCount+=1
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
                tempStandardDev= decimal.Decimal(tempStandardDev)+tempMean
                tempStandardDev=round(tempStandardDev, 2)
                #color assignment
                if tempStandardDev >= 95:
                    tempColors.append("green")
                elif (tempStandardDev >= 85):
                    tempColors.append("green")
                elif (tempStandardDev >= 80):
                    tempColors.append("yellow")
                elif(tempStandardDev < 80):
                    tempColors.append("red")
                else:
                    tempColors.append("White")
                degreeSign=u'\N{DEGREE SIGN}'
                tempStandardDev=str(tempStandardDev)+degreeSign+'C'
                tempDeviations.append(tempStandardDev)
            else:
                tempColors.append("White")
                tempDeviations.append('No Readings')

        #turbidity levels
        turbidityDeviations = []
        turbidityColors = []
        #standard deviation of turbidity
        for poolitem in Pool.objects.all().order_by('pk'):
            turbidityList = Temp_Turbidity.objects.all().filter(pool=poolref.get(pk=poolitem.pk))

            turbiditySum=0
            turbidityCount=0
            for item in turbidityList:
                turbiditySum+=item.temp_turbiditylevel
                turbidityCount+=1
            if(turbidityCount>0):
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
                turbidityStandardDev=decimal.Decimal(turbidityStandardDev)+turbidityMean
                #color assignment
                if turbidityStandardDev >= 95:
                    turbidityColors.append("green")
                elif (turbidityStandardDev >= 85):
                     turbidityColors.append("green")
                elif (turbidityStandardDev >= 80):
                     turbidityColors.append("yellow")
                elif(turbidityStandardDev < 80):
                     turbidityColors.append("red")
                else:
                    turbidityColors.append("White")
                turbidityStandardDev=str(turbidityStandardDev)+" ntu"
                turbidityDeviations.append(turbidityStandardDev)
            else:
                turbidityColors.append("White")
                turbidityDeviations.append('No Readings')

        #ph level
        phDeviations = []
        phColors = []
        for poolitem in Pool.objects.all().order_by('pk'):
            phList = Temp_Ph.objects.all().filter(pool=poolref.get(pk=poolitem.pk))
            phSum=0
            phCount=0
            for item in phList:
                phSum+=item.temp_phlevel
                phCount+=1
            if(phCount>0):
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
                phStandardDev=decimal.Decimal(phStandardDev)+turbidityMean
                phStandardDev=round(phStandardDev, 1)
                #color assignment
                if phStandardDev >= 7.3 and phStandardDev <=7.5:
                    phColors.append("green")
                elif ((phStandardDev >= 7.1 and phStandardDev <= 7.2) or (phStandardDev >= 7.6 and phStandardDev <= 7.7)):
                     phColors.append("green")
                elif((phStandardDev < 7.1 and phStandardDev > 6.9) or (phStandardDev > 7.7 and phStandardDev < 7.9)):
                     phColors.append("yellow")
                elif(phStandardDev >= 7.9 or phStandardDev <= 6.9):
                     phColors.append("red")
                else:
                    phColors.append("White")
                phDeviations.append(phStandardDev)
            else:
                phDeviations.append('No Readings')
                phColors.append("White")

            #2615.97 - 1175.23 x + 185.315 x^2 - 9.90222 x^3
            chlorineLevels=[]
            chlorineColors=[]
            for item in phDeviations:
                debug=2615.97 - 1175.23*5.57+ 185.315*5.57*5.57 - 9.90222*5.57*5.57*5.57
                try:
                    #multiplier=8
                    chlorine = decimal.Decimal(2615.97)
                    multiplier = item
                    chlorine-= decimal.Decimal(1175.23)*multiplier
                    multiplier*=item
                    chlorine+=decimal.Decimal(185.315)*multiplier
                    multiplier*=item
                    chlorine-=decimal.Decimal(9.90222)*multiplier
                    chlorine = round(chlorine, 1)
                    if chlorine>100:
                        chlorine=100
                    elif chlorine<0:
                        chlorine=0
                    #color assignment
                    if chlorine >= 95:
                        chlorineColors.append("green")
                    elif (chlorine >= 85):
                         chlorineColors.append("green")
                    elif (chlorine >= 80):
                         chlorineColors.append("yellow")
                    elif(chlorine < 80):
                         chlorineColors.append("red")
                    else:
                        chlorineColors.append("White")
                    chlorine=str(chlorine)+'%'
                    chlorineLevels.append(chlorine)
                except:
                    chlorineColors.append("White")
                    chlorineLevels.append('Cannot Compute')
        waterColors = []
        waterQuality=0
        #color assignment
        if waterQuality >= 95:
            waterColors.append("green")
        elif (waterQuality >= 85):
             waterColors.append("green")
        elif (waterQuality >= 80):
             waterColors.append("yellow")
        elif(waterQuality < 80):
             waterColors.append("red")
        else:
            waterColors.append("White")
        content= {
            'debug_check': "",
            'pool':poolref,
            'temperature':tempDeviations,
            'turbidity':turbidityDeviations,
            'ph':phDeviations,
            'chlorine':chlorineLevels,
            'notifications':notifications,
            'color':"green",
            'phColors':phColors,
            'chlorineColors':chlorineColors,
            'turbidityColors':turbidityColors,
            'tempColors':tempColors,
            'waterColors':"white",
        }
        return render(request, 'monitoring/pool technician/home.html', content)

    else:
        return render(request, 'monitoring/pool owner/home-owner.html')



@login_required(login_url="/monitoring/login")
def poolDetails_view(request, poolitem_id):
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
    notifications = getNotification(request)
    if not usertype.type == adminType:
        poolref = Pool.objects.get(id=poolitem_id)
        ph = Final_Ph.objects.all().filter(pool=poolref)
        turbidity = Final_Turbidity.objects.all().filter(pool=poolref)
        temperature = Final_Temperature.objects.all().filter(pool=poolref)
        content= {
            'pool':poolref,
            'ph':ph,
            'turbidity':turbidity,
            'temperature':temperature,
            'notifications':notifications,
        }
        print('wwwwwwwwwew')
        return render(request, 'monitoring/pool technician/pool-stat.html', content)
    else:
        print('yopooooo')
        return render(request, 'monitoring/pool owner/result-not-found.html')




@login_required(login_url="/monitoring/login")
def addUser(request):
    notifications = getNotification(request)
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
    if usertype.type == adminType:
        if request.method == 'POST':
            msg = None
            print('request POST')
            form = SignUpForm(request.POST)
            if form.is_valid():
                print('forms valid')
                form.save()
                print('form1 saved')
                print(form.cleaned_data.get('username'))
                print('newtype saved')
                msg='success'
                form = SignUpForm()
                content={
                    'form':form,
                    'msg' : msg,
                    'notifications':notifications,
                }
                return render(request, 'monitoring/pool owner/add-user.html',content)

            else:
                msg='error'
                content={
                    'form':form,
                    'msg' : msg,
                    'notifications':notifications,
                }
                return render(request, 'monitoring/pool owner/add-user.html',content)

        else:
            form = SignUpForm()
            return render(request, 'monitoring/pool owner/add-user.html',locals())
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def setMaintenance(request):
    notifications = getNotification(request)
    try:
        pools = Pool.objects.all()
        content = {
            'pools':pools,
            'notifications':notifications,
        }
        return render(request, 'monitoring/pool technician/set-maintenance-schedule.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def setMaintenanceCompute(request):
    notifications = getNotification(request)
    try:
        poolPK = request.POST['poolPK']
        dRange = request.POST['dRange']
        tStart = request.POST['tStart']
        tEnd = request.POST['tEnd']
        data = dRange.split("-")
        dStart = data[0]
        dEnd = data[1]
        sDate = datetime.datetime.strptime(dStart, '%m/%d/%Y ').strftime('%Y-%m-%d')
        eDate = datetime.datetime.strptime(dEnd, ' %m/%d/%Y').strftime('%Y-%m-%d')
        poolitem = Pool.objects.get(pk=poolPK)
        phList = Temp_Ph.objects.all().filter(pool=poolitem)
        phSum=0
        phCount=0
        for item in phList:
            phSum+=item.temp_phlevel
            phCount+=1
        if(phCount>0):
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
            phStandardDev=decimal.Decimal(phStandardDev)+phMean
        phLevel =  phStandardDev
        #get gallons
        cubicpool = poolitem.pool_width * poolitem.pool_depth * poolitem.pool_length
        poolGallons = cubicpool * decimal.Decimal(7.5)
        squarefeet= poolitem.pool_length * poolitem.pool_width
        #DE powder computation
        dePowder = squarefeet*decimal.Decimal(.1)
        dePowder = dePowder*decimal.Decimal(.8)
        dePowder = round(dePowder, 1)
        if dePowder > 0:
            dePowderOutput = str(dePowder)+" oz / "
            dePowder =  dePowder * decimal.Decimal(0.0625)
            dePowder = round(dePowder, 2)
            dePowderOutput = dePowderOutput+str(dePowder)+" lbs"
        else:
            dePowderOutput = "No Need"
        #multiplier
        gallons = poolGallons
        multiplier = 0
        sodaAsh=0
        muriaticAcid=0
        chlorine=0

        while gallons >= 5000:
            multiplier+=1
            gallons-=5000

        #soda ash computation
        showButton=1
        if phLevel < 7.4:
            muriaticAcidOutput="No Need"
            if phLevel < 6.7:
                sodaAsh = multiplier * 8
            elif phLevel <= 7:
                sodaAsh = multiplier * 6
            elif phLevel <= 7.2:
                sodaAsh = multiplier * 4
            elif phLevel <= 7.4:
                sodaAsh = multiplier * 3
            sodaAsh = round(sodaAsh, 1)
            if(sodaAsh>0):
                sodaAshOutput = str(sodaAsh)+" oz / "
                sodaAsh = sodaAsh*decimal.Decimal(0.0625)
                sodaAsh = round(sodaAsh, 2)
                sodaAshOutput = str(sodaAshOutput)+" lbs"
            else:
                sodaAshOutput="No Need"
        elif phLevel > 7.4:#muriatic acid computation
            sodaAshOutput="No Need"
            if phLevel > 8.4:
                muriaticAcid = multiplier * 16
            elif phLevel >= 8:
                muriaticAcid = multiplier * 12
            elif phLevel >= 7.8:
                muriaticAcid = multiplier * 8
            elif phLevel > 7.5:
                muriaticAcid = multiplier * 6
            muriaticAcid = round(muriaticAcid, 1)
            if muriaticAcid > 0:
                muriaticAcidOutput = str(muriaticAcid)+" oz / "
                muriaticAcid = muriaticAcid * decimal.Decimal(0.03125)
                muriaticAcid = round(muriaticAcid, 2)
                muriaticAcidOutput = muriaticAcidOutput + str(muriaticAcid)+" qts"
            else:
                muriaticAcidOutput = "No need"
        else:
            print('water is balanced')
            sodaAshOutput="No Need"
            muriaticAcidOutput="No Need"
            dePowderOutput="No Need"
            muriaticAcidOutput="No Need"
            showButton=0
        #no chlorine computation
        content = {
            'debugger':"",
            'poolPK':poolPK,
            'dateStart':sDate,
            'dateEnd':eDate,
            'timeStart':tStart,
            'timeEnd':tEnd,
            'sodaAsh':sodaAshOutput,
            'muriaticAcid':muriaticAcidOutput,
            'dePowder':dePowderOutput,
            'notifications':notifications,
            'color':"fill:green;stroke:black;stroke-width:1;opacity:0.5",
            'showButton':showButton,
        }
        return render(request, 'monitoring/pool technician/set-maintenance-schedule-compute.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def submitMaintenanceRequest(request):
    notifications = getNotification(request)
    if 0==0:
        poolPK = request.POST['poolPK']
        dateStart = request.POST['dateStart']
        dateEnd = request.POST['dateEnd']
        timeStart = request.POST['timeStart']
        timeEnd = request.POST['timeEnd']
        bakingSoda = request.POST['sodaAsh']
        muriaticAcid = request.POST['muriaticAcid']
        dePowder = request.POST['dePowder']
        poolitem = Pool.objects.get(pk=poolPK)
        ms = MaintenanceSchedule(
            user=request.user,
            pool=poolitem,
            estimatedStart=timeStart,
            estimatedEnd=timeEnd,
            est_chlorine=0,
            est_muriatic=muriaticAcid,
            est_depowder=dePowder,
            est_bakingsoda=bakingSoda,
            act_chlorine=0,
            act_muriatic=0,
            act_depowder=0,
            act_bakingsoda=0
        )
        ms.save()
        content={
            'debugger':"",
            'message':"Maintenance Schedule has been set!",
            'notifications':notifications,
        }
        return render(request, 'monitoring/pool technician/success.html', content)
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def searchPT(request):
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
    notifications = getNotification(request)
    if usertype.type == adminType:
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
                'notifications':notifications,
            }
        return render(request, 'monitoring/pool owner/search-technician.html', content,)
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')



@login_required(login_url="/monitoring/login")
def profile(request,item_id):
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
    notifications = getNotification(request)
    if usertype.type == adminType:
        user = User.objects.get(id=item_id)
        msg = None
        content = None
        status = user.status.status
        active= Status_Ref.objects.get(pk=1)
        btnFlag = None
        #lagay condition kapag hindi active account = pwede ireactivate
        if status == active:
            btnFlag = 'Active'
            if (request.method == 'POST' ) & ('password' in request.POST):
                form2 = ChangePasswordForm(user, request.POST)
                form1 =EditDetailsForm(request.POST)
                if form2.is_valid():
                    u = form2.save()
                    alert = 'success'
                    update_session_auth_hash(request, u)
                    content = {
                        'item_id': user,
                        'form2': form2,
                        'form1': form1,
                        'msg':alert,
                        'status':status,
                        'btnFlag':btnFlag,
                        'notifications':notifications,
                    }

            elif (request.method == 'POST' ) & ('editDetails' in request.POST):
                form1 =EditDetailsForm(request.POST)
                form2 = ChangePasswordForm(user, request.POST)
                if form1.is_valid():
                    print('uuuuuup')
                    fname = request.POST.get('first_name')
                    lname = request.POST.get('last_name')
                    user.first_name=fname
                    user.last_name=lname
                    user.save()
                    alert = 'success'
                    content = {
                        'item_id': user,
                        'form1': form1,
                        'form2': form2,
                        'msg':alert,
                        'status':status,
                        'btnFlag':btnFlag,
                        'notifications':notifications,
                    }
            elif (request.method == 'POST' ) & ('deactivate' in request.POST):
                Status.objects.filter(pk=user.pk).update(status=2)

                return render(request, 'monitoring/pool owner/home-owner.html', content)


            else:
                form1 = EditDetailsForm()
                form2 = ChangePasswordForm(request.user)
                content = {
                    'item_id': user,
                    'form1': form1,
                    'form2': form2,
                    'status':status,
                    'btnFlag':btnFlag,
                    'notifications':notifications,
                }
            return render(request, 'monitoring/pool owner/technician-profile.html', content)
        else:
            if (request.method == 'POST' ) & ('activate' in request.POST):
                print('nyeaaaaaammmm')
                Status.objects.filter(pk=user.pk).update(status=1)
                btnFlag = 'Inactive'
                content = {
                    'item_id': user,
                    'status':status,
                    'btnFlag':btnFlag,
                    'notifications':notifications,
                    }
                return render(request, 'monitoring/pool owner/home-owner.html', content)
            else:
                btnFlag = 'Inactive'
                content = {
                    'item_id': user,
                    'status':status,
                    'btnFlag':btnFlag,
                    'notifications':notifications,
                    }

        return render(request, 'monitoring/pool owner/technician-profile.html', content)
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')



@login_required(login_url="/monitoring/login")
def editDetails(request):
    notifications = getNotification(request)
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
    if usertype.type == adminType:
        current_user = request.user
        curr_fname = request.user.first_name
        curr_lname = request.user.last_name
        alert = None
        content = None
        user = User.objects.get(id=current_user.id)
        if (request.method == 'POST' ) & ('password' in request.POST):
            form2 = ChangePasswordForm(current_user, request.POST)
            if form2.is_valid():
                userForm = form2.save()
                alert = 'Password Successfully Changed.'
                update_session_auth_hash()
                content = {
                    'form2': form2,
                    'alertmsg':alert,
                    'curr_fname' : curr_fname,
                    'curr_lname' : curr_lname,
                    'username' : current_user.username,
                    'notifications':notifications,
                }
                return render(request, 'monitoring/pool technician/edit-details.html',content)
        elif (request.method == 'POST' ) & ('editDetails' in request.POST):
            form1 =EditDetailsForm(request.POST)
            if form1.is_valid():
                fname = request.POST.get('first_name')
                lname = request.POST.get('last_name')
                user.first_name=fname
                user.last_name=lname
                user.save()
                alert = 'Details Successfully Changed.'
                content = {
                    'form1': form1,
                    'alertmsg':alert,
                    'curr_fname' : fname,
                    'curr_lname' : lname,
                    'username' : current_user.username,
                    'notifications':notifications,
                }
                return render(request, 'monitoring/pool technician/edit-details.html',content)
        elif (request.method == 'POST' ) & ('deactivate' in request.POST):
            print('suhhh')
            print(current_user)
            userStat =Status.objects.get(id=current_user.pk)
            print(userStat.status)
            Status.objects.filter(pk=request.user.id).update(status=2)
            logout(request)
            return render(request,'registration/logout.html')
        else:
            form1 = EditDetailsForm()
            form2 = ChangePasswordForm(current_user)
            content = {
                'form1': form1,
                'form2': form2,
                'curr_fname' : curr_fname,
                'curr_lname' : curr_lname,
                'username' : current_user.username,
                'notifications':notifications,
            }


        return render(request, 'monitoring/pool technician/edit-details.html',content)
    elif not usertype.type == adminType:
        current_user = request.user
        curr_fname = request.user.first_name
        curr_lname = request.user.last_name
        alert = None
        content = None
        user = User.objects.get(id=current_user.id)
        if (request.method == 'POST' ) & ('password' in request.POST):
            form1 =EditDetailsForm(request.POST)
            form2 = ChangePasswordForm(current_user, request.POST)
            if form2.is_valid():
                userForm = form2.save()
                alert = 'Password Successfully Changed.'
                update_session_auth_hash(request, userForm)
                content = {
                    'form2': form2,
                    'form1': form1,
                    'alertmsg':alert,
                    'curr_fname' : curr_fname,
                    'curr_lname' : curr_lname,
                    'username' : current_user.username,
                    'notifications':notifications,
                }
        elif (request.method == 'POST' ) & ('editDetails' in request.POST):
            form1 =EditDetailsForm(request.POST)
            form2 = ChangePasswordForm(current_user, request.POST)
            if form1.is_valid():
                fname = request.POST.get('first_name')
                lname = request.POST.get('last_name')
                user.first_name=fname
                user.last_name=lname
                user.save()
                alert = 'Details Successfully Changed.'
                content = {
                    'form1': form1,
                    'form2': form2,
                    'alertmsg':alert,
                    'curr_fname' : fname,
                    'curr_lname' : lname,
                    'username' : current_user.username,
                    'notifications':notifications,
                }
        elif (request.method == 'POST' ) & ('deactivate' in request.POST):
            print('suhhh')
            print(current_user)
            userStat =Status.objects.get(id=current_user.pk)
            print(userStat.status)
            Status.objects.filter(pk=request.user.id).update(status=2)
            logout(request)
            return render(request,'registration/logout.html')
        else:
            form1 = EditDetailsForm()
            form2 = ChangePasswordForm(current_user)
            content = {
                'form1': form1,
                'form2': form2,
                'curr_fname' : curr_fname,
                'curr_lname' : curr_lname,
                'username' : current_user.username,
                'notifications':notifications,
            }
        return render(request, 'monitoring/pool technician/edit-details.html',content)
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')

@login_required(login_url="/monitoring/login")
def filterPoolStat(request):
    notifications = getNotification(request)
    try:
        poolPk = request.POST['poolPK']
        startDate = request.POST['dateStart']
        endDate = request.POST['dateEnd']
        poolref = Pool.objects.get(id=poolPk)
        xDate = datetime.datetime.strptime(startDate, '%B %d, %Y ').strftime('%Y-%m-%d')
        yDate = datetime.datetime.strptime(endDate, ' %B %d, %Y').strftime('%Y-%m-%d')
        xDate = str(xDate)+" 00:00"
        yDate = str(yDate)+" 00:00"
        display = xDate+" - "+yDate
        ph = Final_Ph.objects.all().filter(pool=poolref, final_phdatetime__range=[xDate, yDate])
        turbidity = Final_Turbidity.objects.all().filter(pool=poolref, final_turbiditydatetime__range=[xDate, yDate])
        temperature = Final_Temperature.objects.all().filter(pool=poolref, final_temperaturedatetime__range=[xDate, yDate])
        content= {
            'debug_check': display,
            'pool':poolref,
            'ph':ph,
            'turbidity':turbidity,
            'temperature':temperature,
            'notifications':notifications,
        }
        return render(request, 'monitoring/pool technician/pool-stat.html', content)
    except:
        try:
            poolPk = request.POST['poolPK']
            poolref = Pool.objects.get(id=poolPk)
            now = datetime.datetime.now()
            endNow = datetime.datetime.now() + datetime.timedelta(days=1)
            xDate = now.strftime('%Y-%m-%d')
            yDate = now.strftime('%Y-%m-%d')
            xDate = str(xDate)+" 00:00"
            yDate = str(yDate)+" 00:00"
            display = str(now)+" - "+str(endNow)
            ph = Final_Ph.objects.all().filter(pool=poolref, final_phdatetime__range=[xDate, yDate])
            turbidity = Final_Turbidity.objects.all().filter(pool=poolref, final_turbiditydatetime__range=[xDate, yDate])
            temperature = Final_Temperature.objects.all().filter(pool=poolref, final_temperaturedatetime__range=[xDate, yDate])
            content= {
                'debug_check': display,
                'pool':poolref,
                'ph':ph,
                'turbidity':turbidity,
                'temperature':temperature,
                'notifications':notifications,
            }
            return render(request, 'monitoring/pool technician/pool-stat.html', content)
        except:
            return render(request, 'monitoring/pool owner/result-not-found.html')

@login_required(login_url="/monitoring/login")
def viewMaintenance(request):
    notifications = getNotification(request)
    try:
        maintenanceSchedule = MaintenanceSchedule.objects.all()
        #"October 13, 2014 11:13:00"
        users=[]
        startSchedules=[]
        endSchedules=[]
        colors=[]
        eventids=[]
        for event in maintenanceSchedule:
            users.append(event.user)
            if event.scheduledStart == None:
                b=event.estimatedStart
            else:
                b=event.scheduledStart
            dString=str(b.month)+"/"+str(b.day)+"/"+str(b.year)+" "+str(b.hour)+":"+str(b.minute)+":00"
            #'7/31/2018 1:30:00' - #"October 13, 2014 11:13:00"
            startDate = datetime.datetime.strptime(dString, '%m/%d/%Y %H:%M:00').strftime('%B %d %Y %H:%M:00')
            if event.scheduledEnd == None:
                b=event.estimatedEnd
            else:
                b=event.scheduledEnd
            dString=str(b.month)+"/"+str(b.day)+"/"+str(b.year)+" "+str(b.hour)+":"+str(b.minute)+":00"
            #'7/31/2018 1:30:00' - #"October 13, 2014 11:13:00"
            endDate = datetime.datetime.strptime(dString, '%m/%d/%Y %H:%M:00').strftime('%B %d %Y %H:%M:00')
            #Notified Scheduled Accomplished
            if event.status == "Notified":
                color="#f39c12"
            elif event.status == "Scheduled":
                color="#0073b7"
            elif event.status == "Accomplished":
                color="#00a65a"
            elif event.status == "Late":
                color="red"
            #appends
            users.append(event.user)
            startSchedules.append(startDate)
            endSchedules.append(endDate)
            colors.append(color)
            eventids.append(event.id)
        content={
            'debugger': "",
            'titles': users,
            'starts': startSchedules,
            'ends': endSchedules,
            'backgroundColors': colors,
            'ids': eventids,
            'notifications':notifications,
        }
        return render(request, 'monitoring/pool technician/view-all-maintenance-schedule.html', content)
    except:
        content = {
            "debugger":""
        }
        return render(request, 'monitoring/pool owner/result-not-found.html', content)

@login_required(login_url="/monitoring/login")
def notFound(request):
    return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def personnel(request):
    return render(request, 'monitoring/pool owner/personnel-efficiency.html')


@login_required(login_url="/monitoring/login")
def maintenanceDetails(request, schedule_id):
    notifications = getNotification(request)
    try:
        actual=0
        item = MaintenanceSchedule.objects.get(id=schedule_id)
        pool = item.pool
        poolPK=pool.pk
        if item.scheduledStart == None:
            fromDate=item.estimatedStart
            toDate=item.estimatedEnd
        else:
            fromDate=item.scheduledStart
            toDate=item.scheduledEnd
        if item.status == "Accomplished":
            muriaticAcid=item.act_muriatic
            sodaAsh=item.act_bakingsoda
            dePowder=item.act_depowder
            chlorine=item.act_chlorine
            actual=1
            showButton=0
        else:
            #OLD
            #muriaticAcid=item.est_muriatic
            #sodaAsh=item.est_bakingsoda
            #dePowder=item.est_depowder
            #chlorine=item.est_chlorine
            #NEW
            poolitem = Pool.objects.get(pk=poolPK)
            phList = Temp_Ph.objects.all().filter(pool=poolitem)
            phSum=0
            phCount=0
            phStandardDev="No Value"
            for phItem in phList:
                phSum+=phItem.temp_phlevel
                phCount+=1
            if(phCount>0):
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
                phStandardDev=decimal.Decimal(phStandardDev)+phMean
            phLevel =  phStandardDev
            #get gallons
            cubicpool = poolitem.pool_width * poolitem.pool_depth * poolitem.pool_length
            poolGallons = cubicpool * decimal.Decimal(7.5)
            squarefeet= poolitem.pool_length * poolitem.pool_width
            #DE powder computation
            dePowder = squarefeet*decimal.Decimal(.1)
            dePowder = dePowder*decimal.Decimal(.8)
            dePowder = round(dePowder, 1)
            if dePowder > 0:
                dePowderOutput = str(dePowder)+" oz / "
                dePowder =  dePowder * decimal.Decimal(0.0625)
                dePowder = round(dePowder, 2)
                dePowderOutput = dePowderOutput+str(dePowder)+" lbs"
                dePowder=dePowderOutput
            else:
                dePowderOutput = "No Need"
                dePowder=dePowderOutput
            #multiplier
            gallons = poolGallons
            multiplier = 0
            sodaAsh=0
            muriaticAcid=0
            chlorine=0

            while gallons >= 5000:
                multiplier+=1
                gallons-=5000

            #soda ash computation
            showButton=1
            if phLevel < 7.4:
                muriaticAcidOutput="No Need"
                if phLevel < 6.7:
                    sodaAsh = multiplier * 8
                elif phLevel <= 7:
                    sodaAsh = multiplier * 6
                elif phLevel <= 7.2:
                    sodaAsh = multiplier * 4
                elif phLevel <= 7.4:
                    sodaAsh = multiplier * 3
                sodaAsh = round(sodaAsh, 1)
                if(sodaAsh>0):
                    sodaAshOutput = str(sodaAsh)+" oz / "
                    sodaAsh = sodaAsh*decimal.Decimal(0.0625)
                    sodaAsh = round(sodaAsh, 2)
                    sodaAshOutput = str(sodaAshOutput)+" lbs"
                    sodAsh=sodaAshOutput
                else:
                    sodaAshOutput="No Need"
                    sodAsh=sodaAshOutput
            elif phLevel > 7.4:#muriatic acid computation
                sodaAshOutput="No Need"
                sodAsh=sodaAshOutput
                if phLevel > 8.4:
                    muriaticAcid = multiplier * 16
                elif phLevel >= 8:
                    muriaticAcid = multiplier * 12
                elif phLevel >= 7.8:
                    muriaticAcid = multiplier * 8
                elif phLevel > 7.5:
                    muriaticAcid = multiplier * 6
                muriaticAcid = round(muriaticAcid, 1)
                if muriaticAcid > 0:
                    muriaticAcidOutput = str(muriaticAcid)+" oz / "
                    muriaticAcid = muriaticAcid * decimal.Decimal(0.03125)
                    muriaticAcid = round(muriaticAcid, 2)
                    muriaticAcidOutput = muriaticAcidOutput + str(muriaticAcid)+" qts"
                    muriaticAcid=muriaticAcidOutput
                else:
                    muriaticAcidOutput = "No need"
                    muriaticAcid=muriaticAcidOutput
            #END OF NEW
            if item.status == "Unfinished":
                showButton=0
            else:
                showButton=1
        poolname=item.pool
        status=item.status
        content={
            'debugger':"",
            'schedule_id':schedule_id,
            'poolname':poolname,
            'fromDate':fromDate,
            'toDate':toDate,
            'muriaticAcid':muriaticAcid,
            'sodaAsh':sodaAsh,
            'dePowder':dePowder,
            'chlorine':chlorine,
            'showButton':showButton,
            'status':status,
            'notifications':notifications,
            'actual':actual,
        }
        #insert notification here content.append/content.add(function())
        return render(request, 'monitoring/pool technician/maintenance-details.html', content)
    except:
        content={
            "backUrl":"monitoring:viewMaintenance"
        }
        return render(request, 'monitoring/pool owner/result-not-found.html', content)


@login_required(login_url="/monitoring/login")
def maintenanceDetailsChemicals(request):
    notifications = getNotification(request)
    try:
        maintenanceId=request.POST['maintenanceid']
        item = MaintenanceSchedule.objects.get(id=maintenanceId)
        poolname=item.pool
        fromDate=item.estimatedStart
        toDate=item.estimatedEnd
        muriaticAcid=item.est_muriatic
        sodaAsh=item.est_bakingsoda
        dePowder=item.est_depowder
        chlorine=item.est_chlorine
        content={
            'debugger':dePowder,
            'schedule_id':maintenanceId,
            'poolname':poolname,
            'fromDate':fromDate,
            'toDate':toDate,
            'muriaticAcid':muriaticAcid,
            'sodaAsh':sodaAsh,
            'dePowder':dePowder,
            'chlorine':chlorine,
            'notifications':notifications,
        }
        return render(request, 'monitoring/pool technician/maintenance-details-chemicals.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')

@login_required(login_url="/monitoring/login")
def submitMaintenanceChemicals(request):
    notifications = getNotification(request)
    try:
        maintenanceId=request.POST['maintenanceId']
        muriaticAcid=request.POST['muriaticAcid']
        sodaAsh=request.POST['sodaAsh']
        dePowder=request.POST['dePowder']
        chlorine=request.POST['chlorine']
        item = MaintenanceSchedule.objects.get(id=maintenanceId)
        item.act_chlorine = decimal.Decimal(chlorine)
        item.act_muriatic = decimal.Decimal(muriaticAcid)
        item.act_depowder = decimal.Decimal(dePowder)
        item.act_bakingsoda = decimal.Decimal(sodaAsh)
        item.status = "Accomplished"
        item.save()
        content={
            'display':"Schedule Complete",
            'notifications':notifications,
        }
        return render(request, 'monitoring/success/success.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def computeChlorine(request):
    notifications = getNotification(request)
    try:
        poolref = Pool.objects.all()
        dc=request.POST['dchlorineLevel']
        ac=request.POST['chlorineLevel']
        poolPK=request.POST['poolPK']
        multiplier=decimal.Decimal(dc) - decimal.Decimal(ac)
        if multiplier<0:
            multiplier=0
        multiplier=decimal.Decimal(multiplier)*decimal.Decimal(0.00013)
        poolitem = Pool.objects.get(id=poolPK)
        cubicpool = poolitem.pool_width * poolitem.pool_depth * poolitem.pool_length
        gallons = cubicpool * decimal.Decimal(7.5)
        chlorine=0
        chlorine=multiplier*gallons
        chlorine=round(chlorine, 1)
        display= str(chlorine) +" ounces of chlorine was successfully added on "+poolitem.pool_location+" pool."
        content={
            'pools':poolref,
            'display':display,
            'notifications':notifications,
        }
        return render(request, 'monitoring/pool technician/chlorine-compute.html', content)
    except:
        try:
            pools = Pool.objects.all()
            content={
                'pools':pools,
                'notifications':notifications,
            }
            return render(request, 'monitoring/pool technician/chlorine-compute.html', content)
        except:
            return render(request, 'monitoring/pool owner/result-not-found.html')

@login_required(login_url="/monitoring/login")
def poolTechList(request):
    return render(request, 'monitoring/pool owner/view-pool-technicians.html')

@login_required(login_url="/monitoring/login")
def success(request):
    return render(request, 'monitoring/success/success.html')

@login_required(login_url="/monitoring/login")
def getNotification(request):
    notifications = Notification_Table.objects.all().filter(user=request.user)
    return notifications

def getNotification(request):
    notifications = Notification_Table.objects.all().filter(user=request.user)
    return notifications

@login_required(login_url="/monitoring/login")
def success(request):
    return render(request, 'monitoring/success/success.html')

@login_required(login_url="/monitoring/login")
def personnelEfficiency(request):
    return render(request, 'monitoring/pool owner/personnel-efficiency-report.html')

@login_required(login_url="/monitoring/login")
def chemicalConsumption(request):
    return render(request, 'monitoring/pool owner/chemical-consumption-report.html')


@login_required(login_url="/monitoring/login")
def addPool(request):
    return render(request, 'monitoring/pool owner/add-pool.html')
