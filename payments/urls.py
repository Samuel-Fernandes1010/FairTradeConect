# payments/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('pagamento/', views.criar_checkout, name='criar_checkout'),
    path('sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('cancelado/', views.pagamento_cancelado, name='pagamento_cancelado'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]