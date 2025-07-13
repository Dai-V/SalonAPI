from rest_framework import serializers
from django.db.models import Sum

from SalonAPI.Main.models import Appointments,SavedServices, Services, User




class SavedServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedServices
        fields = ['ServiceID', 'ServiceName', 'ServicePrice','ServiceDuration']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'UserEmail', 'UserPhone', 'UserAddress', 'UserRole', 'UserAdditionalInfo']

class ServicesSerializer(serializers.ModelSerializer):
    User = serializers.StringRelatedField(source='UserID.username', read_only=True)
    class Meta:
        model = Services
        fields = ['ServiceName', 'ServicePrice', 'ServiceStartTime', 'ServiceDuration', 'AppID', 'User']        

class AppointmentSerializer(serializers.ModelSerializer):
    ServicesList = ServicesSerializer(many=True, read_only=True, source='services')

    class Meta:
        model = Appointments
        fields = ['AppID', 'AppDate', 'AppStatus','AppTotal', 'PaymentType','ServicesList']
