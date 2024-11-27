import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.urls import reverse
import gpiozero
from mfrc522 import SimpleMFRC522
from rasp import settings
from rfid import rfid_reader
from rfid.exceptions import CustomException
from rfid.utils import handle_exception
from .models import User, Weight
from gpiozero import DigitalOutputDevice
import spidev
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish


# 사용자 확인 함수 (ORM 사용)
@handle_exception
def check_user(uid):
    try:
        user = User.objects.get(uid=uid)
        return user
    except User.DoesNotExist:
        raise CustomException(f"UID {uid}에 해당하는 사용자를 찾을 수 없습니다.", status_code=404)

#사용자 추가
@handle_exception
def add_user(request):
    # uid = request.POST.get(uid)
    name = request.POST.get('name')
    company = request.POST.get('company')
    admin_pw = request.POST.get('admin_pw')
    uid = rfid_reader.tagging()
    if admin_pw != settings.ADMIN_PASSWD:
        raise CustomException("관리자 비밀번호가 잘못되었습니다.", status_code=403)
    if User.objects.filter(uid=uid).exists():
        raise CustomException("이미 등록된 사용자입니다.", status_code=409)
    try:
        User.objects.create(uid=uid, name=name, company=company)
        if not Weight.objects.filter(company=company).exists():
            Weight.objects.create(company=company, weight=0)
    except Exception as e:
        raise CustomException(f"사용자 추가 중 오류 발생: {str(e)}")