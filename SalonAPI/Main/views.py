from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.db.models import Sum

from SalonAPI.Main.models import Appointments, SavedServices, Services, User
from SalonAPI.Main.serializers import AppointmentSerializer, SavedServicesSerializer, ServicesSerializer, UserSerializer

class AppointmentsView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):
        if not Appointments.objects.exists(): # Seed data if no appointments exist
            app = Appointments.objects.create(AppStatus="Scheduled")
            UserID = User.objects.get(id=1)
            if ( SavedServices.objects.filter(ServiceName="Basic Service").first()):
                SavedService1 = SavedServices.objects.filter(ServiceName="Basic Service").first()
            else: 
                SavedServices.objects.create(ServiceName="Basic Service", ServicePrice=100.00, ServiceDuration=30)
            
            if ( SavedServices.objects.filter(ServiceName="Premium Service").first()):
                SavedService2 = SavedServices.objects.filter(ServiceName="Premium Service").first()
            else: 
                SavedServices.objects.create(ServiceName="Premium Service", ServicePrice=200.00, ServiceDuration=60)
            
            Services.objects.create(ServiceName=SavedService1.ServiceName, ServicePrice=SavedService1.ServicePrice,   ServiceDuration=SavedService1.ServiceDuration, AppID=app, UserID=UserID)
            Services.objects.create(ServiceName=SavedService2.ServiceName, ServicePrice=SavedService2.ServicePrice,   ServiceDuration=SavedService2.ServiceDuration, AppID=app, UserID=UserID)
            app = Appointments.objects.filter(AppID=app.AppID).update(AppTotal=Services.objects.filter(AppID=app).aggregate(Sum('ServicePrice'))['ServicePrice__sum'])
        appointments = Appointments.objects.all()
        serializer = AppointmentSerializer(appointments, many=True)
        json = JSONRenderer().render(serializer.data)
        return Response(json)
    
    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            json = JSONRenderer().render(serializer.data)
            return Response(json, status=201)
        return Response(serializer.errors, status=400)
   

    
    
    def delete(self, request):
        Appointments.objects.all().delete()
        json = JSONRenderer().render({"message": "All appointments and services deleted successfully."})
        return Response(json)

class SavedServicesView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]


    # Get all saved services, if none exist, create some default services
    def get(self, request):    
        if not SavedServices.objects.exists():
                SavedServices.objects.create(ServiceName="Basic Service", ServicePrice=100.00, ServiceDuration=30)
                SavedServices.objects.create(ServiceName="Premium Service", ServicePrice=200.00, ServiceDuration=60)
        saved_services = SavedServices.objects.all()
        serializer = SavedServicesSerializer(saved_services, many=True)
        json = JSONRenderer().render(serializer.data)
        return Response(json)
    
    # Add a new saved service
    # Ensure that the service name is unique
    def post(self, request):
        if (not SavedServices.objects.filter(ServiceName=request.data.get('ServiceName')).exists()):
            serializer = SavedServicesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                json = JSONRenderer().render(serializer.data)
                return Response(json, status=201)
            return Response(serializer.errors, status=400)
        else: return Response({"message": "Service already exists."}, status=400)
    

class UserView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]


    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        json = JSONRenderer().render(serializer.data)
        return Response(json)
    
    def post(self, request):
        if (not User.objects.filter(username=request.data.get('username')).exists()):
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                json = JSONRenderer().render(serializer.data)
                return Response(json, status=201)
            return Response(serializer.errors, status=400)
        else : return Response({"message": "Username already taken."}, status=400)
    
class ServicesView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        services = Services.objects.all()
        serializer = ServicesSerializer(services, many=True)
        json = JSONRenderer().render(serializer.data)
        return Response(json)
    
   


        
    

