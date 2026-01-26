from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Remove aplicações sociais duplicadas'

    def handle(self, *args, **options):
        # Buscar todas as apps do Google
        google_apps = SocialApp.objects.filter(provider='google')
        
        if google_apps.count() > 1:
            self.stdout.write(self.style.WARNING(f'Encontradas {google_apps.count()} aplicações Google'))
            
            # Manter apenas a primeira e remover as outras
            primeira = google_apps.first()
            duplicadas = google_apps.exclude(id=primeira.id)
            
            for app in duplicadas:
                self.stdout.write(f'Removendo: {app.name} (ID: {app.id})')
                app.delete()
            
            self.stdout.write(self.style.SUCCESS(f'Mantida apenas 1 aplicação Google (ID: {primeira.id})'))
        elif google_apps.count() == 1:
            self.stdout.write(self.style.SUCCESS('Apenas 1 aplicação Google encontrada. Tudo OK!'))
        else:
            self.stdout.write(self.style.WARNING('Nenhuma aplicação Google configurada'))
