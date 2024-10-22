from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse
from mfrc522 import SimpleMFRC522
import pymysql
from .models import User

# Create your views here.


def index(request):
    return render(request, 'index.html')

# 사용자 확인 함수 (ORM 사용)
def check_user(id):
    try:
        user = User.objects.get(uid=id)
        return user
    except User.DoesNotExist:
        return None

# RFID 리더기 객체 생성
reader = SimpleMFRC522()

# 메인 페이지
def index(request):
    return render(request, 'index.html')

# RFID 태그 읽기 및 사용자 확인
def read_tag(request):
    try:
        id, data = reader.read()
        user = check_user(id)

        if user:
            message = f"사용자 {user.name}이(가) 확인되었습니다."
        else:
            message = f"사용자가 없습니다. UID: {id}"
        
        return render(request, 'result.html', {'message': message})
    except Exception as e:
        return render(request, 'error.html', {'message': f"Error reading tag: {e}"})


#사용자 추가
# def add_user(request):
#     if request.method == 'POST':
#         uid = request.POST.get('uid')
#         name = request.POST.get('name')
#         company = request.POST.get('company')

#         if uid and name and company:  # 유효성 검사
#             try:
#                 # ORM을 사용해 사용자 추가
#                 User.objects.create(uid=uid, name=name, company=company)
#                 return redirect(reverse('index'))
#             except Exception as e:
#                 return render(request, 'error.html', {'message': f"Error inserting data: {e}"})
#         else:
#             return render(request, 'error.html', {'message': 'Invalid input data'})

# 사용자 추가(태깅으로 uid입력)
def add_user(request):
    if request.method == 'POST':
        # 사용자가 입력한 이름과 회사 정보 받기
        name = request.POST.get('name')
        company = request.POST.get('company')

        if name and company:  # 입력 데이터 유효성 검사
            try:
                # RFID 태그 읽기
                uid, data = reader.read()

                # ORM을 사용해 사용자 추가 (uid, name, company 정보 저장)
                User.objects.create(uid=uid, name=name, company=company)
                
                # 저장 후 메인 페이지로 리디렉션
                return redirect(reverse('index'))
            except Exception as e:
                # 오류 발생 시 에러 페이지로 이동
                return render(request, 'error.html', {'message': f"Error saving data: {e}"})
        else:
            return render(request, 'error.html', {'message': 'Invalid input data'})

    return render(request, 'add_user.html')