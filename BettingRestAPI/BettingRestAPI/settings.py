"""
Django settings for BettingRestAPI project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import pickle
import sys
from sys import platform

import keras
import tensorflow as tf

# Make sure to always run these 4 lines because tensorflow is giving errors if not
config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.8))
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)

global prediction_model

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if platform == "linux" or platform == "linux2":
    PREDICTION_MODEL_ALL_WINS = keras.models.load_model(
        os.path.join(BASE_DIR, "csgo_api/PredictionModels/NNModel_allMatchesWins_linux.h5"))
    PREDICTION_MODEL_BO3_WINS = keras.models.load_model(
        os.path.join(BASE_DIR, "csgo_api/PredictionModels/NNModel_bestOf3Wins_linux.h5"))
    PREDICTION_MODEL_SVM_ALL_WINS = pickle.load(
        open(os.path.join(BASE_DIR, "csgo_api/PredictionModels/clfSVM_allMatchesWins_linux.sav"), 'rb'))
    PREDICTION_MODEL_SVM_BO3_WINS = pickle.load(
        open(os.path.join(BASE_DIR, "csgo_api/PredictionModels/clfSVM_bestOf3Wins_linux.sav"), 'rb'))
if platform == "win32":
    PREDICTION_MODEL_ALL_WINS = keras.models.load_model(
        os.path.join(BASE_DIR, "csgo_api/PredictionModels/NNModel_allMatchesWins.h5"))
    PREDICTION_MODEL_BO3_WINS = keras.models.load_model(
        os.path.join(BASE_DIR, "csgo_api/PredictionModels/NNModel_bestOf3Wins.h5"))
    PREDICTION_MODEL_SVM_ALL_WINS = pickle.load(
        open(os.path.join(BASE_DIR, "csgo_api/PredictionModels/clfSVM_allMatchesWins.sav"), 'rb'))
    PREDICTION_MODEL_SVM_BO3_WINS = pickle.load(
        open(os.path.join(BASE_DIR, "csgo_api/PredictionModels/clfSVM_bestOf3Wins.sav"), 'rb'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-$wkg1iw9f=2(2s6b2buh@w+c6-%mhjv9aripua2b&m@uj_iqd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8081',
    'http://localhost:8000',
]
CORS_ORIGIN_REGEX_WHITELIST = [
    'http://localhost:8081',
    'http://localhost:8000',
]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=user,csgo_api',
]

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'csgo_api.apps.CsgoApiConfig',
    'user.apps.UserConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'django_nose',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BettingRestAPI.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'BettingRestAPI.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if (len(sys.argv) >= 2 and sys.argv[1] == 'test') or platform == "win32":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get("DB_NAME", 'postgres'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'db'),  # set in docker-compose.yml
            'PORT': os.environ.get('DB_PORT', 5432),  # default postgres port
            'PASSWORD': os.environ.get("DB_PASSWORD", "")
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
