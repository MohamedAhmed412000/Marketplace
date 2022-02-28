from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from marketplace.models import Ownership
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def get_total_cost(orders):
    sum = 0
    for order in orders:
        sum += order.product.price
    return sum

def payment_process(request):
    order_ids = request.session['order_id']
    order = []
    for order_id in order_ids:
        order.append(get_object_or_404(Ownership, id= order_id))
    host = request.get_host()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % get_total_cost(order),
        'item_name': f'Order {order_ids[0]}',
        'invoice': str(order_ids[0]),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('payment:done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('payment:canceled'))
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'payment/process.html', {
        'order': order,
        'form': form
    })

@csrf_exempt
def payment_done(request):
    return render(request, 'payment/done.html')

@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment/canceled.html')