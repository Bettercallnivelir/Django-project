from django.urls import path
from .views import get_request, user_form, upload_file, upload_file_with_form

app_name = 'requestdataapp'

urlpatterns = [
    path('get/', get_request, name='get_request'),
    path('bio/', user_form, name='user_form'),
    path('upload/', upload_file_with_form, name='upload'),
]
