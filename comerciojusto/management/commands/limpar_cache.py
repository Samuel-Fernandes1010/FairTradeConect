from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Limpa todo o cache da aplicação'

    def handle(self, *args, **kwargs):
        self.stdout.write('Limpando cache...')
        cache.clear()
        self.stdout.write(self.style.SUCCESS('✓ Cache limpo com sucesso!'))
