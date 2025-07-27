import json
from django.http import JsonResponse
from django.views.generic import DetailView
from django.contrib.contenttypes.models import ContentType
from ..models import OrganizationUnit, OrganizationalFeedback, Ishchi
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

class OrganizationalUnitDetailView(DetailView):
    model = OrganizationUnit
    template_name = 'core/organizational_unit_detail.html'
    context_object_name = 'unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unit = self.get_object()
        content_type = ContentType.objects.get_for_model(unit)
        context['feedback_thread'] = OrganizationalFeedback.objects.filter(
            target_content_type=content_type,
            target_object_id=unit.id,
            parent__isnull=True
        ).order_by('-created_at')
        return context

@login_required
@require_POST
def post_feedback(request):
    try:
        data = json.loads(request.body)
        content = data.get('content')
        is_anonymous = data.get('is_anonymous', False)
        unit_id = data.get('unit_id')
        parent_id = data.get('parent_id')

        if not content or not unit_id:
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

        unit = OrganizationUnit.objects.get(id=unit_id)
        content_type = ContentType.objects.get_for_model(unit)

        parent = None
        if parent_id:
            parent = OrganizationalFeedback.objects.get(id=parent_id)

        feedback = OrganizationalFeedback.objects.create(
            target_content_type=content_type,
            target_object_id=unit.id,
            author=request.user,
            content=content,
            is_anonymous=is_anonymous,
            parent=parent
        )

        return JsonResponse({
            'status': 'ok',
            'feedback': {
                'id': feedback.id,
                'author': 'Anonymous' if feedback.is_anonymous else feedback.author.get_full_name(),
                'content': feedback.content,
                'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_anonymous': feedback.is_anonymous,
                'author_id': request.user.id
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
