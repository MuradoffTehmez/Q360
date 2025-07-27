from django.views.generic import DetailView
from ..models import Ishchi, OrganizationalFeedback, QuickFeedback


class UserProfileDetailView(DetailView):
    model = Ishchi
    template_name = 'core/user_profile_detail.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # Feedback given by the user
        context['feedback_given'] = OrganizationalFeedback.objects.filter(author=user)

        # Feedback received by the user (assuming QuickFeedback is the model for direct user feedback)
        context['feedback_received'] = QuickFeedback.objects.filter(to_user=user)

        return context
