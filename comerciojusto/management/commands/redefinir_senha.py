from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Redefine a senha de um usuário'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email do usuário')
        parser.add_argument('nova_senha', type=str, help='Nova senha')

    def handle(self, *args, **options):
        email = options['email']
        nova_senha = options['nova_senha']
        
        try:
            user = User.objects.get(email=email)
            user.set_password(nova_senha)
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'Senha redefinida com sucesso para o usuário: {user.username} ({user.email})'))
            self.stdout.write(self.style.WARNING(f'Agora você pode fazer login com:'))
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Senha: {nova_senha}')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuário com email "{email}" não encontrado'))
