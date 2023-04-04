from django.contrib.auth.views import LoginView
from django.urls import path
from .views import get_cookie_view, set_cookie_view, get_session_view, set_session_view, \
    LogoutUser, AboutMeView, RegisterView, FooBarView

app_name = 'myauth'

urlpatterns = [
    path('', LoginView.as_view(template_name='myauth/login.html',
                               redirect_authenticated_user=True),
         name='login'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('about-me/', AboutMeView.as_view(), name='about_me'),
    path('register/', RegisterView.as_view(), name='registr'),
    path('cookie/get/', get_cookie_view, name='cookie_get'),
    path('cookie/set/', set_cookie_view, name='cookie_set'),
    path('session/set/', set_session_view, name='session_set'),
    path('session/get/', get_session_view, name='session_get'),
    path('foo-bar/', FooBarView.as_view(), name='foo-bar'),
]
