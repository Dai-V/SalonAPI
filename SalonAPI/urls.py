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
    path('appointments/', views.AppointmentsView.as_view(), name='appointments'),
    path('appointments/<int:pk>/',views.AppointmentDetailsView.as_view(), name='appointment_details'),
    path('savedservices/', views.SavedServicesView.as_view(), name='saved_services'),
    path('savedservices/<int:pk>/', views.SavedServiceDetailsView.as_view(), name='saved_service_details'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('services/<int:pk>/', views.ServiceDetailsView.as_view(), name='service_details'),
    path('totals/', views.TotalsView.as_view(), name='totals'),
    path('profile/',views.UserView.as_view(), name='profile'),
    path('technicians/', views.TechniciansView.as_view(), name='technicians'),
    path('technicians/<int:pk>', views.TechnicianDetailsView.as_view(), name='technician_details'),
    path('api-auth/', include('rest_framework.urls')),
    path('customers/', views.CustomerView.as_view(), name='customers'),
    path('customers/<int:pk>/', views.CustomerDetailsView.as_view(), name='customer_details'),
    path('customer/standing_appointments/<int:pk>/',views.CustomerStandingAppointmentView.as_view(),name='customer_standing_appointments'),
    path('customer/appointment_history/<int:pk>/',views.CustomerAppointmentHistoryView.as_view(),name='customer_appointment_history'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('signup', views.SignupView.as_view(), name='signup'),
    path('change_password',views.ChangePasswordView.as_view(),name='change_password'),
    path('schedules', views.SchedulesView.as_view(),name='schedule'),
    path('supplies/', views.SuppliesView.as_view(), name='supplies'),
    path('supplies/<int:pk>', views.SupplyDetailsView.as_view(), name='supply_details'),
    

]
