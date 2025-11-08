from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



app_name = "news"

urlpatterns = [
    #path('', views.home, name="home"),
    path('',views.article_list,name='article_list'),
    path('home',views.home,name='home'),

    path("article/<slug:slug>/", views.article_detail, name="article_detail"),

    path('article/<slug:slug>/react', views.handle_reaction, name='handle_reaction'),
    path('contact/', views.contact, name='contact'),

    path('search/', views.search, name='article_search'),
    path('category/<slug:slug>/', views.category_articles, name='category_articles'),
    path('saved-articl/<slug:slug>/delete',views.unsave_artcile,name="unsave_artcile"),

    path('saved-articles/',views.my_saved_articles,name='saved_articles'),
    path('content/',views.about,name='about'),


]
