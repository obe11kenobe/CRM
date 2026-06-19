from django.urls import path
from .views import (
    SignUpViews,
    JobTitleViews,
    JobTitleCreateViews,
    JobTitleUpdateViews,
    JobTitleDeleteViews,
)

urlpatterns = [
    path("signup/", SignUpViews.as_view(), name="signup"),

    path("job_title/", JobTitleViews.as_view(), name="job_title_list"),
    path("job_title/create/", JobTitleCreateViews.as_view(), name="job_title_create"),
    path("job_title/<int:pk>/edit/", JobTitleUpdateViews.as_view(), name="job_title_update"),
    path("job_title/<int:pk>/delete/", JobTitleDeleteViews.as_view(), name="job_title_delete"),
]