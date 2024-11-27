from functools import wraps
import json
from logging import exception
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.urls import reverse
import gpiozero
from mfrc522 import SimpleMFRC522
from rasp import settings
from rfid import rfid_reader, user_management, weight
from rfid.exceptions import CustomException
from rfid.utils import handle_exception
from .models import User, Weight
from gpiozero import DigitalOutputDevice
import spidev
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from django.shortcuts import render
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
# 로깅 설정
logger = logging.getLogger('rasp')
logger.info("로깅 시작")

#잠금장치 ---> on이 열림 / off가 잠김
# lock = DigitalOutputDevice(21, active_high=False)



# 잠금장치 해제 후 메인 화면 렌더링
@handle_exception
def index(request):
    lock.off()  # 잠금 장치 닫기
    return render(request, 'index.html')

# 카드 추가 페이지 렌더링
@handle_exception
def add_card(request):
    return render(request, 'add_user.html')

# 폐기 중 화면 렌더링
@handle_exception
def disposal(request):
    uid = rfid_reader.tagging()
    if not uid:
        raise CustomException("RFID 태그를 읽을 수 없습니다.", status_code=400)
    
    user = user_management.check_user(uid)
    if not user:
        raise CustomException("사용자를 찾을 수 없습니다.", status_code=404)
    
    message = f"사용자 {user.name}이(가) 확인되었습니다."
    return render(request, 'disposal.html', {'message': message, 'user': user, 'uid': uid})

# 폐기 결과 화면 렌더링
@handle_exception
def result(request):
    if request.method != 'GET':
        raise CustomException("잘못된 요청입니다.", status_code=400)
    
    name = request.GET.get('name')
    company = request.GET.get('company')
    uid = request.GET.get('uid')
    
    weight_info = weight.update_weight(company, name)
    
    tag_uid = rfid_reader.tagging()
    if str(tag_uid) != str(uid):
        return render(request, 'err_lock.html', {
        'uid': uid,
        'name': name,
        'company': company,
        'message': weight_info['message'],
    })
    
    return render(request, 'result.html', {
        'name': name,
        'company': company,
        'message': weight_info['message'],
        'Weight': weight_info['disposal_weight'],
        'Company_Weight': weight_info['company_weight'],
    })