# core/urls/ai_risk.py

from django.urls import path
from ..views import ai_risk

app_name = 'ai_risk'

urlpatterns = [
    path('', ai_risk.ai_risk_dashboard, name='ai_risk_dashboard'),
    path('team/', ai_risk.ai_risk_team_analysis, name='ai_risk_team_analysis'),
    path('surveys/', ai_risk.psychological_surveys, name='psychological_surveys'),
    path('flags/', ai_risk.risk_flags_dashboard, name='risk_flags_dashboard'),
    path('strategic-planning/', ai_risk.strategic_hr_planning, name='strategic_hr_planning'),
]