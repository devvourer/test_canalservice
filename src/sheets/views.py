from django.shortcuts import render

from .models import Order


def index(request):
    orders = Order.objects.all()
    return render(request, 'index.html', {'orders': orders})
