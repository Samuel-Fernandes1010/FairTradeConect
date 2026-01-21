from django.contrib import admin
from .models import Produtor, Empresa, Produto, Documento, Administrador, Certificacao, AnuncioMarketplace, Perfil, Carrinho, Mensagem
# Register your models here.

# registro do painel admnistrativo com permissões e afins: falta adicionar camada de proteção e otimizar painels para deixar mais "clean" ou melhorar algo
# search_fields = pesquisa 
# list_display = exibe dados
# list_filter = lista por filtros

@admin.register(Perfil) #Perfil
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo')
    search_fields = ('user__username', 'user__email')

@admin.register(Produtor) #Produtor
class ProdutorAdmin(admin.ModelAdmin):
    list_display = ('id_produtor', 'nome', 'cpf_cnpj', 'email', 'telefone')
    search_fields = ('nome', 'cpf_cnpj', 'email')

@admin.register(Empresa) #Empresa
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('id_empresa', 'nome', 'cnpj', 'email', 'telefone')
    search_fields = ('nome', 'cnpj', 'email')


# Adicionar os outros tipos presentes no models.py
@admin.register(Produto) #Produto
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id_produto', 'nome', 'categoria', 'preco', 'produtor', 'data_producao', 'status_logistica')
    list_filter = ('categoria', 'status_logistica')
    search_fields = ('nome', 'descricao')

@admin.register(Documento) #Documento
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('id_documento', 'tipo', 'status', 'produtor')
    list_filter = ('status', 'tipo')

@admin.register(Administrador) #ADM
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('id_adm', 'nome', 'email')
    search_fields = ('nome', 'email')

@admin.register(Certificacao) #Ceritificação
class CertificacaoAdmin(admin.ModelAdmin):
    list_display = ('id_certificacao', 'produto', 'administrador', 'data_certificacao', 'validade', 'status')
    list_filter = ('status',)

@admin.register(AnuncioMarketplace) #MKT - pode otimizar ?
class AnuncioMarketplaceAdmin(admin.ModelAdmin):
    list_display = ('id_anuncio', 'produto', 'plataforma', 'url', 'data_publicacao', 'status')
    list_filter = ('plataforma', 'status')
    search_fields = ('url',)

@admin.register(Carrinho) # Carrinho
class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ('id_carrinho', 'usuario', 'sessao_id', 'criado_em', 'atualizado_em')
    list_filter = ('criado_em',)

@admin.register(Mensagem) # Chat
class MensagemAdmin(admin.ModelAdmin):
    list_display = ('id_mensagem', 'remetente', 'destinatario', 'assunto', 'lida', 'criada_em')
    list_filter = ('lida', 'criada_em')
    search_fields = ('assunto', 'corpo')
