from rest_framework import serializers
from django.db.models import Sum

from SalonAPI.Main.models import Appointments,SavedServices, Services, Technicians, User




class SavedServicesSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = SavedServices
        fields = '__all__'
        read_only_fields = ['UserID']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password','email', 'UserPhone', 'UserAddress','UserSalonName', 'UserInfo']
        write_only_fields = ['password']

class ServicesSerializer(serializers.ModelSerializer):

 
    class Meta:
        model = Services
        fields = '__all__'  

class AppointmentSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    AppStatus = serializers.ReadOnlyField(default='Created')
    AppTotal = serializers.ReadOnlyField(
        default=0)
    PaymentType = serializers.ReadOnlyField(default='credit_card')
    Services = ServicesSerializer(many=True, read_only=True)

    class Meta:
        model = Appointments
        fields = ['AppID', 'AppDate', 'AppStatus','AppTotal', 'PaymentType','UserID','Services']

class TechniciansSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Technicians
        fields = ['TechID', 'TechName', 'TechEmail', 'TechPhone', 'TechSpecialization', 'TechAvailability', 'TechInfo', 'UserID']
