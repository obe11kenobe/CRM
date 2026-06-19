from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    photo = models.ImageField(blank=True, null=True, verbose_name="Фотография")
    date_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")

    def __str__(self):
        return self.username

class JobTitle (models.Model):
    job_title = models.CharField(max_length=100, verbose_name='Должность', blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='Родительская должность',
    )
    permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        verbose_name='Права',
    )

    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    def __str__(self):
        return self.job_title

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
