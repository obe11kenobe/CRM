from django import forms

from .fields import FIELD_REGISTRY


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
