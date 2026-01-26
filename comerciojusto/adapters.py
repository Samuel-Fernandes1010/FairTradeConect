from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import Perfil


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter customizado para controlar o fluxo de login social
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Verifica se o usuário já tem perfil ao fazer login
        """
        user = sociallogin.user
        if user.id:
            # Usuário já existe, verifica se tem perfil
            if not hasattr(user, 'perfil') or not user.perfil:
                request.session['precisa_completar_perfil'] = True
    
    def save_user(self, request, sociallogin, form=None):
        """
        Salva o usuário e extrai informações do Google
        """
        user = super().save_user(request, sociallogin, form)
        
        # Extrai o nome completo do Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            if 'name' in extra_data and not user.first_name:
                user.first_name = extra_data.get('name', '')
                user.save()
        
        # Marca que o usuário precisa completar o cadastro
        request.session['precisa_completar_perfil'] = True
        return user
    
    def get_login_redirect_url(self, request):
        """
        Redireciona para a página de completar cadastro se não tiver perfil
        """
        user = request.user
        if user.is_authenticated:
            # Verifica se o usuário tem perfil
            if not hasattr(user, 'perfil') or not user.perfil:
                return '/completar-cadastro-social/'
        
        # Se já tem perfil, usa o redirect padrão
        return '/pos-login/'
    
    def get_connect_redirect_url(self, request, socialaccount):
        """
        URL de redirecionamento após conectar conta social
        """
        return '/meu-perfil/'
