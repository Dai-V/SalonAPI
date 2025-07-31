from datetime import date
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions,generics
from rest_framework.renderers import JSONRenderer,BrowsableAPIRenderer,TemplateHTMLRenderer, StaticHTMLRenderer
from django.db.models import Sum, Count, Q
from SalonAPI.Main.models import Appointments, Customer, SavedServices, Schedules, Services, Supplies, Technicians, User
from SalonAPI.Main.serializers import AppointmentSerializer, ChangePasswordSerializer, CreateUserSerializer, CustomerSerializer, LoginUserSerializer, SavedServicesSerializer, SchedulesSerializer, ServicesSerializer, SuppliesSerializer, TechniciansSerializer, UpdateUserSerializer
from django.contrib.auth import authenticate, login,logout
import requests

# Rule of thumb: If it requires UserID, then authenticated users only!
class AppointmentsView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer
    def get_queryset(self):
        return Appointments.objects.filter(UserID=self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}

class AppointmentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

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
        return {"request": self.request}

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
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginUserSerializer
    def post(self, request, format=None):
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                return Response(status=200)
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
    authentication_classes = [authentication.SessionAuthentication]
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
        AppointmentSerializer.updateAppTotal(serializer.validated_data['AppID'].AppID)

    def perform_destroy(self, instance):
        instance.delete()
        AppointmentSerializer.updateAppTotal(instance.AppID.AppID)
        

class TechniciansView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TechniciansSerializer    

    def get_queryset(self):
        return Technicians.objects.filter(UserID=self.request.user)
    
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

class TotalsView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
            # Format is  /api/totals/?StartDate=1997-09-26&EndDate=2025-07-25

            StartDate = request.query_params.get('StartDate', None)
            EndDate = request.query_params.get('EndDate', None)
            if (StartDate is None):
                StartDate = date.today()
            if (EndDate is None):
                EndDate = date.today()
            if StartDate > EndDate:
                return Response(({'message': "Start date can't be later than End Date"}), status=404)
            
            return Response(totals(request,StartDate,EndDate))
    
# Below here is a list of non-view methods for reuse 
# List of totals
def totals(request, StartDate, EndDate):
            total_appointments = AppointmentSerializer.getAllByUser(request.user).filter(AppDate__range=(StartDate,EndDate)).count()
            total_services = ServicesSerializer.getAll().filter(AppID__AppDate__range=(StartDate,EndDate)).count()
            total_technicians = TechniciansSerializer.getAllByUser(request.user).count()
            total_earnings = sum(
                appointment.AppTotal for appointment in AppointmentSerializer.getAllByUser(request.user).filter(AppStatus='Closed', AppDate__range=(StartDate,EndDate))
            )
            total_closed_appointments = AppointmentSerializer.getAllByUser(request.user).filter(AppStatus='Closed', AppDate__range=(StartDate,EndDate)).count()
            total_closed_services = ServicesSerializer.getAll().filter(Q(AppID__AppDate__range=(StartDate,EndDate)) & Q(AppID__AppStatus='Closed')).count()
            total_venmo_appointments = AppointmentSerializer.getAllByUser(request.user).filter(PaymentType='Venmo', AppDate__range=(StartDate,EndDate)).count()
            total_cash_appointments = AppointmentSerializer.getAllByUser(request.user).filter(PaymentType='Cash', AppDate__range=(StartDate,EndDate)).count()
            total_credit_card_appointments = AppointmentSerializer.getAllByUser(request.user).filter(PaymentType='Card', AppDate__range=(StartDate,EndDate)).count()
            total_customers = CustomerSerializer.getAll(request.user).filter(Appointments__AppDate__range=(StartDate,EndDate)).count()
            total_open_appointments = AppointmentSerializer.getAllByUser(request.user).filter(AppDate__range=(StartDate,EndDate)).exclude(AppStatus='Closed').count()
            total_technicians_services = TechniciansSerializer.ServicesDoneByTechnicians(request.user,StartDate,EndDate)
            json = JSONRenderer().render({
                "From" : StartDate,
                "To":EndDate,
                "total_appointments": total_appointments,
                "total_services": total_services,
                "total_technicians": total_technicians,
                "total_customers": total_customers,
                "total_earnings": total_earnings,
                "total_closed_appointments": total_closed_appointments,
                "total_closed_services":total_closed_services,
                "total_venmo_appointments": total_venmo_appointments,   
                "total_cash_appointments": total_cash_appointments,
                "total_credit_card_appointments": total_credit_card_appointments,
                "total_open_appointments":total_open_appointments,
                "total_technicians_services":total_technicians_services,

            })
            return json
    

