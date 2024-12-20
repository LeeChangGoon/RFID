"""
Django settings for rasp project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
# 세션 만료 시간 (초)
SESSION_COOKIE_AGE = 600  # 5분
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 브라우저 닫으면 세션 만료


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, 'rfid/templates') #템플릿파일 경로

# Custom Exception Handlers
HANDLER404 = 'rfid.views_v2.custom_exception_handler'
HANDLER500 = 'rfid.views_v2.custom_exception_handler'
HANDLER401 = 'rfid.views_v2.custom_exception_handler'
HANDLER400 = 'rfid.views_v2.custom_exception_handler'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2l$r1=pr99hu^(#d12)gqe^ts52ed0c%zleuy=a#32cnllw3(7'
ADMIN_PASSWD = 'qwer123'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'raspberrypi.local', '10.150.8.165', '10.150.190.54']


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {funcName} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/pi/Desktop/rasp_v3/logs/error.log',
            'formatter': 'verbose',
        },
        'info_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/pi/Desktop/rasp_v3/logs/info.log',
            'formatter': 'verbose',
        },
        'warning_file': {
        'level': 'WARNING',
        'class': 'logging.FileHandler',
        'filename': '/home/pi/Desktop/rasp_v3/logs/warning.log',
        'formatter': 'verbose',
    },
    },
    'loggers': {
        'rasp': {
            'handlers': ['info_file', 'error_file', 'warning_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}



#APPEND_SLASH = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rfid',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'rfid.middleware.CustomExceptionMiddleware',  # CustomException 처리 미들웨어 추가
]

ROOT_URLCONF = 'rasp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rasp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'testdb',  # 사용할 데이터베이스 이름
        'USER': 'root',    # MariaDB 사용자명
        'PASSWORD': 'qwer123',  # 비밀번호
        'HOST': 'localhost',    # DB 서버 주소
        'PORT': '3306',         # MariaDB 포트 번호 (기본값 3306)
        'OPTIONS': {
            'charset': 'utf8mb4',  # UTF-8 설정
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
