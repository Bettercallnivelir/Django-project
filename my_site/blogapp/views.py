from django.views.generic import ListView

from blogapp.models import Article


class ArticlesListView(ListView):
    """View для вывода списка статей"""
    queryset = Article.objects.defer('content').\
        select_related('author', 'category').\
        prefetch_related('tags')
