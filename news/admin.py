from django.contrib import admin
from .models import *




@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display=['title','author','category','status','created_at','publish','views','featured']
    prepopulated_fields={'slug':('title',)}
    date_hierarchy='publish'
    list_filter=('category','status','created_at')
    search_fields=('title','content')
    list_editable=['status']
    readonly_fields=['created_at','updated_at']


    def created_date(self,obj):
        return obj.created_at.date()
    created_date.short_description='تاريخ النشر'

@admin.register(SavedArticle)
class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'article__title']
    readonly_fields = ['saved_at']

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__username', 'article__title']
    readonly_fields = ['created_at']