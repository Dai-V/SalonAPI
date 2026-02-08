"""
URL configuration for FunApi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from SalonAPI.Main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/appointments/', views.AppointmentsView.as_view(), name='appointments'),
    path('api/appointments/<int:pk>/',views.AppointmentDetailsView.as_view(), name='appointment_details'),
    path('api/savedservices/', views.SavedServicesView.as_view(), name='saved_services'),
    path('api/savedservices/<int:pk>/', views.SavedServiceDetailsView.as_view(), name='saved_service_details'),
    path('api/services/', views.ServicesView.as_view(), name='services'),
    path('api/services/<int:pk>/', views.ServiceDetailsView.as_view(), name='service_details'),
    # path('api/totals/', views.TotalsView.as_view(), name='totals'),
    # path('api/dashboard/',views.DashboardView.as_view(),name='dashboard'),  
    path('api/profile/',views.UserView.as_view(), name='profile'),
    path('api/technicians/', views.TechniciansView.as_view(), name='technicians'),
    path('api/technicians/<int:pk>/', views.TechnicianDetailsView.as_view(), name='technician_details'),
    path('api/technicians/<int:pk>/schedules/', views.TechnicianSchedulesView.as_view(), name='technician_schedules'),
    path('api/technicians/service_history/<int:pk>/', views.TechnicianServiceHistoryView.as_view(), name='technician_service_history'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/customers/', views.CustomerView.as_view(), name='customers'),
    path('api/customers/<int:pk>/', views.CustomerDetailsView.as_view(), name='customer_details'),
    # path('api/customer/standing_appointments/<int:pk>/',views.CustomerStandingAppointmentView.as_view(),name='customer_standing_appointments'),
    path('api/customer/appointment_history/<int:pk>/',views.CustomerAppointmentHistoryView.as_view(),name='customer_appointment_history'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/is_logged_in/',views.IsLoggedIn.as_view(),name='is_logged_in'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/signup/', views.SignupView.as_view(), name='signup'),
    path('api/change_password/',views.ChangePasswordView.as_view(),name='change_password'),
    path('api/schedules/', views.SchedulesView.as_view(),name='schedule'),
    path('api/supplies/', views.SuppliesView.as_view(), name='supplies'),
    path('api/supplies/<int:pk>', views.SupplyDetailsView.as_view(), name='supply_details'),
    

]
