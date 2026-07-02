from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils import timezone


class MiningObject(models.Model):
    class NvosCategory(models.TextChoices):
        FIRST = "I", "I категория"
        SECOND = "II", "II категория"
        THIRD = "III", "III категория"
        FOURTH = "IV", "IV категория"

    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    cadastral_number = models.CharField(max_length=50, blank=True, verbose_name='Кадастровый номер участка')
    municipality = models.CharField(max_length=100, blank=True, verbose_name='Муниципальное образование')
    nvos_category = models.CharField(max_length=5, choices=NvosCategory.choices, blank=True, verbose_name='Категория НВОС')

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

    def clean(self):
        if self.issued_at and self.expires_at and self.expires_at < self.issued_at:
            raise ValidationError({
                'expires_at': 'Дата окончания не может быть раньше даты начала.',
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return self.expires_at < timezone.now()

    def is_expiring_soon(self, days=90):
        if not self.expires_at:
            return False
        return timezone.now() <= self.expires_at  <= timezone.now() + timezone.timedelta(days=days)

    def __str__(self):
        if self.mining_object:
            return f'{self.number} - {self.mining_object}'
        return self.number

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['mining_object', 'number'],
                condition=models.Q(mining_object__isnull=False) & ~models.Q(number=''),
                name='unique_license_per_object',
            ),
        ]


class DocumentDirection(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Назначение')
    description = models.TextField(blank=True, verbose_name='Описание назначения')

    def __str__(self):
        return self.name


class Authority(models.Model):
    class Block(models.TextChoices):
        SUBSOIL = "subsoil", "Недра / лицензии / техпроекты"
        FOREST = "forest", "Лесной фонд"
        LAND = "land", "Земля / муниципалитет"
        WATER = "water", "Водопользование"
        ECOLOGY = "ecology", "Экология / НВОС"
        SANITARY = "sanitary", "Санитарно-эпидемиологический блок"
        EMERGENCY = "emergency", "ГО и ЧС"
        OTHER = "other", "Прочее"

    class PreferredChannel(models.TextChoices):
        GOSUSLUGI = "gosuslugi", "ЕПГУ"
        AGENCY_ACCOUNT = "agency_account", "ЛК ведомства"
        EDO = "edo", "ЭДО"
        OFFICE = "office", "Канцелярия"
        POST = "post", "Почта с описью"
        EMAIL_DUPLICATE = "email_duplicate", "E-mail дубль"
        MANUAL = "manual", "Ручная подача"

    name = models.CharField(max_length=100, unique=True, verbose_name='Название инстанции')
    description = models.TextField(blank=True, verbose_name='Описание инстанции')
    email = models.CharField(max_length=50, blank=True, verbose_name='Почта')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    address = models.CharField(max_length=200, blank=True, verbose_name='Адрес')

    block = models.CharField(
        max_length=20,
        choices=Block.choices,
        blank=True,
        verbose_name='Блок'
    )

    preferred_channel = models.CharField(
        max_length=30,
        choices=PreferredChannel.choices,
        blank=True,
        verbose_name='Канал подачи по умолчанию'
    )

    def clean(self):
        if not self.email:
            return

        validator = EmailValidator(message='Некорректный email: %(value)s')
        errors = []

        for raw_address in self.email.split(';'):
            address = raw_address.strip()
            if not address:
                continue
            try:
                validator(address)
            except ValidationError:
                errors.append(f'Некорректный email: {address}')

        if errors:
            raise ValidationError({'email': errors})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


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
    route = models.ForeignKey(
        'submissions.DocumentRoute',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='document_tasks',
        verbose_name='Маршрут автоматизации',
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

    def save(self, *args, **kwargs):
        if not self.route_id and self.title:
            from submissions.models import DocumentRoute

            matched_route = DocumentRoute.match_for_document(self.title)
            if matched_route:
                self.route = matched_route
                if not self.authority_id:
                    self.authority = matched_route.authority

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['mining_object', 'license_object', 'direction', 'title'],
                name='unique_document_task_plan_item',
            ),
        ]
        indexes = [
            models.Index(fields=['status', 'deadline'], name='doc_task_status_deadline_idx'),
            models.Index(fields=['responsible', 'deadline'], name='doc_task_resp_deadline_idx'),
            models.Index(fields=['mining_object', 'direction'], name='doc_task_object_dir_idx'),
        ]
