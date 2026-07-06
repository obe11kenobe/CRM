from django.urls import path

from . import views

app_name = 'submissions'

urlpatterns = [
    path('<int:task_id>/route_fields_form/', views.route_fields_form, name='route_fields_form'),
    path('<int:task_id>/package_status_form/', views.package_status_form, name='package_status_form'),
    path('package_list/', views.package_list, name='package_list')
]