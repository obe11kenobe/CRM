from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from django.core.paginator import Paginator

from documents.models import DocumentTask
from users.audit import log_action

from .forms import AgencyResponseForm, RouteFieldsForm, SubmissionPackageForm
from .models import AgencyResponse, SubmissionPackage, DocumentRoute

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

@login_required
@permission_required('submissions.change_submissionpackage', raise_exception=True)
def package_status_form(request, task_id):
    task = get_object_or_404(DocumentTask, id=task_id)

    if not task.route:
        return render(request, 'submissions/route_fields_missing.html', {'task': task})

    package, _ = SubmissionPackage.objects.get_or_create(
        task=task,
        route=task.route,
        defaults={'created_by': request.user}
    )

    if request.method == 'POST':
        form = SubmissionPackageForm(request.POST, request.FILES, route=task.route, instance=package)
        if form.is_valid():
            form.save()
            log_action(request.user, 'update', package, details=f'Статус пакета изменён на «{package.get_status_display()}».')
            return redirect('documents:document_task_detail', pk=task.pk)
    else:
        form = SubmissionPackageForm(route=task.route, instance=package)

    responses = package.responses.all()

    return render(
        request,
        'submissions/package_status_form.html',
        {'form': form, 'task': task, 'package': package, 'responses': responses},
    )

@login_required
@permission_required('submissions.change_submissionpackage', raise_exception=True)
def agency_response_create(request, task_id):
    task = get_object_or_404(DocumentTask, id=task_id)

    if not task.route:
        return render(request, 'submissions/route_fields_missing.html', {'task': task})

    package, _ = SubmissionPackage.objects.get_or_create(
        task=task,
        route=task.route,
        defaults={'created_by': request.user}
    )

    if request.method == 'POST':
        form = AgencyResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.package = package
            response.created_by = request.user
            response.save()
            log_action(request.user, 'create', response)

            return redirect('submissions:package_status_form', task_id=task.pk)
    else:
        form = AgencyResponseForm()

    return render(
        request,
        'submissions/agency_response_form.html',
        {'form': form, 'task': task},
    )

def _paginate_queryset(request, queryset, per_page=50):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))

@login_required
@permission_required('submissions.view_submissionpackage', raise_exception=True)
def package_list(request):
    tasks = SubmissionPackage.objects.select_related(
        'task',
        'route',
        'created_by'
    )

    status = request.GET.get('status', '').strip()
    route = request.GET.get('route','').strip()

    if status:
        tasks = tasks.filter(status=status)

    if route:
        tasks = tasks.filter(route_id=route)

    page_obj = _paginate_queryset(request, tasks)

    context = {
        'packages': page_obj.object_list,
        'page_obj': page_obj,
        'filters': {'status': status, 'route': route},
        'total_packages': page_obj.paginator.count,
        'statuses': SubmissionPackage.Status.choices,
        'routes': DocumentRoute.objects.all()
    }

    return render(request, 'submissions/package_list.html', context)