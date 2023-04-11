from django import forms
from django.core.exceptions import ValidationError

from myauth.models import Profile


class ProfileForm(forms.ModelForm):
    """Форма для модели Profile"""

    class Meta:
        model = Profile
        fields = 'avatar',
        labels = {
            'avatar': 'Сменить аватарку->'
        }

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        if not avatar:
            raise ValidationError('Error!')

        return avatar
