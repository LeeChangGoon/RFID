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
from rfid import user_management, views, views_v2

urlpatterns = [
    path('', views.index, name='index'),
    # path('disposal/', views.disposal, name='read_tag'),
    # path('disposal/', views.User_Control.read_tag, name='read_tag'),
    # path('disposal_err_return/', views.disposal_err_return),
    # path('add_user/', views.User_Control.add_user),
    # path('add_card/', views.User_Control.add_card),
    # path('result/', views.Paint_Control.result),
    # path('send_weight/', views.publish_weight),


    path('disposal/', views_v2.disposal),
    path('add_card/', views_v2.add_card),
    path('user_add/', user_management.add_user),
    path('result/', views_v2.result),
    path('disposal_err/', views_v2.disposal_err)
]

