import json
import logging
import re
import serial
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rfid.exceptions import CustomException
from .models import Weight

# 로깅 설정
logger = logging.getLogger('rasp')
logger.setLevel(logging.INFO)

PORT = "/dev/serial0"  # 시리얼 포트 설정
BAUDRATE = 9600        # 통신 속도
TIMEOUT = 1            # 읽기 타임아웃(초)

# 무게 값을 추출할 정규식 패턴 (예시: 무게 값이 "0.0 kg" 형식일 경우)
WEIGHT_PATTERN = r"(\d+\.\d{1,2}) kg"  # 소수점 이하 최대 두 자리까지

def get_weight():  # 측정값 5개 받고 평균내서 리턴
    try:
        # 시리얼 포트 초기화
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT,
            rtscts=False, xonxoff=False
        )
        logger.info("저울과 통신 시작")

        total_weight = 0
        count = 0

        for _ in range(5):
            if ser.in_waiting > 0:
                data = ser.readline().decode('ascii', errors='ignore').strip()  # 데이터를 문자열로 변환하고 공백 제거
                logger.info(f"수신된 원본 데이터: {data}")
                # 정규식으로 무게 값 추출
                match = re.search(WEIGHT_PATTERN, data)
                if match:
                    weight_str = match.group(1)  # 정규식 매칭된 첫 번째 그룹
                    weight = float(weight_str)   # 문자열을 float로 변환
                    logger.info(f"추출된 무게 값: {weight}")
                    total_weight += weight
                    count += 1
                else:
                    logger.warning("무게 값을 추출할 수 없습니다.")

        if count == 0:  # 데이터가 없을 경우 예외 처리
            raise CustomException("무게 데이터를 읽을 수 없습니다.", status_code=404)

        # 평균값 반환
        avg_weight = total_weight / count
        logger.info(f"평균 무게 값: {avg_weight}")
        return avg_weight

    except serial.SerialException as e:
        logger.error(f"시리얼 통신 오류: {str(e)}")
        raise CustomException(f"시리얼 통신 오류: {str(e)}", status_code=404)

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            logger.info("직렬 포트를 닫았습니다.")

def update_weight(company, name):
    if company:
        try:
            # 회사의 현재 상태를 가져옴
            cur_state = Weight.objects.get(company=company)

            # 로드셀에서 읽어온 무게
            disposal_weight = get_weight()

            # 회사 폐기량 계산
            company_disposal = disposal_weight + cur_state.weight

            # 현재 무게 업데이트
            cur_state.weight = company_disposal
            cur_state.save()

            # 폐기량 메시지 반환
            message = f"{name}님의 폐기량은 {disposal_weight:.2f}kg입니다."
            logger.info(f"{name}님의 폐기량 업데이트: {disposal_weight:.2f}kg")
            return {'message': message, 'disposal_weight': disposal_weight, 'company_weight': company_disposal}

        except Weight.DoesNotExist:
            logger.error(f"회사 {company}의 무게 데이터가 존재하지 않습니다.")
            raise CustomException("무게 데이터가 존재하지 않습니다.", status_code=404)
        except Exception as e:
            logger.error(f"서버 오류 발생: {str(e)}")
            raise CustomException("서버 오류 발생", status_code=500)

    else:
        logger.warning("회사명이 입력되지 않았습니다.")
        return {'error': "회사명이 입력되지 않았습니다.", 'status': 400}
