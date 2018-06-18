# Create your models here.
from django.db import models
from datetime import datetime

# Non-Dependent Classes
class Pool(models.Model):
	pool_location = models.CharField(max_length=250)
	pool_length = models.DecimalField(max_digits=8, decimal_places=2, default="")
	pool_width = models.DecimalField(max_digits=8, decimal_places=2, default="")
	pool_depth = models.DecimalField(max_digits=8, decimal_places=2, default="")

class Usertype_Ref(models.Model):
	usertype = models.CharField(max_length=45)

# Dependent Classes

class User(models.Model):
	usertype_refID = models.ForeignKey(Usertype_Ref, on_delete=models.DO_NOTHING)
	username = models.CharField(max_length=45)
	password = models.CharField(max_length=45)
	lastname = models.CharField(max_length=45)
	firstname = models.CharField(max_length=45)

class MaintenanceSchedule(models.Model):
	userID = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	timeStart = models.TimeField(null=True, blank=True)
	timeEnd = models.TimeField(null=True, blank=True)
	timeAccomplished = models.TimeField(null=True, blank=True)
	est_chlorine = models.DecimalField(max_digits=8, decimal_places=2, default="")
	est_muriatic = models.DecimalField(max_digits=8, decimal_places=2, default="")
	est_depowder = models.DecimalField(max_digits=8, decimal_places=2, default="")
	act_chlorine = models.DecimalField(max_digits=8, decimal_places=2, default="")
	act_muriatic = models.DecimalField(max_digits=8, decimal_places=2, default="")
	act_depowder = models.DecimalField(max_digits=8, decimal_places=2, default="")

class Temp_Turbidity(models.Model):
	poolID = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	temp_turbiditylevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	temp_turbiditydatetime = models.DateTimeField(default=datetime.now, blank=True)

class Temp_Temperature(models.Model):
	pools = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	temp_temperaturelevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	temp_temperaturedatetime = models.DateTimeField(default=datetime.now, blank=True)

class Temp_Ph(models.Model):
	pools = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	temp_phlevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	temp_phdatetime = models.DateTimeField(default=datetime.now, blank=True)

class Final_Turbidity(models.Model):
	pools = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	final_turbiditylevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	final_turbiditydatetime = models.DateTimeField(default=datetime.now, blank=True)

class Final_Temperature(models.Model):
	pools = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	final_temperaturelevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	final_temperaturedatetime = models.DateTimeField(default=datetime.now, blank=True)

class Final_Ph(models.Model):
	pools = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	final_phlevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	final_phdatetime = models.DateTimeField(default=datetime.now, blank=True)
