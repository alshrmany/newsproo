from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'
urlpatterns = [
    #path('login/',views.user_login,name='login'),
    path('login/', views.custom_login_view  , name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile, name='profile'),
]