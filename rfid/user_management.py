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

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 50000  # SPI 속도를 50kHz로 낮춤

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

#처음 댔던 카드를 대도록 하는 함수 -------timeout, 리턴값 수정 필
@handle_exception
def disposal_err_return(name, company, uid):
    message = "올바른 카드를 인식해주세요."

    # 사용자 확인
    try:
        user = check_user(uid) 
    except CustomException as e:
        raise CustomException(f"사용자 확인 실패: {e.message}", status_code=404)

    return render(request, 'disposal.html', {
        'message': message,
        'user': user,
        'uid': uid,
        'company': company
    })

# 처음에 댔던 태그랑 맞는지 비교
@handle_exception
def lockTag(name, company):
    reader = SimpleMFRC522(reset_pin=16)  # RFID 리더기 초기화
    try:
        uid, data = reader.read()
        if uid == None:
            return {'Timeout': True}
        disposal_User = User_Control.check_user(uid)
        if disposal_User.name == name and disposal_User.company == company:
            return {'result': True, 'uid': uid}
        else:
            return {'result': False, 'uid': uid}
    except Exception as e:
        return {'error': f"오류가 발생했습니다: {str(e)}", 'status': 500}