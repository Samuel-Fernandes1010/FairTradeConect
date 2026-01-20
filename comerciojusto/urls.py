from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('pos-login/', views.pos_login, name='pos_login'),
    path('area/produtor/', views.area_produtor, name='area_produtor'),
    path('area/empresa/', views.area_empresa, name='area_empresa'),
<<<<<<< HEAD
    path('area/gestor/', views.area_gestor, name='area_gestor'),
    path('area/operador/', views.area_operador, name='area_operador'),
=======
    path('produto/<int:id_produto>/', views.detalhes_produto, name='detalhes_produto'),
    path('meu-perfil/', views.meu_perfil, name='meu_perfil'),
    path('caixa-entrada/', views.caixa_entrada, name='caixa_entrada'),
    path('carrinho/adicionar/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('carrinho/', views.visualizar_carrinho, name='visualizar_carrinho'),
>>>>>>> Samuel

    path('produto/novo/', views.cadastrar_produto, name='cadastrar_produto'),
    path('admin-auditoria/', views.area_admin, name='area_admin'),
    path('aprovar/<int:id_produto>/', views.aprovar_produto, name='aprovar_produto'),
]
