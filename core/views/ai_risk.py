"""
AI Risk Analysis Views
İşçilərin performans risklərini AI vasitəsilə analiz edir
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from ..models import (
    Ishchi, EmployeeRiskAnalysis, RiskFlag, PsychologicalRiskSurvey, 
    PsychologicalRiskResponse, QiymetlendirmeDovru
)
from ..permissions import require_role


@login_required
def ai_risk_dashboard(request):
    """AI Risk Analysis ana səhifəsi"""
    
    # Son aktiv dövrü tap
    active_cycle = QiymetlendirmeDovru.objects.filter(
        aktivdir=True
    ).order_by('-bashlama_tarixi').first()
    
    # İstifadəçinin risk analizi məlumatları
    user_risk_analysis = EmployeeRiskAnalysis.objects.filter(
        employee=request.user,
        cycle=active_cycle
    ).first()
    
    # Aktiv risk bayraqları
    active_risk_flags = RiskFlag.objects.filter(
        employee=request.user,
        is_active=True
    ).order_by('-detected_at')
    
    # Son psixoloji anketlər
    recent_surveys = PsychologicalRiskSurvey.objects.filter(
        is_active=True
    ).order_by('-created_at')[:3]
    
    context = {
        'user_risk_analysis': user_risk_analysis,
        'active_risk_flags': active_risk_flags,
        'recent_surveys': recent_surveys,
        'active_cycle': active_cycle,
        'page_title': 'AI Risk Analizi'
    }
    
    return render(request, 'ai_risk/dashboard.html', context)


@login_required
@require_role(['ADMIN', 'SUPERADMIN', 'REHBER'])
def ai_risk_team_analysis(request):
    """Komanda üzrə AI risk analizi"""
    
    department_id = request.GET.get('department_id')
    cycle_id = request.GET.get('cycle_id')
    
    if not department_id or not cycle_id:
        return JsonResponse({'error': 'Department və cycle seçilməlidir'})
    
    # Şöbədəki işçilərin siyahısı
    team_members = Ishchi.objects.filter(
        organization_unit_id=department_id
    )
    
    # Hər bir komanda üzvü üçün risk analizi
    team_risk_data = []
    high_risk_count = 0
    
    for member in team_members:
        risk_analysis = EmployeeRiskAnalysis.objects.filter(
            employee=member,
            cycle_id=cycle_id
        ).first()
        
        if risk_analysis:
            team_risk_data.append({
                'user_id': member.id,
                'user_name': member.get_full_name(),
                'risk_score': risk_analysis.total_risk_score,
                'risk_level': risk_analysis.get_risk_level_display(),
                'active_flags': risk_analysis.active_flags_count
            })
            
            if risk_analysis.risk_level in ['HIGH', 'CRITICAL']:
                high_risk_count += 1
    
    # Komanda ortalaması
    team_average_risk = 0
    if team_risk_data:
        team_average_risk = sum([item['risk_score'] for item in team_risk_data]) / len(team_risk_data)
    
    context = {
        'team_risk_data': team_risk_data,
        'team_average_risk': team_average_risk,
        'high_risk_count': high_risk_count,
        'department_id': department_id,
        'cycle_id': cycle_id,
        'page_title': 'Komanda Risk Analizi'
    }
    
    return render(request, 'ai_risk/team_analysis.html', context)


@login_required
def psychological_surveys(request):
    """Psixoloji risk anketləri"""
    
    # Aktiv anketlər
    active_surveys = PsychologicalRiskSurvey.objects.filter(
        is_active=True
    ).order_by('-created_at')
    
    # İstifadəçinin cavabları
    user_responses = PsychologicalRiskResponse.objects.filter(
        employee=request.user
    ).select_related('survey')
    
    context = {
        'active_surveys': active_surveys,
        'user_responses': user_responses,
        'page_title': 'Psixoloji Anketlər'
    }
    
    return render(request, 'ai_risk/psychological_surveys.html', context)


@login_required
def risk_flags_dashboard(request):
    """Risk bayraqları dashboard"""
    
    # Aktiv risk bayraqları
    active_flags = RiskFlag.objects.filter(
        employee=request.user,
        is_active=True
    ).order_by('-detected_at')
    
    # Həll edilmiş risk bayraqları
    resolved_flags = RiskFlag.objects.filter(
        employee=request.user,
        is_active=False
    ).order_by('-resolved_at')[:10]
    
    # Risk bayraqları statistikası
    flag_stats = {
        'total_active': active_flags.count(),
        'total_resolved': resolved_flags.count(),
        'by_severity': RiskFlag.objects.filter(
            employee=request.user
        ).values('severity').annotate(count=Count('id'))
    }
    
    context = {
        'active_flags': active_flags,
        'resolved_flags': resolved_flags,
        'flag_stats': flag_stats,
        'page_title': 'Risk Bayraqları'
    }
    
    return render(request, 'ai_risk/risk_flags.html', context)


@login_required
@require_role(['ADMIN', 'SUPERADMIN', 'REHBER'])
def strategic_hr_planning(request):
    """Strategik HR planlaşdırma"""
    
    # Şöbələr üzrə risk analizi
    departments = OrganizationUnit.objects.filter(
        parent__isnull=True
    )
    
    department_risk_data = []
    
    for dept in departments:
        # Şöbədəki işçilərin risk analizi
        dept_employees = Ishchi.objects.filter(
            organization_unit=dept
        )
        
        dept_risk_scores = []
        for emp in dept_employees:
            risk_analysis = EmployeeRiskAnalysis.objects.filter(
                employee=emp
            ).first()
            if risk_analysis:
                dept_risk_scores.append(risk_analysis.total_risk_score)
        
        if dept_risk_scores:
            avg_risk = sum(dept_risk_scores) / len(dept_risk_scores)
            department_risk_data.append({
                'department': dept,
                'avg_risk': avg_risk,
                'employee_count': len(dept_risk_scores)
            })
    
    context = {
        'department_risk_data': department_risk_data,
        'page_title': 'Strategik HR Planlaşdırma'
    }
    
    return render(request, 'ai_risk/strategic_hr_planning.html', context)