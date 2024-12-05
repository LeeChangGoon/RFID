import time
from django.test import TestCase
import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from django.urls import reverse
import gpiozero
from mfrc522 import SimpleMFRC522
from rasp import settings
from rfid.exceptions import CustomException
from rfid.utils import handle_exception
from .models import User, Weight
from gpiozero import DigitalOutputDevice
import spidev
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from smartcard.System import readers
from smartcard.util import toHexString

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000 #표준이 10kHz


# Create your tests here.
import logging

# 로깅 설정
logger = logging.getLogger('rasp')
logger.info("로깅 시작")

reader = SimpleMFRC522(reset_pin=16)

def tagging():
    logger.info("RFID 태그 읽기 시작")
    try:
        uid, data = reader.read()
        if uid:
            logger.info(f"UID Detected: {uid}")
            return uid
        logger.warning("UID not detected, retrying...")
        time.sleep(0.1) 
    except Exception as e:
        logger.error(f"Error during RFID reading: {e}")
        raise CustomException(f"RFID 읽기 중 오류 발생: {str(e)}", status_code=500)
    finally:
        logger.info("RFID 태그 읽기 종료")

    # 타임아웃 예외 처리
    logger.error("Timeout: UID not detected")
    raise CustomException("태깅 시간 초과", status_code=404)

def read_card_uid():
    while True:
        try:
            available_readers = readers()
            if not available_readers:
                print("리더기를 찾을 수 없습니다. 연결 상태를 확인하세요.")
                raise CustomException(f"리더기를 찾을 수 없습니다. {str(e)}", status_code=500)

            print("사용 가능한 리더기:", available_readers)
            reader = available_readers[0] 
            connection = reader.createConnection()
            connection.connect()

            # UID 읽기 명령
            get_uid_command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(get_uid_command)

            if sw1 == 0x90 and sw2 == 0x00:
                uid = toHexString(data)
                print(f"카드 UID: {uid}")
                return uid
            else:
                print(f"UID 읽기 실패: SW1={sw1}, SW2={sw2}")
                raise CustomException(f"리더기를 찾을 수 없습니다. {str(e)}", status_code=500)


        except Exception as e:
            error_message = str(e)
            if "No smart card inserted" in error_message:
                print("카드가 삽입되지 않았습니다. 기다리는 중...")
                time.sleep(0.3)
            else:
                print(f"오류 발생: {e}")
                break