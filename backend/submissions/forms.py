from django import forms

from .fields import FIELD_REGISTRY
from .models import AgencyResponse, SubmissionPackage


class RouteFieldsForm(forms.Form):
    def __init__(self, *args, route, **kwargs):
        super().__init__(*args, **kwargs)

        for code in route.required_fields:
            spec = FIELD_REGISTRY.get(code)
            if not spec:
                continue

            field_class = spec['field_class']
            field_kwargs = spec.get('field_kwargs', {})
            self.fields[code] = field_class(label=spec['label'], **field_kwargs)

class SubmissionPackageForm(forms.ModelForm):
    class Meta:
        model = SubmissionPackage
        fields = (
            'status',
            'outgoing_number',
            'sent_at',
            'agency_incoming_number',
            'registered_at',
            'proof_file',
            'comment'
        )


    def __init__(self, *args, route, **kwargs):
        super().__init__(*args, **kwargs)
        self.route = route
        for code in route.required_attachments:
            self.fields[code] = forms.BooleanField(required=False, label=code.replace('_', ' ').capitalize())
            if self.instance.pk and code in self.instance.confirmed_attachments:
                self.fields[code].initial = True

    def _post_clean(self):
        self.instance.confirmed_attachments = [
            code for code in self.route.required_attachments
            if self.cleaned_data.get(code)
        ]
        super()._post_clean()


class AgencyResponseForm(forms.ModelForm):
    class Meta:
        model = AgencyResponse
        fields = (
            'response_type',
            'received_at',
            'correction_due_date',
            'comment',
            'response_file',
        )
        widgets = {
            'received_at': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            ),
            'correction_due_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            ),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }