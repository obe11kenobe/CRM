from django import forms

from documents.models import MiningObject

FIELD_REGISTRY = {
    "company_full_name": {
        "label": "Полное наименование организации",
        "field_class": forms.CharField,
    },
    "inn": {
        "label": "ИНН",
        "field_class": forms.CharField,
    },
    "ogrn": {
        "label": "ОГРН/ОГРНИП",
        "field_class": forms.CharField,
    },
    "license_number": {
        "label": "Номер лицензии на недра",
        "field_class": forms.CharField,
    },
    "license_end_date": {
        "label": "Дата окончания лицензии",
        "field_class": forms.DateField,
    },
    "object_name": {
        "label": "Объект / месторождение",
        "field_class": forms.ModelChoiceField,
        "field_kwargs": {"queryset": MiningObject.objects.filter(is_active=True)},
    },
    "project_name": {
        "label": "Наименование проекта/документа",
        "field_class": forms.CharField,
    },
    "contact_person": {
        "label": "Контактный специалист",
        "field_class": forms.CharField,
    },
    "mineral_type": {
        "label": "Вид полезного ископаемого",
        "field_class": forms.CharField,
    },
    "requested_action": {
        "label": "Что просим сделать",
        "field_class": forms.ChoiceField,
        "field_kwargs": {
            "choices": [
                ("approve", "Согласовать"),
                ("issue", "Выдать"),
                ("extend", "Продлить"),
                ("amend", "Внести изменения"),
                ("accept_report", "Принять отчет"),
            ],
        },
    },
    "forest_district": {
        "label": "Лесничество / квартал / выдел",
        "field_class": forms.CharField,
    },
    "land_holder": {
        "label": "Правообладатель/арендодатель земли",
        "field_class": forms.CharField,
    },
    "land_cadastral_number": {
        "label": "Кадастровый номер земельного участка",
        "field_class": forms.CharField,
    },
    "land_category": {
        "label": "Категория земли",
        "field_class": forms.ChoiceField,
        "field_kwargs": {
            "choices": [
                ("forest_fund", "Земли лесного фонда"),
                ("industrial", "Земли промышленности"),
                ("other", "Иное"),
            ],
        },
    },
    "court_case_ref": {
        "label": "Номер судебного дела/исполнительного производства",
        "field_class": forms.CharField,
    },
    "deadline_external": {
        "label": "Внешний срок / дедлайн",
        "field_class": forms.DateField,
    },
    "municipality": {
        "label": "Муниципальное образование",
        "field_class": forms.CharField,
    },
    "nvos_category": {
        "label": "Категория объекта НВОС",
        "field_class": forms.ChoiceField,
        "field_kwargs": {
            "choices": [("I", "I"), ("II", "II"), ("III", "III"), ("IV", "IV")],
        },
    },
    "sez_details": {
        "label": "Реквизиты санитарно-эпидемиологического заключения",
        "field_class": forms.CharField,
    },
    "water_body_name": {
        "label": "Водный объект",
        "field_class": forms.CharField,
    },
    "water_body_coordinates": {
        "label": "Координаты места работ/водопользования",
        "field_class": forms.CharField,
    },
}
