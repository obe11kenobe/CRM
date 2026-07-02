from django.test import TestCase

from documents.models import Authority
from submissions.models import DocumentRoute


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
