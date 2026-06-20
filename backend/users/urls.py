from django.urls import path
from .views import (
    SignUpViews,
    JobTitleViews,
    JobTitleCreateViews,
    JobTitleUpdateViews,
    JobTitleDeleteViews,
    ProfileUserView,
    ActivateViews,
    SignUpDoneView,
    ActivationSuccessView,
    ActivationInvalidView,
)

urlpatterns = [
    path("signup/", SignUpViews.as_view(), name="signup"),
    path("signup/done/", SignUpDoneView.as_view(), name="signup_done"),

    path("job_title/", JobTitleViews.as_view(), name="job_title_list"),
    path("job_title/create/", JobTitleCreateViews.as_view(), name="job_title_create"),
    path("job_title/<int:pk>/edit/", JobTitleUpdateViews.as_view(), name="job_title_update"),
    path("job_title/<int:pk>/delete/", JobTitleDeleteViews.as_view(), name="job_title_delete"),
    path("profile/", ProfileUserView.as_view(), name="profile"),
    path("activate/<uidb64>/<token>/", ActivateViews.as_view(), name="activate"),
    path("activate/success/", ActivationSuccessView.as_view(), name="activation_success"),
    path("activate/invalid/", ActivationInvalidView.as_view(), name="activation_invalid"),
]
