from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Pagina inicial
    path('login/', views.login_view, name='login'), # Login
    path('cadastro/', views.cadastro_view, name='cadastro'), # Cadastro
    path('logout/', views.logout_view, name='logout'), # Logout
    path('pos-login/', views.pos_login, name='pos_login'), # Redireciona a pagina após o login para uma pagina especifica
    path('produto/<int:id_produto>/', views.detalhes_produto, name='detalhes_produto'), # Pagina do Produto
        path('dashboard/', views.dashboard_perfil, name='dashboard_perfil'), # Página unificada de perfil/feed
    path('caixa-entrada/', views.caixa_entrada, name='caixa_entrada'), # Caixa de entrada para conversa
    path('carrinho/adicionar/', views.adicionar_carrinho, name='adicionar_carrinho'), # adicionar ao carrinho
    path('carrinho/', views.visualizar_carrinho, name='visualizar_carrinho'), # visualizar o carrinho
    path('admin/certificacoes/', views.gerenciar_certificacoes, name='gerenciar_certificacoes'), # admin: gerenciar certificações
]
