from rest_framework import serializers
from django.db.models import Sum

from SalonAPI.Main.models import Appointments,SavedServices, Services, Technicians, User




class SavedServicesSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def getSavedServicesByUser(User):
        saved_services = SavedServices.objects.filter(UserID=User)
        return saved_services
    class Meta:
        model = SavedServices
        fields = '__all__'
        read_only_fields = ['UserID']



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'password','email', 'UserPhone', 'UserAddress','UserSalonName', 'UserInfo']

class ServicesSerializer(serializers.ModelSerializer):
    def getAll():
        return Services.objects.all()

    def save(self,data):
        id = data.get('AppID')
        App = Appointments.objects.get(AppID=id)
        Appointments.objects.update(AppTotal=Services.objects.filter(AppID=App).aggregate(Sum('ServicePrice'))['ServicePrice__sum'])
        return super().save()
 
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

    def getAllByUser(User):
        appointments = Appointments.objects.filter(UserID=User).order_by('-AppDate')
        return appointments
    
    def deleteAllByUser(User):
        count = Appointments.objects.filter(UserID=User).delete()
        return count

    class Meta:
        model = Appointments
        fields = ['AppID', 'AppDate', 'AppStatus','AppTotal', 'PaymentType','UserID','Services']

class TechniciansSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def getAllByUser(User):
        return Technicians.objects.filter(UserID=User)
    
    class Meta:
        model = Technicians
        fields = ['TechID', 'TechName', 'TechEmail', 'TechPhone', 'TechSpecialization', 'TechAvailability', 'TechInfo', 'UserID']
