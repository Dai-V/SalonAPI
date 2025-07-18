from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.renderers import JSONRenderer
from SalonAPI.Main.serializers import AppointmentSerializer, SavedServicesSerializer, ServicesSerializer, TechniciansSerializer, UserSerializer

class AppointmentsView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get(self, request):
        appointments = AppointmentSerializer.getAllByUser(request.user)
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
        deleteCount = AppointmentSerializer.deleteAllByUser(request.user)[0]
        json = JSONRenderer().render({"message": str(deleteCount) + " appointment(s) deleted successfully."} )
        return Response(json)

class SavedServicesView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedServicesSerializer

    # Get all saved services, if none exist, create some default services
    def get(self, request):    
        if (request.user.is_authenticated):
            saved_services = SavedServicesSerializer.getSavedServicesByUser(request.user)
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
    
class ServicesView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServicesSerializer

    def get(self, request):
         if (request.user.is_authenticated):    
            services = ServicesSerializer.getAll()
            serializer = ServicesSerializer(services, many=True, context={'request': request}  )
            json = JSONRenderer().render(serializer.data)
            return Response(json)
         else:
            return Response({"message": "User not authenticated."}, status=401)
    
    def post(self, request):
         if (request.user.is_authenticated):       
            serializer = ServicesSerializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save(data=request.data)
                json = JSONRenderer().render(serializer.data)  
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
            technicians = TechniciansSerializer.getAllByUser(request.user)
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

        
    

