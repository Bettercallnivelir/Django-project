from django.urls import path
from .views import get_request, user_form, upload_file

app_name = 'requestdataapp'

urlpatterns = [
    path('get/', get_request, name='get_request'),
    path('bio/', user_form, name='user_form'),
    path('upload/', upload_file, name='upload'),
]
