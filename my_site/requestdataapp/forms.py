from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError


class UserBioForm(forms.Form):
    name = forms.CharField(max_length=30, label='Ваше имя')
    age = forms.IntegerField(label='Возраст', max_value=99, min_value=18)
    bio = forms.CharField(label='Биография', widget=forms.Textarea)


def validate_file_name(file: InMemoryUploadedFile) -> None:
    if file.name and 'virus' in file.name:
        raise ValidationError('В имени файла не должно содержаться слово "virus"')

class UploadFileForm(forms.Form):
    file = forms.FileField(validators=[validate_file_name])



