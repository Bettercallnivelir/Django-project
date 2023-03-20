from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy


# def login_user(request: HttpRequest):
#     if request.method == 'GET':
#         if request.user.is_authenticated:
#             return redirect('/admin')
#
#         return render(request, 'myauth/login.html')
#     # Пользователь ввёл данные в форму, проверяем
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         redirect('/admin')
#     return render(request, 'myauth/login.html', {'error': 'Invalid login credentials'})


# def logout_user(request):
#     logout(request)
#     return redirect('/admin')


class LogoutUser(LogoutView):
    """View для выхода пользователя"""
    next_page = reverse_lazy('myauth:login')


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    """Установка данных в cookies"""
    response = HttpResponse('Cookie set!')
    response.set_cookie('Key', 'Hi!', max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    """Чтение данных из cookies"""
    value = request.COOKIES.get('Key', 'default')
    return HttpResponse(f'Answer: {value!r}')


def set_session_view(request: HttpRequest) -> HttpResponse:
    """Установка данных в сессию"""
    request.session['Session key'] = 'some answer to session'
    return HttpResponse('Session set!')


def get_session_view(request: HttpRequest) -> HttpResponse:
    """Чтение данных из сессии"""
    value = request.session.get('Session key', 'Empty')
    return HttpResponse(f'Value: {value}.')
