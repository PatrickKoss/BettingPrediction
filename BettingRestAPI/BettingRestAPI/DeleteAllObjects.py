import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BettingRestAPI.settings')
django.setup()

from django.contrib.contenttypes.models import ContentType

ContentType.objects.all().delete()
