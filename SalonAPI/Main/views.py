from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.renderers import JSONRenderer
from SalonAPI.Main.serializers import AppointmentSerializer, CustomerSerializer, SavedServicesSerializer, ServicesSerializer, TechniciansSerializer, UserSerializer

class AppointmentsView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get(self, request):
        appointments = AppointmentSerializer.getAllByUser(request.user)
        serializer = AppointmentSerializer(appointments)
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
    
class AppointmentDetailsView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get(self,request,AppID):
        app = AppointmentSerializer.getAppDetails(request.user,AppID)
        if (app is not None):
            serializer = AppointmentSerializer(app, many=True)
            json = JSONRenderer().render(serializer.data)
            return Response(json)
        return Response({"message": "Appointment does not exist for the requesting account"}, status=404)
    
    def put(self,request,AppID):
        app = AppointmentSerializer.getAppDetails(request.user,AppID)
        if (app is not None):
            data = request.data
            data['AppID'] = AppID
            serializer = AppointmentSerializer(data=data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                json = JSONRenderer().render(serializer.data)
                return Response(json,status=201)
            return Response(serializer.errors, status=400)
        return Response({"message": "Appointment does not exist for the requesting account"}, status=404)
        
            
    

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
    

class CustomerView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerSerializer

    def get(self, request):
        if( request.user.is_authenticated):
            customers = CustomerSerializer.getAll(request.user)
            serializer = CustomerSerializer(customers, many=True, context={'request': request})
            json = JSONRenderer().render(serializer.data)
        else:
            json = JSONRenderer().render({"message": "User not authenticated."}, status=401)
        return Response(json)
    
    def post(self, request):
        if (request.user.is_authenticated):
            serializer = CustomerSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                json = JSONRenderer().render(serializer.data)
                return Response(json, status=201)
            return Response(serializer.errors, status=400)
        else:
            return Response({"message": "User not authenticated."}, status=401)
    
class ServicesView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServicesSerializer


    def get(self, request):
         if (request.user.is_authenticated):    
            services = ServicesSerializer.getAll()
            serializer = ServicesSerializer(services, many=True, context={'request': request} )
            json = JSONRenderer().render(serializer.data)
            return Response(json)
         else:
            return Response({"message": "User not authenticated."}, status=401)
    
    def post(self, request):
         serializer = ServicesSerializer(data=request.data, context={'request':request})
         if (request.user.is_authenticated):       
            if serializer.is_valid():
                serializer.save(data=request.data)
                json = JSONRenderer().render(serializer.data) 
                AppointmentSerializer.updateAppTotal(serializer.data['AppID'])
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
        
class TotalsView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if (request.user.is_authenticated):
            total_appointments = AppointmentSerializer.getAllByUser(request.user).count()
            total_services = ServicesSerializer.getAll().count()
            total_technicians = TechniciansSerializer.getAllByUser(request.user).count()
            total_earnings = sum(
                appointment.AppTotal for appointment in AppointmentSerializer.getAllByUser(request.user)
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

        
    

