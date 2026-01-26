import stripe
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from comerciojusto.models import Produto

# Configurar a chave secreta do Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def criar_checkout(request):
    """Cria uma sessão de checkout do Stripe"""
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('visualizar_carrinho')
    
    try:
        line_items = []
        
        # Iterar pelos itens do carrinho
        for produto_id, quantidade in carrinho.items():
            produto = Produto.objects.get(id_produto=produto_id)
            line_items.append({
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': produto.nome,
                        'description': produto.descricao[:100] if produto.descricao else '',
                    },
                    'unit_amount': int(produto.preco * 100),  # Converter para centavos
                },
                'quantity': quantidade,
            })
        
        # Criar sessão de checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/sucesso/'),
            cancel_url=request.build_absolute_uri('/cancelado/'),
            customer_email=request.user.email,
            metadata={
                'user_id': request.user.id,
            }
        )
        
        return redirect(session.url)
    
    except Produto.DoesNotExist:
        messages.error(request, 'Produto não encontrado no carrinho.')
        return redirect('visualizar_carrinho')
    except Exception as e:
        messages.error(request, f'Erro ao criar sessão de pagamento: {str(e)}')
        return redirect('visualizar_carrinho')


def pagamento_sucesso(request):
    """Página exibida após pagamento bem-sucedido"""
    # Limpar carrinho
    if 'carrinho' in request.session:
        del request.session['carrinho']
    
    messages.success(request, 'Pagamento realizado com sucesso!')
    return render(request, 'payments/sucesso.html')


def pagamento_cancelado(request):
    """Página exibida quando o pagamento é cancelado"""
    messages.info(request, 'Pagamento cancelado. Você pode tentar novamente quando quiser.')
    return render(request, 'payments/cancelado.html')


@csrf_exempt
def stripe_webhook(request):
    """Webhook para receber eventos do Stripe"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Payload inválido
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Assinatura inválida
        return HttpResponse(status=400)
    
    # Processar evento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Aqui você pode processar o pedido, salvar no banco, etc.
        print(f"Pagamento concluído para sessão: {session['id']}")
    
    return JsonResponse({'status': 'success'})
