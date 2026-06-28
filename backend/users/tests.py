from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from users.forms import JobTitleForm, ProfileUserForm


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
