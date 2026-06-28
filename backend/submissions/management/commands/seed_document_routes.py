from django.core.management.base import BaseCommand

from documents.models import Authority
from submissions.models import DocumentRoute

ROUTES=[
{
        "route_id": "T01",
        "name": "Проект ГРР / Экспертиза ГРР",
        "document_process": "Проект ГРР; Экспертиза ГРР",
        "authority_name": "ФГКУ Росгеолэкспертиза",
        "template_name": "Заявка на проведение экспертизы проектной документации ГРР",
        "required_fields": [
            "company_full_name",
            "inn",
            "license_number",
            "object_name",
            "project_name",
            "contact_person",
        ],
        "required_attachments": [
            "project_documentation",
            "calendar_plan",
            "license_file",
            "power_of_attorney",
        ],
        "submission_channel": DocumentRoute.SubmissionChannel.MANUAL,
        "source_url": "https://www.rgexp.ru/",
        "note": "Сервис должен различать полную экспертизу и экспертизу календарного плана.",
        "risk_level": DocumentRoute.RiskLevel.MEDIUM,
        "allow_auto_generation": True,
    },
    {
        "route_id": "T03",
        "name": "Технический проект / Протокол ТКР",
        "document_process": "Технический проект; изменение календарного плана; протокол ТКР",
        "authority_name": "Уралнедра",
        "template_name": "Заявление о согласовании технического проекта / изменений",
        "required_fields": [
            "company_full_name",
            "inn",
            "license_number",
            "object_name",
            "project_name",
            "requested_action",
            "contact_person",
        ],
        "required_attachments": [
            "technical_project",
            "license_file",
            "reserves_protocol",
            "power_of_attorney",
        ],
        "submission_channel": DocumentRoute.SubmissionChannel.AGENCY_ACCOUNT,
        "source_url": "https://rosnedra.gov.ru/",
        "note": "E-mail не должен быть единственным каналом подачи.",
        "risk_level": DocumentRoute.RiskLevel.HIGH,
        "allow_auto_generation": True,
    },
    {
        "route_id": "T27",
        "name": "ОПР — требуется уточнение",
        "document_process": "ОПР — в файле не расшифровано",
        "authority_name": "Требуется уточнение",
        "template_name": "",
        "required_fields": [
            "object_name",
            "contact_person",
            "requested_actio",
        ],
        "required_attachments": [],
        "submission_channel": DocumentRoute.SubmissionChannel.MANUAL,
        "source_url": "",
        "note": "Не автоматизировать до расшифровки аббревиатуры.",
        "risk_level": DocumentRoute.RiskLevel.HIGH,
        "allow_auto_generation": False,
    },
]

class Command(BaseCommand):
    help = "Create or update document automation routes."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for raw_route_data in ROUTES:
            route_data = raw_route_data.copy()

            route_id = route_data.pop("route_id")
            authority_name = route_data.pop("authority_name")

            authority, _ = Authority.objects.get_or_create(
                name=authority_name,
            )

            route, created = DocumentRoute.objects.update_or_create(
                route_id=route_id,
                defaults={
                    **route_data,
                    "authority": authority,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Routes seeded. Created: {created_count}. Updated: {updated_count}."
            )
        )