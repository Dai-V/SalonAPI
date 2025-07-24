from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions,generics
from rest_framework.renderers import JSONRenderer
from SalonAPI.Main.models import Appointments, Customer, SavedServices, Services, Technicians
from SalonAPI.Main.serializers import AppointmentSerializer, CustomerSerializer, SavedServicesSerializer, ServicesSerializer, TechniciansSerializer, UserSerializer

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
    
    # Ensure that the service name is unique
    def post(self, request, *args, **kwargs):
        print(request.data)
        if (not SavedServices.objects.filter(UserID=request.user.id, ServiceCode=request.data['ServiceCode']).exists()):
            return self.create(request, *args, **kwargs)
        else:
            return Response({"message": "Service Code already in use."}, status=401)
        
class SavedServiceDetailsView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedServicesSerializer
    def get_queryset(self):
        return SavedServices.objects.filter(UserID=self.request.user)

class UserView(APIView):

    serializer_class = UserSerializer
    def get(self, request):
        serializer = UserSerializer(request.user)
        json = JSONRenderer().render(serializer.data)
        return Response(json)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            json = JSONRenderer().render(serializer.data)
            return Response(json, status=201)
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
    
class ServicesView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServicesSerializer
    
    def get_queryset(self):
        return Services.objects.filter(AppID__UserID=self.request.user)

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

class TotalsView(generics.GenericAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if (request.user.is_authenticated):
            total_appointments = AppointmentSerializer.getAllByUser(request.user).count()
            total_services = ServicesSerializer.getAll().count()
            total_technicians = TechniciansSerializer.getAllByUser(request.user).count()
            total_earnings = sum(
                appointment.AppTotal for appointment in AppointmentSerializer.getAllByUser(request.user).filter(AppStatus='Closed')
            )
            total_closed_appointments = AppointmentSerializer.getAllByUser(request.user).filter(AppStatus='Closed').count()
            total_venmo_appointments = AppointmentSerializer.getAllByUser(request.user).filter(PaymentType='Venmo').count()
            total_cash_appointments = AppointmentSerializer.getAllByUser(request.user).filter(PaymentType='Vash').count()
            total_credit_card_appointments = AppointmentSerializer.getAllByUser(request.user).filter(PaymentType='Card').count()
            total_customers = CustomerSerializer.getAll(request.user).count()
            json = JSONRenderer().render({
                "total_appointments": total_appointments,
                "total_services": total_services,
                "total_technicians": total_technicians,
                "total_customers": total_customers,
                "total_earnings": total_earnings,
                "total_closed_appointments": total_closed_appointments,
                "total_venmo_appointments": total_venmo_appointments,   
                "total_cash_appointments": total_cash_appointments,
                "total_credit_card_appointments": total_credit_card_appointments,

            })
            return Response(json)
        else:
            return Response({"message": "User not authenticated."}, status=401)