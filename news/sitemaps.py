from django.contrib.sitemaps import Sitemap
from .models import Article
class ArticleSitemap(Sitemap):
    changeferq="weekly"
    priority=0.9

    def items(self):
        return Article.published.all()

    def lastmod(self,obj):
        return obj.updated_at
    
