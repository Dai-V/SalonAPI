from rest_framework import serializers
from django.db.models import Sum

from SalonAPI.Main.models import Appointments,SavedServices, Services, Technicians, User




class SavedServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedServices
        fields = ['ServiceID', 'ServiceName', 'ServicePrice','ServiceDuration']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password','email', 'UserPhone', 'UserAddress','UserSalonName', 'UserInfo']
        write_only_fields = ['password']

class ServicesSerializer(serializers.ModelSerializer):
    # user = serializers.CurrentUserDefault()
    # TechID = serializers.ChoiceField(  choices=Technicians.objects.filter(UserID=user.id).values_list('TechID', 'TechName'), required=False,   allow_null=True)
    class Meta:
        model = Services
        fields = ['ServiceName', 'ServicePrice', 'ServiceStartTime', 'ServiceDuration', 'AppID', 'TechID']        

class AppointmentSerializer(serializers.ModelSerializer):
    ServicesList = ServicesSerializer(many=True, read_only=True, source='services')

    class Meta:
        model = Appointments
        fields = ['AppID', 'AppDate', 'AppStatus','AppTotal', 'PaymentType','ServicesList']

class TechniciansSerializer(serializers.ModelSerializer):
    UserID = UserSerializer(read_only=True).field_name='UserID'
    class Meta:
        model = Technicians
        fields = ['TechID', 'TechName', 'TechEmail', 'TechPhone', 'TechSpecialization', 'TechAvailability', 'TechInfo', 'UserID']
        read_only_fields = ['UserID']
