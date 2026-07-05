from django.urls import path

from . import views

app_name = 'submissions'

urlpatterns = [
    path('<int:task_id>/route_fields_form/', views.route_fields_form, name='route_fields_form'),

]