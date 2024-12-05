import serial
import re

PORT = "/dev/serial0"  # 시리얼 포트 설정
BAUDRATE = 9600        # 통신 속도
TIMEOUT = 1            # 읽기 타임아웃(초)

# 무게 값을 추출할 정규식 패턴
WEIGHT_PATTERN = r"(\d+\.\d{1,2}) kg"

def get_weight_v2():
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
        
        print(f"CI-400와의 통신 시작! 시리얼 포트 {PORT} 초기화 완료.")
        
        if ser.in_waiting > 0:
            data = ser.readline().decode('ascii', errors='ignore').strip()
            print(f"수신된 원본 데이터: {data}")

            match = re.search(WEIGHT_PATTERN, data)
            if match:
                weight_str = match.group(1)
                weight = float(weight_str)
                print(f"추출된 무게 값: {weight}")
                return {'success': True, 'weight': weight, 'raw_data': data}
            else:
                print("무게 값을 추출할 수 없습니다.")
                return {'success': False, 'weight': None, 'raw_data': data}
        else:
            print("수신된 데이터가 없습니다.")
            return {'success': False, 'weight': None, 'raw_data': None}
            
    except serial.SerialException as e:
        print(f"직렬 통신 오류: {e}")
        return {'success': False, 'error': str(e), 'weight': None, 'raw_data': None}
        
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return {'success': False, 'error': str(e), 'weight': None, 'raw_data': None}
        
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("직렬 포트를 닫았습니다.")
