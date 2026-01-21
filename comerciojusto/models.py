
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Pedido de compra

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('solicitado', 'Solicitado'),
        ('a_caminho', 'A Caminho'),
        ('entregue', 'Entregue'),
    ]
    id_pedido = models.AutoField(primary_key=True)
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, related_name='pedidos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    produtos = models.ManyToManyField('Produto', through='ItemPedido')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='solicitado')
    data_pedido = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Pedido {self.id_pedido} - {self.empresa.nome} - {self.get_status_display()}"

    class Meta:
        db_table = 'pedido'
        ordering = ['-data_pedido']

# Itens do pedido (produto + quantidade)
class ItemPedido(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE)
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.produto.nome} x{self.quantidade}"

    class Meta:
        db_table = 'item_pedido'

from django.db import models
from django.contrib.auth.models import User
import json

# Publicação/feed do perfil
class Publicacao(models.Model):
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='publicacoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username}: {self.conteudo[:30]}..."

    class Meta:
        db_table = 'publicacao'
        ordering = ['-data_publicacao']

# Perfil/pagina do produtor e vendedor:  utilizada para mostrar produtos, marca, contatos e outras informações pertinentes da empresa
# ligada a cada usuario
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo = models.CharField(max_length=20, choices=[
        ('produtor', 'Produtor'),
        ('empresa', 'Empresa'),
    ])
    logo = models.ImageField(upload_to='perfis/logos/', blank=True, null=True)
    capa = models.ImageField(upload_to='perfis/capas/', blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    noticia = models.TextField(blank=True, null=True)
    contato_adicional = models.CharField(max_length=255, blank=True, null=True)
    cpf_cnpj = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    taxa_avaliacao = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    total_vendas = models.IntegerField(default=0)
    total_avaliacoes = models.IntegerField(default=0)
    verificado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.tipo}"

    class Meta:
        db_table = 'perfil'

# Produtor
class Produtor(models.Model):
    id_produtor = models.AutoField(primary_key=True)
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='produtor', null=True, blank=True)
    nome = models.CharField(max_length=100)
    cpf_cnpj = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.cpf_cnpj})"

    class Meta:
        db_table = 'produtor'
        
# Empresa
class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='empresa', null=True, blank=True)
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    senha = models.CharField(max_length=255)
    telefone = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'empresa'

#Produto - aqui estou pensando em colocar outros tipos como adubo, antipragas e materiais relacionados a produção desses produtos
# Adicionar opção de upload de imagem que falta no site
class Produto(models.Model):
    CATEGORIA_CHOICES = [
        ('todas', 'Todas Categorias'),
        ('verduras', 'Verduras, folhas e ervas'),
        ('legumes', 'Legumes Orgânicos'),
        ('frutas', 'Frutas Orgânicas'),
        ('condimentos', 'Condimento & Tempero regional'),
        ('mercearia', 'Mercearia Orgânica'),
    ]
    
    id_produto = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, default='todas')
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preco_original = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    data_producao = models.DateField(blank=True, null=True)
    status_logistica = models.CharField(max_length=30, blank=True, null=True)
    produtor = models.ForeignKey(Produtor, on_delete=models.CASCADE)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, null=True, blank=True, related_name='produtos')
    estoque = models.IntegerField(default=0)
    vendas = models.IntegerField(default=0)
    taxa_avaliacao = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    ativo = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'produto'
        ordering = ['-destaque', '-vendas']

# o que seria Documento?
class Documento(models.Model):
    id_documento = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=50)
    arquivo = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    produtor = models.ForeignKey(Produtor, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipo} - {self.status}"

    class Meta:
        db_table = 'documento'

class Administrador(models.Model):
    id_adm = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    senha = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'administrador'

# Ajustar painel apropriado para o responsável que irá distribuir essas certificações
class Certificacao(models.Model):
    STATUS_CHOICES = [
        ('nao_disponivel', 'Não Disponível'),
        ('enviado_analise', 'Enviado para Análise'),
        ('aprovada', 'Aprovada'),
        ('reprovada', 'Reprovada'),
    ]
    
    id_certificacao = models.AutoField(primary_key=True)
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='certificacoes', null=True, blank=True)  # Produtor ou Empresa
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, blank=True, null=True)  # Opcional
    administrador = models.ForeignKey(Administrador, on_delete=models.SET_NULL, blank=True, null=True)  # Só após análise
    data_certificacao = models.DateField(blank=True, null=True)
    validade = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enviado_analise')
    arquivo_certificado = models.FileField(upload_to='certificacoes/', blank=True, null=True)
    parecer = models.TextField(blank=True, null=True)  # Parecer do administrador

    def clean(self):
        super().clean()
        arquivo = self.arquivo_certificado
        if arquivo:
            # Validação de tamanho (máx 5MB)
            if arquivo.size > 5 * 1024 * 1024:
                from django.core.exceptions import ValidationError
                raise ValidationError({'arquivo_certificado': 'O arquivo não pode exceder 5MB.'})
            # Validação de extensão
            ext = arquivo.name.split('.')[-1].lower()
            extensoes_permitidas = ['pdf', 'jpg', 'jpeg', 'png']
            extensoes_proibidas = ['exe', 'bat']
            if ext not in extensoes_permitidas or ext in extensoes_proibidas:
                from django.core.exceptions import ValidationError
                raise ValidationError({'arquivo_certificado': 'Extensão de arquivo não permitida. Apenas PDF ou imagem (JPG, JPEG, PNG).'})
        return arquivo
    def __str__(self):
        return f"Certificação {self.id_certificacao} - {self.get_status_display()}"

    class Meta:
        db_table = 'certificacao'

class Avaliacao(models.Model):
    id_avaliacao = models.AutoField(primary_key=True)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='avaliacoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estrelas = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)
    verificado_compra = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.estrelas} ⭐"

    class Meta:
        db_table = 'avaliacao'
        ordering = ['-data_avaliacao']

class AnuncioMarketplace(models.Model):
    id_anuncio = models.AutoField(primary_key=True)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    plataforma = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(max_length=255, blank=True, null=True)
    data_publicacao = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.plataforma} - {self.status}"

    class Meta:
        db_table = 'anuncio_marketplace'

class Carrinho(models.Model):
    id_carrinho = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    sessao_id = models.CharField(max_length=255, blank=True, null=True)
    itens = models.JSONField(default=dict)
    criado_em = models.DateTimeField(auto_now_add=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    rascunho_json = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Carrinho {self.id_carrinho}"

    class Meta:
        db_table = 'carrinho'

class Mensagem(models.Model):
    id_mensagem = models.AutoField(primary_key=True)
    remetente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_recebidas')
    assunto = models.CharField(max_length=255)
    corpo = models.TextField()
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"De: {self.remetente} Para: {self.destinatario}"

    class Meta:
        db_table = 'mensagem'