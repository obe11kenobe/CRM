from django.conf import settings
from django.db import models


class MiningObject(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self):
        return self.name


class License(models.Model):
    mining_object = models.ForeignKey(
        MiningObject,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='licenses',
        verbose_name='Объект',
    )
    number = models.CharField(max_length=100, blank=True, verbose_name='Номер лицензии')
    status = models.CharField(max_length=150, blank=True, verbose_name='Статус')
    issued_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата начала')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    def __str__(self):
        if self.mining_object:
            return f'{self.number} - {self.mining_object}'
        return self.number


class DocumentDirection(models.Model):
    name = models.CharField(max_length=100, verbose_name='Назначение')
    description = models.TextField(blank=True, verbose_name='Описание назначения')

    def __str__(self):
        return self.name


class Authority(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название инстанции')
    description = models.TextField(blank=True, verbose_name='Описание инстанции')
    email = models.CharField(max_length=50, blank=True, verbose_name='Почта')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    address = models.CharField(max_length=200, blank=True, verbose_name='Адрес')

    def __str__(self):
        return self.name


class DocumentTask(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'planned', 'запланировано'
        IN_PROGRESS = 'in_progress', 'в работе'
        SEND = 'send', 'отправлено'
        RECEIVED = 'received', 'получено'
        DONE = 'done', 'закрыто'
        OVERDUE = 'overdue', 'просрочено'
        CANCELLED = 'cancelled', 'отменено'

    mining_object = models.ForeignKey(
        MiningObject,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='tasks',
        verbose_name='Объект',
    )
    license_object = models.ForeignKey(
        License,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='tasks',
        verbose_name='Лицензия объекта',
    )
    direction = models.ForeignKey(
        DocumentDirection,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='tasks',
        verbose_name='Направление'
    )
    authority = models.ForeignKey(
        Authority,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='tasks',
        verbose_name='Инстанция',
    )
    title = models.CharField(max_length=100, verbose_name='Название документа')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    is_available = models.BooleanField(default=False, verbose_name='Наличие документа')
    received_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата получения')
    deadline = models.DateTimeField(blank=True, null=True, verbose_name='Дедлайн')
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='document_tasks',
        verbose_name='Ответственный пользователь'
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.title
