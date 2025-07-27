from django.views.generic import DetailView
from ..models import Ishchi, QuickFeedback

class UserProfileDetailView(DetailView):
    model = Ishchi
    template_name = 'core/user_profile_detail.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # Get feedback given by the user
        context['feedback_given'] = QuickFeedback.objects.filter(from_user=user).order_by('-created_at')

        # Get feedback received by the user
        context['feedback_received'] = QuickFeedback.objects.filter(to_user=user).order_by('-created_at')

        return context
