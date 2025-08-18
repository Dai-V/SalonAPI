from rest_framework import serializers
from django.db.models import Sum, Count, Q
from SalonAPI.Main.models import Appointments, Customer,SavedServices, Schedules, Services, Supplies, Technicians, User

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            # email = validated_data['email'],
            # UserPhone = validated_data['UserPhone'],
            # UserAddress = validated_data['UserAddress'],
            # UserSalonName = validated_data['UserSalonName'],
            # UserInfo = validated_data['UserInfo'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    class Meta:
        model = User
        fields = ['id', 'username', 'password','email', 'UserPhone', 'UserAddress','UserSalonName', 'UserInfo']

class LoginUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    class Meta:
        model = User
        fields = ['id', 'username', 'password']

class UpdateUserSerializer(serializers.ModelSerializer):
    last_login = serializers.ReadOnlyField()
    date_joined = serializers.ReadOnlyField()

    class Meta:
        model = User
        exclude = ['password','groups','user_permissions','is_superuser','is_staff','is_active','UserInfo']

class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate_old_password(self,value):
        user = User.objects.get(id=self.context.get('request').user.id)
        if (not user.check_password(value)):
             raise serializers.ValidationError('Wrong password')
        return value
    
    def validate(self,data):
        if (data['confirm_new_password']!=data['new_password'] ):
            raise serializers.ValidationError('Password confirmation does not match')
        return data
    
    def save(self):
        password = self.validated_data['new_password']
        user = User.objects.get(id=self.context.get('request').user.id)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ['old_password','new_password','confirm_new_password']
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ['password']

class SavedServicesSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default = serializers.CurrentUserDefault()
    )
    ServiceDuration = serializers.IntegerField(min_value=0, default = 0)
    def validate_ServiceCode(self,value):
        count = 0
        if (self.context.get('request').method=="PUT"):
                count = SavedServices.objects.filter(UserID=self.context.get('request').user.id, ServiceCode=value).exclude(ServiceID=self.context.get('serviceID')).count()
        elif (self.context.get('request').method=="POST"):
                count = SavedServices.objects.filter(UserID=self.context.get('request').user.id, ServiceCode=value).count()
        if (count > 0):
                    raise serializers.ValidationError('This service code already in use')
        return value
         
    def getSavedServicesByUser(User):
        saved_services = SavedServices.objects.filter(UserID=User)
        return saved_services
    
    class Meta:
        model = SavedServices
        fields = '__all__'

class ServicesSerializer(serializers.ModelSerializer):
    ServiceDuration = serializers.IntegerField(min_value=0, default = 0)
    AppID = serializers.PrimaryKeyRelatedField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if(request is not None):
            self.fields['ServiceCode'] = serializers.ChoiceField(
                choices=[       
                    (choice) for choice in SavedServices.objects.filter(UserID=request.user.id).values_list('ServiceCode', flat=True)
                ],
            )
    

    # def validate_TechID(self,value):
    #     # Check if the newest schedule of the technician that overlaps with AppDate is available.
    #     print (self.initial_data)
    #     AppDate = Appointments.objects.filter(AppID = self.initial_data['AppID']).values('AppDate')
    #     Availability = Schedules.objects.filter(TechID=value,To__gte=AppDate,From__lte=AppDate).values_list('Availability',flat=True).order_by('-Created_At').first()
    #     if not Availability: # Also includes those without a schedule set
    #         raise serializers.ValidationError('This techinician is not on the schedule that day')
    #     else:
    #         return value
    
    def getAll():
        return Services.objects.all()

    class Meta:
        model = Services
        fields = ['ServiceName', 'ServiceCode', 'ServiceDescription', 'ServicePrice', 'ServiceStartTime', 'ServiceDuration',  'TechID','AppID']
        
        
# Get List of customers that is of the current user
class CustomerPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        return Customer.objects.filter(
            UserID = user.id
         )
    
class AppointmentSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default = serializers.CurrentUserDefault()
    )
    # Open (Created), Pending (Checked In), Closed (Paid), Voided, Cancelled
    AppStatus = serializers.ChoiceField(default='Open',
    choices=[
        'Open', 'Closed', 'Voided', 'Cancelled', 'Pending'
    ]
    )
    AppTotal = serializers.ReadOnlyField(
        default=0)
    PaymentType = serializers.CharField(default='')
    Services = ServicesSerializer(many=True)
    CustomerID = CustomerPrimaryKeyRelatedField( 
    )

    # To create appointment and services that are included at the same time
    def create(self, validated_data):
        services = validated_data.pop('Services')
        appointment = Appointments.objects.create(**validated_data)
        print (appointment)
        for service in services:
            Services.objects.create(AppID=appointment,**service)
        return AppointmentSerializer.updateAppTotal(appointment.AppID)
    
    def update(self, instance, validated_data):
        services = validated_data.pop('Services')
        super().update(instance, validated_data)
        # Since Services doesn't have a unique identifier, we delete all services in the app and just create new ones. Might cause troubles in the future but we'll see
        Services.objects.filter(AppID=instance).delete()
        for service in services:
                Services.objects.create(AppID=instance,**service)
        return AppointmentSerializer.updateAppTotal(instance.AppID)

   
    def validate(self,data):
        for service in data['Services']:
            # Check if the newest schedule of the technician that overlaps with AppDate is available.
            Availability = Schedules.objects.filter(TechID=service['TechID'],To__gte=data['AppDate'],From__lte=data['AppDate']).values_list('Availability',flat=True).order_by('-Created_At').first()
            if not Availability: # Also includes those without a schedule yet as unavailable
                raise serializers.ValidationError('The techinician: ' + service['TechID'].TechName + ' is not on the schedule that day')
        return data


    def getAllByUser(User):
        appointments = Appointments.objects.filter(UserID=User).order_by('-AppDate')
        return appointments
    
    def deleteAllByUser(User):
        count = Appointments.objects.filter(UserID=User).delete()
        return count

    def updateAppTotal(AppID):
        App = Appointments.objects.get(AppID=AppID)
        AppTotal =  Services.objects.filter(AppID=App).aggregate(Sum('ServicePrice'))['ServicePrice__sum']
        if (AppTotal is not None):
            App.AppTotal = AppTotal
        else: App.AppTotal = 0
        App.save()
        return App 
    
    
    # def getStandingAppointments(UserID, CustomerID):
    #     app = Appointments.objects.filter(UserID = UserID,CustomerID=CustomerID, AppStatus="Open")
    #     return app
    
    # def getAppointmentHistory(UserID, CustomerID):
    #     app = Appointments.objects.filter(UserID = UserID,CustomerID=CustomerID, AppStatus="Closed")
    #     return app
  
    class Meta:
        model = Appointments
        fields = ['AppID', 'AppDate', 'AppStatus','AppTotal','AppComment', 'PaymentType','UserID','Services','CustomerID']

class TechniciansSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    Services = ServicesSerializer(many=True, read_only=True)



    def getAllByUser(User): 
        return Technicians.objects.filter(UserID=User)
    
    def ServicesDoneByTechnicians(User, StartDate,EndDate):
        # For every technician, show the total amount of services and payment of those services between Start Date and End Date
        query = Technicians.objects.filter(UserID=User).select_related('Technicians','Appointments','Services').values('TechName').annotate(total_services=Count('Services', filter = Q(Services__AppID__AppDate__range=(StartDate,EndDate)) & Q(Services__AppID__AppStatus='Closed')), total_payment=Sum('Services__ServicePrice', filter = Q(Services__AppID__AppDate__range=(StartDate,EndDate)) & Q(Services__AppID__AppStatus='Closed'))).order_by('TechName')
        # Show 0 instead of Null
        for tech in query:
            if (tech['total_payment'] is None):
                tech['total_payment'] = 0

        return query
            
    class Meta:
        model = Technicians
        fields = ['TechID', 'TechName', 'TechEmail', 'TechPhone', 'TechInfo', 'Services', 'UserID']

class SchedulesSerializer(serializers.ModelSerializer):
    Created_At = serializers.ReadOnlyField()
    class Meta:
        model = Schedules
        fields = ['ScheduleID','From','To','Availability','Created_At', 'TechID']


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
    
    
    class Meta:
        model = Customer
        fields = ['CustomerID', 'CustomerFirstName', 'CustomerLastName', 'CustomerEmail', 'CustomerPhone', 'CustomerAddress', 'CustomerInfo', 'UserID','Appointments']


class SuppliesSerializer(serializers.ModelSerializer):
    UserID = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    Created_At = serializers.ReadOnlyField()
    Last_Modified = serializers.ReadOnlyField()
    class Meta:
        model = Supplies
        fields = ['SupplyID','SupplyName','Created_At','Last_Modified','Quantity','Cost','UserID']