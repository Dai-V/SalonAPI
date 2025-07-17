from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.db.models import Sum

from SalonAPI.Main.models import Appointments, SavedServices, Services, Technicians, User
from SalonAPI.Main.serializers import AppointmentSerializer, SavedServicesSerializer, ServicesSerializer, TechniciansSerializer, UserSerializer

class AppointmentsView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get(self, request):
        appointments = Appointments.objects.filter(UserID=request.user.id).order_by('-AppDate')
        serializer = AppointmentSerializer(appointments, many=True)
        json = JSONRenderer().render(serializer.data)
        return Response(json)
    
    def post(self, request):
        serializer = AppointmentSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            json = JSONRenderer().render(serializer.data)
            return Response(json, status=201)
        return Response(serializer.errors, status=400)
   

    
    
    def delete(self, request):
        Appointments.objects.filter(UserID=request.user).delete()
        json = JSONRenderer().render({"message": "All appointments and services deleted successfully."})
        return Response(json)

class SavedServicesView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedServicesSerializer

    # Get all saved services, if none exist, create some default services
    def get(self, request):    
        if (request.user.is_authenticated):
            saved_services = SavedServices.objects.filter(UserID=request.user.id)
            serializer = SavedServicesSerializer(saved_services, many=True)
            json = JSONRenderer().render(serializer.data)
            return Response(json)
        else:
            return Response({"message": "User not authenticated."}, status=401)
    
    # Add a new saved service
    # Ensure that the service name is unique
    def post(self, request):
        if( request.user.is_authenticated):
                serializer = SavedServicesSerializer(data=request.data, context={'request':request})
                if serializer.is_valid():
                    serializer.save()
                    json = JSONRenderer().render(serializer.data)
                    return Response(json, status=201)
                return Response(serializer.errors, status=400)
        else:
            return Response({"message": "User not authenticated."}, status=401)
    

class UserView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]

    serializer_class = UserSerializer
    def get(self, request):
        user = User.objects.filter(id=request.user.id).first()
        serializer = UserSerializer(user)
        json = JSONRenderer().render(serializer.data)
        return Response(json)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            json = JSONRenderer().render(serializer.data)
            return Response(json, status=201)
        return Response(serializer.errors, status=400)
    
class ServicesView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServicesSerializer

    def get(self, request):
         if (request.user.is_authenticated):    
            services = Services.objects.all()
            serializer = ServicesSerializer(services, many=True, context={'request': request})
            json = JSONRenderer().render(serializer.data)
            return Response(json)
         else:
            return Response({"message": "User not authenticated."}, status=401)
    
    def post(self, request):
         if (request.user.is_authenticated):       
            serializer = ServicesSerializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                AppID = serializer.data.get('AppID')
                json = JSONRenderer().render(serializer.data)
                app = Appointments.objects.filter(AppID=AppID).update(AppTotal=Services.objects.filter(AppID=AppID).aggregate(Sum('ServicePrice'))['ServicePrice__sum'])
                return Response(json, status=201)
            return Response(serializer.errors, status=400)
         else:
            return Response({"message": "User not authenticated."}, status=401)
    
   
class TechniciansView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = TechniciansSerializer    
    def get(self, request):
        if (request.user.is_authenticated):    
            technicians = Technicians.objects.filter(UserID=request.user.id)
            serializer = TechniciansSerializer(technicians, many=True)
            json = JSONRenderer().render(serializer.data)
            return Response(json)
        else:
             return Response({"message": "User not authenticated."}, status=401)
    
    def post(self, request):
        if (request.user.is_authenticated):
            serializer = TechniciansSerializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                json = JSONRenderer().render(serializer.data)
                return Response(json, status=201)
            return Response(serializer.errors, status=400)
        else :
            return Response({"message": "User not authenticated."}, status=401)

        
    

