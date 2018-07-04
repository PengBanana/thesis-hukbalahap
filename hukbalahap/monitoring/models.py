# Create your models here.
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Non-Dependent Classes
class Pool(models.Model):
	pool_location = models.CharField(max_length=250)
	pool_length = models.DecimalField(max_digits=8, decimal_places=2, default="")
	pool_width = models.DecimalField(max_digits=8, decimal_places=2, default="")
	pool_depth = models.DecimalField(max_digits=8, decimal_places=2, default="")

	def __str__(self):
		return self.pool_location

class Usertype_Ref(models.Model):
	usertype = models.CharField(max_length=45)

	def __str__(self):
		return self.usertype

class Type(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	type = models.ForeignKey(Usertype_Ref, default = 1, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.user)

@receiver(post_save, sender=User)
def create_user_type(sender, instance, created, **kwargs):
    if created:
       Type.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_type(sender, instance, **kwargs):
    instance.type.save()


# Dependent Classes
'''
class User(models.Model):
	usertype_ref = models.ForeignKey(Usertype_Ref, on_delete=models.DO_NOTHING)
	username = models.CharField(max_length=45)
	password = models.CharField(max_length=45)
	lastname = models.CharField(max_length=45)
	firstname = models.CharField(max_length=45)

	def __str__(self):
		return self.username
'''
class MaintenanceSchedule(models.Model):
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	timeStart = models.TimeField(null=True, blank=True)
	timeEnd = models.TimeField(null=True, blank=True)
	timeAccomplished = models.TimeField(null=True, blank=True)
	est_chlorine = models.DecimalField(max_digits=8, decimal_places=2, default="")
	est_muriatic = models.DecimalField(max_digits=8, decimal_places=2, default="")
	est_depowder = models.DecimalField(max_digits=8, decimal_places=2, default="")
	act_chlorine = models.DecimalField(max_digits=8, decimal_places=2, default="")
	act_muriatic = models.DecimalField(max_digits=8, decimal_places=2, default="")
	act_depowder = models.DecimalField(max_digits=8, decimal_places=2, default="")

	def __str__(self):
		return self.user

class Temp_Turbidity(models.Model):
	pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	temp_turbiditylevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	temp_turbiditydatetime = models.DateTimeField(default=datetime.now, blank=True)

	def __str__(self):
		return self.pool.pool_location

class Temp_Temperature(models.Model):
	pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	temp_temperaturelevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	temp_temperaturedatetime = models.DateTimeField(default=datetime.now, blank=True)

	def __str__(self):
		return self.pool.pool_location

class Temp_Ph(models.Model):
	pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	temp_phlevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	temp_phdatetime = models.DateTimeField(default=datetime.now, blank=True)

	def __str__(self):
		return self.pool.pool_location

class Final_Turbidity(models.Model):
	pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	final_turbiditylevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	final_turbiditydatetime = models.DateTimeField(default=datetime.now, blank=True)

	def __str__(self):
		return self.pool.pool_location

class Final_Temperature(models.Model):
	pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	final_temperaturelevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	final_temperaturedatetime = models.DateTimeField(default=datetime.now, blank=True)

	def __str__(self):
		return self.pool.pool_location

class Final_Ph(models.Model):
	pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	final_phlevel = models.DecimalField(max_digits=5, decimal_places=2, default="")
	final_phdatetime = models.DateTimeField(default=datetime.now, blank=True)

	def __str__(self):
		return self.pool.pool_location
