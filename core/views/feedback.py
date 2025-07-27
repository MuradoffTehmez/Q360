from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from ..models import OrganizationalFeedback, OrganizationUnit

def organizational_unit_detail(request, unit_id):
    unit = get_object_or_404(OrganizationUnit, id=unit_id)
    content_type = ContentType.objects.get_for_model(unit)
    feedback = OrganizationalFeedback.objects.filter(
        target_content_type=content_type,
        target_object_id=unit.id,
        parent__isnull=True
    ).order_by('-created_at')

    context = {
        'unit': unit,
        'feedback': feedback,
    }
    return render(request, 'core/department_detail.html', context)


@login_required
@require_POST
def post_organizational_feedback(request):
    content = request.POST.get('content')
    is_anonymous = request.POST.get('is_anonymous') == 'true'
    parent_id = request.POST.get('parent_id')
    unit_id = request.POST.get('unit_id')

    try:
        unit = OrganizationUnit.objects.get(id=unit_id)
    except OrganizationUnit.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid unit.'}, status=400)


    parent = None
    if parent_id:
        parent = get_object_or_404(OrganizationalFeedback, id=parent_id)

    feedback = OrganizationalFeedback.objects.create(
        target_object=unit,
        author=request.user,
        content=content,
        is_anonymous=is_anonymous,
        parent=parent
    )

    return JsonResponse({
        'status': 'ok',
        'feedback': {
            'id': feedback.id,
            'content': feedback.content,
            'author': 'Anonymous User' if feedback.is_anonymous else feedback.author.get_full_name(),
            'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_anonymous': feedback.is_anonymous,
            'author_profile_url': '' if feedback.is_anonymous else f'/profile/{feedback.author.pk}/'
        }
    })
