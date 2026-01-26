from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Remove todas as aplicações sociais do Django Admin'

    def handle(self, *args, **options):
        google_apps = SocialApp.objects.filter(provider='google')
        
        if google_apps.exists():
            count = google_apps.count()
            google_apps.delete()
            self.stdout.write(self.style.SUCCESS(f'{count} aplicação(ões) Google removida(s) do Django Admin'))
            self.stdout.write(self.style.WARNING('Agora as credenciais virão apenas do arquivo .env'))
        else:
            self.stdout.write(self.style.SUCCESS('Nenhuma aplicação Google no Django Admin'))
