from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from logs.models import SystemLog


class Command(BaseCommand):
    help = 'Visualiza os logs do sistema via terminal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Filtrar logs por nome de usuário'
        )
        parser.add_argument(
            '--level',
            type=str,
            help='Filtrar logs por nível (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
        )
        parser.add_argument(
            '--action',
            type=str,
            help='Filtrar logs por tipo de ação'
        )
        parser.add_argument(
            '--module',
            type=str,
            help='Filtrar logs por módulo'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Número máximo de logs a exibir (padrão: 50)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Logs das últimas N horas (padrão: 24)'
        )
        parser.add_argument(
            '--errors-only',
            action='store_true',
            help='Mostrar apenas erros'
        )

    def handle(self, *args, **options):
        logs = SystemLog.objects.all()
        
        # Filtro por período
        hours = options.get('hours', 24)
        time_threshold = timezone.now() - timedelta(hours=hours)
        logs = logs.filter(created_at__gte=time_threshold)
        
        # Filtros adicionais
        if options['user']:
            logs = logs.filter(user__username__icontains=options['user'])
        
        if options['level']:
            logs = logs.filter(level=options['level'].upper())
        
        if options['action']:
            logs = logs.filter(action_type=options['action'].upper())
        
        if options['module']:
            logs = logs.filter(module=options['module'])
        
        if options['errors_only']:
            logs = logs.filter(level__in=['ERROR', 'CRITICAL'])
        
        # Limite
        limit = options.get('limit', 50)
        logs = logs[:limit]
        
        # Exibição
        self.stdout.write(self.style.SUCCESS(f'\n📋 Últimos {len(logs)} logs do sistema\n'))
        self.stdout.write('─' * 150)
        self.stdout.write(
            f"{'Data/Hora':<20} | {'Nível':<8} | {'Ação':<10} | {'Usuário':<15} | {'Módulo':<12} | {'Título':<40}"
        )
        self.stdout.write('─' * 150)
        
        for log in logs:
            # Cores para níveis
            if log.level == 'ERROR':
                level_str = self.style.ERROR(f"{log.level:<8}")
            elif log.level == 'CRITICAL':
                level_str = self.style.ERROR(f"{log.level:<8}")
            elif log.level == 'WARNING':
                level_str = self.style.WARNING(f"{log.level:<8}")
            else:
                level_str = self.style.SUCCESS(f"{log.level:<8}")
            
            username = log.user.username if log.user else 'N/A'
            data_hora = log.created_at.strftime('%d/%m/%Y %H:%M:%S')
            
            self.stdout.write(
                f"{data_hora:<20} | {level_str} | {log.action_type:<10} | {username:<15} | {log.module:<12} | {log.title:<40}"
            )
        
        self.stdout.write('─' * 150)
        self.stdout.write(self.style.SUCCESS(f'\nTotal: {len(logs)} logs\n'))

