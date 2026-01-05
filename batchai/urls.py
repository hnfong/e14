from django.urls import path
from . import views

urlpatterns = [
    path('pending_requests', views.pending_requests, name='pending_requests'),
    path('submit_inference_result', views.submit_inference_result, name='submit_inference_result'),
    path('', views.html_list, name='html_list'),
    # path('results/<str:job_id>/', views.job_results, name='job_results'),
]
