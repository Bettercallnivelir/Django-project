from django.db import models
from django.urls import reverse


class Author(models.Model):
    """Модель представляет автора статьи"""
    name = models.CharField(max_length=100)
    bio = models.TextField()

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель представляет категорию статьи"""
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель представляет тэг для статьи"""
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Article(models.Model):
    """Модель представляет статью"""

    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='articles')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blogapp:article', kwargs={'pk': self.pk})
