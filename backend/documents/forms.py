from django import forms

from .models import DocumentTask


class DocumentTaskForm(forms.ModelForm):
    class Meta:
        model = DocumentTask
        fields = (
            'title',
            'mining_object',
            'license_object',
            'direction',
            'authority',
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
        self.fields['responsible'].queryset = self.fields['responsible'].queryset.order_by('username')
