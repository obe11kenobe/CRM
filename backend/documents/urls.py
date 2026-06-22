from django.urls import path

from . import views


app_name = 'documents'

urlpatterns = [
    path('', views.document_task_list, name='document_task_list'),
    path('create/', views.document_task_create, name='document_task_create'),
    path('<int:pk>/', views.document_task_detail, name='document_task_detail'),
    path('<int:pk>/edit/', views.document_task_update, name='document_task_update'),
    path('<int:pk>/delete/', views.document_task_delete, name='document_task_delete'),
]
