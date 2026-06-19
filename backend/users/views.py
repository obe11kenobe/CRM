from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView, UpdateView, DeleteView
from .forms import CustomUserCreationForm
from .models import CustomUser, JobTitle


class SignUpViews(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

class JobTitleViews(ListView):
    model = JobTitle
    template_name = 'positions/jobtitle.html'
    context_object_name = "positions"

class JobTitleCreateViews(CreateView):
    model = JobTitle
    fields = "__all__"
    template_name = 'positions/jobtitle.html'
    success_url = reverse_lazy('job_title_list')

class JobTitleUpdateViews(UpdateView):
    model = JobTitle
    fields = "__all__"
    template_name = 'positions/jobtitle.html'
    success_url = reverse_lazy('job_title_list')

class JobTitleDeleteViews(DeleteView):
    model = JobTitle
    template_name = 'positions/jobtitle.html'
    success_url = reverse_lazy('job_title_list')
