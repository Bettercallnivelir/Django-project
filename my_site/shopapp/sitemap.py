from django.contrib.sitemaps import Sitemap

from .models import Product


class ShopSiteMap(Sitemap):
    changefreq = 'never'

    def items(self):
        return Product.objects.filter(archived=False)

    def lastmod(self, obj: Product):
        return obj.created
