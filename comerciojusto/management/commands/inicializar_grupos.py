from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from comerciojusto.models import Produto, Certificacao, Perfil


class Command(BaseCommand):
    help = 'Inicializa os grupos de usuários e suas permissões'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando grupos de usuários...')
        
        # Grupo Produtor
        grupo_produtor, created = Group.objects.get_or_create(name='Produtor')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Produtor criado'))
            
            # Permissões para Produtor
            content_type_produto = ContentType.objects.get_for_model(Produto)
            content_type_certificacao = ContentType.objects.get_for_model(Certificacao)
            
            # Adicionar produtos
            perm_add_produto = Permission.objects.get(
                codename='add_produto',
                content_type=content_type_produto,
            )
            perm_change_produto = Permission.objects.get(
                codename='change_produto',
                content_type=content_type_produto,
            )
            perm_delete_produto = Permission.objects.get(
                codename='delete_produto',
                content_type=content_type_produto,
            )
            perm_view_produto = Permission.objects.get(
                codename='view_produto',
                content_type=content_type_produto,
            )
            
            # Adicionar certificações
            perm_add_certificacao = Permission.objects.get(
                codename='add_certificacao',
                content_type=content_type_certificacao,
            )
            perm_view_certificacao = Permission.objects.get(
                codename='view_certificacao',
                content_type=content_type_certificacao,
            )
            
            grupo_produtor.permissions.set([
                perm_add_produto, perm_change_produto, perm_delete_produto, perm_view_produto,
                perm_add_certificacao, perm_view_certificacao
            ])
            self.stdout.write(self.style.SUCCESS('Permissões do Produtor configuradas'))
        else:
            self.stdout.write(self.style.WARNING('Grupo Produtor já existe'))
        
        # Grupo Empresa
        grupo_empresa, created = Group.objects.get_or_create(name='Empresa')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Empresa criado'))
            
            # Mesmas permissões do Produtor (podem cadastrar, comprar e vender)
            content_type_produto = ContentType.objects.get_for_model(Produto)
            content_type_certificacao = ContentType.objects.get_for_model(Certificacao)
            
            perm_add_produto = Permission.objects.get(
                codename='add_produto',
                content_type=content_type_produto,
            )
            perm_change_produto = Permission.objects.get(
                codename='change_produto',
                content_type=content_type_produto,
            )
            perm_delete_produto = Permission.objects.get(
                codename='delete_produto',
                content_type=content_type_produto,
            )
            perm_view_produto = Permission.objects.get(
                codename='view_produto',
                content_type=content_type_produto,
            )
            
            perm_add_certificacao = Permission.objects.get(
                codename='add_certificacao',
                content_type=content_type_certificacao,
            )
            perm_view_certificacao = Permission.objects.get(
                codename='view_certificacao',
                content_type=content_type_certificacao,
            )
            
            grupo_empresa.permissions.set([
                perm_add_produto, perm_change_produto, perm_delete_produto, perm_view_produto,
                perm_add_certificacao, perm_view_certificacao
            ])
            self.stdout.write(self.style.SUCCESS('Permissões da Empresa configuradas'))
        else:
            self.stdout.write(self.style.WARNING('Grupo Empresa já existe'))
        
        # Grupo Consumidor (Usuário Comum)
        grupo_consumidor, created = Group.objects.get_or_create(name='Consumidor')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Consumidor criado'))
            
            # Apenas visualização de produtos
            content_type_produto = ContentType.objects.get_for_model(Produto)
            perm_view_produto = Permission.objects.get(
                codename='view_produto',
                content_type=content_type_produto,
            )
            
            grupo_consumidor.permissions.set([perm_view_produto])
            self.stdout.write(self.style.SUCCESS('Permissões do Consumidor configuradas'))
        else:
            self.stdout.write(self.style.WARNING('Grupo Consumidor já existe'))
        
        self.stdout.write(self.style.SUCCESS('Grupos e permissões configurados com sucesso!'))
