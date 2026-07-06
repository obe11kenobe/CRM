from django import forms

from .fields import FIELD_REGISTRY
from .models import SubmissionPackage


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