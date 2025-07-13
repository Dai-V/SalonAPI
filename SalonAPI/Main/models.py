from datetime import time,date
import django
from django.db import models
from django.contrib.auth.models import AbstractUser



class Appointments(models.Model):
    AppID   = models.AutoField(primary_key=True)
    AppDate = models.DateField(default=django.utils.timezone.now)
    AppStatus = models.CharField(max_length=20,blank=True, null=True)
    AppTotal = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    PaymentType = models.CharField(max_length=20,blank=True, null=True)  # e.g., 'credit_card', 'cash'

class User(AbstractUser):
    UserEmail = models.EmailField(unique=True)
    UserPhone = models.CharField(max_length=15, unique=True)
    UserAddress = models.CharField(max_length=255, blank=True, null=True)
    UserRole = models.CharField(max_length=20, default='customer')  # e.g., 'customer', 'admin'
    UserAdditionalInfo = models.TextField(blank=True, null=True)

class Services(models.Model):
    ServiceName = models.CharField(max_length=100)
    ServicePrice = models.DecimalField(max_digits=10, decimal_places=2, default = 0)
    ServiceStartTime = models.TimeField(default=time(0,0))
    ServiceDuration = models.IntegerField(default=30)
    AppID = models.ForeignKey(Appointments, on_delete=models.CASCADE, related_name='services')
    UserID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')

class SavedServices(models.Model):
    ServiceID = models.AutoField(primary_key=True)
    ServiceName = models.CharField(max_length=100)
    ServicePrice = models.DecimalField(max_digits=10, decimal_places=2)
    ServiceDuration = models.IntegerField()



class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'