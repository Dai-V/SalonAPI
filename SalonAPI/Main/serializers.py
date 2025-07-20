from rest_framework import serializers
from django.db.models import Sum

from SalonAPI.Main.models import Appointments, Customer,SavedServices, Services, Technicians, User




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


class CustomerSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    def getAll(User):
        return Customer.objects.filter(UserID=User).order_by('CustomerFirstName')
    
    def getServiceHistory(CustomerID):
        return AppointmentSerializer.getAppByCustomer(CustomerID)
    
    class Meta:
        model = Customer
        fields = ['CustomerID', 'CustomerFirstName', 'CustomerLastName', 'CustomerEmail', 'CustomerPhone', 'CustomerAddress', 'CustomerInfo', 'UserID']

class ServicesSerializer(serializers.ModelSerializer):
  
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if(request is not None):
            self.fields['ServiceCode'] = serializers.ChoiceField(
                choices=[       
                    (choice) for choice in SavedServices.objects.filter(UserID=request.user.id).values_list('ServiceCode', flat=True)
                ],
            )
           
    def getAll():
        return Services.objects.all()

    def save(self,data):
        return super().save()
    
 
 
    class Meta:
        model = Services
        fields = ['ServiceName', 'ServiceCode', 'ServiceDescription', 'ServicePrice', 'ServiceStartTime', 'ServiceDuration', 'AppID', 'TechID']
        
        

class AppointmentSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    AppStatus = serializers.ReadOnlyField(default='Open')
    AppTotal = serializers.ReadOnlyField(
        default=0)
    PaymentType = serializers.ReadOnlyField(default='Card')
    Services = ServicesSerializer(many=True, read_only=True)
    def getAllByUser(User):
        appointments = Appointments.objects.filter(UserID=User).order_by('-AppDate')
        return appointments
    
    def deleteAllByUser(User):
        count = Appointments.objects.filter(UserID=User).delete()
        return count

    def updateAppTotal(AppID):
        App = Appointments.objects.get(AppID=AppID)
        App.AppTotal = Services.objects.filter(AppID=App).aggregate(Sum('ServicePrice'))['ServicePrice__sum']
        App.save()
        return App 
    
    def getAppByCustomer(CustomerID):
        App = Appointments.objects.filter(CustomerID=CustomerID)
        return App
    class Meta:
        model = Appointments
        fields = ['AppID', 'AppDate', 'AppStatus','AppTotal', 'PaymentType','UserID','Services', 'CustomerID']

class TechniciansSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def getAllByUser(User):
        return Technicians.objects.filter(UserID=User)
    
    class Meta:
        model = Technicians
        fields = ['TechID', 'TechName', 'TechEmail', 'TechPhone', 'TechSpecialization', 'TechAvailability', 'TechInfo', 'UserID']
