from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    photo = models.ImageField(blank=True, null=True, verbose_name="Фотография")
    date_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    job_title = models.ForeignKey(
        'JobTitle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Должность',
    )

    email_verified = models.BooleanField(default=False, verbose_name='Email подтвержден')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    middle_name = models.CharField(max_length=50, blank=True, verbose_name='Отчество')

    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='subordinates',
        verbose_name='Руководитель',
    )

    @property
    def full_name(self):
        return ' '.join(
            part for part in [self.last_name, self.first_name, self.middle_name] if part
        ) or self.username

    def __str__(self):
        return self.username

class JobTitle (models.Model):
    job_title = models.CharField(
        max_length=100,
        verbose_name='Должность',
        unique=True
    )
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


class AuditLogEntry(models.Model):
    class Action(models.TextChoices):
        CREATE = 'create', 'Создание'
        UPDATE = 'update', 'Изменение'
        DELETE = 'delete', 'Удаление'

    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='audit_log_entries',
        verbose_name='Пользователь',
    )
    action = models.CharField(max_length=10, choices=Action.choices, verbose_name='Действие')
    model_name = models.CharField(max_length=100, verbose_name='Модель')
    object_id = models.CharField(max_length=50, verbose_name='ID объекта')
    object_repr = models.CharField(max_length=200, verbose_name='Объект')
    details = models.TextField(blank=True, verbose_name='Подробности')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Когда')

    def __str__(self):
        return f'{self.get_action_display()}: {self.model_name} «{self.object_repr}»'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запись аудита'
        verbose_name_plural = 'Журнал аудита'
