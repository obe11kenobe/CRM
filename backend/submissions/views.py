from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from documents.models import DocumentTask

from .forms import RouteFieldsForm
from .models import SubmissionPackage

def _serialize_value(value):
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if hasattr(value, 'pk'):
        return value.pk
    return value

@login_required
@permission_required('submissions.change_submissionpackage', raise_exception=True)
def route_fields_form(request, task_id):
    task = get_object_or_404(DocumentTask, id=task_id)

    if not task.route:
        return render(request, 'submissions/route_fields_missing.html', {'task': task})

    package, _ = SubmissionPackage.objects.get_or_create(
        task=task,
        route=task.route,
        defaults={'created_by': request.user}
    )

    if request.method == 'POST':
        form = RouteFieldsForm(request.POST, route=task.route)
        if form.is_valid():
            package.field_values = {
                code: _serialize_value(value)
                for code, value in form.cleaned_data.items()
            }
            package.save()
            return redirect('documents:document_task_detail', pk=task.pk)
    else:
        form = RouteFieldsForm(route=task.route)

    return render(request, 'submissions/route_fields_form.html', {'form': form, 'task': task, 'package': package})