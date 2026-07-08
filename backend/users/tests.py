from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from users.audit import log_action
from users.forms import JobTitleForm, ProfileUserForm
from users.models import AuditLogEntry, JobTitle


class UserFormsTests(TestCase):
    def test_profile_form_excludes_staff_managed_fields(self):
        form = ProfileUserForm()

        self.assertNotIn("username", form.fields)
        self.assertNotIn("email", form.fields)
        self.assertNotIn("job_title", form.fields)
        self.assertNotIn("manager", form.fields)

    def test_job_title_form_excludes_permissions(self):
        form = JobTitleForm()

        self.assertEqual(
            list(form.fields),
            ["job_title", "description", "parent", "is_active"],
        )
        self.assertNotIn("permissions", form.fields)

    def test_job_title_form_rejects_blank_title(self):
        form = JobTitleForm(
            data={
                "job_title": "   ",
                "description": "",
                "parent": "",
                "is_active": "on",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("job_title", form.errors)


class JobTitlePermissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="employee",
            password="password123",
        )

    def test_job_title_list_requires_permission(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("job_title_list"))

        self.assertEqual(response.status_code, 403)

    def test_job_title_list_allows_user_with_view_permission(self):
        permission = Permission.objects.get(codename="view_jobtitle")
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        response = self.client.get(reverse("job_title_list"))

        self.assertEqual(response.status_code, 200)


class AuditLogTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="auditor2", password="password123")

    def test_log_action_creates_entry_with_expected_fields(self):
        job_title = JobTitle.objects.create(job_title="Специалист по недрам")

        log_action(self.user, "create", job_title, details="via test")

        entry = AuditLogEntry.objects.get()
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.action, "create")
        self.assertEqual(entry.model_name, "JobTitle")
        self.assertEqual(entry.object_id, str(job_title.pk))
        self.assertEqual(entry.object_repr, "Специалист по недрам")
        self.assertEqual(entry.details, "via test")

    def test_log_action_with_anonymous_user_stores_null_user(self):
        from django.contrib.auth.models import AnonymousUser

        job_title = JobTitle.objects.create(job_title="Аноним")
        log_action(AnonymousUser(), "create", job_title)

        entry = AuditLogEntry.objects.get()
        self.assertIsNone(entry.user)

    def test_job_title_crud_creates_audit_entries(self):
        for codename in ["add_jobtitle", "change_jobtitle", "delete_jobtitle", "view_jobtitle"]:
            self.user.user_permissions.add(Permission.objects.get(codename=codename))
        self.client.force_login(self.user)

        create_response = self.client.post(
            reverse("job_title_create"),
            data={"job_title": "Юрист", "description": "", "parent": "", "is_active": "on"},
        )
        self.assertEqual(create_response.status_code, 302)
        job_title = JobTitle.objects.get(job_title="Юрист")
        self.assertTrue(
            AuditLogEntry.objects.filter(action="create", model_name="JobTitle", object_id=str(job_title.pk)).exists()
        )

        self.client.post(
            reverse("job_title_update", args=[job_title.pk]),
            data={"job_title": "Юрист (изменено)", "description": "", "parent": "", "is_active": "on"},
        )
        self.assertTrue(
            AuditLogEntry.objects.filter(action="update", model_name="JobTitle", object_id=str(job_title.pk)).exists()
        )

        self.client.post(reverse("job_title_delete", args=[job_title.pk]))
        self.assertTrue(
            AuditLogEntry.objects.filter(action="delete", model_name="JobTitle", object_id=str(job_title.pk)).exists()
        )
