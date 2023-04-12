from django.contrib.auth.models import User
from django.db import models


def profile_avatar_path(instance: 'Profile', filename: str) -> str:
    return f'profiles/profile_{instance.pk}/avatar/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=300, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_avatar_path)

    def get_absolute_url(self):
        return f'/accounts/about_user/{self.pk}'
