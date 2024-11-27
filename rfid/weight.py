import json
import logging
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.urls import reverse
import gpiozero
from mfrc522 import SimpleMFRC522
from numpy import double
from rasp import settings
from rfid.exceptions import CustomException
from rfid.utils import handle_exception
from .models import User, Weight
from gpiozero import DigitalOutputDevice
import spidev
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

import serial
logger = logging.getLogger('rasp')
logger.info("로깅 시작")

PORT = "/dev/serial0"  # 시리얼 포트 설정
BAUDRATE = 9600        # 통신 속도
TIMEOUT = 1            # 읽기 타임아웃(초)

def get_weight():  # 측정값 5개 받고 평균내서 리턴
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT,
            rtscts=False, xonxoff=False
        )
        print("저울과 통신 시작")

        total_weight = 0
        count = 0

        for _ in range(5):
            if ser.in_waiting > 0:
                data = ser.readline()
                try:
                    decoded_data = data.decode('utf-8', errors='ignore').strip()
                    parts = decoded_data.split(',')
                    if len(parts) == 4:  # 데이터 포맷 확인
                        print(f"상태: {parts[0]}, 모드: {parts[1]}, 값: {parts[2]}, 단위: {parts[3]}")
                        weight = float(parts[2])  # 값에서 무게만 추출
                        total_weight += weight
                        count += 1
                except UnicodeDecodeError:
                    print(f"디코딩 오류: {data.hex()}")
                    raise CustomException("디코딩 오류", status_code=404)

        if count == 0:  # 데이터가 없는 경우 예외 처리
            raise CustomException("무게 데이터를 읽을 수 없습니다.", status_code=404)

        return total_weight / count  # 평균값 반환

    except serial.SerialException as e:
        raise CustomException(f"시리얼 통신 오류: {str(e)}", status_code=404)

    finally:
        if ser.is_open:
            ser.close()
            print("직렬 포트를 닫았습니다.")

def update_weight(company, name):
    if company:
        try:
            # 현재 회사의 상태를 가져옴
            cur_state = Weight.objects.get(company=company)

            # 로드셀에서 읽어온 무게
            disposal_weight = get_weight()

            # 회사 폐기량 계산
            company_disposal = disposal_weight + cur_state.weight

            # 현재 무게 업데이트
            cur_state.weight = company_disposal
            cur_state.save()

            # Message와 폐기량 반환
            message = f"{name}님의 폐기량은 {disposal_weight:.2f}kg입니다."
            return {'message': message, 'disposal_weight': disposal_weight, 'company_weight': company_disposal}

        except Weight.DoesNotExist:
            return {'error': "무게 정보가 없습니다.", 'status': 404}
        except CustomException as ce:
            return {'error': ce.message, 'status': ce.status_code}
        except Exception as e:
            return {'error': f"오류가 발생했습니다: {str(e)}", 'status': 500}
    else:
        return {'error': "회사명이 입력되지 않았습니다.", 'status': 400}
