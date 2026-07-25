from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import DeleteView, ListView, TemplateView, UpdateView
from django.views.generic.edit import CreateView

import time
import jwt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .audit import log_action
from .forms import CustomUserCreationForm, ProfileUserForm, JobTitleForm
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

class JobTitleViews(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = JobTitle
    template_name = 'positions/jobtitle.html'
    context_object_name = "positions"
    permission_required = 'users.view_jobtitle'
    raise_exception = True

class JobTitleCreateViews(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = JobTitle
    form_class = JobTitleForm
    template_name = 'positions/jobtitle.html'
    success_url = reverse_lazy('job_title_list')
    permission_required = 'users.add_jobtitle'
    raise_exception = True

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.request.user, 'create', self.object)
        return response

class JobTitleUpdateViews(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = JobTitle
    form_class = JobTitleForm
    template_name = 'positions/jobtitle.html'
    success_url = reverse_lazy('job_title_list')
    permission_required = 'users.change_jobtitle'
    raise_exception = True

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.request.user, 'update', self.object)
        return response

class JobTitleDeleteViews(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = JobTitle
    template_name = 'positions/jobtitle.html'
    success_url = reverse_lazy('job_title_list')
    permission_required = 'users.delete_jobtitle'
    raise_exception = True

    def form_valid(self, form):
        log_action(self.request.user, 'delete', self.object)
        response = super().form_valid(form)
        if self.request.headers.get('HX-Request') == 'true':
            return HttpResponse(status=200)
        return response

class ProfileUserView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'users/chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        colleagues = CustomUser.objects.exclude(pk=self.request.user.pk)
        context['colleagues_data'] = [
            {'id': user.id, 'full_name': user.full_name} for user in colleagues
        ]
        return context

@login_required
def messenger_token(request):
    payload = {
        "user_id" : request.user.id,
        "exp": int(time.time()) + 300,
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')
    return HttpResponse(token)