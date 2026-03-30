
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from monitor.models import Empresa

User = get_user_model()

username = 'testclient'
email = 'testclient@example.com'
password = 'testpassword'

if not User.objects.filter(username=username).exists():
    user = User.objects.create_user(username=username, email=email, password=password)
    print('Created user', username)
else:
    user = User.objects.get(username=username)
    print('User exists', username)

if not Empresa.objects.filter(user=user).exists():
    Empresa.objects.create(user=user, cnpj='12345678000199', razao_social='Empresa Teste Ltda', cidade='Sao Paulo', estado='SP', tipo='MEI', ativa=True)
    print('Created Empresa for user')
else:
    print('Empresa already exists for user')
