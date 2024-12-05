import json
import logging
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

logger = logging.getLogger('rasp')
logger.setLevel(logging.INFO)

# 사용자 확인 함수 (ORM 사용)
from django.core.exceptions import ObjectDoesNotExist

# 사용자 확인 함수 (ORM 사용)
def check_user(uid):
    try:
        # UID를 기반으로 사용자 검색
        user = User.objects.get(uid=uid)
        logger.info(f"사용자 확인 성공: {user.name}, UID: {uid}")
        return user
    except ObjectDoesNotExist:
        # 사용자를 찾지 못한 경우 예외 처리
        logger.error(f"사용자를 찾을 수 없음: UID {uid}")
        raise CustomException("사용자를 찾을 수 없습니다.", status_code=404)
    except Exception as e:
        # 기타 예외 처리
        logger.error(f"사용자 확인 중 예기치 못한 오류: {str(e)}")
        raise CustomException("서버에서 오류가 발생했습니다.", status_code=500)


@handle_exception
def add_user(request):
    name = request.POST.get('name')
    company = request.POST.get('company')
    admin_pw = request.POST.get('admin_pw')

    try:
        uid = rfid_reader.read_card_uid()
        logger.info(f"사용자 추가 시도: 이름: {name}, 회사: {company}, UID: {uid}")
        if admin_pw != settings.ADMIN_PASSWD:
            logger.warning(f"관리자 비밀번호 실패: {admin_pw}")
            raise CustomException("관리자 비밀번호가 잘못되었습니다.", status_code=403)

        if User.objects.filter(uid=uid).exists():
            logger.warning(f"중복된 UID 존재: {uid}")
            raise CustomException("이미 등록된 사용자입니다.", status_code=409)

        # 사용자 추가
        user = User.objects.create(uid=uid, name=name, company=company)

        if not Weight.objects.filter(company=company).exists():
            logger.info(f"새로운 회사 무게 정보 생성: {company}")
            Weight.objects.create(company=company, weight=0)

        logger.info(f"사용자 추가 성공: 이름: {name}, UID: {uid}")
        return render(request, 'index.html', {'success_addUser': True})

    except Exception as e:
        logger.error(f"사용자 추가 오류: {str(e)}")
        raise CustomException(f"사용자 추가 중 오류 발생: {str(e)}", status_code=500)