from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from monitor.models import Empresa

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a test client user and empresa for local development'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='testclient')
        parser.add_argument('--email', default='testclient@example.com')
        parser.add_argument('--password', default='testpassword')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f'Created user {username}')
        else:
            self.stdout.write(f'User {username} already exists')

        if not Empresa.objects.filter(user=user).exists():
            Empresa.objects.create(user=user, cnpj='12345678000199', razao_social='Empresa Teste Ltda', cidade='Sao Paulo', estado='SP', tipo='MEI', ativa=True)
            self.stdout.write('Created Empresa for user')
        else:
            self.stdout.write('Empresa already exists for user')
