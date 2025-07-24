from rest_framework import serializers
from django.db.models import Sum

from SalonAPI.Main.models import Appointments, Customer,SavedServices, Services, Technicians, User



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'password','email', 'UserPhone', 'UserAddress','UserSalonName', 'UserInfo']
class SavedServicesSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default = serializers.CurrentUserDefault()
    )
    ServiceCode = serializers.CharField()

 

    def getSavedServicesByUser(User):
        saved_services = SavedServices.objects.filter(UserID=User)
        return saved_services
    class Meta:
        model = SavedServices
        fields = '__all__'







    

class ServicesSerializer(serializers.ModelSerializer):
  
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     request = self.context.get('request')
    #     if(request is not None):
    #         self.fields['ServiceCode'] = serializers.ChoiceField(
    #             choices=[       
    #                 (choice) for choice in SavedServices.objects.filter(UserID=request.user.id).values_list('ServiceCode', flat=True)
    #             ],
    #         )
           
    def getAll():
        return Services.objects.all()

    
 
 
    class Meta:
        model = Services
        fields = ['ServiceName', 'ServiceCode', 'ServiceDescription', 'ServicePrice', 'ServiceStartTime', 'ServiceDuration', 'AppID', 'TechID']
        
        
# Get List of customers that is of the current user
class CustomerSlugRelatedField(serializers.SlugRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        return Customer.objects.filter(
            UserID = user.id
         )
    
class AppointmentSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default = serializers.CurrentUserDefault()
    )
    AppStatus = serializers.ReadOnlyField(default='Open')
    AppTotal = serializers.ReadOnlyField(
        default=0)
    PaymentType = serializers.ReadOnlyField(default='')
    Services = ServicesSerializer(many=True, read_only=True)
    CustomerID = CustomerSlugRelatedField(
        slug_field = "CustomerFirstName"
    )





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
    
    def getAppDetails(User,AppID):
        if (Appointments.objects.filter(UserID=User, AppID=AppID).exists()):
            app = Appointments.objects.filter(UserID=User, AppID=AppID)
            return app
        else:
            return None
    
  
    class Meta:
        model = Appointments
        fields = ['AppID', 'AppDate', 'AppStatus','AppTotal', 'PaymentType','UserID','Services','CustomerID']

class TechniciansSerializer(serializers.ModelSerializer):
    UserID = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault()
        , read_only = True
    )
   
    def getAllByUser(User):
        return Technicians.objects.filter(UserID=User)
    
    class Meta:
        model = Technicians
        fields = ['TechID', 'TechName', 'TechEmail', 'TechPhone', 'TechSpecialization', 'TechAvailability', 'TechInfo', 'UserID']


class CustomerSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    Appointments = AppointmentSerializer(many=True,read_only=True)


    def getAll(User):
        return Customer.objects.filter(UserID=User).order_by('CustomerFirstName')
    
    
    def getCustomer(User,CustomerID):
        if (Customer.objects.filter(UserID=User,CustomerID=CustomerID).exists()):
            return Customer.objects.filter(UserID=User,CustomerID=CustomerID)
        else: return None
    
    def getServiceHistory(CustomerID):
        app = AppointmentSerializer.getAppByCustomer(CustomerID)
        app = app.filter(AppStatus = "Closed")
        return app
    
    def getStandingAppointments(CustomerID):
        app = AppointmentSerializer.getAppByCustomer(CustomerID)
        app = app.filter(AppStatus="Open")
        return app
    
    class Meta:
        model = Customer
        fields = ['CustomerID', 'CustomerFirstName', 'CustomerLastName', 'CustomerEmail', 'CustomerPhone', 'CustomerAddress', 'CustomerInfo', 'UserID','Appointments']