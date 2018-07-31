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
    if 0==0:
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
    else:
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
def finishMaintenance(request):
    return render(request, 'monitoring/pool technician/finish-maintenance-schedule.html')


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
        if (request.method == 'POST' ) & ('password' in request.POST):
            form2 = ChangePasswordForm(user, request.POST)
            if form2.is_valid():
                form2.save()
                alert = 'success'

                content = {
                    'item_id': user,
                    'form2': form2,
                    'msg':alert,

                }

        elif (request.method == 'POST' ) & ('editDetails' in request.POST):
            form1 =EditDetailsForm(request.POST)
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
                    'msg':alert,

                }
        elif (request.method == 'POST' ) & ('deactivate' in request.POST):
            Status.objects.filter(pk=user.pk).update(status=2)


        else:
            form1 = EditDetailsForm()
            form2 = ChangePasswordForm(request.user)
            content = {
                'item_id': user,
                'form1': form1,
                'form2': form2,

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
                update_session_auth_hash(request, userForm)


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
                form1.first_name = manu
                alert = 'Details Successfully Changed.'
                content = {
                    'form1': form1,
                    'alertmsg':alert,
                    'curr_fname' : curr_fname,
                    'curr_lname' : curr_lname,
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
        if(0==0):
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
        else:
            return render(request, 'monitoring/pool owner/result-not-found.html')

@login_required(login_url="/monitoring/login")
def viewMaintenance(request):
    maintenanceSchedule = MaintenanceSchedule.objects.all()
    #"October 13, 2014 11:13:00"
    users=[]
    schedules=[]
    colors=[]
    eventids=[]
    for event in maintenanceSchedule:
        if event.scheduledStart == None:
            users.append(event.user)
            schedules.append("")
            colors.append("")
            eventids.append(event.id)
    content={
        'debugger': "",
        'calendar': "maintenanceSchedule",
    }
    return render(request, 'monitoring/pool technician/view-all-maintenance-schedule.html', content)


@login_required(login_url="/monitoring/login")
def notFound(request):
    return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def personnel(request):
    return render(request, 'monitoring/pool owner/personnel-efficiency.html')


@login_required(login_url="/monitoring/login")
def maintenanceDetails(request):
    return render(request, 'monitoring/pool technician/maintenance-details.html')


@login_required(login_url="/monitoring/login")
def maintenanceDetailsChemicals(request):
    return render(request, 'monitoring/pool technician/maintenance-details-chemicals.html')
