"""
Middleware customizado para otimizações de cache e performance
"""
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser


class UserCacheMiddleware:
    """
    Middleware para cachear informações do usuário autenticado
    Reduz consultas ao banco de dados
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Cachear usuário autenticado
        if request.user.is_authenticated:
            cache_key = f'user_data_{request.user.id}'
            user_data = cache.get(cache_key)
            
            if user_data is None:
                # Armazenar dados do usuário no cache
                user_data = {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'is_staff': request.user.is_staff,
                    'is_superuser': request.user.is_superuser,
                }
                cache.set(cache_key, user_data, 300)  # 5 minutos
            
            # Adicionar dados cacheados ao request
            request.cached_user_data = user_data
        
        response = self.get_response(request)
        return response


class PerfilCacheMiddleware:
    """
    Middleware para cachear perfil do usuário (Produtor/Empresa)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            cache_key = f'perfil_{request.user.id}'
            perfil = cache.get(cache_key)
            
            if perfil is None:
                try:
                    from .models import Perfil
                    perfil = Perfil.objects.select_related('user').get(user=request.user)
                    # Cachear o perfil por 10 minutos
                    cache.set(cache_key, perfil, 600)
                except:
                    perfil = None
            
            request.cached_perfil = perfil
        
        response = self.get_response(request)
        return response


class CarrinhoCountMiddleware:
    """
    Middleware para otimizar contagem de itens no carrinho
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se já existe contagem na sessão
        if 'carrinho_itens' not in request.session:
            if request.user.is_authenticated:
                # Buscar do banco
                from .models import Carrinho
                carrinho = Carrinho.objects.filter(usuario=request.user).first()
                if carrinho and carrinho.itens:
                    request.session['carrinho_itens'] = len(carrinho.itens)
                else:
                    request.session['carrinho_itens'] = 0
            else:
                # Buscar da sessão
                sessao_id = request.session.session_key
                if sessao_id:
                    from .models import Carrinho
                    carrinho = Carrinho.objects.filter(sessao_id=sessao_id).first()
                    if carrinho and carrinho.itens:
                        request.session['carrinho_itens'] = len(carrinho.itens)
                    else:
                        request.session['carrinho_itens'] = 0
                else:
                    request.session['carrinho_itens'] = 0
        
        response = self.get_response(request)
        return response
