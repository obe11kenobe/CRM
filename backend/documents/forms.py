from django import forms
from django.contrib.auth import get_user_model

from .models import DocumentTask


class DocumentImportForm(forms.Form):
    file = forms.FileField(
        label='Excel-файл',
        help_text='Поддерживается файл .xlsx с детальным планом документов.',
    )
    year = forms.IntegerField(
        label='Год календаря',
        required=False,
        min_value=2000,
        max_value=2100,
        help_text='Если оставить пустым, год будет взят из названия файла.',
    )
    dry_run = forms.BooleanField(
        label='Только проверить, без записи в базу',
        required=False,
        initial=True,
    )
    update_existing = forms.BooleanField(
        label='Обновлять уже существующие документы',
        required=False,
        initial=True,
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('Загрузи файл в формате .xlsx.')
        return file


class DocumentTaskForm(forms.ModelForm):
    class Meta:
        model = DocumentTask
        fields = (
            'title',
            'mining_object',
            'license_object',
            'direction',
            'authority',
            'route',
            'status',
            'is_available',
            'received_at',
            'deadline',
            'responsible',
            'comment',
        )
        widgets = {
            'received_at': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            ),
            'deadline': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            ),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['mining_object'].queryset = self.fields['mining_object'].queryset.order_by('name')
        self.fields['license_object'].queryset = self.fields['license_object'].queryset.order_by('number')
        self.fields['direction'].queryset = self.fields['direction'].queryset.order_by('name')
        self.fields['authority'].queryset = self.fields['authority'].queryset.order_by('name')
        self.fields['route'].queryset = self.fields['route'].queryset.order_by('route_id')
        self.fields['responsible'].queryset = self.fields['responsible'].queryset.order_by('username')


class DocumentAssignmentForm(forms.Form):
    responsible = forms.ModelChoiceField(
        label='Исполнитель',
        queryset=get_user_model().objects.none(),
    )
    tasks = forms.ModelMultipleChoiceField(
        label='Документы',
        queryset=DocumentTask.objects.none(),
    )

    def __init__(self, *args, tasks_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['responsible'].queryset = get_user_model().objects.filter(
            is_active=True,
        ).order_by('last_name', 'first_name', 'username')
        self.fields['tasks'].queryset = tasks_queryset or DocumentTask.objects.none()
