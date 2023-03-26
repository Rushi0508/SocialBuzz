from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('likepost', views.likepost, name='likepost'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('delete/<str:pk>', views.delete, name='delete'),
]