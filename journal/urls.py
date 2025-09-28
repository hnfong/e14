from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.blog_list, name='blog_list'),
    path('comments/', views.comment_list, name='comment_list'),
    path('archival/', views.archival_list, name='archival_list'),
]
