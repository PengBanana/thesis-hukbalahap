from django.contrib import admin

# Register your models here.
from .models import Pool, Usertype_Ref, Type, Status_Ref, Status, MaintenanceSchedule, Temp_Turbidity, Temp_Temperature, Temp_Ph, Final_Turbidity, Final_Temperature, Final_Ph, Chlorine_Effectiveness, Notification_Table, uPool, Chemical_Price_Reference, MobileNumber

admin.site.register(Pool)
admin.site.register(Usertype_Ref)
admin.site.register(Type)
admin.site.register(Status_Ref)
admin.site.register(Status)
admin.site.register(MaintenanceSchedule)
admin.site.register(Temp_Turbidity)
admin.site.register(Temp_Temperature)
admin.site.register(Temp_Ph)
admin.site.register(Final_Turbidity)
admin.site.register(Final_Temperature)
admin.site.register(Final_Ph)
admin.site.register(Chlorine_Effectiveness)
admin.site.register(Notification_Table)
admin.site.register(uPool)
admin.site.register(Chemical_Price_Reference)
admin.site.register(MobileNumber)
