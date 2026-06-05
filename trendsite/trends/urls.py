from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('post/', views.generated_post, name='generated_post'),
]
