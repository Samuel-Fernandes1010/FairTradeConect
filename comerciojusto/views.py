from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Perfil, Produto, Carrinho, Mensagem
import json

# Comentário geral: seria interessante ajustar para reduzir If/else e Try/Except com classes e afins...

# Funções auxiliares para verificação de grupos
def is_produtor(user):
    """Verifica se o usuário pertence ao grupo Produtor"""
    return user.groups.filter(name='Produtor').exists()

def is_empresa(user):
    """Verifica se o usuário pertence ao grupo Empresa"""
    return user.groups.filter(name='Empresa').exists()

def is_produtor_ou_empresa(user):
    """Verifica se o usuário pertence ao grupo Produtor ou Empresa"""
    return is_produtor(user) or is_empresa(user)

def verifica_acesso_perfil(user, perfil_tipo):
    """Verifica se o usuário tem acesso ao tipo de perfil especificado"""
    if user.is_superuser:
        return True
    if perfil_tipo == 'produtor':
        return is_produtor(user)
    elif perfil_tipo == 'empresa':
        return is_empresa(user)
    return False

def acesso_negado(request):
    """View para exibir página de acesso negado"""
    return render(request, 'comerciojusto/acesso_negado.html', status=403)


@login_required(login_url='login')
def completar_cadastro_social(request):
    """
    View para completar cadastro de usuários que entraram via login social (Google)
    Solicita informações adicionais: tipo de perfil, CPF/CNPJ, etc.
    """
    # Verificar se o usuário já tem perfil
    perfil_existe = Perfil.objects.filter(user=request.user).exists()
    
    if perfil_existe:
        # Se já tem perfil, redirecionar para dashboard
        return redirect('dashboard_perfil')
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        cpf_cnpj = request.POST.get('cpf_cnpj', '')
        nome = request.POST.get('nome', request.user.first_name)
        senha = request.POST.get('senha', '')
        senha_confirmacao = request.POST.get('senha_confirmacao', '')
        
        # Validações básicas
        if not tipo or tipo not in ['produtor', 'empresa']:
            return render(request, 'comerciojusto/completar_cadastro_social.html', {
                'erro': 'Selecione um tipo de conta válido',
                'nome': nome
            })
        
        if not cpf_cnpj:
            return render(request, 'comerciojusto/completar_cadastro_social.html', {
                'erro': 'CPF/CNPJ é obrigatório',
                'tipo': tipo,
                'nome': nome
            })
        
        if not senha:
            return render(request, 'comerciojusto/completar_cadastro_social.html', {
                'erro': 'Senha é obrigatória',
                'tipo': tipo,
                'nome': nome,
                'cpf_cnpj': cpf_cnpj
            })
        
        if senha != senha_confirmacao:
            return render(request, 'comerciojusto/completar_cadastro_social.html', {
                'erro': 'As senhas não coincidem',
                'tipo': tipo,
                'nome': nome,
                'cpf_cnpj': cpf_cnpj
            })
        
        if len(senha) < 6:
            return render(request, 'comerciojusto/completar_cadastro_social.html', {
                'erro': 'A senha deve ter pelo menos 6 caracteres',
                'tipo': tipo,
                'nome': nome,
                'cpf_cnpj': cpf_cnpj
            })
        
        # Atualizar nome do usuário se fornecido
        if nome and nome != request.user.first_name:
            request.user.first_name = nome
            request.user.save()
        
        # Definir senha para permitir login tradicional
        request.user.set_password(senha)
        request.user.save()
        
        # Criar perfil
        perfil = Perfil.objects.create(
            user=request.user,
            tipo=tipo,
            cpf_cnpj=cpf_cnpj
        )
        
        # Criação automática do Produtor/Empresa vinculado ao perfil
        if tipo == 'produtor':
            from .models import Produtor
            Produtor.objects.create(
                perfil=perfil,
                nome=nome or request.user.first_name,
                cpf_cnpj=cpf_cnpj,
                email=request.user.email,
                senha=senha  # Salvar senha no modelo Produtor
            )
        elif tipo == 'empresa':
            from .models import Empresa
            Empresa.objects.create(
                perfil=perfil,
                nome=nome or request.user.first_name,
                cnpj=cpf_cnpj,
                email=request.user.email,
                senha=senha  # Salvar senha no modelo Empresa
            )
        
        # Adicionar usuário ao grupo correspondente
        from django.contrib.auth.models import Group
        grupo = Group.objects.filter(name=tipo.capitalize()).first()
        if grupo:
            request.user.groups.add(grupo)
        
        # Redirecionar para dashboard
        return redirect('dashboard_perfil')
    
    # GET - mostrar formulário
    context = {
        'nome': request.user.first_name or request.user.username,
        'email': request.user.email,
    }
    return render(request, 'comerciojusto/completar_cadastro_social.html', context)


def index(request):
    categoria = request.GET.get('categoria', 'todas')
    pesquisa = request.GET.get('pesquisa', '')
    
    produtos = Produto.objects.all()
    
    if categoria != 'todas':
        produtos = produtos.filter(categoria=categoria)
    
    if pesquisa:
        produtos = produtos.filter(nome__icontains=pesquisa) | produtos.filter(descricao__icontains=pesquisa)
   # Possibilidade de adicionar outras categorias (adubos, fertilizantes, maquinário e etc..) 
    categorias = [
        ('todas', 'Todas Categorias'),
        ('verduras', 'Verduras, folhas e ervas'),
        ('legumes', 'Legumes Orgânicos'),
        ('frutas', 'Frutas Orgânicas'),
        ('condimentos', 'Condimento & Tempero regional'),
        ('mercearia', 'Mercearia Orgânica'),
    ]
    
    context = {
        'produtos': produtos,
        'categorias': categorias,
        'categoria_selecionada': categoria,
        'pesquisa': pesquisa
    }
    return render(request, 'comerciojusto/index.html', context)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        # Salvar session_key ANTES do login (pode mudar após autenticação)
        sessao_id_antiga = request.session.session_key
        
        user = authenticate(username=email, password=senha)
        if user:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Transferir carrinho da sessão antiga para o usuário
            if sessao_id_antiga:
                carrinho_sessao = Carrinho.objects.filter(sessao_id=sessao_id_antiga).first()
                if carrinho_sessao and carrinho_sessao.itens:
                    # Buscar ou criar carrinho do usuário
                    carrinho_usuario, created = Carrinho.objects.get_or_create(usuario=user)
                    
                    # Mesclar itens
                    itens_usuario = carrinho_usuario.itens or {}
                    itens_sessao = carrinho_sessao.itens or {}
                    
                    for produto_id, dados in itens_sessao.items():
                        if produto_id in itens_usuario:
                            # Somar quantidades se produto já existe
                            itens_usuario[produto_id]['quantidade'] += dados['quantidade']
                        else:
                            # Adicionar novo produto
                            itens_usuario[produto_id] = dados
                    
                    # Salvar carrinho do usuário
                    carrinho_usuario.itens = itens_usuario
                    carrinho_usuario.rascunho_json = itens_usuario
                    carrinho_usuario.save()
                    
                    # Atualizar sessão
                    request.session['carrinho_itens'] = len(itens_usuario)
                    
                    # Deletar carrinho da sessão
                    carrinho_sessao.delete()
            
            return redirect('pos_login')
        return render(request, 'comerciojusto/login.html', {'erro': 'Credenciais inválidas'})
    return render(request, 'comerciojusto/login.html')

def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        tipo = request.POST.get('tipo')
        cpf_cnpj = request.POST.get('cpf_cnpj', '')

        # Verificar se já existe usuário com esse email ou username
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            return render(request, 'comerciojusto/cadastro.html', {'erro': 'Email já cadastrado'})

        # Salvar session_key ANTES do login
        sessao_id_antiga = request.session.session_key

        try:
            user = User.objects.create_user(username=email, email=email, password=senha, first_name=nome)
            perfil = Perfil.objects.create(user=user, tipo=tipo, cpf_cnpj=cpf_cnpj)
            
            # Criação automática do Produtor ou Empresa vinculado ao perfil
            if tipo == 'produtor':
                from .models import Produtor
                Produtor.objects.create(perfil=perfil, nome=nome, cpf_cnpj=cpf_cnpj, email=email, senha=senha)
            elif tipo == 'empresa':
                from .models import Empresa
                Empresa.objects.create(perfil=perfil, nome=nome, cnpj=cpf_cnpj, email=email, senha=senha)
            
            # Adicionar usuário ao grupo correspondente
            from django.contrib.auth.models import Group
            if tipo in ['produtor', 'empresa']:
                grupo = Group.objects.filter(name=tipo.capitalize()).first()
                if grupo:
                    user.groups.add(grupo)
            
            # Fazer login automático
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Transferir carrinho da sessão antiga para o usuário
            if sessao_id_antiga:
                carrinho_sessao = Carrinho.objects.filter(sessao_id=sessao_id_antiga).first()
                if carrinho_sessao and carrinho_sessao.itens:
                    # Buscar ou criar carrinho do usuário
                    carrinho_usuario, created = Carrinho.objects.get_or_create(usuario=user)
                    
                    # Mesclar itens
                    itens_usuario = carrinho_usuario.itens or {}
                    itens_sessao = carrinho_sessao.itens or {}
                    
                    for produto_id, dados in itens_sessao.items():
                        if produto_id in itens_usuario:
                            itens_usuario[produto_id]['quantidade'] += dados['quantidade']
                        else:
                            itens_usuario[produto_id] = dados
                    
                    # Salvar carrinho do usuário
                    carrinho_usuario.itens = itens_usuario
                    carrinho_usuario.rascunho_json = itens_usuario
                    carrinho_usuario.save()
                    
                    # Atualizar sessão
                    request.session['carrinho_itens'] = len(itens_usuario)
                    
                    # Deletar carrinho da sessão
                    carrinho_sessao.delete()
            
            return redirect('dashboard_perfil')
        except Exception as e:
            return render(request, 'comerciojusto/cadastro.html', {'erro': f'Erro ao criar usuário: {str(e)}'})
    return render(request, 'comerciojusto/cadastro.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login')
def pos_login(request):
    # Verificar se o usuário tem perfil
    try:
        perfil = Perfil.objects.get(user=request.user)
        # Tem perfil, vai para dashboard
        return redirect('dashboard_perfil')
    except Perfil.DoesNotExist:
        # Não tem perfil, precisa completar cadastro
        return redirect('completar_cadastro_social')


@login_required(login_url='login')
def dashboard_perfil(request):
    # Verificar se o usuário tem perfil
    try:
        perfil = Perfil.objects.get(user=request.user)
    except Perfil.DoesNotExist:
        # Se for admin/superuser sem perfil, redirecionar para admin
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')
        # Se for usuário comum sem perfil, redirecionar para completar cadastro
        return redirect('completar_cadastro_social')
    
    # Verificar se o usuário tem permissão para acessar este tipo de perfil
    if not verifica_acesso_perfil(request.user, perfil.tipo):
        return redirect('acesso_negado')
    
    produtos = None
    pedidos = None
    
    # Para produtor e empresa visualizar seus produtos
    if perfil.tipo in ['produtor', 'empresa']:
        produtos = Produto.objects.filter(perfil=perfil)
    
    # Para produtor e empresa verificar seus pedidos (pedidos dos produtos deles)
    if perfil.tipo in ['produtor', 'empresa']:
        from .models import Pedido
        # Buscar pedidos que contenham produtos do perfil
        pedidos = Pedido.objects.filter(
            itempedido__produto__perfil=perfil
        ).distinct().order_by('-data_pedido')

    # Gerenciar certificações
    from .models import Certificacao
    erro_certificacao = None
    if request.method == 'POST':
        
        if 'excluir_produto_id' in request.POST:
            prod_id = request.POST.get('excluir_produto_id')
            prod = Produto.objects.filter(id_produto=prod_id, perfil=perfil).first()
            if prod:
                prod.delete()
            return redirect('dashboard_perfil')
        
        # Adicionar produto (para produtor e empresa)
        if 'nome_produto' in request.POST and perfil.tipo in ['produtor', 'empresa']:
            nome = request.POST.get('nome_produto')
            preco = request.POST.get('preco_produto')
            imagem = request.FILES.get('imagem_produto')
            descricao = request.POST.get('descricao_produto', '')
            categoria = request.POST.get('categoria_produto', 'todas')
            
            # Obter ou criar o produtor vinculado apenas se for tipo 'produtor'
            from .models import Produtor
            produtor = None
            
            if perfil.tipo == 'produtor':
                produtor = getattr(perfil, 'produtor', None)
                if not produtor:
                    # Criar produtor automaticamente se não existir
                    produtor = Produtor.objects.create(
                        perfil=perfil,
                        nome=request.user.first_name or request.user.username,
                        cpf_cnpj=perfil.cpf_cnpj or '',
                        email=request.user.email,
                        senha=''
                    )
            
            # Para empresas, produtor fica None (campo agora é opcional)
            if nome and preco and categoria:
                Produto.objects.create(
                    nome=nome,
                    preco=preco,
                    produtor=produtor,
                    perfil=perfil,
                    imagem=imagem,
                    descricao=descricao,
                    categoria=categoria
                )
            return redirect('dashboard_perfil')

        # Envio da certificação (vincular a um produto)
        if 'nova_certificacao' in request.POST:
            produto_id = request.POST.get('produto_certificacao', '').strip()
            validade = request.POST.get('validade_certificacao', '').strip()
            arquivo = request.FILES.get('arquivo_certificado')
            
            if not produto_id or not arquivo:
                erro_certificacao = 'Selecione um produto e envie o arquivo da certificação.'
            else:
                produto = Produto.objects.filter(id_produto=produto_id, perfil=perfil).first()
                if produto:
                    cert = Certificacao.objects.create(
                        perfil=perfil,
                        produto=produto,
                        status='enviado_analise',
                        arquivo_certificado=arquivo,
                        validade=validade if validade else None,
                        data_certificacao=None
                    )
                    return redirect('dashboard_perfil')
                else:
                    erro_certificacao = 'Produto inválido.'

        # Atualizar perfil
        if 'atualizar_perfil' in request.POST:
            perfil.descricao = request.POST.get('descricao', perfil.descricao)
            perfil.bio = request.POST.get('bio', perfil.bio)
            if 'logo' in request.FILES:
                perfil.logo = request.FILES['logo']
            perfil.save()
            return redirect('dashboard_perfil')

    # Certificações do perfil
    certificacoes = perfil.certificacoes.all().order_by('-id_certificacao')
    context = {
        'perfil': perfil,
        'produtos': produtos,
        'pedidos': pedidos,
        'user': request.user,
        'certificacoes': certificacoes,
        'erro_certificacao': erro_certificacao,
    }
    return render(request, 'comerciojusto/dashboard_perfil.html', context)


def detalhes_produto(request, id_produto):
    produto = get_object_or_404(Produto, id_produto=id_produto)
    
    # Se o produto tem produtor, usar perfil do produtor; caso contrário, usar perfil direto
    if produto.produtor:
        produtor_info = produto.produtor
        perfil_produto = produtor_info.perfil
    else:
        produtor_info = None
        perfil_produto = produto.perfil
    
    from .models import Avaliacao, Certificacao
    avaliacoes = Avaliacao.objects.filter(perfil=perfil_produto)
    certificacoes_aprovadas = Certificacao.objects.filter(perfil=perfil_produto, status='aprovada')
    
    # Verificar se este produto específico tem certificação aprovada
    produto_certificado = Certificacao.objects.filter(
        produto=produto, 
        status='aprovada'
    ).exists()
    
    # Avaliação
    erro_avaliacao = None
    if request.method == 'POST' and request.user.is_authenticated:
        estrelas_raw = request.POST.get('estrelas', '').strip()
        comentario = request.POST.get('comentario', '').strip()
        if estrelas_raw.isdigit():
            estrelas = int(estrelas_raw)
            if estrelas > 0:
                Avaliacao.objects.create(perfil=perfil_produto, usuario=request.user, estrelas=estrelas, comentario=comentario)
                return redirect('detalhes_produto', id_produto=produto.id_produto)
        else:
            erro_avaliacao = 'Selecione sua estrela para avaliar.'
    context = {
        'produto': produto,
        'produtor_info': produtor_info,
        'perfil_produto': perfil_produto,
        'produtor_info': produtor_info,
        'avaliacoes': avaliacoes,
        'erro_avaliacao': erro_avaliacao,
        'certificacoes_aprovadas': certificacoes_aprovadas,
        'produto_certificado': produto_certificado,
    }
    return render(request, 'comerciojusto/detalhes_produto.html', context)
# Admin aprovar/reprovar certificações
from django.contrib.auth.decorators import user_passes_test
@user_passes_test(lambda u: u.is_superuser)
def gerenciar_certificacoes(request):
    from .models import Certificacao
    certificacoes = Certificacao.objects.exclude(status='aprovada').order_by('-id_certificacao')
    msg = None
    if request.method == 'POST':
        cert_id = request.POST.get('cert_id')
        acao = request.POST.get('acao')
        parecer = request.POST.get('parecer', '').strip()
        cert = Certificacao.objects.filter(id_certificacao=cert_id).first()
        if cert:
            if acao == 'aprovar':
                cert.status = 'aprovada'
                cert.parecer = parecer
            elif acao == 'reprovar':
                cert.status = 'reprovada'
                cert.parecer = parecer
            cert.save()
            msg = 'Certificação atualizada com sucesso.'
    return render(request, 'comerciojusto/gerenciar_certificacoes.html', {'certificacoes': certificacoes, 'msg': msg})


@login_required(login_url='login')


@login_required(login_url='login')
def caixa_entrada(request):
    from django.db.models import Q, Max
    
    # Processar ações (excluir, marcar como não lida)
    if request.method == 'POST':
        acao = request.POST.get('acao')
        mensagens_ids = request.POST.getlist('mensagens_selecionadas')
        
        if acao == 'excluir' and mensagens_ids:
            Mensagem.objects.filter(
                Q(remetente=request.user) | Q(destinatario=request.user),
                id_mensagem__in=mensagens_ids
            ).delete()
        elif acao == 'marcar_nao_lida' and mensagens_ids:
            Mensagem.objects.filter(
                destinatario=request.user,
                id_mensagem__in=mensagens_ids
            ).update(lida=False)
        
        return redirect('caixa_entrada')
    
    # Buscar todas as mensagens do usuário
    mensagens = Mensagem.objects.filter(
        Q(remetente=request.user) | Q(destinatario=request.user)
    )
    
    # Agrupar por conversas (identificar o outro usuário)
    conversas_dict = {}
    for msg in mensagens:
        outro_usuario = msg.destinatario if msg.remetente == request.user else msg.remetente
        
        if outro_usuario.id not in conversas_dict:
            conversas_dict[outro_usuario.id] = {
                'usuario': outro_usuario,
                'mensagens': [],
                'ultima_mensagem': msg,
                'nao_lidas': 0
            }
        
        conversas_dict[outro_usuario.id]['mensagens'].append(msg)
        
        # Atualizar última mensagem se for mais recente
        if msg.criada_em > conversas_dict[outro_usuario.id]['ultima_mensagem'].criada_em:
            conversas_dict[outro_usuario.id]['ultima_mensagem'] = msg
        
        # Contar não lidas
        if msg.destinatario == request.user and not msg.lida:
            conversas_dict[outro_usuario.id]['nao_lidas'] += 1
    
    # Ordenar conversas por última mensagem
    conversas = sorted(
        conversas_dict.values(),
        key=lambda x: x['ultima_mensagem'].criada_em,
        reverse=True
    )
    
    # Total de mensagens não lidas
    total_nao_lidas = sum(c['nao_lidas'] for c in conversas)
    
    context = {
        'conversas': conversas,
        'total_nao_lidas': total_nao_lidas,
    }
    return render(request, 'comerciojusto/caixa_entrada.html', context)


@login_required(login_url='login')
def visualizar_conversa(request, usuario_id):
    """View para visualizar uma conversa completa com outro usuário"""
    from django.db.models import Q
    
    outro_usuario = get_object_or_404(User, id=usuario_id)
    
    # Buscar todas as mensagens entre os dois usuários
    mensagens = Mensagem.objects.filter(
        Q(remetente=request.user, destinatario=outro_usuario) |
        Q(remetente=outro_usuario, destinatario=request.user)
    ).order_by('criada_em')
    
    # Marcar como lidas as mensagens recebidas
    mensagens.filter(destinatario=request.user, lida=False).update(lida=True)
    
    # Enviar nova mensagem
    if request.method == 'POST':
        corpo = request.POST.get('corpo', '').strip()
        if corpo:
            Mensagem.objects.create(
                remetente=request.user,
                destinatario=outro_usuario,
                assunto='Re: Conversa',
                corpo=corpo
            )
            return redirect('visualizar_conversa', usuario_id=usuario_id)
    
    context = {
        'outro_usuario': outro_usuario,
        'mensagens': mensagens,
    }
    return render(request, 'comerciojusto/visualizar_conversa.html', context)


@require_POST
def adicionar_carrinho(request):
    produto_id = request.POST.get('produto_id')
    quantidade = int(request.POST.get('quantidade', 1))
    
    try:
        produto = Produto.objects.get(id_produto=produto_id)
    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado'})
    
    if request.user.is_authenticated:
        carrinho, created = Carrinho.objects.get_or_create(usuario=request.user)
    else:
        # Garantir que a sessão existe
        if not request.session.session_key:
            request.session.create()
        sessao_id = request.session.session_key
        
        carrinho, created = Carrinho.objects.get_or_create(sessao_id=sessao_id)
    
    itens = carrinho.itens or {}
    
    if str(produto_id) in itens:
        itens[str(produto_id)]['quantidade'] += quantidade
    else:
        itens[str(produto_id)] = {
            'quantidade': quantidade,
            'preco': str(produto.preco),
            'nome': produto.nome,
        }
    
    carrinho.itens = itens
    carrinho.rascunho_json = itens
    carrinho.save()
    
    request.session['carrinho_itens'] = len(itens)
    request.session.modified = True  # Forçar salvamento da sessão
    
    from django.shortcuts import redirect
    return redirect('visualizar_carrinho')


def visualizar_carrinho(request):

    carrinho = None
    if request.user.is_authenticated:
        carrinho = Carrinho.objects.filter(usuario=request.user).first()
    else:
        sessao_id = request.session.session_key
        carrinho = Carrinho.objects.filter(sessao_id=sessao_id).first()

    if request.method == 'POST' and 'remover_produto_id' in request.POST:
        produto_id_remover = request.POST.get('remover_produto_id')
        if carrinho and carrinho.itens and produto_id_remover in carrinho.itens:
            itens_carrinho = carrinho.itens
            itens_carrinho.pop(produto_id_remover, None)
            carrinho.itens = itens_carrinho
            carrinho.rascunho_json = itens_carrinho
            carrinho.save()
            request.session['carrinho_itens'] = len(itens_carrinho)
            return redirect('visualizar_carrinho')

    itens = []
    total = 0
    
    if carrinho and carrinho.itens:
        for produto_id, info in carrinho.itens.items():
            try:
                produto = Produto.objects.get(id_produto=produto_id)
                subtotal = float(info['preco']) * info['quantidade']
                itens.append({
                    'produto': produto,
                    'quantidade': info['quantidade'],
                    'subtotal': subtotal,
                })
                total += subtotal
            except Produto.DoesNotExist:
                pass
    
    context = {
        'itens': itens,
        'total': total,
        'carrinho': carrinho,
    }
    return render(request, 'comerciojusto/carrinho.html', context)


@login_required(login_url='login')
def editar_perfil(request):
    """View para edição completa do perfil do usuário"""
    try:
        perfil = Perfil.objects.get(user=request.user)
    except Perfil.DoesNotExist:
        # Se for admin/superuser sem perfil, redirecionar para admin
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')
        # Se não tem perfil, redirecionar para completar cadastro social
        return redirect('completar_cadastro_social')
    
    # Verificar se o usuário tem permissão para acessar este tipo de perfil
    if not verifica_acesso_perfil(request.user, perfil.tipo):
        return redirect('acesso_negado')
    
    if request.method == 'POST':
        # Atualizar dados do usuário
        request.user.first_name = request.POST.get('nome', request.user.first_name)
        request.user.save()
        
        # Atualizar dados do perfil
        perfil.bio = request.POST.get('bio', perfil.bio)
        perfil.descricao = request.POST.get('descricao', perfil.descricao)
        perfil.contato_adicional = request.POST.get('contato_adicional', perfil.contato_adicional)
        perfil.cpf_cnpj = request.POST.get('cpf_cnpj', perfil.cpf_cnpj)
        perfil.endereco = request.POST.get('endereco', perfil.endereco)
        perfil.cidade = request.POST.get('cidade', perfil.cidade)
        perfil.estado = request.POST.get('estado', perfil.estado)
        
        # Upload de foto de perfil
        if 'logo' in request.FILES:
            perfil.logo = request.FILES['logo']
        
        perfil.save()
        
        return redirect('meu_perfil')
    
    context = {
        'perfil': perfil,
        'user': request.user,
    }
    return render(request, 'comerciojusto/meu_perfil.html', context)


@login_required(login_url='login')
@require_POST
def desconectar_google(request):
    """View para desconectar conta Google do perfil do usuário"""
    from allauth.socialaccount.models import SocialAccount
    
    try:
        # Buscar a conta Google associada ao usuário
        social_account = SocialAccount.objects.get(user=request.user, provider='google')
        social_account.delete()
    except SocialAccount.DoesNotExist:
        pass
    
    return redirect('meu_perfil')


@login_required(login_url='login')
def enviar_mensagem(request, destinatario_id):
    """View para enviar mensagem a outro usuário"""
    destinatario = get_object_or_404(User, id=destinatario_id)
    
    if request.method == 'POST':
        assunto = request.POST.get('assunto', '').strip()
        corpo = request.POST.get('corpo', '').strip()
        
        if assunto and corpo:
            Mensagem.objects.create(
                remetente=request.user,
                destinatario=destinatario,
                assunto=assunto,
                corpo=corpo
            )
            return redirect('detalhes_produto', id_produto=request.POST.get('produto_id', 0))
    
    return redirect('index')


@login_required(login_url='login')
def marcar_mensagem_lida(request, mensagem_id):
    """View para marcar mensagem como lida"""
    mensagem = get_object_or_404(Mensagem, id_mensagem=mensagem_id, destinatario=request.user)
    mensagem.lida = True
    mensagem.save()
    return redirect('caixa_entrada')


def perfil_publico(request, perfil_id):
    """View para exibir perfil público de produtor/empresa"""
    perfil = get_object_or_404(Perfil, id=perfil_id)
    produtos = Produto.objects.filter(perfil=perfil, ativo=True)
    
    from .models import Certificacao
    certificacoes_aprovadas = Certificacao.objects.filter(
        perfil=perfil, 
        status='aprovada'
    )
    
    from .models import Avaliacao
    avaliacoes = Avaliacao.objects.filter(perfil=perfil).order_by('-data_avaliacao')[:10]
    
    context = {
        'perfil': perfil,
        'produtos': produtos,
        'certificacoes_aprovadas': certificacoes_aprovadas,
        'avaliacoes': avaliacoes,
    }
    return render(request, 'comerciojusto/perfil_publico.html', context)


