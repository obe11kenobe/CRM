from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from documents.models import Authority, DocumentTask
from submissions.forms import RouteFieldsForm, SubmissionPackageForm
from submissions.models import DocumentRoute, SubmissionPackage


class DocumentRouteMatchingTests(TestCase):
    def setUp(self):
        self.authority = Authority.objects.create(name="Уралнедра")
        self.route = DocumentRoute.objects.create(
            route_id="T03",
            name="Технический проект",
            document_process="Технический проект; изменение календарного плана; протокол ТКР",
            authority=self.authority,
        )

    def test_match_found_by_keyword(self):
        matched = DocumentRoute.match_for_document("Технический проект 1")

        self.assertEqual(matched, self.route)

    def test_match_is_case_insensitive(self):
        matched = DocumentRoute.match_for_document("ТЕХНИЧЕСКИЙ ПРОЕКТ")

        self.assertEqual(matched, self.route)

    def test_no_match_returns_none(self):
        matched = DocumentRoute.match_for_document("Совершенно другой документ")

        self.assertIsNone(matched)

    def test_empty_title_returns_none(self):
        matched = DocumentRoute.match_for_document("")

        self.assertIsNone(matched)

    def test_inactive_route_is_not_matched(self):
        self.route.is_active = False
        self.route.save()

        matched = DocumentRoute.match_for_document("Технический проект 1")

        self.assertIsNone(matched)


class RouteFieldsFormTests(TestCase):
    def setUp(self):
        self.authority = Authority.objects.create(name="Уралнедра")

    def test_form_only_includes_fields_from_route(self):
        route = DocumentRoute.objects.create(
            route_id="T08",
            name="Лицензия на маркшейдерские работы",
            document_process="Лицензия на маркшейдерские работы",
            authority=self.authority,
            required_fields=["company_full_name", "inn", "ogrn", "contact_person"],
        )

        form = RouteFieldsForm(route=route)

        self.assertEqual(set(form.fields.keys()), {"company_full_name", "inn", "ogrn", "contact_person"})

    def test_different_routes_produce_different_fields(self):
        route_a = DocumentRoute.objects.create(
            route_id="T12",
            name="Лесная декларация",
            document_process="Лесная декларация",
            authority=self.authority,
            required_fields=["company_full_name", "forest_district"],
        )
        route_b = DocumentRoute.objects.create(
            route_id="T23",
            name="Договор водопользования",
            document_process="Договор водопользования",
            authority=self.authority,
            required_fields=["water_body_name", "water_body_coordinates"],
        )

        form_a = RouteFieldsForm(route=route_a)
        form_b = RouteFieldsForm(route=route_b)

        self.assertEqual(set(form_a.fields.keys()), {"company_full_name", "forest_district"})
        self.assertEqual(set(form_b.fields.keys()), {"water_body_name", "water_body_coordinates"})

    def test_unknown_field_code_is_skipped(self):
        route = DocumentRoute.objects.create(
            route_id="T99",
            name="Тестовый маршрут",
            document_process="Тестовый маршрут",
            authority=self.authority,
            required_fields=["company_full_name", "no_such_field_code"],
        )

        form = RouteFieldsForm(route=route)

        self.assertEqual(set(form.fields.keys()), {"company_full_name"})

    def test_object_name_is_model_choice_field(self):
        route = DocumentRoute.objects.create(
            route_id="T01",
            name="Проект ГРР",
            document_process="Проект ГРР",
            authority=self.authority,
            required_fields=["object_name"],
        )

        form = RouteFieldsForm(route=route)

        self.assertIsInstance(form.fields["object_name"], forms.ModelChoiceField)


class RouteFieldsViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="specialist", password="password123")
        for codename in ["change_submissionpackage", "view_documenttask"]:
            self.user.user_permissions.add(Permission.objects.get(codename=codename))
        self.client.force_login(self.user)

        self.authority = Authority.objects.create(name="Уралнедра")
        self.route = DocumentRoute.objects.create(
            route_id="T08",
            name="Лицензия на маркшейдерские работы",
            document_process="Лицензия на маркшейдерские работы",
            authority=self.authority,
            required_fields=["company_full_name", "inn", "ogrn", "contact_person"],
        )

    def test_get_renders_form_when_route_assigned(self):
        task = DocumentTask.objects.create(title="Лицензия на маркшейдерские работы")
        self.assertEqual(task.route, self.route)

        response = self.client.get(reverse("submissions:route_fields_form", args=[task.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ИНН")

    def test_get_shows_missing_route_page_when_no_route(self):
        task = DocumentTask.objects.create(title="Совсем неизвестный документ 12345")
        self.assertIsNone(task.route)

        response = self.client.get(reverse("submissions:route_fields_form", args=[task.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "не выбран маршрут")

    def test_valid_post_saves_field_values_and_redirects(self):
        task = DocumentTask.objects.create(title="Лицензия на маркшейдерские работы")
        data = {
            "company_full_name": "ООО Ромашка",
            "inn": "6600000000",
            "ogrn": "1026600000000",
            "contact_person": "Иванов И.И.",
        }

        response = self.client.post(reverse("submissions:route_fields_form", args=[task.pk]), data=data)

        self.assertRedirects(response, reverse("documents:document_task_detail", args=[task.pk]))
        package = SubmissionPackage.objects.get(task=task, route=self.route)
        self.assertEqual(package.field_values, data)

    def test_invalid_post_reshows_form_with_entered_data(self):
        task = DocumentTask.objects.create(title="Лицензия на маркшейдерские работы")

        response = self.client.post(
            reverse("submissions:route_fields_form", args=[task.pk]),
            data={"company_full_name": "ООО Ромашка"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertContains(response, "ООО Ромашка")


class SubmissionPackageFormTests(TestCase):
    def setUp(self):
        self.authority = Authority.objects.create(name="Уралнедра")
        self.route = DocumentRoute.objects.create(
            route_id="T08",
            name="Лицензия на маркшейдерские работы",
            document_process="Лицензия на маркшейдерские работы",
            authority=self.authority,
            required_attachments=["license_file", "power_of_attorney"],
        )
        self.task = DocumentTask.objects.create(title="Лицензия на маркшейдерские работы")
        self.package, _ = SubmissionPackage.objects.get_or_create(task=self.task, route=self.route)

    def test_form_includes_checkbox_per_required_attachment(self):
        form = SubmissionPackageForm(route=self.route, instance=self.package)

        self.assertIn("license_file", form.fields)
        self.assertIn("power_of_attorney", form.fields)
        self.assertIsInstance(form.fields["license_file"], forms.BooleanField)

    def test_ready_status_without_confirmed_attachments_is_invalid(self):
        form = SubmissionPackageForm(
            {"status": "ready", "comment": ""},
            route=self.route,
            instance=self.package,
        )

        self.assertFalse(form.is_valid())

    def test_ready_status_with_all_attachments_confirmed_is_valid(self):
        form = SubmissionPackageForm(
            {
                "status": "ready",
                "comment": "",
                "license_file": "on",
                "power_of_attorney": "on",
            },
            route=self.route,
            instance=self.package,
        )

        self.assertTrue(form.is_valid())

    def test_saving_valid_form_stores_confirmed_attachments(self):
        form = SubmissionPackageForm(
            {
                "status": "ready",
                "comment": "",
                "license_file": "on",
                "power_of_attorney": "on",
            },
            route=self.route,
            instance=self.package,
        )

        self.assertTrue(form.is_valid())
        form.save()

        self.package.refresh_from_db()
        self.assertEqual(set(self.package.confirmed_attachments), {"license_file", "power_of_attorney"})

    def test_previously_confirmed_attachments_are_preselected(self):
        self.package.confirmed_attachments = ["license_file"]
        self.package.save()

        form = SubmissionPackageForm(route=self.route, instance=self.package)

        self.assertTrue(form.fields["license_file"].initial)
        self.assertFalse(form.fields["power_of_attorney"].initial)


class PackageStatusViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="specialist2", password="password123")
        for codename in ["change_submissionpackage", "view_documenttask"]:
            self.user.user_permissions.add(Permission.objects.get(codename=codename))
        self.client.force_login(self.user)

        self.authority = Authority.objects.create(name="Уралнедра")
        self.route = DocumentRoute.objects.create(
            route_id="T08",
            name="Лицензия на маркшейдерские работы",
            document_process="Лицензия на маркшейдерские работы",
            authority=self.authority,
            required_attachments=["license_file", "power_of_attorney"],
        )
        self.task = DocumentTask.objects.create(title="Лицензия на маркшейдерские работы")

    def test_get_renders_status_form_with_checklist(self):
        response = self.client.get(reverse("submissions:package_status_form", args=[self.task.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Комплектность вложений")

    def test_get_shows_missing_route_page_when_no_route(self):
        task = DocumentTask.objects.create(title="Совсем неизвестный документ 12345")

        response = self.client.get(reverse("submissions:package_status_form", args=[task.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "не выбран маршрут")

    def test_post_ready_without_attachments_does_not_save(self):
        response = self.client.post(
            reverse("submissions:package_status_form", args=[self.task.pk]),
            data={"status": "ready", "comment": ""},
        )

        self.assertEqual(response.status_code, 200)
        package = SubmissionPackage.objects.get(task=self.task, route=self.route)
        self.assertEqual(package.status, "draft")

    def test_post_ready_with_all_attachments_saves_and_redirects(self):
        response = self.client.post(
            reverse("submissions:package_status_form", args=[self.task.pk]),
            data={
                "status": "ready",
                "comment": "",
                "license_file": "on",
                "power_of_attorney": "on",
            },
        )

        self.assertRedirects(response, reverse("documents:document_task_detail", args=[self.task.pk]))
        package = SubmissionPackage.objects.get(task=self.task, route=self.route)
        self.assertEqual(package.status, "ready")
        self.assertEqual(set(package.confirmed_attachments), {"license_file", "power_of_attorney"})
