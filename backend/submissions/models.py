from django.db import models

class DocumentRoute(models.Model):
    class SubmissionChannel(models.TextChoices):
        GOSUSLUGI = "gosuslugi", "ЕПГУ"
        AGENCY_ACCOUNT = "agency_account", "ЛК ведомства"
        EDO = "edo", "ЭДО"
        OFFICE = "office", "Канцелярия"
        POST = "post", "Почта с описью"
        EMAIL_DUPLICATE = "email_duplicate", "E-mail дубль"
        MANUAL = "manual", "Ручная подача"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"

    route_id = models.CharField(
        max_length=10,
        db_index=True,
        unique=True,
        verbose_name='Route ID'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    document_process = models.TextField(
        verbose_name='Документ / процесс из файла'
    )
    authority = models.ForeignKey(
        'documents.Authority',
        on_delete=models.PROTECT,
        related_name='routes',
        verbose_name='Основная инстанция'
    )
    template_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Название шаблона'
    )
    required_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Обязательное поле'
    )
    required_attachments = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Обязательное вложение'
    )
    submission_channel = models.CharField(
        max_length=30,
        choices=SubmissionChannel.choices,
        default=SubmissionChannel.MANUAL,
        verbose_name='Канал подачи'
    )
    source_url = models.TextField(
        blank=True,
        verbose_name='Источник / форма'
    )
    note = models.TextField(
        blank=True,
        verbose_name='Примечание'
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.MEDIUM,
        verbose_name='Риск автоматизации'
    )
    allow_auto_generation = models.BooleanField(
        default=True,
        verbose_name='Можно формировать автоматически'
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    def __str__(self):
        return f'{self.route_id} - {self.name}'

    class Meta:
        ordering = ["route_id"]
        verbose_name = "Маршрут документа"
        verbose_name_plural = "Маршруты документов"

class SubmissionPackage(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        READY = "ready", "Готов к подаче"
        SENT = "sent", "Отправлено"
        REGISTERED = "registered", "Зарегистрировано"
        RESPONSE_RECEIVED = "response_received", "Получен ответ"
        REJECTED = "rejected", "Отказ / замечания"
        CLOSED = "closed", "Закрыто"
        CANCELLED = "cancelled", "Отменено"

    task = models.ForeignKey(
        'documents.DocumentTask',
        on_delete=models.CASCADE,
        related_name='packages',
        verbose_name='Документ'
    )
    route = models.ForeignKey(
        'submissions.DocumentRoute',
        on_delete=models.PROTECT,
        related_name='packages',
        verbose_name='Маршрут'
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Статус подачи'
    )
    outgoing_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Исходящий номер'
    )
    sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата отправки'
    )
    agency_incoming_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Входящий номер ведомства',
    )
    registered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата регистрации'
    )
    proof_file = models.FileField(
        upload_to="submission_proofs/",
        blank=True,
        null=True,
        verbose_name="Доказательство подачи",
    )
    comment = models.TextField(
        max_length=1000,
        blank=True,
    )
    created_by = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_submission_packages",
        verbose_name="Создал",
    )
    created_at =  models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return f'{self.task} - {self.route}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пакет отправки'
        verbose_name_plural = 'Пакеты отправки'
