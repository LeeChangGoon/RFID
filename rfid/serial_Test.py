import serial
import re

PORT = "/dev/serial0"  # 시리얼 포트 설정
BAUDRATE = 9600        # 통신 속도
TIMEOUT = 1            # 읽기 타임아웃(초)

# 무게 값을 추출할 정규식 패턴 (예시: 무게 값이 "0.0 kg" 형식일 경우)
WEIGHT_PATTERN = r"(\d+\.\d{1,2}) kg"  # 소수점 이하 최대 두 자리까지

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
    
    print("CI-400와의 통신 시작!")

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('ascii', errors='ignore').strip()  # 데이터를 문자열로 변환하고 공백 제거
            print(f"수신된 원본 데이터: {data}")

            # 정규식으로 무게 값 추출
            match = re.search(WEIGHT_PATTERN, data)
            if match:
                weight_str = match.group(1)  # 정규식 매칭된 첫 번째 그룹
                weight = float(weight_str)   # 문자열을 float로 변환
                print(f"추출된 무게 값: {weight}")

                # 무게 값에 1.2를 더하는 예시
                weight += 123.558
                print(f"수정된 무게 값: {weight}")
            else:
                print("무게 값을 추출할 수 없습니다.")
            
except serial.SerialException as e:
    print(f"직렬 통신 오류: {e}")

except KeyboardInterrupt:
    print("사용자에 의해 프로그램 종료")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("직렬 포트를 닫았습니다.")
