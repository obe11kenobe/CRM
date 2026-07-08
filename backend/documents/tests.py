from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from documents.models import Authority, DeadlineReminder, DocumentDirection, DocumentTask, License, MiningObject
from users.models import AuditLogEntry
from submissions.models import DocumentRoute


class DocumentPermissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="employee",
            password="password123",
        )

    def test_document_list_requires_view_permission(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("documents:document_task_list"))

        self.assertEqual(response.status_code, 403)

    def test_document_list_allows_user_with_view_permission(self):
        permission = Permission.objects.get(codename="view_documenttask")
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        response = self.client.get(reverse("documents:document_task_list"))

        self.assertEqual(response.status_code, 200)

    def test_document_create_requires_add_permission(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("documents:document_task_create"))

        self.assertEqual(response.status_code, 403)


class DocumentListPaginationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="employee",
            password="password123",
        )
        permission = Permission.objects.get(codename="view_documenttask")
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        self.mining_object = MiningObject.objects.create(name="Object A")
        self.direction = DocumentDirection.objects.create(name="Direction A")

        DocumentTask.objects.bulk_create(
            DocumentTask(
                title=f"Document {index:02d}",
                mining_object=self.mining_object,
                direction=self.direction,
            )
            for index in range(55)
        )

    def test_document_list_is_paginated(self):
        response = self.client.get(reverse("documents:document_task_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_tasks"], 55)
        self.assertEqual(len(response.context["tasks"]), 50)
        self.assertTrue(response.context["page_obj"].has_next())


class DocumentTaskConstraintTests(TestCase):
    def test_document_task_plan_item_is_unique(self):
        mining_object = MiningObject.objects.create(name="Object A")
        license_object = License.objects.create(
            mining_object=mining_object,
            number="LICENSE-1",
        )
        direction = DocumentDirection.objects.create(name="Direction A")

        DocumentTask.objects.create(
            title="Annual report",
            mining_object=mining_object,
            license_object=license_object,
            direction=direction,
        )

        with self.assertRaises(IntegrityError):
            DocumentTask.objects.create(
                title="Annual report",
                mining_object=mining_object,
                license_object=license_object,
                direction=direction,
            )

class LicenseValidationTests(TestCase):
    def test_expires_before_issued_is_invalid(self):
        mining_object = MiningObject.objects.create(name="Object B")
        license_object = License(
            mining_object=mining_object,
            number="LICENSE-2",
            issued_at=timezone.now(),
            expires_at=timezone.now() - timezone.timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            license_object.full_clean()

    def test_is_expired_property(self):
        mining_object = MiningObject.objects.create(name="Object C")
        license_object = License.objects.create(
            mining_object=mining_object,
            number="LICENSE-3",
            issued_at=timezone.now() - timezone.timedelta(days=10),
            expires_at=timezone.now() - timezone.timedelta(days=1),
        )

        self.assertTrue(license_object.is_expired)
        self.assertFalse(license_object.is_expiring_soon(days=90))

    def test_is_expiring_soon_property(self):
        mining_object = MiningObject.objects.create(name="Object D")
        license_object = License.objects.create(
            mining_object=mining_object,
            number="LICENSE-4",
            issued_at=timezone.now() - timezone.timedelta(days=10),
            expires_at=timezone.now() + timezone.timedelta(days=30),
        )

        self.assertFalse(license_object.is_expired)
        self.assertTrue(license_object.is_expiring_soon(days=90))


class AuthorityValidationTests(TestCase):
    def test_single_invalid_email_is_rejected(self):
        authority = Authority(name="Roskomnadzor", email="not-an-email")

        with self.assertRaises(ValidationError):
            authority.full_clean()

    def test_multiple_valid_emails_are_accepted(self):
        authority = Authority.objects.create(
            name="Rosnedra",
            email="ural@rosnedra.gov.ru; sverdlovsk@rosnedra.gov.ru",
        )

        self.assertEqual(authority.email, "ural@rosnedra.gov.ru; sverdlovsk@rosnedra.gov.ru")

    def test_one_invalid_email_among_several_is_rejected(self):
        authority = Authority(
            name="Rosvodresursy",
            email="valid@example.com; not-valid",
        )

        with self.assertRaises(ValidationError):
            authority.full_clean()

    def test_blank_email_is_allowed(self):
        authority = Authority.objects.create(name="Administration")

        self.assertEqual(authority.email, "")


class DocumentTaskRouteAutoAssignTests(TestCase):
    def setUp(self):
        self.authority = Authority.objects.create(name="Уралнедра")
        self.route = DocumentRoute.objects.create(
            route_id="T03",
            name="Технический проект",
            document_process="Технический проект",
            authority=self.authority,
        )

    def test_route_and_authority_are_auto_assigned(self):
        task = DocumentTask.objects.create(title="Технический проект 1")

        self.assertEqual(task.route, self.route)
        self.assertEqual(task.authority, self.authority)

    def test_manual_route_is_not_overridden(self):
        other_authority = Authority.objects.create(name="Другая инстанция")
        other_route = DocumentRoute.objects.create(
            route_id="T04",
            name="Горный отвод",
            document_process="Горный отвод",
            authority=other_authority,
        )

        task = DocumentTask.objects.create(
            title="Технический проект 1",
            route=other_route,
        )

        self.assertEqual(task.route, other_route)

    def test_manual_authority_is_not_overridden(self):
        other_authority = Authority.objects.create(name="Другая инстанция")

        task = DocumentTask.objects.create(
            title="Технический проект 1",
            authority=other_authority,
        )

        self.assertEqual(task.route, self.route)
        self.assertEqual(task.authority, other_authority)

    def test_no_match_leaves_route_empty(self):
        task = DocumentTask.objects.create(title="Совсем другой документ")

        self.assertIsNone(task.route)


class SendDeadlineRemindersTests(TestCase):
    def setUp(self):
        self.responsible = get_user_model().objects.create_user(
            username="responsible",
            password="password123",
            email="responsible@example.com",
        )

    def _create_task_with_deadline(self, days_from_now, title="Task with deadline"):
        return DocumentTask.objects.create(
            title=title,
            deadline=timezone.now() + timezone.timedelta(days=days_from_now),
            responsible=self.responsible,
        )

    def test_sends_reminder_when_deadline_matches_threshold(self):
        task = self._create_task_with_deadline(30)

        call_command("send_deadline_reminders")

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(task.title, mail.outbox[0].message().as_string())
        self.assertTrue(DeadlineReminder.objects.filter(task=task, threshold_days=30).exists())

    def test_no_reminder_when_deadline_does_not_match_threshold(self):
        self._create_task_with_deadline(45)

        call_command("send_deadline_reminders")

        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(DeadlineReminder.objects.exists())

    def test_reminder_is_not_sent_twice_for_same_threshold(self):
        task = self._create_task_with_deadline(7)

        call_command("send_deadline_reminders")
        call_command("send_deadline_reminders")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(DeadlineReminder.objects.filter(task=task, threshold_days=7).count(), 1)

    def test_no_reminder_when_task_has_no_responsible(self):
        DocumentTask.objects.create(
            title="No responsible",
            deadline=timezone.now() + timezone.timedelta(days=14),
        )

        call_command("send_deadline_reminders")

        self.assertEqual(len(mail.outbox), 0)

    def test_done_tasks_are_excluded(self):
        task = self._create_task_with_deadline(60, title="Done task")
        task.status = DocumentTask.Status.DONE
        task.save()

        call_command("send_deadline_reminders")

        self.assertEqual(len(mail.outbox), 0)


class DocumentTaskAuditLogTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="auditedspecialist", password="password123")
        for codename in ["add_documenttask", "change_documenttask", "delete_documenttask", "view_documenttask"]:
            self.user.user_permissions.add(Permission.objects.get(codename=codename))
        self.client.force_login(self.user)

    def test_create_logs_audit_entry(self):
        self.client.post(reverse("documents:document_task_create"), data={"title": "Новая задача", "status": "planned"})

        task = DocumentTask.objects.get(title="Новая задача")
        self.assertTrue(
            AuditLogEntry.objects.filter(action="create", model_name="DocumentTask", object_id=str(task.pk)).exists()
        )

    def test_update_logs_audit_entry(self):
        task = DocumentTask.objects.create(title="Задача")

        self.client.post(
            reverse("documents:document_task_update", args=[task.pk]),
            data={"title": "Задача (изменена)", "status": "planned"},
        )

        self.assertTrue(
            AuditLogEntry.objects.filter(action="update", model_name="DocumentTask", object_id=str(task.pk)).exists()
        )

    def test_delete_logs_audit_entry(self):
        task = DocumentTask.objects.create(title="Задача на удаление")
        task_id = task.pk

        self.client.post(reverse("documents:document_task_delete", args=[task_id]))

        self.assertTrue(
            AuditLogEntry.objects.filter(action="delete", model_name="DocumentTask", object_id=str(task_id)).exists()
        )
