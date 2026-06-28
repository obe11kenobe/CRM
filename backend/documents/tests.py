from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from documents.models import DocumentDirection, DocumentTask, License, MiningObject


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
