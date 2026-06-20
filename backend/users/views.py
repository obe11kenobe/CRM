from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import DeleteView, ListView, TemplateView, UpdateView
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm, ProfileUserForm
from .models import CustomUser, JobTitle

import logging

logger = logging.getLogger(__name__)

class SignUpViews(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.email_verified = False
        user.save()
        logger.info("User registered: %s", user.email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activate_path = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        activate_url = self.request.build_absolute_uri(activate_path)

        send_mail(
            subject = 'Подтверждение email',
            message = f'Перейдите по ссылке, чтобы подтвердить email: {activate_url} ',
            from_email=None,
            recipient_list=[user.email],
        )

        logger.info("Activation email sent: %s", user.email)

        return redirect('signup_done')

class ActivateViews(View):
    def get(self, request, uidb64, token):
        User = get_user_model()

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.email_verified = True
            user.is_active = True
            user.save()

            logger.info("User email activated: %s", user.email)

            return redirect('activation_success')

        logger.warning("Invalid activation link: uid=%s", uidb64)

        return redirect('activation_invalid')

class SignUpDoneView(TemplateView):
    template_name = 'registration/signup_done.html'

class ActivationSuccessView(TemplateView):
    template_name = 'registration/activation_success.html'

class ActivationInvalidView(TemplateView):
    template_name = 'registration/activation_invalid.html'

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

class ProfileUserView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user
