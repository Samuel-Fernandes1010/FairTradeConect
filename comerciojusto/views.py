from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Perfil, Produto, Carrinho, Mensagem
import json

def index(request):
    categoria = request.GET.get('categoria', 'todas')
    pesquisa = request.GET.get('pesquisa', '')
    
    produtos = Produto.objects.all()
    
    if categoria != 'todas':
        produtos = produtos.filter(categoria=categoria)
    
    if pesquisa:
        produtos = produtos.filter(nome__icontains=pesquisa) | produtos.filter(descricao__icontains=pesquisa)
    
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
        user = authenticate(username=email, password=senha)
        if user:
            login(request, user)
            return redirect('pos_login')
        return render(request, 'comerciojusto/login.html', {'erro': 'Credenciais inválidas'})
    return render(request, 'comerciojusto/login.html')

def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        tipo = request.POST.get('tipo')

        if User.objects.filter(username=email).exists():
            return render(request, 'comerciojusto/cadastro.html', {'erro': 'Usuário já existe'})

        from django.db import IntegrityError
        try:
            user = User.objects.create_user(username=email, email=email, password=senha, first_name=nome)
            perfil = Perfil.objects.create(user=user, tipo=tipo)
            # Criação automática do Produtor ou Empresa vinculado ao perfil
            if tipo == 'produtor':
                from .models import Produtor
                Produtor.objects.create(perfil=perfil, nome=nome, cpf_cnpj='', email=email, senha=senha)
            elif tipo == 'empresa':
                from .models import Empresa
                Empresa.objects.create(perfil=perfil, nome=nome, cnpj='', email=email, senha=senha)
            return redirect('login')
        except IntegrityError:
            return render(request, 'comerciojusto/cadastro.html', {'erro': 'Usuário já existe'})
    return render(request, 'comerciojusto/cadastro.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login')
def pos_login(request):
    return redirect('dashboard_perfil')


# PERFIL/FEED
@login_required(login_url='login')
def dashboard_perfil(request):
    perfil = Perfil.objects.get(user=request.user)
    produtos = None
    pedidos = None
    publicacoes = perfil.publicacoes.all()
    # Para produtor publicar produtos
    if perfil.tipo == 'produtor':
        produtos = Produto.objects.filter(produtor__perfil=perfil)
    # Para empresa verificar seus pedidos
    elif perfil.tipo == 'empresa':
        from .models import Pedido
        pedidos = Pedido.objects.filter(empresa__perfil=perfil).order_by('-data_pedido')

    # Gerenciar Feed
    from .models import Certificacao
    erro_certificacao = None
    if request.method == 'POST':
        from .models import Publicacao
        
        if 'excluir_publicacao_id' in request.POST:
            pub_id = request.POST.get('excluir_publicacao_id')
            pub = Publicacao.objects.filter(id=pub_id, usuario=request.user).first()
            if pub:
                pub.delete()
            return redirect('dashboard_perfil')

        if 'editar_publicacao_id' in request.POST:
            pub_id = request.POST.get('editar_publicacao_id')
            novo_conteudo = request.POST.get('editar_conteudo', '').strip()
            pub = Publicacao.objects.filter(id=pub_id, usuario=request.user).first()
            if pub and novo_conteudo:
                pub.conteudo = novo_conteudo
                pub.save()
            return redirect('dashboard_perfil')

        if 'noticia' in request.POST and request.POST.get('noticia').strip():
            Publicacao.objects.create(perfil=perfil, usuario=request.user, conteudo=request.POST.get('noticia'))
            return redirect('dashboard_perfil')
        
        if 'excluir_produto_id' in request.POST and perfil.tipo == 'produtor':
            prod_id = request.POST.get('excluir_produto_id')
            prod = Produto.objects.filter(id_produto=prod_id, produtor=perfil.produtor).first()
            if prod:
                prod.delete()
            return redirect('dashboard_perfil')
        
        if 'nome_produto' in request.POST and perfil.tipo == 'produtor':
            nome = request.POST.get('nome_produto')
            preco = request.POST.get('preco_produto')
            imagem = request.FILES.get('imagem_produto')
            descricao = request.POST.get('descricao_produto', '')
            categoria = request.POST.get('categoria_produto', 'todas')
            produtor = getattr(perfil, 'produtor', None)
            if not produtor:
                return render(request, 'comerciojusto/dashboard_perfil.html', {
                    'perfil': perfil,
                    'produtos': produtos,
                    'publicacoes': publicacoes,
                    'user': request.user,
                    'erro_produto': 'Seu perfil não está vinculado a um produtor. Contate o administrador.'
                })
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

        # Envio da certificação
        if 'nova_certificacao' in request.POST:
            nome_cert = request.POST.get('nome_certificacao', '').strip()
            validade = request.POST.get('validade_certificacao', '').strip()
            arquivo = request.FILES.get('arquivo_certificado')
            if not nome_cert or not arquivo:
                erro_certificacao = 'Preencha o nome e envie o arquivo da certificação.'
            else:
                cert = Certificacao.objects.create(
                    perfil=perfil,
                    status='enviado_analise',
                    arquivo_certificado=arquivo,
                    validade=validade if validade else None,
                    data_certificacao=None
                )
                return redirect('dashboard_perfil')

        
        perfil.descricao = request.POST.get('descricao', perfil.descricao)
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
        'publicacoes': publicacoes,
        'user': request.user,
        'certificacoes': certificacoes,
        'erro_certificacao': erro_certificacao,
    }
    return render(request, 'comerciojusto/dashboard_perfil.html', context)


def detalhes_produto(request, id_produto):
    produto = get_object_or_404(Produto, id_produto=id_produto)
    produtor_info = produto.produtor
    from .models import Avaliacao, Certificacao
    avaliacoes = Avaliacao.objects.filter(perfil=produtor_info.perfil)
    certificacoes_aprovadas = Certificacao.objects.filter(perfil=produtor_info.perfil, status='aprovada')
    
    # Avaliação
    erro_avaliacao = None
    if request.method == 'POST' and request.user.is_authenticated:
        estrelas_raw = request.POST.get('estrelas', '').strip()
        comentario = request.POST.get('comentario', '').strip()
        if estrelas_raw.isdigit():
            estrelas = int(estrelas_raw)
            if estrelas > 0:
                Avaliacao.objects.create(perfil=produtor_info.perfil, usuario=request.user, estrelas=estrelas, comentario=comentario)
                return redirect('detalhes_produto', id_produto=produto.id_produto)
        else:
            erro_avaliacao = 'Selecione sua estrela para avaliar.'
    context = {
        'produto': produto,
        'produtor_info': produtor_info,
        'avaliacoes': avaliacoes,
        'erro_avaliacao': erro_avaliacao,
        'certificacoes_aprovadas': certificacoes_aprovadas,
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
    mensagens = Mensagem.objects.filter(destinatario=request.user).order_by('-criada_em')
    nao_lidas = mensagens.filter(lida=False).count()
    
    context = {
        'mensagens': mensagens,
        'nao_lidas': nao_lidas,
    }
    return render(request, 'comerciojusto/caixa_entrada.html', context)


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
        sessao_id = request.session.session_key
        if not sessao_id:
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
    
    from django.shortcuts import redirect
    return redirect('visualizar_carrinho')


@login_required(login_url='login')
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


