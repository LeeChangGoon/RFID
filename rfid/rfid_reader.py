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
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 50000  # SPI 속도를 50kHz로 낮춤
# Create your tests here.
import logging

# 로깅 설정
logger = logging.getLogger('rasp')
logger.info("로깅 시작")

reader = SimpleMFRC522(reset_pin=16)

def tagging():
    try:
        uid, data = reader.read()
        if uid:
            logger.info(f"UID Detected: {uid}")
            return uid
        time.sleep(0.1) 
    except Exception as e:
        logger.error(f"Error during RFID reading: {e}")
        raise CustomException(f"RFID 읽기 중 오류 발생: {str(e)}", status_code=500)
    finally:
        logger.info("RFID 태그 읽기 종료")

    # 타임아웃 예외 처리
    logger.warning("Timeout: UID not detected")
    raise CustomException("태깅 시간 초과", status_code=404)
