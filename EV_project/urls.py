"""EV_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.auth.views import LoginView
from my_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('my_app.urls')),
    path('accounts/login/', 
        LoginView.as_view(template_name='login.html'), 
        name='login'),
    
    # Your custom password reset URLs
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('password-reset-change/', views.password_reset_change, name='password_reset_change'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
]
