from django.contrib import admin

# Register your models here.
from .models import Pool, Usertype_Ref, User, MaintenanceSchedule, Temp_Turbidity, Temp_Temperature, Temp_Ph, Final_Turbidity, Final_Temperature, Final_Ph

admin.site.register(Pool)
admin.site.register(Usertype_Ref)
admin.site.register(User)
admin.site.register(MaintenanceSchedule)
admin.site.register(Temp_Turbidity)
admin.site.register(Temp_Temperature)
admin.site.register(Temp_Ph)
admin.site.register(Final_Turbidity)
admin.site.register(Final_Temperature)
admin.site.register(Final_Ph)