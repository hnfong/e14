from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('blog/', views.blog_list, name='blog_list'),
    path('topic/', views.topic_list, name='topic_list'),
    path('archive/', views.archive_list, name='archive_list'),
    path('tag/<str:tag>/', views.tagged_entries, name='tagged_entries'),
    path('view/<str:slug>/', views.entry_slug, name='view_slug'),
    path('view/<int:entry_id>/', views.entry_id, name='view_id'),
]
