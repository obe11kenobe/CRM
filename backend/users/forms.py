import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','email')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username','email')

class ProfileUserForm(forms.ModelForm):
    this_year = datetime.date.today().year
    date_birth = forms.DateField(
        widget=forms.SelectDateWidget(
            years=tuple(range(this_year - 100, this_year - 5))
        )
    )

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email", "date_birth"]