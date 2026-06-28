import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser, JobTitle

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','email')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            raise forms.ValidationError('Email обязателен')

        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с такой почтой уже существует')

        return email

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username','email')

class ProfileUserForm(forms.ModelForm):
    this_year = datetime.date.today().year
    date_birth = forms.DateField(
        required=False,
        widget=forms.SelectDateWidget(
            years=tuple(range(this_year - 100, this_year - 5))
        )
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "date_birth",
            "photo",
            "phone",
        ]


class JobTitleForm(forms.ModelForm):
    class Meta:
        model = JobTitle
        fields = [
            "job_title",
            "description",
            "parent",
            "is_active",
        ]

    def clean_job_title(self):
        job_title = self.cleaned_data.get("job_title", "").strip()
        if not job_title:
            raise forms.ValidationError("Название должности обязательно.")
        return job_title
