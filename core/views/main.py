# core/views.py
# --- Sistem modulları (Python-un daxili) ---
import json
import random
# --- Django və Django modulları ---
from django.conf import settings
# --- Django auth modulları ---
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.db.models import Avg, Q
from django.http import HttpResponse
# --- Django core və HTTP modulları ---
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
# --- gemini AI modulu (Gemini AI module) ---
from ..ai_utils import generate_recommendations # <-- 
# --- Django util modulları ---
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import TemplateView
# --- Xarici paketlər ---
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from weasyprint import HTML
# --- core modulları ---
from ..decorators import rehber_required, superadmin_required
from ..forms import (HedefFormSet, IshchiCreationForm, IshchiPasswordChangeForm,
                    IshchiUpdateForm, YeniDovrForm)
# --- Lokal Layihə Modulları ---
from ..models import (Cavab, Hedef, InkishafPlani, Ishchi, OrganizationUnit,
                     Qiymetlendirme, QiymetlendirmeDovru, Sual,
                     SualKateqoriyasi)
from ..tokens import account_activation_token
from ..utils import get_detailed_report_context, get_performance_trend


# --- ÜMUMİ VƏ QEYDİYYAT GÖRÜNÜŞLƏRİ ---
# # İstifadəçilərin aktiv qiymətləndirmə tapşırıqlarını və inkişaf planını göstərən görünüş.
# # Bu görünüş, istifadəçilərin öz hesabatlarını və rəhbərlərin komanda üzvlərinin hesabatlarını görməsinə imkan verir.

@login_required
def dashboard(request):
    """İstifadəçinin aktiv qiymətləndirmə tapşırıqlarını və inkişaf planını göstərir."""

    # Aktiv qiymətləndirmə tapşırıqları
    qiymetlendirmeler = Qiymetlendirme.objects.filter(
        qiymetlendiren=request.user, status="GOZLEMEDE"
    ).select_related("qiymetlendirilen", "dovr")

    # İstifadəçinin aktiv inkişaf planını tapırıq
    aktiv_plan = (
        InkishafPlani.objects.filter(ishchi=request.user, status="AKTIV")
        .select_related("dovr")
        .first()
    )

    # Clean template üçün statistika məlumatları
    pending_evaluations_count = qiymetlendirmeler.count()
    completed_evaluations_count = Qiymetlendirme.objects.filter(
        qiymetlendiren=request.user, status="TAMAMLANMIS"
    ).count()
    total_evaluations_count = Qiymetlendirme.objects.filter(
        qiymetlendiren=request.user
    ).count()
    
    # Manager üçün əlavə məlumatlar
    team_members_count = 0
    is_manager = False
    if hasattr(request.user, 'rol') and request.user.rol in ['REHBER', 'ADMIN']:
        is_manager = True
        if hasattr(request.user, 'organization_unit') and request.user.organization_unit:
            team_members_count = Ishchi.objects.filter(
                organization_unit=request.user.organization_unit
            ).exclude(id=request.user.id).count()

    context = {
        "qiymetlendirmeler": qiymetlendirmeler,
        "aktiv_plan": aktiv_plan,
        "pending_evaluations_count": pending_evaluations_count,
        "completed_evaluations_count": completed_evaluations_count,
        "total_evaluations_count": total_evaluations_count,
        "team_members_count": team_members_count,
        "is_manager": is_manager,
    }
    return render(request, "core/dashboard_clean.html", context)

# --- QEYDİYYAT GÖRÜNÜŞLƏRİ ---
# # Yeni istifadəçiləri qeydiyyatdan keçirən və aktivasiya e-poçtu göndərən görünüş.
#

def qeydiyyat_sehifesi(request):
    """Yeni istifadəçiləri qeydiyyatdan keçirir və aktivasiya e-poçtu göndərir."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = IshchiCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Hesabı qeyri-aktiv edirik
            user.save()

            # Aktivasiya e-poçtu signal vasitəsilə avtomatik göndəriləcək
            messages.success(
                request,
                "Qeydiyyat uğurla tamamlandı! Zəhmət olmasa, hesabınızı aktivləşdirmək üçün e-poçtunuzu yoxlayın.",
            )
            return redirect("/az/accounts/login/")

    else:
        form = IshchiCreationForm()

    return render(request, "registration/qeydiyyat_form.html", {"form": form})


@login_required
def qiymetlendirme_etmek(request, qiymetlendirme_id):
    """Qiymətləndirmə formasını göstərir və POST sorğularını emal edir."""
    qiymetlendirme = get_object_or_404(
        Qiymetlendirme.objects.select_related(
            "qiymetlendirilen__sektor__shobe__departament"
        ),
        id=qiymetlendirme_id,
    )

    if qiymetlendirme.qiymetlendiren != request.user:
        raise PermissionDenied

    if qiymetlendirme.status == "TAMAMLANDI":
        messages.warning(request, "Bu qiymətləndirmə artıq tamamlanıb.")
        return redirect("dashboard")

    ishchi = qiymetlendirme.qiymetlendirilen
    # Yeni təşkilati struktura görə bütün sualları alırıq
    suallar = Sual.objects.all().distinct()

    if request.method == "POST":
        for sual in suallar:
            try:
                xal = int(request.POST.get(f"xal_{sual.id}"))
                rey = request.POST.get(f"rey_{sual.id}", "")
                Cavab.objects.create(
                    qiymetlendirme=qiymetlendirme, sual=sual, xal=xal, metnli_rey=rey
                )
            except (ValueError, TypeError):
                continue

        qiymetlendirme.status = "TAMAMLANDI"
        qiymetlendirme.save()
        messages.success(
            request, f"{ishchi.get_full_name()} üçün qiymətləndirmə uğurla tamamlandı."
        )
        return redirect("dashboard")

    return render(
        request,
        "core/qiymetlendirme_form.html",
        {"qiymetlendirme": qiymetlendirme, "suallar": suallar},
    )


# --- HESABAT GÖRÜNÜŞLƏRİ ---
## Həm işçinin öz hesabatı, həm də rəhbərin işçinin hesabatına baxması üçün ortaq, təkmilləşdirilmiş view.


@login_required
def hesabat_gorunumu(request, ishchi_id=None):
    """
    Həm işçinin öz hesabatı, həm də rəhbərin işçinin hesabatına baxması üçün ortaq,
    təkmilləşdirilmiş view.
    """
    # 1. Hədəf işçini və icazələri müəyyən edirik
    if ishchi_id:
        hedef_ishchi = get_object_or_404(Ishchi, id=ishchi_id)
        is_allowed_to_view = request.user.is_superuser or (
            request.user.rol == "REHBER" and request.user.organization_unit == hedef_ishchi.organization_unit
        )
        if not is_allowed_to_view:
            raise PermissionDenied
    else:
        hedef_ishchi = request.user

    # 2. Performans trendini və mövcud dövrləri alırıq
    trend_data, all_user_cycles = get_performance_trend(hedef_ishchi)

    if not all_user_cycles:
        messages.warning(
            request,
            f"{hedef_ishchi.get_full_name()} üçün heç bir tamamlanmış qiymətləndirmə tapılmadı.",
        )
        return redirect("dashboard" if not ishchi_id else "rehber_paneli")

    # 3. Hansı dövrün hesabatının göstəriləcəyini təhlükəsiz şəkildə təyin edirik
    selected_dovr_id = request.GET.get("dovr_id", all_user_cycles.last().id)
    try:
        selected_dovr = get_object_or_404(QiymetlendirmeDovru, id=int(selected_dovr_id))
    except (ValueError, TypeError):
        selected_dovr = all_user_cycles.last()

    # 4. Detallı hesabat məlumatlarını alırıq
    detailed_context = get_detailed_report_context(hedef_ishchi, selected_dovr)

    # --- AI TÖVSİYƏLƏRİNİ GENERASİYA EDİRİK ---
    # Şərhlər mövcuddursa, tövsiyələri avtomatik yaradıb kontekstə əlavə edirik
    ai_recommendations = None
    if detailed_context.get('yazili_reyler'):
        ai_recommendations = generate_recommendations(detailed_context['yazili_reyler'])

    # 5. Şablon üçün əlavə məntiqi dəyərləri hazırlayırıq
    can_manage_idp = request.user.is_superuser or (
        request.user.rol == "REHBER" and request.user.organization_unit == hedef_ishchi.organization_unit
    )
    movcud_plan = InkishafPlani.objects.filter(
        ishchi=hedef_ishchi, dovr=selected_dovr
    ).first()

    cycles_for_template = [
        {"id": dovr.id, "ad": dovr.ad, "is_selected": dovr.id == selected_dovr.id}
        for dovr in all_user_cycles
    ]

    # 6. Bütün məlumatları şablona göndəririk
    context = {
        "detailed_context": detailed_context,
        "cycles_for_template": cycles_for_template,
        "can_manage_idp": can_manage_idp,
        "movcud_plan": movcud_plan,
        "trend_chart_labels": json.dumps(list(trend_data.keys())),
        "trend_chart_data": json.dumps(list(trend_data.values())),
        "ai_recommendations": ai_recommendations, # AI tövsiyələrini əlavə edirik
    }

    return render(request, "core/hesabat.html", context)


# --- SUPERADMIN GÖRÜNÜŞLƏRİ ---

@login_required
@superadmin_required
def yeni_dovr_yarat(request):
    """
    Yeni qiymətləndirmə dövrü yaradır və aşağıdakı qiymətləndirmə təyinatlarını avtomatik generasiya edir:
    1. Hər işçi üçün özünüqiymətləndirmə
    2. Birbaşa rəhbər tərəfindən qiymətləndirmə
    3. Eyni unitdən 2 təsadüfi komanda yoldaşı tərəfindən qiymətləndirmə
    """
    if request.method == 'POST':
        form = YeniDovrForm(request.POST)
        if form.is_valid():
            # Yeni dövrü yaradırıq
            yeni_dovr = form.save()
            
            # Seçilmiş unitləri və onlara bağlı işçiləri alırıq
            secilmish_unitler = form.cleaned_data['units']
            butun_ishchiler = Ishchi.objects.filter(
                is_active=True,
                organization_unit__in=secilmish_unitler
            ).select_related('organization_unit')
            
            # Bütün yeni qiymətləndirmələr üçün boş siyahı
            yeni_qiymetlendirmeler = []
            
            # Hər işçi üçün lazımi qiymətləndirmələri yaradırıq
            for ishchi in butun_ishchiler:
                current_unit = ishchi.organization_unit
                if not current_unit:
                    continue # Əgər işçinin unit-i yoxdursa, onu ötürürük

                # 1. Özünüqiymətləndirmə əlavə edirik
                yeni_qiymetlendirmeler.append(
                    Qiymetlendirme(dovr=yeni_dovr, qiymetlendirilen=ishchi, qiymetlendiren=ishchi)
                )
                
                # 2. Rəhbər tərəfindən qiymətləndirmə
                # Qəbul etdiyimiz qayda: Rəhbər, işçi ilə eyni unit-də olan və rolu 'REHBER' olan şəxsdir
                rehberler = Ishchi.objects.filter(organization_unit=current_unit, rol='REHBER')
                for rehber in rehberler:
                    if rehber != ishchi:
                        yeni_qiymetlendirmeler.append(
                            Qiymetlendirme(dovr=yeni_dovr, qiymetlendirilen=ishchi, qiymetlendiren=rehber)
                        )
                
                # 3. Komanda yoldaşları tərəfindən qiymətləndirmə
                # Rəhbərləri çıxmaqla, eyni unit-dəki digər işçilər
                komanda_yoldashlari = list(
                    butun_ishchiler.filter(organization_unit=current_unit)
                    .exclude(id=ishchi.id)
                    .exclude(rol='REHBER')
                )
                
                # Təsadüfi 2 komanda yoldaşı seçirik (əgər varsa)
                peer_sayi = min(len(komanda_yoldashlari), 2)
                if peer_sayi > 0:
                    secilmish_peerler = random.sample(komanda_yoldashlari, peer_sayi)
                    for peer in secilmish_peerler:
                        yeni_qiymetlendirmeler.append(
                            Qiymetlendirme(dovr=yeni_dovr, qiymetlendirilen=ishchi, qiymetlendiren=peer)
                        )
            
            # Bütün qiymətləndirmələri bir dəfəyə yaradırıq (təkrarların qarşısını almaq üçün ignore_conflicts=True)
            created_objects = Qiymetlendirme.objects.bulk_create(yeni_qiymetlendirmeler, ignore_conflicts=True)
            
            messages.success(
                request,
                f"'{yeni_dovr.ad}' dövrü uğurla yaradıldı. "
                f"{len(created_objects)} unikal qiymətləndirmə təyinatı generasiya edildi."
            )
            return redirect('superadmin_paneli')
    else:
        form = YeniDovrForm()
    
    context = {
        'form': form,
        'title': 'Yeni Qiymətləndirmə Dövrü Yaradın'
    }
    return render(request, 'core/yeni_dovr_form.html', context)

# --- RƏHBƏR VƏ SUPERADMIN GÖRÜNÜŞLƏRİ ---


@login_required
@rehber_required
def rehber_paneli(request):
    """Rəhbərin öz komandasını və komandanın ümumi statistikasını gördüyü panel."""

    tabe_olan_ishchiler = Ishchi.objects.none()
    team_competency_stats = {}

    # Rəhbərin sektoru varsa, tabeliyindəki işçiləri tapırıq
    if request.user.organization_unit:
        tabe_olan_ishchiler = Ishchi.objects.filter(organization_unit=request.user.organization_unit).exclude(
            id=request.user.id
        )

    # Ən son qiymətləndirmə dövrünü tapırıq
    latest_dovr = QiymetlendirmeDovru.objects.order_by("-bitme_tarixi").first()

    if tabe_olan_ishchiler.exists() and latest_dovr:
        # Komandanın kompetensiyalar üzrə ortalama ballarını hesablayırıq
        categories = SualKateqoriyasi.objects.all()
        for cat in categories:
            avg_score = Cavab.objects.filter(
                qiymetlendirme__dovr=latest_dovr,
                qiymetlendirme__qiymetlendirilen__in=tabe_olan_ishchiler,
                sual__kateqoriya=cat,
            ).aggregate(ortalama=Avg("xal"))["ortalama"]

            if avg_score is not None:
                team_competency_stats[cat.ad] = round(avg_score, 2)

    context = {
        "tabe_olan_ishchiler": tabe_olan_ishchiler,
        "team_competency_stats": team_competency_stats,
        "chart_labels": json.dumps(list(team_competency_stats.keys())),
        "chart_data": json.dumps(list(team_competency_stats.values())),
    }
    return render(request, "core/rehber_paneli.html", context)

# --- SUPERADMIN GÖRÜNÜŞLƏRİ ---
# # Superadmin paneli, bütün təşkilat üzrə statistikaları göstərir və departamentlər üzrə hesabatlar ixrac etməyə imkan verir.

@login_required
@superadmin_required
def superadmin_paneli(request):
    """Bütün təşkilat üzrə ümumi statistikaları göstərən panel."""
    dovr = QiymetlendirmeDovru.objects.order_by("-bitme_tarixi").first()
    context = {"dovr": dovr}
    if dovr:
        total_qiymetlendirmeler = Qiymetlendirme.objects.filter(dovr=dovr)
        tamamlanmish_sayi = total_qiymetlendirmeler.filter(status="TAMAMLANDI").count()
        total_sayi = total_qiymetlendirmeler.count()
        tamamlama_faizi = (
            (tamamlanmish_sayi / total_sayi) * 100 if total_sayi > 0 else 0
        )
        context.update(
            {
                "tamamlanmish_sayi": tamamlanmish_sayi,
                "total_sayi": total_sayi,
                "tamamlama_faizi": round(tamamlama_faizi, 2),
            }
        )

        # Departament səviyyəsindəki təşkilati vahidləri alırıq
        departamentler = OrganizationUnit.objects.filter(type=OrganizationUnit.UnitType.ALI_IDARE)
        departament_stat = []
        for dep in departamentler:
            # Bu departamenta bağlı bütün alt vahidləri tapırıq
            alt_vahidler = OrganizationUnit.objects.filter(
                Q(id=dep.id) | Q(parent=dep) | Q(parent__parent=dep) | Q(parent__parent__parent=dep)
            )
            ortalama_bal = Cavab.objects.filter(
                qiymetlendirme__dovr=dovr,
                qiymetlendirme__qiymetlendirilen__organization_unit__in=alt_vahidler,
            ).aggregate(ortalama=Avg("xal"))["ortalama"]
            departament_stat.append(
                {
                    "ad": dep.name,
                    "ortalama_bal": round(ortalama_bal, 2) if ortalama_bal else 0,
                }
            )

        context["departament_stat"] = departament_stat
        context["chart_labels"] = json.dumps([item["ad"] for item in departament_stat])
        context["chart_data"] = json.dumps(
            [item["ortalama_bal"] for item in departament_stat]
        )
    return render(request, "core/superadmin_paneli.html", context)

# --- PDF YÜKLƏMƏ GÖRÜNÜŞÜ ---
# # Rəhbər və ya superuser, işçinin hesabatını PDF formatında yükləyə bilər.
@login_required
def hesabat_pdf_yukle(request, ishchi_id):
    ishchi = get_object_or_404(Ishchi, id=ishchi_id)
    is_rehber = request.user.rol == "REHBER" and request.user.organization_unit == ishchi.organization_unit
    is_self = request.user.id == ishchi.id
    if not (request.user.is_superuser or is_rehber or is_self):
        raise PermissionDenied

    dovr_id = request.GET.get("dovr_id")
    if dovr_id:
        dovr = get_object_or_404(QiymetlendirmeDovru, id=dovr_id)
    else:
        dovr = (
            QiymetlendirmeDovru.objects.filter(
                qiymetlendirme__qiymetlendirilen=ishchi,
                qiymetlendirme__status="TAMAMLANDI",
            )
            .distinct()
            .order_by("-bitme_tarixi")
            .first()
        )

    if not dovr:
        messages.error(
            request, "Hesabat yaratmaq üçün heç bir qiymətləndirmə dövrü tapılmadı."
        )
        return redirect("dashboard")

    context = get_detailed_report_context(ishchi, dovr)
    if context.get("error"):
        messages.error(request, context["error"])
        return redirect("dashboard")

    html_string = render_to_string("core/hesabat_pdf.html", context)
    pdf_file = HTML(
        string=html_string, base_url=request.build_absolute_uri()
    ).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="hesabat_{ishchi.username}_{dovr.ad}.pdf"'
    )
    return response


# --- EXCEL İXRAÇLARI ---
# Superadmin paneli üçün departament statistikasını Excel faylı olaraq ixrac edir.
# Bu funksiya, superadminin departamentlər üzrə qiymətləndirmə statistikasını Excel faylı olaraq yükləməsinə imkan verir.
@login_required
@superadmin_required
def export_departments_excel(request):
    """Superadmin paneli üçün departament statistikasını Excel faylı olaraq ixrac edir."""

    # Ən son qiymətləndirmə dövrünü tapırıq
    dovr = QiymetlendirmeDovru.objects.order_by("-bitme_tarixi").first()
    if not dovr:
        messages.error(
            request, "Hesabat yaratmaq üçün heç bir qiymətləndirmə dövrü tapılmadı."
        )
        return redirect("superadmin_paneli")

    # Məlumatları yenidən hesablayırıq (superadmin_paneli view-undakı məntiqin təkrarı)
    departamentler = OrganizationUnit.objects.filter(type=OrganizationUnit.UnitType.ALI_IDARE)
    departament_stat = []
    for dep in departamentler:
        # Bu departamenta bağlı bütün alt vahidləri tapırıq
        alt_vahidler = OrganizationUnit.objects.filter(
            Q(id=dep.id) | Q(parent=dep) | Q(parent__parent=dep) | Q(parent__parent__parent=dep)
        )
        ortalama_bal = Cavab.objects.filter(
            qiymetlendirme__dovr=dovr,
            qiymetlendirme__qiymetlendirilen__organization_unit__in=alt_vahidler,
        ).aggregate(ortalama=Avg("xal"))["ortalama"]
        departament_stat.append(
            {
                "ad": dep.name,
                "ortalama_bal": round(ortalama_bal, 2) if ortalama_bal else 0,
            }
        )

    # --- Excel Faylının Yaradılması ---

    # Yeni bir Excel kitabı yaradırıq
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = f"{dovr.ad} - Departament Hesabatı"

    # Başlıq sətrini yaradırıq və stilləndiririk
    headers = ["Departament Adı", "Ortalama Bal"]
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Məlumatları sətirlərə əlavə edirik
    for stat in departament_stat:
        sheet.append([stat["ad"], stat["ortalama_bal"]])

    # Sütunların enini avtomatik tənzimləyirik
    sheet.column_dimensions["A"].width = 40
    sheet.column_dimensions["B"].width = 20

    # HTTP cavabını hazırlayırıq
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="departament_hesabati_{dovr.ad}.xlsx"'
    )

    # Excel kitabını cavaba yazırıq
    workbook.save(response)

    return response


# --- PDF İXRAÇLARI ---
# Superadmin paneli üçün departament statistikasını PDF faylı olaraq ixrac edir.
# Bu funksiya, superadminin departamentlər üzrə qiymətləndirmə statistikasını PDF faylı olaraq yükləməsinə imkan verir.

@login_required
@superadmin_required
def export_departments_pdf(request):
    """Superadmin paneli üçün departament statistikasını PDF faylı olaraq ixrac edir."""

    dovr = QiymetlendirmeDovru.objects.order_by("-bitme_tarixi").first()
    if not dovr:
        messages.error(
            request, "Hesabat yaratmaq üçün heç bir qiymətləndirmə dövrü tapılmadı."
        )
        return redirect("superadmin_paneli")

    # Məlumatları alırıq (bu kod Excel ixracı ilə eynidir)
    departamentler = OrganizationUnit.objects.filter(type=OrganizationUnit.UnitType.ALI_IDARE)
    departament_stat = []
    for dep in departamentler:
        # Bu departamenta bağlı bütün alt vahidləri tapırıq
        alt_vahidler = OrganizationUnit.objects.filter(
            Q(id=dep.id) | Q(parent=dep) | Q(parent__parent=dep) | Q(parent__parent__parent=dep)
        )
        ortalama_bal = Cavab.objects.filter(
            qiymetlendirme__dovr=dovr,
            qiymetlendirme__qiymetlendirilen__organization_unit__in=alt_vahidler,
        ).aggregate(ortalama=Avg("xal"))["ortalama"]
        departament_stat.append(
            {
                "ad": dep.name,
                "ortalama_bal": round(ortalama_bal, 2) if ortalama_bal else 0,
            }
        )

    # --- PDF Faylının Yaradılması ---
    context = {
        "departament_stat": departament_stat,
        "dovr": dovr,
    }

    # PDF üçün xüsusi bir HTML şablonu render edirik
    html_string = render_to_string("reports/summary_departments_pdf.html", context)

    # WeasyPrint ilə HTML-dən PDF yaradırıq
    pdf_file = HTML(
        string=html_string, base_url=request.build_absolute_uri()
    ).write_pdf()

    # Brauzerə PDF faylı olaraq göndəririk
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="departament_hesabati_{dovr.ad}.pdf"'
    )

    return response


# --- FƏRDİ İNKİŞAF PLANI YARATMA VƏ REDAKTE ETMƏ ---
# # Rəhbərin və ya superuser-in işçi üçün İnkişaf Planı yaratması və ya redaktə etməsi üçün görünüş.
# Bu funksiya, rəhbərin və ya superuser-in işçi üçün İnkişaf Planı yaratmasına və ya mövcud planı redaktə etməsinə imkan verir.
# Rəhbər yalnız öz komandasına plan yaza bilər.
# # Əgər işçi və dövr üçün plan artıq varsa, onu tapırıq. Yoxdursa, yenisini yaradırıq.
# # HedefFormSet istifadə edərək hədəfləri əlavə və redaktə edirik.
# # Əgər formset düzgün doldurulubsa, hədəfləri yadda saxlayırıq və rəhbəri işçinin hesabat səhifəsinə yönləndiririk.
# # Əgər formsetdə səhvlər varsa, səhvləri göstəririk və formu yenidən göstəririk.


@login_required
@rehber_required
def plan_yarat_ve_redakte_et(request, ishchi_id, dovr_id):
    """
    Rəhbərin, işçi üçün verilmiş dövrə əsasən yeni bir İnkişaf Planı
    yaratması və ya mövcud olanı redaktə etməsi üçün.
    """
    ishchi = get_object_or_404(Ishchi, id=ishchi_id)
    dovr = get_object_or_404(QiymetlendirmeDovru, id=dovr_id)

    # Rəhbərin yalnız öz komandasına plan yaza bilməsini təmin edirik
    if not (
        request.user.is_superuser
        or (request.user.rol == "REHBER" and request.user.organization_unit == ishchi.organization_unit)
    ):
        raise PermissionDenied

    # Əgər bu işçi və dövr üçün plan artıq varsa, onu tapırıq. Yoxdursa, yenisini yaradırıq.
    plan, created = InkishafPlani.objects.get_or_create(ishchi=ishchi, dovr=dovr)

    formset = HedefFormSet(request.POST or None, instance=plan)

    if request.method == "POST":
        if formset.is_valid():
            formset.save()
            messages.success(
                request,
                f"{ishchi.get_full_name()} üçün İnkişaf Planı uğurla yadda saxlanıldı.",
            )
            # Rəhbəri həmin işçinin hesabat səhifəsinə geri yönləndiririk
            return redirect("hesabat_bax", ishchi_id=ishchi.id)

    context = {
        "formset": formset,
        "ishchi": ishchi,
        "dovr": dovr,
    }
    return render(request, "core/plan_form.html", context)


# --- MÖVCUD FƏRDİ İNKİŞAF PLANINA BAXMA VƏ STATUS YENİLƏMƏ ---
# # Rəhbərin və ya işçinin mövcud İnkişaf Planına baxması və hədəflərin statuslarını yeniləməsi üçün görünüş.
# Bu funksiya, rəhbərin və ya işçinin mövcud İnkişaf Planına baxmasına və hədəflərin statuslarını yeniləməsinə imkan verir.
# # Əgər istifadəçi planın sahibi deyilsə və rəhbər və ya superuser deyilsə, icazə verilməyəcək.
# # Əgər istifadəçi planın sahibi isə, hədəflərin statuslarını yeniləyə bilər.
# # Hədəflərin statuslarını yeniləmək üçün POST sorğusu göndərməliyik.
# # Hədəflərin statuslarını yeniləmək üçün Hedef.Status modelindən istifadə edirik.
# # Hədəflərin statuslarını yeniləmək üçün formdan istifadə edirik.
# # Hədəflərin statuslarını yeniləmək üçün POST sorğusu göndərməliyik.


@login_required
def plan_bax(request, plan_id):
    """Mövcud inkişaf planına baxmaq və statusları yeniləmək üçün."""
    plan = get_object_or_404(
        InkishafPlani.objects.select_related("ishchi", "dovr").prefetch_related(
            "hedefler"
        ),
        id=plan_id,
    )
    # Rəhbərin və ya işçinin planı görmək icazəsini yoxlayırıq
    try:
        rehber = Ishchi.objects.get(organization_unit=plan.ishchi.organization_unit, rol="REHBER")
    except (Ishchi.DoesNotExist, Ishchi.MultipleObjectsReturned):
        rehber = None

    is_allowed = (
        request.user == plan.ishchi
        or request.user == rehber
        or request.user.is_superuser
    )
    if not is_allowed:
        raise PermissionDenied

    is_plan_owner = request.user == plan.ishchi

    if request.method == "POST" and is_plan_owner:
        hedef_id = request.POST.get("hedef_id")
        yeni_status = request.POST.get("status")
        if hedef_id and yeni_status and yeni_status in Hedef.Status.values:
            try:
                hedef = get_object_or_404(Hedef, id=int(hedef_id), plan=plan)
                hedef.status = yeni_status
                hedef.save(update_fields=["status"])
                messages.success(request, "Hədəfin statusu uğurla yeniləndi.")
            except (ValueError, TypeError):
                messages.error(request, "Xətalı sorğu.")
            return redirect("plan_bax", plan_id=plan.id)

    # Bütün məntiqi burada hazırlayırıq
    hedefler_with_choices = []
    for hedef in plan.hedefler.all():
        choices = []
        for key, value in Hedef.Status.choices:
            choices.append(
                {"key": key, "value": value, "is_selected": hedef.status == key}
            )
        hedefler_with_choices.append({"hedef_obj": hedef, "status_choices": choices})

    context = {
        "plan": plan,
        "is_plan_owner": is_plan_owner,
        "hedefler_with_choices": hedefler_with_choices,
    }
    return render(request, "core/plan_detail.html", context)


# --- XÜSUSİ GİRİŞ VƏ "MƏNİ XATIRLA" FUNKSİYASI ---
# # Xüsusi giriş görünüşü, istifadəçilərin "Məni xatırla" funksiyasını istifadə edərək
# # brauzer bağlanana qədər və ya 30 gün ərzində sessiyanı saxlamağa imkan verir.

class CustomLoginView(LoginView):
    """ "Məni xatırla" funksionallığını əlavə edən xüsusi LoginView."""

    template_name = "registration/login.html"
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        remember_me = self.request.POST.get("remember_me")
        if not remember_me:
            # Əgər seçilməyibsə, sessiya brauzer bağlananda bitsin
            self.request.session.set_expiry(0)
        else:
            # Əgər seçilibsə, sessiya 30 gün aktiv qalsın (saniyə ilə)
            self.request.session.set_expiry(30 * 24 * 60 * 60)
        return super().form_valid(form)


# --- HESAB AKTİVLƏŞDİRMƏ ---
# # İstifadəçilərin e-poçt vasitəsilə hesablarını aktivləşdirməsi üçün görünüş.

def activate(request, uidb64, token):
    """E-poçtdakı link vasitəsilə hesabı aktivləşdirir."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Ishchi.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Ishchi.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request,
            "Təşəkkürlər! Hesabınız uğurla aktivləşdirildi. İndi daxil ola bilərsiniz.",
        )
        return redirect("login")
    else:
        messages.error(request, "Aktivasiya linki etibarsızdır!")
        return redirect("dashboard")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "core/profil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "info_form" not in context:
            context["info_form"] = IshchiUpdateForm(instance=self.request.user)
        if "password_form" not in context:
            context["password_form"] = IshchiPasswordChangeForm(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        context = {}
        if "update_info" in request.POST:
            info_form = IshchiUpdateForm(
                request.POST, request.FILES, instance=request.user
            )
            if info_form.is_valid():
                info_form.save()
                messages.success(request, "Profil məlumatlarınız uğurla yeniləndi!")
                return redirect("profil")
            else:
                context["info_form"] = info_form

        elif "change_password" in request.POST:
            password_form = IshchiPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Şifrəniz uğurla dəyişdirildi!")
                return redirect("profil")
            else:
                context["password_form"] = password_form

        return self.render_to_response(self.get_context_data(**context))
        return self.render_to_response(self.get_context_data(**context))
