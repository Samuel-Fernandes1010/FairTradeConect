from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Pagina inicial
    path('login/', views.login_view, name='login'), # Login
    path('cadastro/', views.cadastro_view, name='cadastro'), # Cadastro
    path('completar-cadastro-social/', views.completar_cadastro_social, name='completar_cadastro_social'), # Completar cadastro após login social
    path('logout/', views.logout_view, name='logout'), # Logout
    path('acesso-negado/', views.acesso_negado, name='acesso_negado'), # Acesso negado
    path('pos-login/', views.pos_login, name='pos_login'), # Redireciona a pagina após o login para uma pagina especifica
    path('produto/<int:id_produto>/', views.detalhes_produto, name='detalhes_produto'), # Pagina do Produto
    path('perfil/<int:perfil_id>/', views.perfil_publico, name='perfil_publico'), # Perfil público
    path('dashboard/', views.dashboard_perfil, name='dashboard_perfil'), # Página unificada de perfil/feed
    path('meu-perfil/', views.editar_perfil, name='meu_perfil'), # Edição de perfil
    path('desconectar-google/', views.desconectar_google, name='desconectar_google'), # Desconectar conta Google
    path('caixa-entrada/', views.caixa_entrada, name='caixa_entrada'), # Caixa de entrada para conversa
    path('conversa/<int:usuario_id>/', views.visualizar_conversa, name='visualizar_conversa'), # Visualizar conversa
    path('mensagem/enviar/<int:destinatario_id>/', views.enviar_mensagem, name='enviar_mensagem'), # Enviar mensagem
    path('mensagem/marcar-lida/<int:mensagem_id>/', views.marcar_mensagem_lida, name='marcar_mensagem_lida'), # Marcar mensagem como lida
    path('carrinho/adicionar/', views.adicionar_carrinho, name='adicionar_carrinho'), # adicionar ao carrinho
    path('carrinho/', views.visualizar_carrinho, name='visualizar_carrinho'), # visualizar o carrinho
    path('admin/certificacoes/', views.gerenciar_certificacoes, name='gerenciar_certificacoes'), # admin: gerenciar certificações
]
