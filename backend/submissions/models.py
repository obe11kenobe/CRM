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
        verbose_name='Route ID',
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