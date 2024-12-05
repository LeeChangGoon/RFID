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
# 로깅 설정
logger = logging.getLogger('rasp')
logger.info("로깅 시작")
logger.setLevel(logging.INFO)

#잠금장치 ---> on이 열림 / off가 잠김
lock = DigitalOutputDevice(21, active_high=True)

# 잠금장치 해제 후 메인 화면 렌더링
@handle_exception
def index(request):
    lock.on()  # 잠금 장치 닫기
    if 'uid' in request.session:
        del request.session['uid']
        logger.info("세션 UID 삭제 완료")
    return render(request, 'index.html')

# 카드 추가 페이지 렌더링
@handle_exception
def add_card(request):
    return render(request, 'add_user.html')

# 폐기 중 화면 렌더링
@handle_exception
def disposal(request):
    uid = rfid_reader.read_card_uid()
    if not uid:
        logger.warning("RFID 태그를 읽을 수 없습니다.")
        raise CustomException("RFID 태그를 읽을 수 없습니다.", status_code=400)
    
    # 세션에 UID 저장
    request.session['uid'] = uid
    uid_session = request.session.get('uid')
    if not uid_session:
        raise CustomException("세션에 UID가 없습니다. 작업을 다시 시작하세요.", status_code=400)
    
    user = user_management.check_user(uid_session)
    message = f"사용자 {user.name}이(가) 확인되었습니다."
    lock.on()
    return render(request, 'disposal.html', {'message': message, 'user': user, 'uid': uid_session})


# 폐기 결과 화면 렌더링
@handle_exception
def result(request):
    if request.method != 'GET':
        raise CustomException("잘못된 요청입니다.", status_code=400)
    
    name = request.GET.get('name')
    company = request.GET.get('company')
    # uid = request.GET.get('uid')

    uid = request.session.get('uid')
    if not uid:
        logger.error("세션에 UID가 없습니다.")
        raise CustomException("세션에 UID가 없습니다. 작업을 다시 시작하세요.", status_code=400)

    try:
        tag_uid = rfid_reader.read_card_uid()  # RFID 태깅 시도
    except CustomException as e:
        if e.status_code == 404:  # 시간 초과 예외
            logger.warning("RFID 태깅 시간 초과 예외 발생")
            raise CustomException("태그 읽기가 너무 오래 걸렸습니다. 카드를 다시 태깅해주세요.", status_code=556)

    # 태그된 UID와 세션에 저장된 UID가 일치하지 않으면 예외 발생
    if str(tag_uid) != str(uid):
        # CustomException에 딕셔너리 전달
        logger.warning(f"태그된 UID가 세션 UID와 일치하지 않습니다. 세션 UID: {uid}, 태그된 UID: {tag_uid}")
        raise CustomException(
            "올바른 카드 태깅", 
            status_code=555, 
            extra_data={'uid': uid, 'name': name, 'company': company, 'message': "올바른 카드 태깅"}
        )
    weight_info = weight.update_weight(company, name)  
    # 작업 완료 후 세션 정리
    del request.session['uid']
    lock.off()  # 잠금 장치 닫기

    return render(request, 'result.html', {
        'name': name,
        'company': company,
        'message': weight_info['message'],
        'Weight': weight_info['disposal_weight'],
        'Company_Weight': weight_info['company_weight'],
    })

@handle_exception
def disposal_err(request):
    if request.method != 'GET':
        raise CustomException("잘못된 요청입니다.", status_code=400)
    message = "다시 태깅해주세요."
    uid = request.session.get('uid')
    user = user_management.check_user(uid)

    return render(request, 'disposal.html', {'message': message, 'user': user, 'uid': uid})

def clear_uid_session(request):
    """세션에서 UID 제거 (존재 여부 확인)"""
    if 'uid' in request.session:
        del request.session['uid']
        logger.info("세션 UID 삭제 완료")