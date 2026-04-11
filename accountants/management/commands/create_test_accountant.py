from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accountants.models import AccountantProfile, ClientAccount
from monitor.models import Empresa

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria um contador de teste com clientes para demonstração'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nome de usuário do contador')
        parser.add_argument('--email', type=str, default='contador@test.com', help='Email do contador')
        parser.add_argument('--password', type=str, default='senha123', help='Senha do contador')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Verificar se usuário já existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'❌ Usuário {username} já existe'))
            return

        # Criar usuário
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Contador'
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Usuário criado: {username}'))

        # Criar perfil de contador
        profile = AccountantProfile.objects.create(
            user=user,
            professional_name=f'Studio {username.capitalize()} Contabilidade',
            cpf='123.456.789-00',
            phone='(11) 98765-4321',
            account_type='PREMIUM',
            is_active=True
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Perfil de contador criado'))

        # Buscar empresas para vincular
        empresas = Empresa.objects.all()[:3]
        if empresas:
            for empresa in empresas:
                # Verificar se já não está vinculada
                if not ClientAccount.objects.filter(accountant=profile, empresa=empresa).exists():
                    ClientAccount.objects.create(
                        accountant=profile,
                        empresa=empresa,
                        status='ACTIVE',
                        monthly_fee=150.00,
                        notes=f'Cliente gerenciado por {profile.professional_name}'
                    )
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Cliente adicionado: {empresa.razao_social}'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Nenhuma empresa encontrada no sistema'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Contador {username} criado com sucesso!'))
        self.stdout.write(f'📝 Acesse: http://127.0.0.1:8000/accountants/')
        self.stdout.write(f'👤 Usuário: {username}')
        self.stdout.write(f'🔑 Senha: {password}')

