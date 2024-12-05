import json
import logging
import re
import serial
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rfid.loadcell import get_weight_v2
from rfid.exceptions import CustomException
from .models import Weight


logger = logging.getLogger('rasp')
logger.setLevel(logging.INFO)
def get_weight():
    # 로드셀로부터 5개의 무게 값을 읽어 평균을 계산
    PORT = "/dev/serial0"
    BAUDRATE = 9600
    TIMEOUT = 1
    WEIGHT_PATTERN = r"(\d+\.\d{1,2}) kg"

    total_weight = 0
    count = 0

    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT,
            rtscts=False,
            xonxoff=False,
        )
        logger.info("저울과 통신 시작")
        print("저울과 통신 시작")
        for _ in range(5):
            try:
                data = ser.readline().decode("ascii", errors="ignore").strip()
                logger.info(f"수신된 원본 데이터: {data}")
                print(f"수신된 원본 데이터: {data}")
                match = re.search(WEIGHT_PATTERN, data)
                if match:
                    weight = float(match.group(1))
                    logger.info(f"추출된 무게 값: {weight}")
                    print(f"추출된 무게 값: {weight}")
                    total_weight += weight
                    count += 1
                else:
                    logger.warning("무게 값을 추출할 수 없습니다.")
            except Exception as e:
                logger.warning(f"데이터 처리 중 오류 발생: {e}")

        if count == 0:
            raise CustomException("유효한 데이터가 수신되지 않았습니다.", status_code=404)

        avg_weight = total_weight / count
        logger.info(f"평균 무게 값: {avg_weight}")
        return avg_weight

    except serial.SerialException as e:
        logger.error(f"시리얼 통신 오류: {e}")
        raise CustomException(f"시리얼 통신 오류: {e}", status_code=404)

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            logger.info("직렬 포트를 닫았습니다.")


def update_weight(company, name):
    # 회사의 무게 데이터를 업데이트

    if not company:
        logger.warning("회사명이 입력되지 않았습니다.")
        return {'error': "회사명이 입력되지 않았습니다.", 'status': 400}

    try:
        cur_state = Weight.objects.get(company=company)
        disposal_weight = get_weight()
        company_disposal = float(cur_state.weight) + disposal_weight

        cur_state.weight = company_disposal
        cur_state.save()

        message = f"{name}님의 폐기량은 {disposal_weight:.2f}kg입니다."
        logger.info(f"{name}님의 폐기량 업데이트: {disposal_weight:.2f}kg")
        return {'message': message, 'disposal_weight': disposal_weight, 'company_weight': company_disposal}

    except Weight.DoesNotExist:
        logger.error(f"회사 '{company}' 데이터가 없습니다.")
        raise CustomException("회사 무게 데이터가 존재하지 않습니다.", status_code=404)

    except Exception as e:
        logger.error(f"서버 오류 발생: {e}")
        raise CustomException("서버 오류 발생", status_code=500)

