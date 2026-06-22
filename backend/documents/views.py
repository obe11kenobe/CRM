import logging
import tempfile
from datetime import timedelta
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DocumentAssignmentForm, DocumentImportForm, DocumentTaskForm
from .importers import import_document_plan
from .models import DocumentDirection, DocumentTask, MiningObject

logger = logging.getLogger(__name__)


@login_required
def document_task_list(request):
    tasks = DocumentTask.objects.select_related(
        'mining_object',
        'license_object',
        'direction',
        'authority',
        'responsible',
    )

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    mining_object_id = request.GET.get('mining_object', '').strip()
    direction_id = request.GET.get('direction', '').strip()
    deadline = request.GET.get('deadline', '').strip()

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query)
            | Q(comment__icontains=query)
            | Q(mining_object__name__icontains=query)
            | Q(license_object__number__icontains=query)
            | Q(authority__name__icontains=query)
        )

    if status:
        tasks = tasks.filter(status=status)

    if mining_object_id:
        tasks = tasks.filter(mining_object_id=mining_object_id)

    if direction_id:
        tasks = tasks.filter(direction_id=direction_id)

    today = timezone.localdate()
    if deadline == 'overdue':
        tasks = tasks.filter(deadline__date__lt=today).exclude(status=DocumentTask.Status.DONE)
    elif deadline == 'week':
        week_end = today + timedelta(days=7)
        tasks = tasks.filter(deadline__date__range=(today, week_end))
    elif deadline == 'no_deadline':
        tasks = tasks.filter(deadline__isnull=True)

    tasks = tasks.order_by('deadline', 'title')

    context = {
        'tasks': tasks,
        'objects': MiningObject.objects.filter(is_active=True).order_by('name'),
        'directions': DocumentDirection.objects.order_by('name'),
        'statuses': DocumentTask.Status.choices,
        'filters': {
            'q': query,
            'status': status,
            'mining_object': mining_object_id,
            'direction': direction_id,
            'deadline': deadline,
        },
    }

    return render(request, 'documents/document_task_list.html', context)


@login_required
def document_import(request):
    result = None

    if request.method == 'POST':
        form = DocumentImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            suffix = Path(uploaded_file.name).suffix

            with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                try:
                    result = import_document_plan(
                        temp_file.name,
                        year=form.cleaned_data['year'],
                        dry_run=form.cleaned_data['dry_run'],
                        update_existing=form.cleaned_data['update_existing'],
                    )
                except Exception as exc:
                    logger.exception(
                        'Document plan import failed from web: file=%s dry_run=%s user=%s',
                        uploaded_file.name,
                        form.cleaned_data['dry_run'],
                        request.user,
                    )
                    form.add_error(None, f'Импорт не выполнен: {exc}')
                else:
                    logger.info(
                        'Document plan imported from web: file=%s dry_run=%s user=%s created=%s updated=%s skipped=%s',
                        uploaded_file.name,
                        form.cleaned_data['dry_run'],
                        request.user,
                        result.tasks_created,
                        result.tasks_updated,
                        result.rows_skipped,
                    )
        else:
            logger.warning(
                'Invalid document import form: user=%s errors=%s',
                request.user,
                form.errors.as_json(),
            )
    else:
        form = DocumentImportForm(initial={'dry_run': True, 'update_existing': True})

    return render(request, 'documents/document_import.html', {'form': form, 'result': result})


@login_required
def document_assignment(request):
    tasks = DocumentTask.objects.filter(
        responsible__isnull=True,
    ).select_related(
        'mining_object',
        'license_object',
        'direction',
        'authority',
    )

    query = request.GET.get('q', '').strip()
    mining_object_id = request.GET.get('mining_object', '').strip()
    direction_id = request.GET.get('direction', '').strip()

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query)
            | Q(comment__icontains=query)
            | Q(mining_object__name__icontains=query)
            | Q(license_object__number__icontains=query)
            | Q(authority__name__icontains=query)
        )

    if mining_object_id:
        tasks = tasks.filter(mining_object_id=mining_object_id)

    if direction_id:
        tasks = tasks.filter(direction_id=direction_id)

    tasks = tasks.order_by('deadline', 'title')
    assigned_count = None

    if request.method == 'POST':
        form = DocumentAssignmentForm(request.POST, tasks_queryset=tasks)
        if form.is_valid():
            selected_tasks = form.cleaned_data['tasks']
            responsible = form.cleaned_data['responsible']
            task_ids = list(selected_tasks.values_list('pk', flat=True))
            assigned_count = selected_tasks.update(responsible=responsible)

            logger.info(
                'Document tasks assigned: count=%s responsible=%s task_ids=%s user=%s',
                assigned_count,
                responsible,
                task_ids,
                request.user,
            )

            tasks = tasks.exclude(pk__in=task_ids)
            form = DocumentAssignmentForm(tasks_queryset=tasks)
        else:
            logger.warning(
                'Invalid document assignment form: user=%s errors=%s',
                request.user,
                form.errors.as_json(),
            )
    else:
        form = DocumentAssignmentForm(tasks_queryset=tasks)

    context = {
        'form': form,
        'tasks': tasks,
        'assigned_count': assigned_count,
        'objects': MiningObject.objects.filter(is_active=True).order_by('name'),
        'directions': DocumentDirection.objects.order_by('name'),
        'filters': {
            'q': query,
            'mining_object': mining_object_id,
            'direction': direction_id,
        },
    }

    return render(request, 'documents/document_assignment.html', context)


@login_required
def document_task_detail(request, pk):
    task = get_object_or_404(
        DocumentTask.objects.select_related(
            'mining_object',
            'license_object',
            'direction',
            'authority',
            'responsible',
        ),
        pk=pk,
    )

    return render(request, 'documents/document_task_detail.html', {'task': task})


@login_required
def document_task_create(request):
    if request.method == 'POST':
        form = DocumentTaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            logger.info(
                'Document task created: id=%s title=%s user=%s',
                task.pk,
                task.title,
                request.user,
            )
            return redirect('documents:document_task_detail', pk=task.pk)
        logger.warning(
            'Invalid document task create form: user=%s errors=%s',
            request.user,
            form.errors.as_json(),
        )
    else:
        form = DocumentTaskForm()

    return render(request, 'documents/document_task_form.html', {'form': form})


@login_required
def document_task_update(request, pk):
    task = get_object_or_404(DocumentTask, pk=pk)

    if request.method == 'POST':
        form = DocumentTaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            logger.info(
                'Document task updated: id=%s title=%s user=%s',
                task.pk,
                task.title,
                request.user,
            )
            return redirect('documents:document_task_detail', pk=task.pk)
        logger.warning(
            'Invalid document task update form: id=%s user=%s errors=%s',
            task.pk,
            request.user,
            form.errors.as_json(),
        )
    else:
        form = DocumentTaskForm(instance=task)

    return render(request, 'documents/document_task_form.html', {'form': form, 'task': task})


@login_required
def document_task_delete(request, pk):
    task = get_object_or_404(DocumentTask, pk=pk)

    if request.method == 'POST':
        task_id = task.pk
        task_title = task.title
        task.delete()
        logger.info(
            'Document task deleted: id=%s title=%s user=%s',
            task_id,
            task_title,
            request.user,
        )
        return redirect('documents:document_task_list')

    return render(request, 'documents/document_task_confirm_delete.html', {'task': task})


@login_required
def document_task_bulk_delete(request):
    if request.method != 'POST':
        return redirect('documents:document_task_list')

    task_ids = request.POST.getlist('tasks')
    tasks = DocumentTask.objects.filter(pk__in=task_ids)
    deleted_ids = list(tasks.values_list('pk', flat=True))
    deleted_count = tasks.count()
    tasks.delete()

    logger.info(
        'Document tasks bulk deleted: count=%s task_ids=%s user=%s',
        deleted_count,
        deleted_ids,
        request.user,
    )

    return redirect('documents:document_task_list')
