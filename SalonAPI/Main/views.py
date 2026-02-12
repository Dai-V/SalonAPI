from datetime import date
import json
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions,generics
from rest_framework.renderers import JSONRenderer,BrowsableAPIRenderer,TemplateHTMLRenderer, StaticHTMLRenderer
from django.db.models import Sum, Count, Q, Min, Max, Avg
from django.db.models.functions import Extract
from SalonAPI.Main.models import Appointments, Customer, SavedServices, Schedules, Services, Supplies, Technicians, User
from SalonAPI.Main.serializers import AppointmentGetSerializer, AppointmentPostSerializer, ChangePasswordSerializer, CreateUserSerializer, CustomerSerializer, LoginUserSerializer, SavedServicesSerializer, SchedulesSerializer, ServicesSerializer, SuppliesSerializer, TechniciansSerializer, UpdateUserSerializer
from django.contrib.auth import authenticate, login,logout
from django.middleware.csrf import get_token
import requests

# Rule of thumb: If it requires UserID, then authenticated users only!
# Get Appointments of a certain date. All appointments if no date is set
class AppointmentsView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        # /api/appointments/?Date=1997-09-26
        Date = self.request.query_params.get('Date', None)
        if (Date is None):
                return Appointments.objects.filter(UserID=self.request.user.id).exclude(AppStatus="Cancelled")
        return Appointments.objects.filter(UserID=self.request.user.id,AppDate=Date).exclude(AppStatus="Cancelled")
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentPostSerializer
        return AppointmentGetSerializer

    def get_serializer_context(self):
        return {"request": self.request}
    

class AppointmentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return AppointmentPostSerializer
        return AppointmentGetSerializer

    def get_queryset(self):
        return Appointments.objects.filter(UserID=self.request.user)


class SavedServicesView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedServicesSerializer

    def get_queryset(self):
        return SavedServices.objects.filter(UserID=self.request.user)
    
    def get_serializer_context(self):
        return {"request": self.request}
    
        
        
class SavedServiceDetailsView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedServicesSerializer

    def get_queryset(self):
        return SavedServices.objects.filter(UserID=self.request.user)
    
    def get_serializer_context(self):
        return {"request": self.request, "serviceID" : self.kwargs['pk']}

# User profile view that allows an user to update their infos. Not for admin use
class UserView(generics.RetrieveUpdateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateUserSerializer 
    queryset = User.objects.all()

    def get_object(self):
        user = get_object_or_404(User, id=self.request.user.id)
        return user

    
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginUserSerializer


    def post(self, request):
        data = request.data
        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                response = JsonResponse({'detail': 'CSRF cookie set'})
                response['X-CSRFToken'] = get_token(request)
                response.status_code = 200
                return response
            else:
                return Response(status=404)
        else:
            return Response(status=404)
        
class LogoutView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': "Logout successful"})
        

class SignupView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = CreateUserSerializer

    def get(self,request):
        return Response()
    
    def post(self,request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer._errors, status=400)

class ChangePasswordView(generics.UpdateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    def get_object(self):
            user = self.request.user
            return user
    
    def get_serializer_context(self):
        return {"request": self.request}

    def update(self, request):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Password change success! Log in with your new password"}, status=200)

            return Response(serializer.errors, status=400)   
class CustomerView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerSerializer
    def get_queryset(self):
        return Customer.objects.filter(UserID=self.request.user)

class CustomerDetailsView(generics.RetrieveUpdateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerSerializer
    def get_queryset(self):
        return Customer.objects.filter(UserID=self.request.user)
    
# class CustomerStandingAppointmentView(generics.ListAPIView):
#     authentication_classes = [authentication.SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = AppointmentSerializer
#     def get_queryset(self, *args, **kwargs):
#         CustomerID = self.kwargs['pk']
#         return Appointments.objects.filter(UserID = self.request.user,CustomerID=CustomerID, AppStatus="Open")
    
class CustomerAppointmentHistoryView(generics.ListAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentGetSerializer
    def get_queryset(self, *args, **kwargs):
        CustomerID = self.kwargs['pk']
        return Appointments.objects.filter(UserID = self.request.user,CustomerID=CustomerID)
    
class ServicesView(generics.ListAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServicesSerializer


    
    def get_queryset(self):
        return Services.objects.filter(AppID__UserID=self.request.user)
    
    def get_serializer_context(self):
        return {"request": self.request}


class ServiceDetailsView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServicesSerializer

    def get_queryset(self):
        return Services.objects.filter(AppID__UserID=self.request.user)
    
    def get_serializer_context(self):
        return {"request": self.request}
        
    def perform_update(self, serializer):
        serializer.save()
        AppointmentPostSerializer.updateAppTotal(serializer.validated_data['AppID'].AppID)

    def perform_destroy(self, instance):
        instance.delete()
        AppointmentPostSerializer.updateAppTotal(instance.AppID.AppID)
        

class TechniciansView(generics.ListCreateAPIView):
    serializer_class = TechniciansSerializer    
    def get_queryset(self):
        Date = self.request.query_params.get('Date', None)
        if (Date is None):
            return Technicians.objects.filter(UserID=self.request.user.id)
        else:
            techs = Technicians.objects.filter(UserID=self.request.user.id)
            for tech in techs:
                Availability = Schedules.objects.filter(TechID=tech,To__gte=Date,From__lte=Date).values_list('Availability',flat=True).order_by('-Created_At').first()
                if not Availability:
                    techs = techs.exclude(TechID=tech.TechID)
            return techs
    def get_serializer_context(self):
        return {"request": self.request}
    
        
class TechnicianDetailsView(generics.RetrieveUpdateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TechniciansSerializer 
   
    def get_queryset(self):
        return Technicians.objects.filter(UserID=self.request.user)
    
    def get_serializer_context(self):
        return {"request": self.request}
    
class TechnicianSchedulesView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SchedulesSerializer 
   
    def get_queryset(self):
        TechID = self.kwargs['pk']
        return Schedules.objects.filter(TechID__UserID=self.request.user, TechID = TechID)
    
    def get_serializer_context(self):
        return {"request": self.request}
    
class TechnicianServiceHistoryView(generics.ListAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentGetSerializer

    def get_queryset(self, *args, **kwargs):
        TechID = self.kwargs['pk']
        return Appointments.objects.filter(UserID=self.request.user, Services__TechID=TechID).distinct()
    
class SchedulesView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SchedulesSerializer 
   
    def get_queryset(self):
        return Schedules.objects.filter(TechID__UserID=self.request.user)
    
    def get_serializer_context(self):
        return {"request": self.request}
    
class SuppliesView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SuppliesSerializer 
   
    def get_queryset(self):
        return Supplies.objects.filter(UserID=self.request.user).order_by('SupplyName')
    
    def get_serializer_context(self):
        return {"request": self.request}
    
class SupplyDetailsView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SuppliesSerializer 
   
    def get_queryset(self):
        return Supplies.objects.filter(UserID=self.request.user).order_by('SupplyName')
    
    def get_serializer_context(self):
        return {"request": self.request}

# class TotalsView(APIView):
#     authentication_classes = [authentication.SessionAuthentication]
#     permission_classes = [permissions.IsAuthenticated]
    
#     def get(self, request):
#             # Format is  /api/totals/?StartDate=1997-09-26&EndDate=2025-07-25

#             StartDate = request.query_params.get('StartDate', None)
#             EndDate = request.query_params.get('EndDate', None)
#             if (StartDate is None):
#                 StartDate = date.today()
#             if (EndDate is None):
#                 EndDate = date.today()
#             if StartDate > EndDate:
#                 return Response(({'message': "Start date can't be later than End Date"}), status=404)
            
#             return Response(totals(request,StartDate,EndDate))
    
# Below here is a list of non-view methods for reuse 
# List of totals
# def totals(request, StartDate, EndDate):
#             Appointments =  AppointmentGetSerializer.getAllByUser(request.user).filter(AppDate__range=(StartDate,EndDate))
#             OpenAppointments = AppointmentGetSerializer.getAllByUser(request.user).filter(AppDate__range=(StartDate,EndDate)).exclude(AppStatus='Closed')
#             ClosedAppointments = AppointmentGetSerializer.getAllByUser(request.user).filter(AppStatus='Closed', AppDate__range=(StartDate,EndDate))
#             TotalEarningsByPaymentType = ClosedAppointments.values('PaymentType').annotate(TotalPayments=Sum('AppTotal',distinct=True )).order_by('-TotalPayments')
#             ClosedServices = Services.objects.filter(Q(AppID__AppDate__range=(StartDate,EndDate)) & Q(AppID__AppStatus='Closed') & Q(AppID__UserID=request.user))
#             Customers =  CustomerSerializer.getAll(request.user).filter(Appointments__AppDate__range=(StartDate,EndDate))
#             CountAppointments = Appointments.count()
#             CountServices = ServicesSerializer.getAll().filter(AppID__AppDate__range=(StartDate,EndDate)).count()
#             CountTechnicians = TechniciansSerializer.getAvailableByUser(request.user,StartDate,EndDate).count()
#             TotalEarnings = sum(
#                 appointment.AppTotal for appointment in AppointmentSerializer.getAllByUser(request.user).filter(AppStatus='Closed', AppDate__range=(StartDate,EndDate))
#             )
#             CountClosedAppointments = ClosedAppointments.count()
#             CountClosedServices = ClosedServices.count()
#             CountCustomers = Customers.count()
#             CountOpenAppointments = OpenAppointments.count()
#             TotalServicesByTechnicians = TechniciansSerializer.ServicesDoneByTechnicians(request.user,StartDate,EndDate)
#             TotalsByServices = ServicesSerializer.TotalsByServices(request.user,StartDate,EndDate)
#             json = JSONRenderer().render({
#                 'From' : StartDate,
#                 "To":EndDate,
#                  "CountAppointments": CountAppointments,
#                  "CountServices": CountServices,
#                  "CountTechnicians": CountTechnicians,
#                  "TotalEarnings":TotalEarnings,
#                  "TotalEarningsByPaymentType":TotalEarningsByPaymentType,
#                  "CountClosedAppointments":CountClosedAppointments,
#                  "CountClosedServices": CountClosedServices,
#                  "CountCustomers":CountCustomers,
#                  "CountOpenAppointments":CountOpenAppointments,
#                  "TotalServicesByTechnicians":TotalServicesByTechnicians,
#                  "TotalsByServices":TotalsByServices,
#             })
#             return json

class DashboardView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
            # Format is  /api/dashboard/?StartDate=1997-09-26&EndDate=2025-07-25

            StartDate = request.query_params.get('StartDate', None)
            EndDate = request.query_params.get('EndDate', None)
            if (StartDate is None):
                StartDate = date.today()
            if (EndDate is None):
                EndDate = date.today()
            if StartDate > EndDate:
                return Response(({'message': "Start date can't be later than End Date"}), status=400)
            
            return Response(getDashBoard(request,StartDate,EndDate))
    
def getDashBoard(request, StartDate, EndDate):
            TopServices = Services.objects.filter(AppID__AppDate__range=(StartDate,EndDate),  AppID__UserID=request.user).values('ServiceName').annotate(Count=Count('ServiceName')).order_by('-Count')[:4]
            ServiceCount = Services.objects.filter(AppID__AppDate__range=(StartDate,EndDate),  AppID__UserID=request.user).count()

            AppointmentCountByStatus = Appointments.objects.filter(AppDate__range=(StartDate,EndDate), UserID=request.user).values('AppStatus').annotate(Count=Count('AppStatus')).order_by('-Count')
            EarnedTotals = Appointments.objects.filter(AppDate__range=(StartDate,EndDate), UserID=  request.user, AppStatus='Closed').aggregate(Total=Sum('AppTotal'))['Total']
            AppointmentAverage = Appointments.objects.filter(AppDate__range=(StartDate, EndDate), UserID=request.user,AppStatus='Closed').aggregate(Avg=Avg('AppTotal'),Max=Max('AppTotal'),Min=Min('AppTotal'))
            DailyRevenueAverage = Appointments.objects.filter(AppDate__range=(StartDate, EndDate), UserID=request.user, AppStatus='Closed').values('AppDate').annotate(Total=Sum('AppTotal')).aggregate(Avg=Avg('Total'),Max=Max('Total'),Min=Min('Total'))
            TotalsByDayOfWeek = Appointments.objects.filter(AppDate__range=(StartDate,EndDate), UserID=request.user, AppStatus='Closed').annotate(DayOfWeek=Extract('AppDate', 'week_day')).values('DayOfWeek').annotate(Total=Sum('AppTotal')).order_by('DayOfWeek')
            TechTotalsByDate = Services.objects.filter(AppID__AppDate__range=(StartDate,EndDate), AppID__UserID=request.user).values('TechID__TechName').annotate(Total=Sum('ServicePrice')).order_by('-Total')
            return ({
                'From' : StartDate,
                "To":EndDate,
                "ServiceCount": ServiceCount,
                "TopServices": TopServices, 
                "AppointmentCountByStatus": AppointmentCountByStatus,
                "EarnedTotals": EarnedTotals,
                "AppointmentAverage": AppointmentAverage,
                "DailyRevenueAverage": DailyRevenueAverage,
                "TechTotalsByDate": TechTotalsByDate,
                "TotalsByDayOfWeek": TotalsByDayOfWeek,
            })


class IsLoggedIn(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self,request):
        print(request.user)
        if (request.user.is_authenticated):
            response = JsonResponse({'detail': 'CSRF cookie set', 'X-CSRFToken': get_token(request)})
            response.status_code = 200
            return response
        else:
            return Response(status=401)

    