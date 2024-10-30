"""
URL configuration for rasp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from django.conf.urls import ( handler400, handler403, handler404, handler500)
from rfid import views

urlpatterns = [
    path('', views.index, name='index'),
    path('disposal/', views.User_Control.read_tag, name='read_tag'),
    path('add_user/', views.User_Control.add_user),
#path('disposal/', views.Paint_Control.disposal, name='disposal'),
    path('result/', views.Paint_Control.result)

]

