import logging
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DocumentTaskForm
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
