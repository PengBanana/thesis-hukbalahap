from django.shortcuts import render, get_object_or_404,redirect
from .models import Pool, Usertype_Ref, User,Type, Temp_Turbidity, Temp_Temperature, Temp_Ph, Final_Turbidity, Final_Temperature, Final_Ph, Status, Status_Ref, MaintenanceSchedule
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
#Import for Sensor Reading
import threading
import time
#import spidev
import datetime
from time import sleep
#import numpy as np
#import Adafruit_GPIO.SPI as SPI
#import Adafruit_MCP3008

#end of import
#Sensor Reading Start
SPI_PORT   = 0
SPI_DEVICE = 0
#mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
turbidityChannel = 0
phChannel = 0
sleepTime = 2
ctr = 0
arrayLength = 40
printInterval = .800
samplingInterval = 20

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
    print ("na average na")
    return avg

class TurbiditySensor(threading.Thread):

    def run(self):
        while True:
            x = voltArray(arrayLength, mcp, phChannel)
            finalVoltage = averageVolt(x, arrayLength)*5.0/1024
            print(finalVoltage)
            ctr =0
            print("pH Value :" + str(1.5*finalVoltage))
            ctr = ctr+1
            sleep(5)

turbidity = TurbiditySensor()
turbidity.start()

#Sensor Reading end
def login(request):
    msg = None
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            userStat =Status.objects.get(id=user.pk)
            notDeactivated =  Status_Ref.objects.get(pk=1)
            if user.is_active and userStat.status == notDeactivated:
                auth_login(request, user)
                usertype = Type.objects.get(pk=user.pk)
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
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
    if not usertype.type == adminType:
        poolref = Pool.objects.all().order_by('pk')
        #temperature levels
        tempDeviations = []
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
                degreeSign=u'\N{DEGREE SIGN}'
                tempStandardDev=str(tempStandardDev)+degreeSign+'C'
                tempDeviations.append(tempStandardDev)
            else:
                tempDeviations.append('No Readings')

        #turbidity levels
        turbidityDeviations = []
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
                turbidityStandardDev=str(turbidityStandardDev)+" ntu"
                turbidityDeviations.append(turbidityStandardDev)
            else:
                turbidityDeviations.append('No Readings')

        #ph level
        phDeviations = []
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
                phDeviations.append(phStandardDev)
            else:
                phDeviations.append('No Readings')

            #2615.97 - 1175.23 x + 185.315 x^2 - 9.90222 x^3
            chlorineLevels=[]
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
                    chlorine = round(chlorine, 2)
                    if chlorine>100:
                        chlorine=100
                    elif chlorine<0:
                        chlorine=0
                    chlorine=str(chlorine)+'%'
                    chlorineLevels.append(chlorine)
                except:
                    chlorineLevels.append('Cannot Compute')
        content= {
            'debug_check': '',
            'pool':poolref,
            'temperature':tempDeviations,
            'turbidity':turbidityDeviations,
            'ph':phDeviations,
            'chlorine':chlorineLevels,
        }

        return render(request, 'monitoring/pool technician/home.html', content)

    else:
        return render(request, 'monitoring/pool owner/home-owner.html')



@login_required(login_url="/monitoring/login")
def poolDetails_view(request, poolitem_id):
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
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
        }
        print('wwwwwwwwwew')
        return render(request, 'monitoring/pool technician/pool-stat.html', content)
    else:
        print('yopooooo')
        return render(request, 'monitoring/pool owner/result-not-found.html')




@login_required(login_url="/monitoring/login")
def addUser(request):
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
                }
                return render(request, 'monitoring/pool owner/add-user.html',content)

            else:
                msg='error'
                content={
                    'form':form,
                    'msg' : msg,
                }
                return render(request, 'monitoring/pool owner/add-user.html',content)

        else:
            form = SignUpForm()
            return render(request, 'monitoring/pool owner/add-user.html',locals())
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def setMaintenance(request):
    try:
        pools = Pool.objects.all()
        content = {
            'pools':pools,
        }
        return render(request, 'monitoring/pool technician/set-maintenance-schedule.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def setMaintenanceCompute(request):
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
        dePowder = round(dePowder, 2)
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
        if phLevel < 7.4:
            if phLevel < 6.7:
                sodaAsh = multiplier * 8
            elif phLevel <= 7:
                sodaAsh = multiplier * 6
            elif phLevel <= 7.2:
                sodaAsh = multiplier * 4
            elif phLevel <= 7.4:
                sodaAsh = multiplier * 3
            sodaAsh = round(sodaAsh, 2)
        elif phLevel > 7.4:#muriatic acid computation
            if phLevel > 8.4:
                muriaticAcid = multiplier * 16
            elif phLevel >= 8:
                muriaticAcid = multiplier * 12
            elif phLevel >= 7.8:
                muriaticAcid = multiplier * 8
            elif phLevel > 7.5:
                muriaticAcid = multiplier * 6
            muriaticAcid = round(muriaticAcid, 2)
        else:
            print('water is balanced')
            sodaAsh=0
            muriaticAcid=0
            dePowder=0
        #no chlorine computation
        content = {
            'debugger':"",
            'poolPK':poolPK,
            'dateStart':sDate,
            'dateEnd':eDate,
            'timeStart':tStart,
            'timeEnd':tEnd,
            'sodaAsh':sodaAsh,
            'muriaticAcid':muriaticAcid,
            'dePowder':dePowder,
        }
        return render(request, 'monitoring/pool technician/set-maintenance-schedule-compute.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def submitMaintenanceRequest(request):
    try:
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
            'message':"Maintenance Schedule has been set!"
        }
        return render(request, 'monitoring/pool technician/success.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def searchPT(request):
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
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
            }
        return render(request, 'monitoring/pool owner/search-technician.html', content,)
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')



@login_required(login_url="/monitoring/login")
def profile(request,item_id):
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
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

                    }
                return render(request, 'monitoring/pool owner/home-owner.html', content)
            else:
                btnFlag = 'Inactive'
                content = {
                    'item_id': user,
                    'status':status,
                    'btnFlag':btnFlag,

                    }

        return render(request, 'monitoring/pool owner/technician-profile.html', content)
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')



@login_required(login_url="/monitoring/login")
def editDetails(request):
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

            }


        return render(request, 'monitoring/pool technician/edit-details.html',content)
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def filterPoolStat(request):
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
            }
            return render(request, 'monitoring/pool technician/pool-stat.html', content)
        except:
            return render(request, 'monitoring/pool owner/result-not-found.html')

@login_required(login_url="/monitoring/login")
def viewMaintenance(request):
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
    try:
        item = MaintenanceSchedule.objects.get(id=schedule_id)
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
            showButton=0
        else:
            muriaticAcid=item.est_muriatic
            sodaAsh=item.est_bakingsoda
            dePowder=item.est_depowder
            chlorine=item.est_chlorine
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
            'status':status
        }
        #insert notification here content.append/content.add(function())
        return render(request, 'monitoring/pool technician/maintenance-details.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def maintenanceDetailsChemicals(request):
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
        }
        return render(request, 'monitoring/pool technician/maintenance-details-chemicals.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')

@login_required(login_url="/monitoring/login")
def submitMaintenanceChemicals(request):
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
            'display':"Schedule Complete"
        }
        return render(request, 'monitoring/success/success.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def computeChlorine(request):
    try:
        pools = Pool.objects.all()
        content={
            'pools':pools,
        }
        return render(request, 'monitoring/pool technician/chlorine-compute.html', content)
    except:
        return render(request, 'monitoring/pool owner/result-not-found.html')

@login_required(login_url="/monitoring/login")
def displayChlorineChemical(request):
    display = None
    try:
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
        chlorine=round(chlorine, 2)
        display= str(chlorine) +" ounces of chlorine was successfully added on "+poolitem.pool_location+" pool."
        content={
            'display':display,
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
def success(request):
    return render(request, 'monitoring/success/success.html')


@login_required(login_url="/monitoring/login")
def personnelEfficiency(request):
    return render(request, 'monitoring/pool owner/personnel-efficiency-report.html')



@login_required(login_url="/monitoring/login")
def chemicalConsumption(request):
    return render(request, 'monitoring/pool owner/chemical-consumption-report.html')
