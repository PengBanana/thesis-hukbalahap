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
	pool_availabletimestart = models.TimeField(null=True, blank=True)
	pool_availabletimeend = models.TimeField(null=True, blank=True)

	def __str__(self):
		return self.pool_location

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()



class Usertype_Ref(models.Model):
	usertype = models.CharField(max_length=45)

	def __str__(self):
		return self.usertype

class Type(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	type = models.ForeignKey(Usertype_Ref, default = 2, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.user)

@receiver(post_save, sender=User)
def create_user_type(sender, instance, created, **kwargs):
    if created:
       Type.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_type(sender, instance, **kwargs):
    instance.type.save()


#Status
class Status_Ref(models.Model):
	status_ref = models.CharField(max_length=45)

	def __str__(self):
		return self.status_ref

class Status(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	status = models.ForeignKey(Status_Ref, default = 1, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.user)

@receiver(post_save, sender=User)
def create_user_status(sender, instance, created, **kwargs):
    if created:
       Status.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_status(sender, instance, **kwargs):
    instance.status.save()


# Dependent Classes
class MaintenanceSchedule(models.Model):
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	date = models.DateField(null=True, default=datetime.today().strftime('%Y-%m-%d'))
	estimatedStart = models.DateTimeField(null=True, blank=True)
	estimatedEnd = models.DateTimeField(null=True, blank=True)
	scheduledStart = models.DateTimeField(null=True, blank=True)
	scheduledEnd = models.DateTimeField(null=True, blank=True)
	datetimeAccomplished = models.DateTimeField(null=True, blank=True)
	est_chlorine = models.DecimalField(null=True, max_digits=8, decimal_places=2, default=None)
	est_muriatic = models.DecimalField(max_digits=8, decimal_places=2, default=None)
	est_depowder = models.DecimalField(max_digits=8, decimal_places=2, default=None)
	est_bakingsoda = models.DecimalField(max_digits=8, decimal_places=2, default=None)
	act_chlorine = models.DecimalField(null=True, max_digits=8, decimal_places=2, default=None)
	act_muriatic = models.DecimalField(max_digits=8, decimal_places=2, default=None)
	act_depowder = models.DecimalField(max_digits=8, decimal_places=2, default=None)
	act_bakingsoda = models.DecimalField(max_digits=8, decimal_places=2, default=None)
	status = models.TextField(default="Scheduled")

	def __str__(self):
		return self.user.username + " - " + self.pool.pool_location

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

class Chlorine_Effectiveness(models.Model):
	pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING)
	ce_datettime = models.DateTimeField(default=datetime.now, blank=True)
	ce_percentage = models.DecimalField(max_digits=5, decimal_places=2, default="")

	def __str__(self):
		return self.pool.pool_location

class Notification_Table(models.Model):
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	message = models.TextField()
	number = models.IntegerField(null=True)
	type = models.TextField(default="Pool Technician")
	date = models.DateField(null=True, default=datetime.today().strftime('%Y-%m-%d'))

	def __str__(self):
		return str(self.user) +" - "+str(self.number)

class Chemical_Item(models.Model):
	chemicalName = models.TextField()
	chemicalUsageLimit = models.IntegerField()
	chemicalDescription = models.TextField()

	def __str__(self):
		return str(self.checmicalName)

class Chemical_Price_Reference(models.Model):
	chemical = models.ForeignKey(Chemical_Item, on_delete=models.DO_NOTHING)
	effectiveDate = models.DateField()
	price = models.DecimalField(max_digits=8, decimal_places=2, default="")

	def __str__(self):
		return str(self.chemical) +" - "+ str(self.effectiveDate) +" - "+ str(self.price)

class Chemical_Usage_Log(models.Model):
	chemical = models.ForeignKey(Chemical_Item, on_delete=models.DO_NOTHING)
	pool = models.ForeignKey(Pool, null=True, on_delete=models.DO_NOTHING)
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	usageDate = models.DateField()
	quantity = models.IntegerField()

	def __str__(self):
		return str(self.chemical) +" - "+ str(self.usageDate)
