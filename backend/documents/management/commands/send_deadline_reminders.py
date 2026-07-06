from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

from documents.models import DeadlineReminder, DocumentTask

logger = logging.getLogger(__name__)

THRESHOLDS = [180, 90, 60, 30, 14, 7]


class Command(BaseCommand):
    help = "Отправка напоминаний о приближении дедлайнов задач"

    def handle(self, *args, **options):
        today = timezone.now().date()
        tasks = DocumentTask.objects.filter(deadline__isnull=False).exclude(
            status__in=[DocumentTask.Status.DONE, DocumentTask.Status.CANCELLED]
        )

        for task in tasks:
            days_left = (task.deadline.date() - today).days

            if days_left not in THRESHOLDS:
                continue

            already_sent = DeadlineReminder.objects.filter(
                task=task,
                threshold_days=days_left
            ).exists()

            if already_sent:
                continue

            success = self.send_reminder_email(task, days_left)

            if success:
                DeadlineReminder.objects.create(
                    task=task,
                    threshold_days=days_left,
                    sent_at=timezone.now()
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Напоминание ({days_left} дн.) успешно отправлено для задачи {task.id}")
                )

    def send_reminder_email(self, task, days_left):
        subject = f"Напоминание: до дедлайна задачи осталось {days_left} дней"
        message = f"Добрый день! По задаче '{task.title}' подходит дедлайн: {task.deadline.date()}."

        recipient = task.responsible
        if not recipient or not recipient.email:
            self.stdout.write(self.style.WARNING(f"У задачи {task.id} отсутствует email исполнителя"))
            return False

        try:
            sent_count = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            return sent_count > 0

        except Exception as e:
            logger.error(f"Ошибка отправки письма для задачи {task.id}: {e}")
            self.stdout.write(self.style.ERROR(f"Не удалось отправить письмо для задачи {task.id}"))
            return False
