# 공통 예외 처리 함수
from functools import wraps
from venv import logger

from django.shortcuts import render

from rfid.exceptions import CustomException


def handle_exception(func):
    """View 함수의 공통 예외 처리를 위한 데코레이터"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except CustomException as e:
            logger.warning(f"CustomException 발생: {e}")
            return render(request, 'error.html', {
                'message': str(e),
                'status_code': e.status_code,
            }, status=e.status_code)
        except Exception as e:
            logger.error(f"예기치 못한 오류: {e}", exc_info=True)
            return render(request, 'error.html', {
                'message': "내부 서버 오류가 발생했습니다.",
                'status_code': 500,
            }, status=500)
    return wrapper