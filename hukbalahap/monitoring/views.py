from django.shortcuts import render, get_object_or_404,redirect
from .models import Pool, Usertype_Ref, Type, Status_Ref, Status, MaintenanceSchedule, Temp_Turbidity, Temp_Temperature, Temp_Ph, Final_Turbidity, Final_Temperature, Final_Ph, Chlorine_Effectiveness, Notification_Table, uPool, Chemical_Price_Reference, MobileNumber, ipaddress_ref
from .forms import SignUpForm, SignUpType, Pool,EditDetailsForm,ChangePasswordForm,RegisterPool
from django.views.generic import TemplateView
from django.db.models import Q
from django.db.models import Sum, Count
from django.contrib.auth.models import User
import math, decimal, datetime
from django.contrib.auth import login as auth_login, authenticate, update_session_auth_hash,logout
from django.contrib.auth.views import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import timedelta

#email api imports
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
from httplib2 import Http
from base64 import urlsafe_b64encode

#checkerimports
import ipaddress
import socket

#email api code start
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://mail.google.com/'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  encoded_message = urlsafe_b64encode(message.as_bytes())
  return {'raw': encoded_message.decode()}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message ID: %s' % message['id'])
    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)
#email api code end

#start of import by migs and  francis###
import threading, time, numpy as np, os, sqlite3
from time import sleep
import sqlite3
import socket
#end of import

turbidityChannel = 1
phChannel = 0
sleepTime = 2
ctr = 0
arrayLength = 60
printInterval = .800
samplingInterval = 20
ipAddress = 0
sensorStart = False
assignedPoolID = 0
ipExists = False


#insert checker if exist
ipobjects = ipaddress_ref.objects.all()
poolobjects = Pool.objects.all()

def getLocalIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    #print(s.getsockname()[0])
    ipadd = s.getsockname()[0]
    s.close()
    return ipadd

ipAddress = getLocalIp()

def insertIP(ip):
    ipaddress_ref.objects.create(ipaddress = ip)

for x in ipobjects:
    if x.ipaddress == ipAddress:
        ipExists = True
    else:
        ipExists = False
print("after for loop ip exists = " + str(ipExists))

#####################################
def getPoolID(ipAddress):
    ipAdd = ipAddress
    ctr = 1
    arraySize = Pool.objects.count()
    poolIdKey = 0
    if arraySize > 0:
        while(ctr <= arraySize):
            x = str(poolobjects.get(pk = ctr).pool_ip)
            if x == ipAdd:
                print("IP Addresses are the same!")
                poolIdKey = ctr
            else:
                print("IP Address at Counter: " + str(ctr) + " are not the same")
            ctr = ctr + 1
    else:
        print("There is no pool present in the database")
    return poolIdKey

#######################################
assignedPoolID = getPoolID(ipAddress)

######################################
def sensorStartChecker(ipAddress, assignedPoolID, ipExists):
    if(ipExists == True):
        print("IP Address is in IP Objects")
        if(assignedPoolID != 0):
            print("IP Address is in Pool Objects")
            print("Assigned Pool ID: " + str(assignedPoolID))
            sensorStart = True
            print("Sensor Start = " + str(sensorStart))
            return sensorStart
        else:
            print("IP Address is NOT in Pool Objects")
            print("Sensor Will NOT Start!")
    else:
        print("IP Address is NOT in IP Objects")
        print("IP Address: " + ipAddress + " Added!")
        insertIP(ipAddress)

######################################
sensorStart = sensorStartChecker(ipAddress,assignedPoolID,ipExists)
print("After Checker the Sensor Start is = " + str(sensorStart))

#if poolobjects.filter(pool_ip = ipAddress) != null:
#    isAssigned = True
#    print("isAssigned changed to True")
#elif poolobjects.filter(pool_ip = ipAddress) == null:
#    isAssigned = False
#    print("isAssigned changed to False")

#if(ipExists == True):
#    print("IP Address is in IP Objects")
#    if(isAssigned == True):
#        print("IP Address is in Pool Objects")
#        assignedPoolID = poolobjects.filter(pool_ip=ipAddress).pool_id
#        print("Assigned Pool ID: " + assignedPoolID)
#        sensorStart = True
#    elif(isAssigned == False):
#        print("IP Address is NOT in Pool Objects")
#        print("Sensor Will NOT Start!")
#elif(ipExists == False):
#    print("IP Address is NOT in IP Objects")
#    print("IP Address: " + ipAddress + " Added!")
#    insertIP(ipAddress)
#endof checker

#start of sensor code
def voltArray(arrayLength, channel):
    voltArray = np.zeros(arrayLength,float)
    i = 0
    data = 0
    while i < arrayLength:
        if(channel == 1):
            data = 4.20019
        else:
            data = 792.43231
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

def read():
    celsius = 27
    return celsius

#temp_pH queries
def insert_to_temp_pH():
    #reads pH value voltage and translates to actual pH value
    phVoltage = voltArray(arrayLength, phChannel)
    finalPhVoltage = averageVolt(phVoltage, arrayLength)*5.0/1024
    phValue = round((1.5 * finalPhVoltage),2)
    phValue = phValue + 1.33
    Temp_Ph.objects.create(pool_id=assignedPoolID, temp_phlevel=phValue, temp_phdatetime=datetime.datetime.now())
    print("Temp_Ph Value Added: Enrique Razon Building, " + str(phValue) + ", " + str(datetime.datetime.now()))

def del_insert_to_temp_pH():
    phVoltage = voltArray(arrayLength, phChannel)
    finalPhVoltage = averageVolt(phVoltage, arrayLength)*5.0/1024
    phValue = round((1.5 * finalPhVoltage),2)
    phValue = phValue + 1.33
    print("Deleted: " + str(Temp_Ph.objects.all()[0]))
    Temp_Ph.objects.all()[0].delete()
    Temp_Ph.objects.create(pool_id=assignedPoolID, temp_phlevel=phValue, temp_phdatetime=datetime.datetime.now())
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
            reading = reading * reading
            tempx.append(reading)
        newTempSum = 0
        for read in tempx:
            newTempSum+= read
        pHVariance = newTempSum/tempCount
        pHStandardDev = math.sqrt(pHVariance)
        pHStandardDev= decimal.Decimal(pHStandardDev)+tempMean
        pHStandardDev = round(pHStandardDev, 1)
        print("yah")
        Final_Ph.objects.create(pool_id=assignedPoolID, final_phlevel=pHStandardDev, final_phdatetime=datetime.datetime.now())
        print("Final_Ph Value Added: Enrique Razon Building, " + str(pHStandardDev) + ", " + str(datetime.datetime.now()))
        ##new notification
        if pHStandardDev < 7.2 or pHStandardDev > 7.8:
            poolx=Pool.objects.get(id=1)
            messagex = poolx.pool_location+" needs attention"
            userx = User.objects.get(username="pooltech3")
            try:
                getNotification=Notification_Table.objects.all().filter(user=userx, number=1)
            except Notification_Table.DoesNotExist:
                newNotification= Notification_Table(
                    user=userx,
                    message=messagex,
                    number = 1
                )
                newNotification.save()
        ##end of new notification

def count_temp_ph():
    rc = Temp_Ph.objects.count()
    return rc

#temp_turbidity queries
def insert_to_temp_turbidity():
    #reads turbidity voltage
    turbVoltage = voltArray(arrayLength, turbidityChannel)
    finalTurbVoltage = averageVolt(turbVoltage, arrayLength)*5.0/1024
    turbValue = round((getTurbidity(finalTurbVoltage)),5)
    Temp_Turbidity.objects.create(pool_id=assignedPoolID, temp_turbiditylevel=turbValue, temp_turbiditydatetime=datetime.datetime.now())
    print("Temp_Turbidity Value Added: Enrique Razon Building, " + str(turbValue) + ", " + str(datetime.datetime.now()))

def del_insert_to_temp_turbidity():
    turbVoltage = voltArray(arrayLength, turbidityChannel)
    finalTurbVoltage = averageVolt(turbVoltage, arrayLength)*5.0/1024
    turbValue = round((getTurbidity(finalTurbVoltage)),5)
    print("Deleted: " + str(Temp_Turbidity.objects.all()[0]))
    Temp_Turbidity.objects.all()[0].delete()
    Temp_Turbidity.objects.create(pool_id=assignedPoolID, temp_turbiditylevel=turbValue, temp_turbiditydatetime=datetime.datetime.now())
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
            reading = reading * reading
            tempx.append(reading)
        newTempSum = 0
        for read in tempx:
            newTempSum+= read
        turbidityVariance = newTempSum/tempCount
        turbidityStandardDev = math.sqrt(turbidityVariance)
        turbidityStandardDev = decimal.Decimal(turbidityStandardDev)+tempMean
        Final_Turbidity.objects.create(pool_id=assignedPoolID, final_turbiditylevel=turbidityStandardDev, final_turbiditydatetime=datetime.datetime.now())
        print("Final_Turbidity Value Added: Enrique Razon Building, " + str(turbidityStandardDev) + ", " + str(datetime.datetime.now()))

def count_temp_turbidity():
    rc = Temp_Turbidity.objects.count()
    return rc

#temp_temperature queries
def insert_to_temp_temperature():
    #reads temperature sensor
    tempData = read()
    Temp_Temperature.objects.create(pool_id=assignedPoolID, temp_temperaturelevel=tempData, temp_temperaturedatetime=datetime.datetime.now())
    print("Temp_Temperature Value Added: Enrique Razon Building, " + str(tempData) + ", " + str(datetime.datetime.now()))

def del_insert_to_temp_temperature():
    tempData = read()
    print("Deleted: " + str(Temp_Temperature.objects.all()[0]))
    Temp_Temperature.objects.all()[0].delete()
    Temp_Temperature.objects.create(pool_id=assignedPoolID, temp_temperaturelevel=tempData, temp_temperaturedatetime=datetime.datetime.now())
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
            reading = reading*reading
            tempx.append(reading)
        newTempSum = 0
        for read in tempx:
            newTempSum+= read
        tempVariance = newTempSum/tempCount
        tempStandardDev = math.sqrt(tempVariance)
        tempStandardDev= decimal.Decimal(tempStandardDev)+tempMean
        Final_Temperature.objects.create(pool_id=assignedPoolID, final_temperaturelevel=tempStandardDev, final_temperaturedatetime=datetime.datetime.now())
        print("Final_Temperature Value Added: Enrique Razon Building, " + str(tempStandardDev) + ", " + str(datetime.datetime.now()))

def count_temp_temperature():
    rc = Temp_Temperature.objects.count()
    return rc

class sensorReading(threading.Thread):

    def run(self):
        pH_batchCount = 6
        turb_batchCount = 6
        temp_batchCount = 6
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

            #while pH counters
            if(pH_rowCount < 10 and pH_batchCount != 10):
                insert_to_temp_pH()
                pH_batchCount += 1
            elif(pH_rowCount >= 10 and pH_batchCount != 10):
                del_insert_to_temp_pH()
                pH_batchCount += 1
            elif(pH_rowCount >= 10 and pH_batchCount == 10):
                batchCount10pH()
                pH_batchCount = 0
            elif(pH_rowCount < 10 and pH_batchCount == 10):
                batchCount10pH()
                pH_batchCount = 0

            #while turb counters
            if(turb_rowCount < 10 and turb_batchCount != 10):
                insert_to_temp_turbidity()
                turb_batchCount += 1
            elif(turb_rowCount >= 10 and turb_batchCount != 10):
                del_insert_to_temp_turbidity()
                turb_batchCount += 1
            elif(turb_rowCount >= 10 and turb_batchCount == 10):
                batchCount10Turbidity()
                turb_batchCount = 0
            elif(turb_rowCount < 10 and turb_batchCount == 10):
                batchCount10Turbidity()
                turb_batchCount = 0

            #while temp counters
            if(temp_rowCount < 10 and pH_batchCount != 10):
                insert_to_temp_temperature()
                temp_batchCount += 1
            elif(temp_rowCount >= 10 and temp_batchCount != 10):
                del_insert_to_temp_temperature()
                temp_batchCount += 1
            elif(temp_rowCount >= 10 and temp_batchCount == 10):
                batchCount10Temp()
                temp_batchCount = 0
                sleep(180)
                del_insert_to_temp_pH()
                pH_batchCount += 1
                del_insert_to_temp_turbidity()
                turb_batchCount += 1
                del_insert_to_temp_temperature()
                temp_batchCount += 1
            elif(temp_rowCount < 10 and temp_batchCount == 10):
                batchCount10Temp()
                temp_batchCount = 0
                sleep(180)
                insert_to_temp_pH()
                pH_batchCount += 1
                insert_to_temp_turbidity()
                turb_batchCount += 1
                insert_to_temp_temperature()
                temp_batchCount += 1

        sleep(180)
if sensorStart == True:
    sensorRead = sensorReading()
    sensorRead.start()
elif sensorStart == False:
    print("System would not Start, IP Address Not Yet Assigned In a Pool")

#Sensor Reading end###

###rendering definitions
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
    #notification code
    #sendMail('luismerleee@gmail.com', 'luismerleee@gmail.com', 'test', 'testing')
    notifications = getNotification(request)
    notifCount=notifications.count()
    try:
        usertype = Type.objects.get(user=request.user)
        adminType= Usertype_Ref.objects.get(pk=1)
        poolref = Pool.objects.all().order_by('pk')
        WaterQualityIndexes = []
        #temperature levels
        tempDeviations = []
        tempColors = []
        temperatureIndexes = []
        for poolitem in Pool.objects.all().order_by('pk'):
            temperatureList = Temp_Temperature.objects.all().filter(pool=poolref.get(pk=poolitem.pk))
            tempSum=0
            tempCount=0
            for item in temperatureList:
                tempSum+=item.temp_temperaturelevel
                tempCount+=1
            if(tempCount>0):
                tempStandardDev=computeStandardDeviation(tempSum, tempCount, temperatureList)
                #Water Quality Temperature
                if tempStandardDev>=25:
                    badVal=38.5
                else:
                    badVal=6.3
                temperatureIndex=Quality(tempStandardDev, 25, badVal, .10)
                temperatureIndexes.append(temperatureIndex)
                #color assignment
                color=getQualityColorTemperature(tempStandardDev)
                tempColors.append(color)
                degreeSign=u'\N{DEGREE SIGN}'
                tempStandardDev=str(tempStandardDev)+degreeSign+'C'
                tempDeviations.append(tempStandardDev)
            else:
                temperatureIndexes.append(0)
                tempColors.append("White")
                tempDeviations.append('No Readings')

        #turbidity levels
        turbidityDeviations = []
        turbidityColors = []
        turbidityIndexes = []
        #standard deviation of turbidity
        for poolitem in Pool.objects.all().order_by('pk'):
            turbidityList = Temp_Turbidity.objects.all().filter(pool=poolref.get(pk=poolitem.pk))
            turbiditySum=0
            turbidityCount=0
            for item in turbidityList:
                turbiditySum+=item.temp_turbiditylevel
                turbidityCount+=1
            if(turbidityCount>0):
                turbidityStandardDev=computeStandardDeviation(turbiditySum, turbidityCount, turbidityList)
                #Water Quality Turbidity
                turbidityIndex=Quality(turbidityStandardDev, 0, 26, .08)
                turbidityIndexes.append(turbidityIndex)
                #color assignment
                color=getQualityColorTurbidity(turbidityStandardDev)
                turbidityColors.append(color)
                turbidityStandardDev=str(turbidityStandardDev)+" ntu"
                turbidityDeviations.append(turbidityStandardDev)
            else:
                turbidityIndexes.append(0)
                turbidityColors.append("White")
                turbidityDeviations.append('No Readings')

        #ph level
        phDeviations = []
        phColors = []
        phIndexes=[]
        for poolitem in Pool.objects.all().order_by('pk'):
            phList = Temp_Ph.objects.all().filter(pool=poolref.get(pk=poolitem.pk))
            phSum=0
            phCount=0
            for item in phList:
                phSum+=item.temp_phlevel
                phCount+=1
            if(phCount>0):
                phStandardDev=computeStandardDeviation(phSum, phCount, phList)
                #Water Quality pH
                if phStandardDev>=7.4:
                    badVal=8.2
                else:
                    badVal=6.8
                phIndex=Quality(phStandardDev, 7.4, badVal, .11)
                phIndexes.append(phIndex)
                #color assignment
                color=getQualityColorPH(phStandardDev)
                phColors.append(color)
                phDeviations.append(phStandardDev)
            else:
                phIndexes.append(0)
                phDeviations.append('No Readings')
                phColors.append("White")
            #2615.97 - 1175.23 x + 185.315 x^2 - 9.90222 x^3
            chlorineLevels=[]
            chlorineColors=[]
        for item in phDeviations:
            try:
                #multiplier=8
                chlorine=chlorineEffectivenessComputation(item)
                #color assignment
                try:
                    if(chlorine>=0):
                        color=getQualityColorChlorine(chlorine)
                    else:
                        color=getQualityColorChlorine(chlorine)
                except:
                    color="white"
                try:
                    if(chlorine>0):
                        chlorine=str(chlorine)+'%'
                except:
                    chlorine=chlorine
                chlorineColors.append(color)
                chlorineLevels.append(chlorine)
            except:
                chlorineColors.append("White")
                chlorineLevels.append('Cannot Compute')
        waterColors = []
        wqIndexes=computeWaterQuality(temperatureIndexes, turbidityIndexes, phIndexes)
        for item in wqIndexes:
            waterColors.append(getWaterQualityColor(item))
            debugger=""
        content= {
            'debug_check': debugger,
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
            'waterColors':waterColors,
            'wqIndexes':wqIndexes,
        }
        if not usertype.type == adminType:
            return render(request, 'monitoring/pool technician/home.html', content)
        else:
            return render(request, 'monitoring/pool owner/home-owner.html', content)
    except:
        return render(request,'monitoring/BadRequest.html')



@login_required(login_url="/monitoring/login")
def poolDetails_view(request, poolitem_id):
    if 0==0:
        #poolstat
        usertype = Type.objects.get(pk=request.user.pk)
        adminType= Usertype_Ref.objects.get(pk=1)
        notifications = getNotification(request)
        notifCount=notifications.count()
        poolref = Pool.objects.get(id=poolitem_id)
        today=datetime.date.today()
        today= today - timedelta(0)
        fromDate=today
        toDate=today
        ph = Final_Ph.objects.all().filter(pool=poolref, final_phdatetime__gte=today)
        turbidity = Final_Turbidity.objects.all().filter(pool=poolref, final_turbiditydatetime=today)
        temperature = Final_Temperature.objects.all().filter(pool=poolref, final_temperaturedatetime__year=today.year, final_temperaturedatetime__month=today.month, final_temperaturedatetime__day=today.day)
        debugger=today
        #pool calendar stuff
        poolSchedule = MaintenanceSchedule.objects.filter(pool=poolref, scheduledStart__gte=fromDate, scheduledEnd__lte=toDate).reverse()
        poolSchedule= poolSchedule.exclude(scheduledStart__isnull=True)
        sd=[]
        st=[]
        pt=[]
        ss=[]
        for item in poolSchedule:
            #for pool calendar data
            startDateString=str(item.scheduledStart.month)+"/"+str(item.scheduledStart.day)+"/"+str(item.scheduledStart.year)
            endDateString=str(item.scheduledEnd.month)+"/"+str(item.scheduledEnd.day)+"/"+str(item.scheduledEnd.year)
            startDateString = datetime.datetime.strptime(startDateString, '%m/%d/%Y').strftime('%B %m, %Y')
            endDateString = datetime.datetime.strptime(endDateString, '%m/%d/%Y').strftime('%B %m, %Y')
            dateString=startDateString+" - "+endDateString
            sd.append(dateString)
            timeString=str(item.scheduledStart.hour)+" "+str(item.scheduledStart.minute)+"-"+str(item.scheduledEnd.hour)+" "+str(item.scheduledEnd.minute)
            startTimeString=str(item.scheduledStart.hour)+":"+str(item.scheduledStart.minute)
            endTimeString=str(item.scheduledEnd.hour)+":"+str(item.scheduledEnd.minute)
            startTimeString = datetime.datetime.strptime(startTimeString, '%H:%M').strftime('%I:%M%p')
            endTimeString = datetime.datetime.strptime(endTimeString, '%H:%M').strftime('%I:%M%p')
            timeString=startTimeString+" - "+endTimeString
            st.append(timeString)
            allUsers = User.objects.all()
            pt.append(str(item.user.first_name)+" "+str(item.user.last_name))
            ss.append(item.status)
        #chemical usage data stuff
        accomplishDates=[]
        chemicalTechnician=[]
        #for chemical usage data
        chemicalSchedule = poolSchedule.exclude(status="Scheduled", datetimeAccomplished__isnull=True)
        chemicalSchedule = chemicalSchedule.exclude(status="Unfinished")
        for item in chemicalSchedule:
            #for pool calendar data
            accomplishDateString=str(item.datetimeAccomplished.month)+"/"+str(item.datetimeAccomplished.day)+"/"+str(item.datetimeAccomplished.year)
            accomplishDateString = datetime.datetime.strptime(accomplishDateString, '%m/%d/%Y').strftime('%B %m, %Y')
            accomplishDates.append(accomplishDateString)
            allUsers = User.objects.all()
            chemicalTechnician.append(str(item.user.first_name)+" "+str(item.user.last_name))
        content= {
            #poolstat stuff
            'poolid':poolitem_id,
            'poolSchedule':poolSchedule,
            'sd':sd,
            'st':st,
            'pt':pt,
            'ss':ss,
            'debugger':debugger,
            'pool':poolref,
            'ph':ph,
            'turbidity':turbidity,
            'temperature':temperature,
            'notifications':notifications,
            'cs':chemicalSchedule,
            'ct':chemicalTechnician,
            'ad':accomplishDates
        }
        print('----------------------------- Success in processing Pool Details ---------------------------')
        if not usertype.type == adminType:
            return render(request, 'monitoring/pool technician/pool-stat.html', content)
        else:
            return render(request, 'monitoring/pool owner/pool-stat.html', content)
    else:
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Error in viewing pool Details xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        return render(request,'monitoring/BadRequest.html')




@login_required(login_url="/monitoring/login")
def addUser(request):

        notifications = getNotification(request)
        notifCount=notifications.count()
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
            return render(request,'monitoring/BadRequest.html')


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
        return render(request,'monitoring/BadRequest.html')


@login_required(login_url="/monitoring/login")
def setMaintenanceCompute(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
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
            phStandardDev = computeStandardDeviation(phSum, phCount, phList)
        else:
            phStandardDev = "No Value"
        phLevel=phStandardDev
        #get gallons
        cubicpool = poolitem.pool_width * poolitem.pool_depth * poolitem.pool_length
        poolGallons = cubicpool * decimal.Decimal(7.5)
        squarefeet= poolitem.pool_length * poolitem.pool_width
        #DE powder computation
        dePowderVal=computeDEPowderValOnly(squarefeet)
        dePowderOutput=computeDEPowder(squarefeet)
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
        try:
            if phLevel < 7.4:
                muriaticAcidOutput="No Need"
                muriaticAcidVal=0
                sodaAsh=computeSodaAsh(phLevel, multiplier)
                sodaAshVal = sodaAsh
                sodaAshOutput=fixSodaAshOutputDisplay(sodaAsh)
                if(sodaAshOutput=="No need"):
                    sodaAshVal=0
            elif phLevel > 7.4:#muriatic acid computation
                sodaAshOutput="No Need"
                sodaAshVal=0
                muriaticAcid=computeMuriaticAcid(phLevel, multiplier)
                muriaticAcidVal = fixMuriaticAcidDisplay(muriaticAcid)
                if(muriaticAcidVal=="No need"):
                    muriaticAcidVal=0
            else:
                print('water is balanced')
                sodaAshOutput="No Need"
                muriaticAcidOutput="No Need"
                dePowderOutput="No Need"
                muriaticAcidOutput="No Need"
                sodaAshVal=0
                muriaticAcidVal=0
                dePowderVal=0
                muriaticAcidVal=0
                showButton=0
        except:
            print('No Value Retrieved')
            sodaAshOutput="Cannot Compute"
            muriaticAcidOutput="Cannot Compute"
            dePowderOutput="Cannot Compute"
            muriaticAcidOutput="Cannot Compute"
            sodaAshVal=0
            muriaticAcidVal=0
            dePowderVal=0
            muriaticAcidVal=0
            showButton=1
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
            'sodaAshVal':sodaAshVal,
            'muriaticAcidVal':muriaticAcidVal,
            'dePowderVal':dePowderVal,
            'notifications':notifications,
            'color':"fill:green;stroke:black;stroke-width:1;opacity:0.5",
            'showButton':showButton,
        }
        return render(request, 'monitoring/pool technician/set-maintenance-schedule-compute.html', content)
    else:
        return render(request,'monitoring/BadRequest.html')


@login_required(login_url="/monitoring/login")
def submitMaintenanceRequest(request):
    try:
        notifications = getNotification(request)
        notifCount=notifications.count()
        poolPK = request.POST['poolPK']
        dateStart = request.POST['dateStart']
        dateEnd = request.POST['dateEnd']
        timeStart = request.POST['timeStart']
        timeEnd = request.POST['timeEnd']
        bakingSoda = request.POST['sodaAsh']
        muriaticAcid = request.POST['muriaticAcid']
        dePowder = request.POST['dePowder']
        poolitem = Pool.objects.get(pk=poolPK)
        inStart=str(dateStart)+" "+str(timeStart)
        inEnd=str(dateEnd)+" "+str(timeEnd)
        #YYYY-MM-DD HH:MM
        ms = MaintenanceSchedule(
            user=request.user,
            pool=poolitem,
            scheduledStart=inEnd,
            scheduledEnd=inStart,
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
        debugger=""
        content={
            'debugger':debugger,
            'display':"Success",
            'notifications':notifications,
        }
        return render(request, 'monitoring/pool technician/set-maintenance-schedule.html', content)
    except:
        return render(request,'monitoring/BadRequest.html')


@login_required(login_url="/monitoring/login")
def searchPT(request):
    try:
        usertype = Type.objects.get(pk=request.user.pk)
        adminType= Usertype_Ref.objects.get(pk=1)
        notifications = getNotification(request)
        notifCount=notifications.count()
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
    except:
        return render(request,'monitoring/BadRequest.html')

@login_required(login_url="/monitoring/login")
def profile(request,item_id):
    try:
        usertype = Type.objects.get(pk=request.user.pk)
        adminType= Usertype_Ref.objects.get(pk=1)
        notifications = getNotification(request)
        notifCount=notifications.count()
        if usertype.type == adminType:
            print("sad 1")
            user = User.objects.get(id=item_id)
            userSchedule = MaintenanceSchedule.objects.all().filter(user=user)
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
                    print("sad 4")
                    Status.objects.filter(pk=user.pk).update(status=2)
                    return render(request, 'monitoring/pool owner/home-owner.html', content)


                else:
                    print("sad 5")
                    form1 = EditDetailsForm()
                    form2 = ChangePasswordForm(request.user)
                    content = {
                        "userSchedule":userSchedule,
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
                    print("sad 6")
                    btnFlag = 'Inactive'
                    content = {
                        "userSchedule":userSchedule,
                        'item_id': user,
                        'status':status,
                        'btnFlag':btnFlag,
                        'notifications':notifications,
                        }
            return render(request, 'monitoring/pool owner/technician-profile.html', content)
        else:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx bad request at edit details 1 xxxxxxxxxxxxxxxxxxxxx")
            return render(request,'monitoring/BadRequest.html')
    except:
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx bad request at edit details 2 xxxxxxxxxxxxxxxxxxxxx")
        return render(request,'monitoring/BadRequest.html')


@login_required(login_url="/monitoring/login")
def editDetails(request):
    try:
        notifications = getNotification(request)
        notifCount=notifications.count()
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
                    alert = 'success'

                    content = {
                        'form2': form2,
                        'alert':alert,
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
    except:
        return render(request,'monitoring/BadRequest.html')

@login_required(login_url="/monitoring/login")
def filterPoolStat(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
    try:
        poolPk = request.POST['poolPK']
        startDate = request.POST['dateStart']
        endDate = request.POST['dateEnd']
        poolref = Pool.objects.get(id=poolPk)
        xDate = datetime.datetime.strptime(startDate, '%B %d, %Y ').strftime('%Y-%m-%d')
        yDate = datetime.datetime.strptime(endDate, ' %B %d, %Y')
        yDate = yDate + timedelta(1)
        yDate= yDate.strftime('%Y-%m-%d')
        xDate = str(xDate)+" 00:00"
        yDate = str(yDate)+" 00:00"
        display = xDate+" - "+yDate
        ph = Final_Ph.objects.all().filter(pool=poolref, final_phdatetime__range=[xDate, yDate])
        turbidity = Final_Turbidity.objects.all().filter(pool=poolref, final_turbiditydatetime__range=[xDate, yDate])
        temperature = Final_Temperature.objects.all().filter(pool=poolref, final_temperaturedatetime__range=[xDate, yDate])
        content= {
            'debug_check': "",
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
                'debug_check': "",
                'pool':poolref,
                'ph':ph,
                'turbidity':turbidity,
                'temperature':temperature,
                'notifications':notifications,
            }
            return render(request, 'monitoring/pool technician/pool-stat.html', content)
        except:
            return render(request,'monitoring/BadRequest.html')

@login_required(login_url="/monitoring/login")
def viewMaintenance(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
    if 0==0:
        maintenanceSchedule = MaintenanceSchedule.objects.all().order_by("scheduledStart")
        #"October 13, 2014 11:13:00"
        users=[]
        startSchedules=[]
        endSchedules=[]
        colors=[]
        eventids=[]
        debugger=[]
        for eventObject in maintenanceSchedule:
            startDate=calendarGetDate(eventObject.scheduledStart)
            if eventObject.scheduledStart == None:
                startDate=calendarGetDate(eventObject.estimatedStart)
            else:
                startDate=calendarGetDate(eventObject.scheduledStart)
            if eventObject.scheduledEnd == None:
                endDate=calendarGetDate(eventObject.estimatedEnd)
            else:
                endDate=calendarGetDate(eventObject.scheduledEnd)
            #Notified Scheduled Accomplished
            color = getCalendarColorByStatus(eventObject.status)
            #appends
            users.append(eventObject.user)
            startSchedules.append(startDate)
            endSchedules.append(endDate)
            colors.append(color)
            eventids.append(eventObject.id)
            #appends
            users.append(eventObject.user)
            startSchedules.append(startDate)
            endSchedules.append(endDate)
            colors.append(color)
            eventids.append(eventObject.id)
            #debugger.append(str(eventObject.user)+" - "+str(eventObject.scheduledStart)+" - "+str(eventObject.scheduledEnd))
        debugger=""
        content={
            'debugger': debugger,
            'titles': users,
            'starts': startSchedules,
            'ends': endSchedules,
            'backgroundColors': colors,
            'ids': eventids,
            'notifications':notifications,
        }
        return render(request, 'monitoring/pool technician/view-all-maintenance-schedule.html', content)
    else:
        return render(request,'monitoring/BadRequest.html')

@login_required(login_url="/monitoring/login")
def notFound(request):
    return render(request, 'monitoring/pool owner/result-not-found.html')


@login_required(login_url="/monitoring/login")
def maintenanceDetails(request, schedule_id):
    notifications = getNotification(request)
    notifCount=notifications.count()
    if 0==0:
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
            #NEW
            poolitem = Pool.objects.get(pk=poolPK)
            phList = Temp_Ph.objects.all().filter(pool=poolitem)
            phSum=0
            phCount=0
            phStandardDev="No Value"
            for phItem in phList:
                phSum+=phItem.temp_phlevel
                phCount+=1
            computeStandardDeviation(phSum, phCount, phList)
            if(phCount>0):
                phStandardDev=computeStandardDeviation(phSum, phCount, phList)
            phLevel =  phStandardDev
            #get gallons
            cubicpool = poolitem.pool_width * poolitem.pool_depth * poolitem.pool_length
            poolGallons = cubicpool * decimal.Decimal(7.5)
            squarefeet= poolitem.pool_length * poolitem.pool_width
            #DE powder computation
            dePowder=computeDEPowder(squarefeet)
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
                muriaticAcidVal=0
                sodaAsh=computeSodaAsh(phLevel, multiplier)
                sodaAshVal = sodaAsh
                sodaAshOutput=fixSodaAshOutputDisplay(sodaAsh)
                if(sodaAshOutput=="No need"):
                    sodaAshVal=0
            elif phLevel > 7.4:#muriatic acid computation
                sodaAshOutput="No Need"
                sodaAshVal=0
                muriaticAcid=computeMuriaticAcid(phLevel, multiplier)
                muriaticAcidVal = fixMuriaticAcidDisplay(muriaticAcid)
                if(muriaticAcidVal=="No need"):
                    muriaticAcidVal=0
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
    else:
        return render(request,'monitoring/BadRequest.html')


@login_required(login_url="/monitoring/login")
def maintenanceDetailsChemicals(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
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
        return render(request,'monitoring/BadRequest.html')

@login_required(login_url="/monitoring/login")
def submitMaintenanceChemicals(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
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
        #TODO: record Chemical usage
        #useItem(chemicalName, usageCount, item.pool, item.user)
        maintenanceSchedule = MaintenanceSchedule.objects.all().order_by("scheduledStart")
        #"October 13, 2014 11:13:00"
        users=[]
        startSchedules=[]
        endSchedules=[]
        colors=[]
        eventids=[]
        debugger=[]
        for eventObject in maintenanceSchedule:
            startDate=calendarGetDate(eventObject.scheduledStart)
            if eventObject.scheduledStart == None:
                startDate=calendarGetDate(eventObject.estimatedStart)
            else:
                startDate=calendarGetDate(eventObject.scheduledStart)
            if eventObject.scheduledEnd == None:
                endDate=calendarGetDate(eventObject.estimatedEnd)
            else:
                endDate=calendarGetDate(eventObject.scheduledEnd)
            #Notified Scheduled Accomplished
            color = getCalendarColorByStatus(eventObject.status)
            #appends
            users.append(eventObject.user)
            startSchedules.append(startDate)
            endSchedules.append(endDate)
            colors.append(color)
            eventids.append(eventObject.id)
            #debugger.append(str(eventObject.user)+" - "+str(eventObject.scheduledStart)+" - "+str(eventObject.scheduledEnd))
        debugger=""
        content={
            'debugger': debugger,
            'titles': users,
            'starts': startSchedules,
            'ends': endSchedules,
            'backgroundColors': colors,
            'ids': eventids,
            'notifications':notifications,
            'success':"Success",
            'notifications':notifications,
        }
        return render(request, 'monitoring/pool technician/view-all-maintenance-schedule.html', content)
    except:
        return render(request,'monitoring/BadRequest.html')

def filterPoolDetails(request, poolitem_id):
    if 0==0:
        #get from and to date
        #dc=request.POST['dchlorineLevel']
        #mm/dd/yyyy
        fromDate=request.POST['startDate']
        toDate=request.POST['endDate']
        #'08/01/2018' value has an invalid format. It must be in YYYY-MM-DD
        fromDate=datetime.datetime.strptime(fromDate, '%m/%d/%Y').strftime('%Y-%m-%d')
        toDate=datetime.datetime.strptime(toDate, '%m/%d/%Y').strftime('%Y-%m-%d')
        #poolstat
        usertype = Type.objects.get(pk=request.user.pk)
        adminType= Usertype_Ref.objects.get(pk=1)
        notifications = getNotification(request)
        notifCount=notifications.count()
        poolref = Pool.objects.get(id=poolitem_id)
        today=datetime.date.today()
        today= today - timedelta(0)
        ph = Final_Ph.objects.all().filter(pool=poolref, final_phdatetime__gte=fromDate, final_phdatetime__lte=toDate)
        turbidity = Final_Turbidity.objects.all().filter(pool=poolref, final_turbiditydatetime__gte=fromDate, final_turbiditydatetime__lte=toDate)
        temperature = Final_Temperature.objects.all().filter(pool=poolref, final_temperaturedatetime__gte=fromDate, final_temperaturedatetime__lte=toDate)
        debugger=str(fromDate)+" - "+str(toDate)
        print("------------------------- Filter Pool Date "+debugger+" ---------------------")
        print(debugger)
        #pool calendar stuff
        poolSchedule = MaintenanceSchedule.objects.filter(pool=poolref, scheduledStart__gte=fromDate, scheduledEnd__lte=toDate).reverse()
        poolSchedule= poolSchedule.exclude(scheduledStart__isnull=True)
        sd=[]
        st=[]
        pt=[]
        ss=[]
        for item in poolSchedule:
            #for pool calendar data
            startDateString=str(item.scheduledStart.month)+"/"+str(item.scheduledStart.day)+"/"+str(item.scheduledStart.year)
            endDateString=str(item.scheduledEnd.month)+"/"+str(item.scheduledEnd.day)+"/"+str(item.scheduledEnd.year)
            startDateString = datetime.datetime.strptime(startDateString, '%m/%d/%Y').strftime('%B %m, %Y')
            endDateString = datetime.datetime.strptime(endDateString, '%m/%d/%Y').strftime('%B %m, %Y')
            dateString=startDateString+" - "+endDateString
            sd.append(dateString)
            timeString=str(item.scheduledStart.hour)+" "+str(item.scheduledStart.minute)+"-"+str(item.scheduledEnd.hour)+" "+str(item.scheduledEnd.minute)
            startTimeString=str(item.scheduledStart.hour)+":"+str(item.scheduledStart.minute)
            endTimeString=str(item.scheduledEnd.hour)+":"+str(item.scheduledEnd.minute)
            startTimeString = datetime.datetime.strptime(startTimeString, '%H:%M').strftime('%I:%M%p')
            endTimeString = datetime.datetime.strptime(endTimeString, '%H:%M').strftime('%I:%M%p')
            timeString=startTimeString+" - "+endTimeString
            st.append(timeString)
            allUsers = User.objects.all()
            pt.append(str(item.user.first_name)+" "+str(item.user.last_name))
            ss.append(item.status)
        #chemical usage data stuff
        accomplishDates=[]
        chemicalTechnician=[]
        #for chemical usage data
        chemicalSchedule = poolSchedule.exclude(status="Scheduled", datetimeAccomplished__isnull=True)
        chemicalSchedule = chemicalSchedule.exclude(status="Unfinished")
        for item in chemicalSchedule:
            #for pool calendar data
            accomplishDateString=str(item.datetimeAccomplished.month)+"/"+str(item.datetimeAccomplished.day)+"/"+str(item.datetimeAccomplished.year)
            accomplishDateString = datetime.datetime.strptime(accomplishDateString, '%m/%d/%Y').strftime('%B %m, %Y')
            accomplishDates.append(accomplishDateString)
            allUsers = User.objects.all()
            chemicalTechnician.append(str(item.user.first_name)+" "+str(item.user.last_name))
        #water level forecast
        forecastData_ph = Final_Ph.objects.filter(pool=poolref).order_by('final_phdatetime').reverse()[:12]
        #forecastData_ph = Final_Ph.objects.filter(pool=poolref, final_phdatetime=today).order_by('final_phdatetime').reverse()[:12]
        forecast_ph=getForecast(forecastData_ph, 6.8, 7.2)
        timeCounter=0
        timeToForecast=datetime.datetime.today()
        forecast_time=[]
        while timeCounter<12:
            timeCounter+=1
            timeToForecast+=timedelta(hours=1)
            forecast_time.append(timeToForecast)
        content= {
            'forecastData':forecast_ph,
            'forecastTimeData':forecast_time,
            'poolid':poolitem_id,
            'poolSchedule':poolSchedule,
            'sd':sd,
            'st':st,
            'pt':pt,
            'ss':ss,
            'debugger':debugger,
            'pool':poolref,
            'ph':ph,
            'turbidity':turbidity,
            'temperature':temperature,
            'notifications':notifications,
            'cs':chemicalSchedule,
            'ct':chemicalTechnician,
            'ad':accomplishDates
        }
        print('----------------------------- Success in processing Pool Details ---------------------------')
        if not usertype.type == adminType:
            return render(request, 'monitoring/pool technician/pool-stat.html', content)
        else:
            return render(request, 'monitoring/pool owner/pool-stat.html', content)
    else:
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Error in viewing pool Details xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        return render(request,'monitoring/BadRequest.html')

##reusable methods
@login_required(login_url="/monitoring/login")
def computeChlorine(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
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
        display = "Computed Chlorine: "+str(chlorine) +" ounces / "
        chlorine = chlorine * decimal.Decimal(0.0625)
        chlorine = round(chlorine, 2)
        display = display+str(chlorine)+" lbs on"+poolitem.pool_location+" pool."
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
            return render(request,'monitoring/BadRequest.html')

@login_required(login_url="/monitoring/login")
def poolTechList(request):
    x=User.objects.all()
    debugger=""
    techType= Usertype_Ref.objects.get(pk=2)
    names=[]
    status=[]
    for itemX in x:
        itemType=Type.objects.get(user=itemX)
        if itemType.type == techType:
            fullname=str(itemX.first_name)+" "+itemX.last_name
            names.append(fullname)
            s=Status.objects.get(user=itemX)
            s=str(s.status.status_ref)
            status.append(s)
    context = {
        'debugger':debugger,
        'names':names,
        'status':status,
    }
    return render(request, 'monitoring/pool owner/view-pool-technicians.html', context)

@login_required(login_url="/monitoring/login")
def success(request):
    return render(request, 'monitoring/success/success.html')

def getNotification(request):
    notifications = Notification_Table.objects.all().filter(user=request.user)
    return notifications

@login_required(login_url="/monitoring/login")
def success(request):
    return render(request, 'monitoring/success/success.html')

@login_required(login_url="/monitoring/login")
def personnelEfficiency(request):
    print("============================ Entering Personnel Efficiency ======================")
    employeeList=User.objects.all()#working here
    try:
        if request.method == 'POST':
            year=request.POST['yearFilter']
            month=request.POST['monthFilter']
            month=datetime.datetime.strptime(month, '%B').strftime('%m')
            month=str(month)
            year=str(year)
        else:
            today=datetime.date.today()
            month=today.month
            year=today.year
            compareDate=convertToDateTime(today.month, "1", today.year)
    except:
        today=datetime.date.today()
        month=today.month
        year=today.year
    compareDate=convertToDateTime(month, "1", year)
    try:
        compareDate2=convertToDateTime(month, "31", year)
    except:
        compareDate2=convertToDateTime(month, "30", year)
    counts=[]
    accomplishedCounts=[]
    lateCounts=[]
    unfinishedCounts=[]
    efficiencyList=[]
    eNames=[]
    for employee in employeeList:
        eName=str(employee.first_name)+" "+str(employee.last_name)
        eNames.append(eName)
        employeeReport=MaintenanceSchedule.objects.all().filter(user=employee)
        employeeReport=employeeReport.filter(date__gte=compareDate)
        employeeReport=employeeReport.filter(date__lte=compareDate2)
        totalCount=employeeReport.exclude(status="Scheduled").count()
        counts.append(totalCount)
        badCount=employeeReport.exclude(status="Scheduled").exclude(status="Accomplished").count()
        lateCount=employeeReport.filter(status="Late").count()
        lateCounts.append(lateCount)
        unfinishedCount=employeeReport.filter(status="Unfinished").count()
        unfinishedCounts.append(unfinishedCount)
        goodCount=totalCount-badCount
        accomplishedCounts.append(goodCount)
        try:
            efficiency=goodCount/totalCount*100
            efficiency=round(efficiency)
        except:
            efficiency=0
        efficiencyList.append(efficiency)
        ec=0
        asum=0
    for item in efficiencyList:
        asum+=item
        ec+=1
    try:
        averageAverage=asum/ec
        averageAverage=round(averageAverage)
    except:
        averageAverage=0
    content={
        "zl":eNames,
        "cl":counts,
        "al":accomplishedCounts,
        "ll":lateCounts,
        "ul":unfinishedCounts,
        "el":efficiencyList,
        "avgavg":averageAverage
    }
    return render(request, 'monitoring/pool owner/personnel-efficiency-report.html', content)

@login_required(login_url="/monitoring/login")
def chemicalConsumption(request):
    yearNow=datetime.date.today().year
    monthNow=datetime.date.today().month
    chemicalReport=MaintenanceSchedule.objects.all().filter(date__year=yearNow).exclude(status="Scheduled").exclude(status="Unfinished")
    chlorineTotal=0
    muriaticTotal=0
    dePowderTotal=0
    bakingSodaTotal=0
    itemCounter=0
    totalCost=0
    itemCounter=0
    ccl=[]
    mcl=[]
    dcl=[]
    bscl=[]
    rcl=[]
    #retrieve price
    for item in chemicalReport:
        chlorineTotal+=item.act_chlorine
        chlorineCost=computeCost("Chlorine", item.act_chlorine, item.datetimeAccomplished)
        muriaticTotal+=item.act_muriatic
        muriaticCost=computeCost("Muriatic Acid", item.act_muriatic, item.datetimeAccomplished)
        dePowderTotal+=item.act_depowder
        deCost=computeCost("DE Powder", item.act_depowder, item.datetimeAccomplished)
        bakingSodaTotal+=item.act_bakingsoda
        bakingsodaCost=computeCost("Baking Soda", item.act_bakingsoda, item.datetimeAccomplished)
        itemCounter+=1
        rowCost=chlorineCost+muriaticCost+deCost+bakingsodaCost
        ccl.append(chlorineCost)
        mcl.append(muriaticCost)
        dcl.append(deCost)
        bscl.append(bakingsodaCost)
        rcl.append(rowCost)
        totalCost+=rowCost
    dateGenerated= datetime.datetime.now().strftime('%B %d, %Y')
    reportMonth= str(datetime.datetime.now().strftime('%B %Y'))
    chlorineQuarterlyForecast=generateForecastedAmount(ccl, 3)
    muriaticQuarterlyForecast=generateForecastedAmount(mcl, 3)
    dePowderQuarterlyForecast=generateForecastedAmount(dcl, 3)
    bakingSodaQuarterlyForecast=generateForecastedAmount(bscl, 3)
    sumQuarterlyCost=chlorineQuarterlyForecast+muriaticQuarterlyForecast+dePowderQuarterlyForecast+bakingSodaQuarterlyForecast
    chlorineYearlyForecast=generateForecastedAmount(ccl, 12)
    muriaticYearlyForecast=generateForecastedAmount(mcl, 12)
    dePowderYearlyForecast=generateForecastedAmount(dcl, 12)
    bakingSodaYearlyForecast=generateForecastedAmount(bscl, 12)
    sumYearlyCost=chlorineYearlyForecast+muriaticYearlyForecast+dePowderYearlyForecast+bakingSodaYearlyForecast
    if itemCounter<1:
        chlorineTotal="n/a"
        muraticTotal="n/a"
        dePowderTotal="n/a"
        bakingSodaTotal="n/a"
    #date display format August 5, 2018
    context={
        "syc":sumYearlyCost,
        "sqc":sumQuarterlyCost,
        "rcl":rcl,
        "tc":totalCost,
        "ic":itemCounter,
        "ct":chlorineTotal,
        "mt":muriaticTotal,
        "dt":dePowderTotal,
        "bt":bakingSodaTotal,
        "dg":dateGenerated,
        "rm":reportMonth,
        "chemicalItems":chemicalReport,
    }
    return render(request, 'monitoring/pool owner/chemical-consumption-report.html', context)

@login_required(login_url="/monitoring/login")
def addPool(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
    try:
        usertype = Type.objects.get(pk=request.user.pk)
        adminType= Usertype_Ref.objects.get(pk=1)
        if usertype.type == adminType:
            if request.method == 'POST':
                msg = None
                print('request POST')
                form = RegisterPool(request.POST)
                if form.is_valid():
                    print('forms valid YEYYYYYYYYYYYY')
                    form.save()
                    print('form1 saved')

                    msg='success'
                    form = RegisterPool()
                    content={
                        'form':form,
                        'msg' : msg,
                        'notifications':notifications,
                        'notifCount':notifCount,
                    }
                    return render(request, 'monitoring/pool owner/add-pool.html',content)

                else:
                    msg='error'
                    content={
                        'form':form,
                        'msg' : msg,
                        'notifications':notifications,
                        'notifCount':notifCount,
                    }
                    return render(request, 'monitoring/pool owner/add-pool.html',content)

            else:
                form = RegisterPool()
                return render(request, 'monitoring/pool owner/add-pool.html',locals())
        else:
            return render(request,'monitoring/BadRequest.html')
    except:
        return render(request,'monitoring/BadRequest.html')



@login_required(login_url="/monitoring/login")
def addItem(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
    try:
        usertype = Type.objects.get(pk=request.user.pk)
        adminType= Usertype_Ref.objects.get(pk=1)
        if usertype.type != adminType:
            if request.method == 'POST':
                return render(request, 'monitoring/pool technician/add-item.html',locals())

                    #logic here
            else:

                return render(request, 'monitoring/pool technician/add-item.html',locals())
        else:
            return render(request,'monitoring/BadRequest.html')
    except:
        return render(request,'monitoring/BadRequest.html')

@login_required(login_url="/monitoring/login")
def setPoolConnection(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
    if usertype.type == adminType:
        if request.method == 'POST':
            msg = None
            print('request POST')
            form = RegisterPool(request.POST)
            if form.is_valid():
                print('forms valid YEYYYYYYYYYYYY')
                form.save()
                print('form1 saved')

                msg='success'
                form = RegisterPool()
                content={
                    'form':form,
                    'msg' : msg,
                    'notifications':notifications,
                    'notifCount':notifCount,
                }
                return render(request, 'monitoring/pool owner/set-pool-connection.html',content)

            else:
                msg='error'
                content={
                    'form':form,
                    'msg' : msg,
                    'notifications':notifications,
                    'notifCount':notifCount,
                }
                return render(request, 'monitoring/pool owner/set-pool-connection.html',content)

        else:
            form = RegisterPool()
            return render(request, 'monitoring/pool owner/set-pool-connection.html',locals())
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')




@login_required(login_url="/monitoring/login")
def disconnectPool(request):
    notifications = getNotification(request)
    notifCount=notifications.count()
    usertype = Type.objects.get(pk=request.user.pk)
    adminType= Usertype_Ref.objects.get(pk=1)
    if usertype.type == adminType:
        if request.method == 'POST':
            msg = None
            print('request POST')
            form = RegisterPool(request.POST)
            if form.is_valid():
                print('forms valid YEYYYYYYYYYYYY')
                form.save()
                print('form1 saved')

                msg='success'
                form = RegisterPool()
                content={
                    'form':form,
                    'msg' : msg,
                    'notifications':notifications,
                    'notifCount':notifCount,
                }
                return render(request, 'monitoring/pool owner/disconnect-pool.html',content)

            else:
                msg='error'
                content={
                    'form':form,
                    'msg' : msg,
                    'notifications':notifications,
                    'notifCount':notifCount,
                }
                return render(request, 'monitoring/pool owner/disconnect-pool.html',content)

        else:
            form = RegisterPool()
            return render(request, 'monitoring/pool owner/disconnect-pool.html',locals())
    else:
        return render(request, 'monitoring/pool owner/result-not-found.html')

def getReportMonthYear(request):
    if 0==0:
        yearNow=request.POST['yearOption']
        monthNow=request.POST['monthOption']
        monthAsIs=monthNow
        monthNow=datetime.datetime.strptime(monthNow, '%B').strftime('%m')
        #yearNow=datetime.datetime.strptime(yearNow, '%Y')
        monthNow=str(monthNow)
        yearNow=str(yearNow)
        chemicalReport=MaintenanceSchedule.objects.all().filter(date__year=yearNow, date__month=monthNow).exclude(status="Late").filter(status="Accomplished")
        #TODO: chemical consumption report
        chlorineTotal=0
        muriaticTotal=0
        dePowderTotal=0
        bakingSodaTotal=0
        totalCost=0
        itemCounter=0
        ccl=[]
        mcl=[]
        dcl=[]
        bscl=[]
        rcl=[]
        #retrieve price
        for item in chemicalReport:
            chlorineTotal+=item.act_chlorine
            compareDate=convertToDateTime(item.datetimeAccomplished.month, item.datetimeAccomplished.day, item.datetimeAccomplished.year)
            chlorineCost=computeCost("Chlorine", item.act_chlorine, compareDate)
            muriaticTotal+=item.act_muriatic
            muriaticCost=computeCost("Muriatic Acid", item.act_muriatic, compareDate)
            dePowderTotal+=item.act_depowder
            deCost=computeCost("DE Powder", item.act_depowder, compareDate)
            bakingSodaTotal+=item.act_bakingsoda
            bakingsodaCost=computeCost("Baking Soda", item.act_bakingsoda, compareDate)
            itemCounter+=1
            rowCost=chlorineCost+muriaticCost+deCost+bakingsodaCost
            ccl.append(chlorineCost)
            mcl.append(muriaticCost)
            dcl.append(deCost)
            bscl.append(bakingsodaCost)
            totalCost+=rowCost
            rcl.append(rowCost)
        dateGenerated= datetime.datetime.now().strftime('%B %d, %Y')
        reportMonth= str(monthAsIs)+" "+str(yearNow)
        chlorineQuarterlyForecast=generateForecastedAmount(ccl, 3)
        muriaticQuarterlyForecast=generateForecastedAmount(mcl, 3)
        dePowderQuarterlyForecast=generateForecastedAmount(dcl, 3)
        bakingSodaQuarterlyForecast=generateForecastedAmount(bscl, 3)
        sumQuarterlyCost=chlorineQuarterlyForecast+muriaticQuarterlyForecast+dePowderQuarterlyForecast+bakingSodaQuarterlyForecast
        chlorineYearlyForecast=generateForecastedAmount(ccl, 12)
        muriaticYearlyForecast=generateForecastedAmount(mcl, 12)
        dePowderYearlyForecast=generateForecastedAmount(dcl, 12)
        bakingSodaYearlyForecast=generateForecastedAmount(bscl, 12)
        sumYearlyCost=chlorineYearlyForecast+muriaticYearlyForecast+dePowderYearlyForecast+bakingSodaYearlyForecast
        if itemCounter<1:
            chlorineTotal="n/a"
            muraticTotal="n/a"
            dePowderTotal="n/a"
            bakingSodaTotal="n/a"
        #date display format August 5, 2018
        context={
            "syc":sumYearlyCost,
            "sqc":sumQuarterlyCost,
            "rcl":rcl,
            "tc":totalCost,
            "ic":itemCounter,
            "ct":chlorineTotal,
            "mt":muriaticTotal,
            "dt":dePowderTotal,
            "bt":bakingSodaTotal,
            "dg":dateGenerated,
            "rm":reportMonth,
            "chemicalItems":chemicalReport,
        }
        return render(request, 'monitoring/pool owner/chemical-consumption-report.html', context)
    else:
        return render(request,'monitoring/BadRequest.html')

@login_required(login_url="/monitoring/login")
def changePrice(request):
    print("view change Price")
    notifications = getNotification(request)
    if 0==0:
        print("trying to post at change Price")
        if request.method == 'POST':
            print("=========================== change Price initiated ====================")
            chemicalName=request.POST['chemical']
            newPrice=request.POST['Price']
            newQuantity=request.POST['Quantity']
            effectiveDate=request.POST['eDate']
            successCheck=updatePrice(chemicalName, newPrice, newQuantity, effectiveDate)
            if(successCheck>0):
                print("Price Successfuly updated")
            else:
                print("Failure occured in change price")
            return render(request, 'monitoring/pool technician/change-price.html',locals())
        else:
            return render(request, 'monitoring/pool technician/change-price.html',locals())
    else:
        return render(request,'monitoring/BadRequest.html')

### reusable methods
def Quality(observedVal, idealVal, badVal, weightVal):
    try:
        observedVal = decimal.Decimal(observedVal)
        idealVal = decimal.Decimal(idealVal)
        badVal = decimal.Decimal(badVal)
        weightVal = decimal.Decimal(weightVal)
        indexNum=0
        qualityIndex=(observedVal-idealVal)/(badVal-idealVal)
        qualityIndex=qualityIndex*100
        indexNum=qualityIndex*weightVal
        indexNum=indexNum
        indexNum=round(indexNum, 0)
    except:
        indexNum=None
        print("xxxxxxxxxxxxxxxxxxxxx FAILURE: QualityIndex could not be computed xxxxxxxxxxxxxxx")
    print("============================ Returning:"+str(indexNum)+" as quality index========================")
    return indexNum

def getQualityColorPH(phlevel):
    color = "white"
    try:
        if phlevel >= 7.3 and phlevel <=7.7:
            color = "green"
        elif((phlevel < 7.3 and phlevel >= 7.2) or (phlevel > 7.7 and phlevel < 7.9)):
            color = "yellow"
        elif(phlevel < 7.2 or phlevel > 7.8):
            color = "red"
        else:
            print("============================ setting PH Color to default: white========================")
        return color
    except:
        print("xxxxxxxxxxxxxxxxxxxxx FAILURE: PH color cannot be retrieved xxxxxxxxxxxxxxx")
    print("============================ Returning:"+color+" as PH Color========================")
    return color

def getQualityColorChlorine(chlorine):
    color="white"
    try:
        if chlorine >= 85:
            color="green"
        elif (chlorine >= 65):
             color="orange"
        elif (chlorine >= 50):
             color="yellow"
        elif(chlorine < 50):
             color="red"
        else:
            print("============================ setting Chlorine Effectiveness Color to default: white========================")
    except:
            print("xxxxxxxxxxxxxxxxxxxxxxxxx FAILURE: Chlorine color was not retrieved xxxxxxxxxxxxxxxxxxxxxxxx")
    print("============================ Returning:"+color+" as Chlorine Effectiveness Color========================")
    return color

def getQualityColorTemperature(temperature):
    color="white"
    try:
        if temperature >= 25 and temperature <= 28:
            color = "green"
        elif (temperature >= 23 and temperature < 25) or (temperature > 28 and temperature <= 30):
            color = "yellow"
        elif(temperature < 23 or temperature > 30):
            color = "red"
        else:
            print("============================ setting Temperature Color to default: white========================")
    except:
        print("xxxxxxxxxxxxxxxxxxxxxxxxx FAILURE: Temperature color was not retrieved xxxxxxxxxxxxxxxxxxxxxxxx")
    print("============================ Returning:"+color+" as Water Quality Color========================")
    return color

def getQualityColorTurbidity(turbidity):
    color="white"
    try:
        if turbidity < 1:
            color = "green"
        elif (turbidity >= 1 and turbidity < 2):
            color = "yellow"
        elif(turbidity >= 2):
            color = "red"
        else:
            print("============================ setting Turbidity Color to default: white========================")
    except:
        print("xxxxxxxxxxxxxxxxxxxxxxxxx FAILURE: Turbidity color was not retrieved xxxxxxxxxxxxxxxxxxxxxxxx")
    print("============================ Returning:"+color+" as Turbidity Color========================")
    return color

def computeStandardDeviation(cSum, cCount, cList):
    try:
        cNewList=[]
        cMean = cSum/cCount
        cx = []
        for level in cList:
            try:
                reading = level.temp_turbiditylevel
            except:
                try:
                    reading = level.temp_temperaturelevel
                except:
                    try:
                        reading = level.temp_phlevel
                    except:
                        print("xxxxxxxxxxxxxxxxxxxxxxxxx FAILURE: standard deviation cannot be computed due to list xxxxxxxxxxxxxxxxxxxxxxxxx")
            reading -=cMean
            reading = reading*reading
            cNewList.append(reading)
        newcSum = 0
        for read in cNewList:
            newcSum+= read
        cVariance = newcSum/cCount
        cStandardDev = math.sqrt(cVariance)
        cStandardDev=decimal.Decimal(cStandardDev)+cMean
        cStandardDev=round(cStandardDev, 1)
    except:
        cStandardDev=None
        print("xxxxxxxxxxxxxxxxxxxxxxxxx FAILURE: standard deviation cannot be computed start of method computeStandardDeviation("+str(cSum)+" "+str(cCount)+"and List)xxxxxxxxxxxxxxxxxxxxxxxxx")
    print("============================ Returning "+str(cStandardDev)+" as the Standard Deviation ========================")
    return cStandardDev

def addChemicalItem(name, price, usageLimit):
    try:
        #TODO: add item
        itemName = name
        itemPrice = price
        itemEffectiveDate = datetime.date.today()
        itemUsageCount=usageLimit
        #####add the chemical item to database
        return "=================item added to database====================="
    except:
        return "xxxxxxxxxxxxxxxx FAILURE: item was not added (def addChemicalItem) xxxxxxxxxxxxxxxxxxxx"

def useItem(chemicalName, usageCount, poolRef, user):
    try:
        #todo:chemicalUsageLog
        #####get referenced item
        today=datetime.date.today()
        ##### get pool used at
        #poolUsed=Pool.objects.filter(pool_name=poolRef.pool_name)
        #####add To Logs Table
        print("========================= item used =======================" + str(today))
    except:
        print("xxxxxxxxxxxxxxxxx FAILURE: item was not used (def useItem) xxxxxxxxxxxxxxx")

def updatePoolChemicalItemtPrice(productid, newPrice, effectiveDate):
    try:
        itemProductId = productId
        itemNewPrice = newPrice
        itemEffectiveDate = effectiveDate
        print("==================== item price updated ============================")
    except:
        print("xxxxxxxxxxxxxxxxxxxxxx FAILURE: item price not updated (def updatePoolChemicalItemtPrice) xxxxxxxxxxxxxxxxx")

def chlorineEffectivenessComputation(item):
    try:
        chlorine = decimal.Decimal(2615.97)
        multiplier = item
        chlorine-= decimal.Decimal(1175.23)*multiplier
        multiplier*=item
        chlorine+=decimal.Decimal(185.315)*multiplier
        multiplier*=item
        chlorine-=decimal.Decimal(9.90222)*multiplier
        chlorine = round(chlorine, 1)
    except:
        if(item==None):
            print("xxxxxxxxxxxxxxxxxxxxxx FAILURE: chlorine Effectiveness cannot be computed xxxxxxxxxxxxxxxxx")
        chlorine="Cannot be Computed"
    print("============================ Returning "+str(chlorine)+" as chlorine Effectiveness========================")
    return chlorine

def computeWaterQuality(temperatureIndexes, turbidityIndexes, phIndexes):
    try:
        wqIndexes =[]
        mainCount=0
        for tempIndexItem in temperatureIndexes:
            waterQuality = 0
            tCount=0
            pCount=0
            tempIQ=tempIndexItem
            mainCount+=1
            for turbIndexItem in turbidityIndexes:
                tCount+=1
                if mainCount == tCount:
                    turbIQ=turbIndexItem
            for phIndexItem in phIndexes:
                pCount+=1
                if mainCount == pCount:
                    phIQ=phIndexItem
            waterQuality=(tempIQ+turbIQ+phIQ)/decimal.Decimal(.29)
            #waterQuality=float(waterQuality)
            waterQuality=round(waterQuality, 0)
            if waterQuality > 0:
                waterQuality=100-waterQuality
                if waterQuality < 0:
                    wqIndexes.append(str(0))
                else:
                    wqIndexes.append(waterQuality)
            else:
                waterQuality="No Index"
                wqIndexes.append(waterQuality)
    except:
        print("xxxxxxxxxxxxxxxxxxxxxxxxx FAILURE: Failure at computeWaterQuality() xxxxxxxxxxxxxxxxxxxxxxxxx")
        wqIndexes=None
    print("============================ Returning "+str(wqIndexes)+" as Water Quality========================")
    return wqIndexes

def getWaterQualityColor(waterQuality):
    waterColor = "White"
    try:
        if waterQuality >= 95:
            waterColor = "green"
        elif (waterQuality >= 85):
            waterColor = "green"
        elif (waterQuality >= 80):
            waterColor = "yellow"
        elif(waterQuality < 80):
            waterColor = "red"
        else:
            print("============================ setting Water Quality Color to default: white========================")
        return waterColor
    except:
        if(waterQuality==None):
            print("xxxxxxxxxxxxxxxxxxxxxxxxx FAILURE: Water Quality Color cannot be retrieved xxxxxxxxxxxxxxxxxxxxxxxx")
    print("============================ Returning "+waterColor+" as Water Quality Color========================")
    return waterColor

def computeDEPowder(squarefeet):
    try:
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
    except:
        print("xxxxxxxxxxxxxxxxxxxxxxxxx FAILURE: Cannot compute DE Powder xxxxxxxxxxxxxxxxxxxxxxxxx")
        dePowder=None
    print("============================ Returning "+str(dePowder)+" DE Powder use========================")
    return dePowder
def computeDEPowderValOnly(squarefeet):
    try:
        dePowder = squarefeet*decimal.Decimal(.1)
        dePowder = dePowder*decimal.Decimal(.8)
        dePowder = round(dePowder, 1)
    except:
        dePowder=0
    return dePowder
def computeSodaAsh(phLevel, multiplier):
    #FOR every 5000 gallons increment multiplier by 1
    if phLevel < 6.7:
        sodaAsh = multiplier * 8
    elif phLevel <= 7:
        sodaAsh = multiplier * 6
    elif phLevel <= 7.2:
        sodaAsh = multiplier * 4
    elif phLevel <= 7.4:
        sodaAsh = multiplier * 3
    sodaAsh = round(sodaAsh, 1)
    return sodaAsh

def computeMuriaticAcid(phLevel, multiplier):
    if phLevel > 8.4:
        muriaticAcid = multiplier * 16
    elif phLevel >= 8:
        muriaticAcid = multiplier * 12
    elif phLevel >= 7.8:
        muriaticAcid = multiplier * 8
    elif phLevel > 7.5:
        muriaticAcid = multiplier * 6
    muriaticAcid = round(muriaticAcid, 1)
    return muriaticAcid

def fixSodaAshOutputDisplay(sodaAsh):
    if(sodaAsh>0):
        sodaAshOutput = str(sodaAsh)+" oz / "
        sodaAsh = sodaAsh*decimal.Decimal(0.0625)
        sodaAsh = round(sodaAsh, 2)
        sodaAshOutput = str(sodaAshOutput)+" lbs"
    else:
        sodaAshOutput="No Need"
    return sodaAshOutput

def fixMuriaticAcidDisplay(muriaticAcid):
    if muriaticAcid > 0:
        muriaticAcidOutput = str(muriaticAcid)+" oz / "
        muriaticAcid = muriaticAcid * decimal.Decimal(0.03125)
        muriaticAcid = round(muriaticAcid, 2)
        muriaticAcidOutput = muriaticAcidOutput + str(muriaticAcid)+" qts"
    else:
        muriaticAcidOutput = "No need"
    return muriaticAcidOutput

def updatePoolChemicalProductPrice(productId, newPrice, effectiveDate):
    productId = productId
    newPrice = newPrice
    effectiveDate = effectiveDate
    return productId

def calendarGetDate(b):
    ihour=b.hour
    dday=b.day
    ihour+=8
    if ihour>=24:
        ihour-=24
        dday+=1
        try:
            b=b.replace(day=dday)
        except:
            dday=1
            b=b.replace(day=dday)
    if ihour>=24:
        ihour-=24
    b=b.replace(hour=ihour)
    dString=str(b.month)+"/"+str(b.day)+"/"+str(b.year)+" "+str(b.hour)+":"+str(b.minute)+":00"
    #'7/31/2018 1:30:00' - #"October 13, 2014 11:13:00"
    returnDate = datetime.datetime.strptime(dString, '%m/%d/%Y %H:%M:00').strftime('%B %d, %Y %H:%M:00')
    #startDate = datetime.datetime.strptime(dString, '%m/%d/%Y %H:%M:00').strftime('%B %d, %Y')
    return returnDate

def getCalendarColorByStatus(status):
    if status == "Notified":
        color="#00cccc"
    elif status == "Scheduled":
        color="#0073b7"
    elif status == "Accomplished":
        color="#00a65a"
    elif status == "Late":
        color="#f39c12"
    elif status == "Unfinished":
        color="red"
    else:
        color="grey"
    return color

def computeCost(chemicalname, quantity, priceDate):
    returnVal=0
    try:
        print("============================ 1 ============================")
        chemicalReference=Chemical_Price_Reference.objects.filter(chemical=chemicalname, effectiveDate__lte=priceDate).order_by().reverse()[0]
        print("============================ 2 ============================")
        if(chemicalname == "Chlorine"):
            print("============================ chemical price for chlorine computed ============================")
            chemicalPrice=chemicalReference.price/chemicalReference.quantity
            returnVal=quantity*chemicalPrice
        elif(chemicalname == "Muriatic Acid"):
            print("============================ chemical price for Muriatic Acid computed ============================")
            chemicalPrice=chemicalReference.price/chemicalReference.quantity
            returnVal=quantity*chemicalPrice
        elif(chemicalname == "Baking Soda"):
            print("============================ chemical price for Baking Soda computed ============================")
            chemicalPrice=chemicalReference.price/chemicalReference.quantity
            returnVal=quantity*chemicalPrice
        elif(chemicalname == "DE Powder"):
            print("============================ chemical price for DE Powder computed ============================")
            chemicalPrice=chemicalReference.price/chemicalReference.quantity
            returnVal=quantity*chemicalPrice
        else:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxError: No Chemical price retirevedxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    except:
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Try Error: No Chemical price retirevedxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    returnVal=round(returnVal, 2)
    return returnVal

def convertToDateTime(month, day, year):
    yearCompare=year
    monthCompare=month
    dayCompare=day
    compareDate=str(monthCompare)+"/"+str(dayCompare)+"/"+str(yearCompare)
    compareDate=datetime.datetime.strptime(compareDate, '%m/%d/%Y').strftime('%Y-%m-%d')
    #compareDate=datetime.datetime.strptime(compareDate, '%m/%d/%Y').date
    returnVal=compareDate
    return returnVal

def generateForecastedAmount(costs, multiplier):
    returnVal=0
    itemSum=0
    itemCount=0
    try:
        for item in costs:
            itemSum+=item
            itemCount+=1
        monthlyAverage=itemSum/itemCount
        returnVal=monthlyAverage*multiplier
        returnVal=round(returnVal, 2)
    except:
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxx Error Cannot compute Forecasted Amount Quarterly xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    return returnVal

def sendMail(sender, to, subject, body):
    message = create_message(sender, to, subject, body)
    sendMail = send_message(service, sender, message)

def getForecast(data_list, lowerlimit, upperlimit):
    returnVal=0
    dataCount=0
    rateOfChanges=[]
    try:
        for item in data_list:
            dataCount+=1
            try:
                if(dataCount%2==0):
                    dataItem2=item.final_temperaturelevel
                    change=dataItem-dataItem2
                    rateOfChanges.append(change)
                else:
                    dataItem=item.final_temperaturelevel
            except:
                try:
                    if(dataCount%2==0):
                        dataItem2=item.final_phlevel
                        change=dataItem-dataItem2
                        rateOfChanges.append(change)
                    else:
                        dataItem=item.final_phlevel
                except:
                    try:
                        if(dataCount%2==0):
                            dataItem2=item.final_turbiditylevel
                            change=dataItem-dataItem2
                            rateOfChanges.append(change)
                        else:
                            dataItem=item.final_turbiditylevel
                    except:
                        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx Error in computing forecast 1 xxxxxxxxxxxxxxxxxxxxx")
        rateCount=0
        rateSum=0
        for item in rateOfChanges:
            rateCount+=1
            rateSum+=item
        rateAverage=rateSum/rateCount
        currentLevel=data_list[0]
        currentLevel=currentLevel.final_phlevel
        predictionCount=0
        returnVal=[]
        if(rateAverage>0):
            while predictionCount<=12:
                predictionCount+=1
                if(currentLevel<8.2):
                    currentLevel+=rateAverage
                    if currentLevel>8.2:
                        currentLevel=8.2
                currentLevel=round(currentLevel, 2)
                returnVal.append(currentLevel)
        else:
            while predictionCount<=12:
                predictionCount+=1
                if(currentLevel>6.8):
                    currentLevel+=rateAverage
                    if currentLevel<6.8:
                        currentLevel=6.8
                currentLevel=round(currentLevel, 2)
                returnVal.append(currentLevel)
        return returnVal
    except:
        print("xxxxxxxxxxxxxxxxxxxxxxxxx Error in computing forecast 2 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    return returnVal

def updatePrice(chemicalName, newPrice, newQuantity, effectiveDateNew):
    try:
        effectiveDateNew=datetime.datetime.strptime(effectiveDateNew, '%m/%d/%Y').strftime('%Y-%m-%d')
        returnVal=1
        if(chemicalName=="1"):
            returnVal=1
            itemCount = Chemical_Price_Reference.objects.filter(chemical = "Chlorine", effectiveDate=effectiveDateNew).count()
            if itemCount > 0:
                item = Chemical_Price_Reference.objects.get(chemical = "Chlorine", effectiveDate=effectiveDateNew)
                item.price = newPrice
            else:
                item=Chemical_Price_Reference(
                chemical = "Chlorine",
                    quantity = newQuantity,
                    price = newPrice,
                    effectiveDate = effectiveDateNew
                )
        elif(chemicalName=="2"):
            returnVal=1
            Chemical_Price_Reference.objects.filter(chemical = "DE Powder", effectiveDate=effectiveDateNew).count()
            if itemCount > 0:
                item = Chemical_Price_Reference.objects.get(chemical = "DE Powder", effectiveDate=effectiveDateNew)
                item.price = newPrice
            else:
                item=Chemical_Price_Reference(
                chemical = "DE Powder",
                    quantity = newQuantity,
                    price = newPrice,
                    effectiveDate = effectiveDateNew
                )
        elif(chemicalName=="3"):
            returnVal=1
            Chemical_Price_Reference.objects.filter(chemical = "Baking Soda", effectiveDate=effectiveDateNew).count()
            if itemCount > 0:
                item = Chemical_Price_Reference.objects.get(chemical = "Baking Soda", effectiveDate=effectiveDateNew)
                item.price = newPrice
            else:
                item=Chemical_Price_Reference(
                chemical = "Baking Soda",
                    quantity = newQuantity,
                    price = newPrice,
                    effectiveDate = effectiveDateNew
                )
        elif(chemicalName=="4"):
            returnVal=1
            Chemical_Price_Reference.objects.filter(chemical = "Muriatic Acid", effectiveDate=effectiveDateNew).count()
            if itemCount > 0:
                item = Chemical_Price_Reference.objects.get(chemical = "Muriatic Acid", effectiveDate=effectiveDateNew)
                item.price = newPrice
            else:
                item=Chemical_Price_Reference(
                chemical = "Muriatic Acid",
                    quantity = newQuantity,
                    price = newPrice,
                    effectiveDate = effectiveDateNew
                )
        item.save()
        return returnVal
    except:
        returnVal=0
        return returnVal
