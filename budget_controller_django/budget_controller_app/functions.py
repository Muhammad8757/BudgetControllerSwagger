import hashlib
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from .models import Category, UserTransaction, models
from .models import User

def hasher(password) -> str:
    return hashlib.md5(str(password).encode()).hexdigest()

def get_user_from_session(request):
    phone_number = request.session.get('phone_number')
    password = request.session.get('password')
    if phone_number and password:
        return User.objects.filter(phone_number=phone_number, password=password).first()
    return None

def check_user(request):
    user = get_user_from_session(request)
    if user is None:
        login_url = reverse('login')
        return HttpResponseRedirect(f"{login_url}?toast=unauthorized")
    return None

def add_category_id(request, id=None, name=None):
    if id is None and name is None:
        name = request.POST.get('categoryName')
        Category.objects.create(name=name, created_category_by=request.user)
    elif id is not None and name is not None:
        Category.objects.create(name=name, created_category_by=id)

def sorted_transactions(request, sort_field):
        sort_order = request.session.get('sort_order', 'desc')
        order = f'-{sort_field}' if sort_order == 'desc' else sort_field
        transactions = UserTransaction.objects.filter(user=request.user).order_by(order)
        request.session['sort_order'] = 'asc' if sort_order == 'desc' else 'desc'
        return transactions