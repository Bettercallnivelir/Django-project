from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest
from django.shortcuts import render

from requestdataapp.forms import UserBioForm, UploadFileForm


# Create your views here.


def get_request(request: HttpRequest):
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')
    result = a + b
    context = {
        'a': a,
        'b': b,
        'result': result
    }
    return render(request, 'requestdataapp/request-query.html', context=context)


def user_form(request: HttpRequest):
    context = {
        'form': UserBioForm(),
    }
    return render(request, "requestdataapp/user-bio-form.html", context=context)


def upload_file(request: HttpRequest):
    """Сохраняем загружаемый файл. Если файл более 1Мб, то выдаёт ошибку"""
    if request.method == 'POST' and request.FILES.get('myfile'):
        myfile = request.FILES['myfile']
        if myfile.size < 1e6:
            data = FileSystemStorage()
            filename = data.save(myfile.name, myfile)
            print(f"{filename} saved.")
        else:
            raise ValidationError('Размер вашего файла превышает 1Mб')

    return render(request, 'requestdataapp/file-upload.html')


def upload_file_with_form(request: HttpRequest):
    """Сохраняем загружаемый файл через форму UploadFileForm"""

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # myfile = request.FILES['myfile']
            myfile = form.cleaned_data['file']
            data = FileSystemStorage()
            filename = data.save(myfile.name, myfile)
            print(f"{filename} saved.")
    else:
        form = UploadFileForm()

    context = {
        'form': form,
    }

    return render(request, 'requestdataapp/file-upload.html', context=context)
