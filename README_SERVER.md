# Q360 Performance Management System

## 🚀 Server Başlatma

### Yeni Başlayanlar üçün Tam Quraşdırma Təlimatı

#### Addım 1: İlkin Tələblər

Kompüterinizdə Python (versiya 3.8 və ya daha yeni) və pip-in quraşdırıldığından əmin olun.

#### Addım 2: Layihəni Klonlamaq və ya Yükləmək

Əgər layihə bir Git repozitoriyasındadırsa, onu klonlayın:

```bash
git clone <repository_url>
cd Q360-52baf0fca2cb17de1c099b9fc9cbf8e3af342b25/
```

Əgər layihəni ZIP olaraq yükləmisinizsə, onu arxivdən çıxarıb terminalda həmin qovluğa daxil olun.

#### Addım 3: Virtual Mühit Yaratmaq və Aktivləşdirmək

Virtual mühit (virtual environment), layihənizin asılılıqlarını sisteminizdəki digər Python layihələrindən təcrid etməyə kömək edir.

```bash
# 'venv' adlı virtual mühit yaradın
python -m venv venv

# Virtual mühiti aktivləşdirin

# Windows üçün:
venv\\Scripts\\activate

# macOS/Linux üçün:
source venv/bin/activate
```

Aktivləşdirdikdən sonra terminalın başında `(venv)` yazısını görməlisiniz.

#### Addım 4: Asılılıqları Quraşdırmaq

Layihənin tələb etdiyi bütün Python kitabxanalarını requirements.txt faylından quraşdırın.

```bash
pip install -r requirements.txt
```

#### Addım 5: .env faylını yaratmaq

Layihənin ana qovluğunda `.env` faylı yaradın və `.env.example` faylindan nümunə götürün. Ən azı SECRET_KEY və DEBUG dəyərlərini doldurun.

#### Addım 6: Verilənlər Bazasını Hazırlamaq (Migration)

Django-ya verilənlər bazasında lazımi cədvəlləri yaratmasını söyləyin.

```bash
python manage.py migrate
```

#### Addım 7: Superuser (Admin) Yaratmaq

Django-nun admin panelinə daxil olmaq üçün bir admin istifadəçisi yaradın. Sizdən istifadəçi adı, e-poçt və parol istəniləcək.

```bash
python manage.py createsuperuser
```

#### Addım 8: Layihənin İlkin Qurulum Skriptlərini İşə Salmaq

Layihənizin düzgün işləməsi üçün lazım olan rolları və digər ilkin məlumatları yaratmaq üçün xüsusi idarəetmə əmlərini işə salın.

```bash
python manage.py setup_roles
python manage.py setup_site
python manage.py create_default_surveys
```

#### Addım 9: Development Server-i Başlatmaq

Nəhayət, layihəni yerli serverdə işə salın.

```bash
python manage.py runserver
```

Server işə düşdükdən sonra terminalda belə bir mesaj görəcəksiniz:
```
Starting development server at http://127.0.0.1:8000/
```

Brauzerinizdə http://127.0.0.1:8000/ ünvanına daxil olaraq layihənizi görə bilərsiniz. Admin panelinə isə http://127.0.0.1:8000/admin/ ünvanından daxil ola bilərsiniz.

#### Addım 10 (Vacib): Arxa Fon Tapşırıqlarını (Celery) Başlatmaq

Layihədə e-poçt göndərmə və ya digər asinxron tapşırıqlar varsa, Celery işçisini (worker) ayrı bir terminalda işə salmalısınız.

Yeni bir terminal açın və virtual mühiti aktivləşdirin (Addım 3).

Aşağıdakı əmrlə Celery worker-i başladın:

```bash
celery -A config.celery_app worker --loglevel=info
```

Əgər periodik (müəyyən vaxtlarda təkrarlanan) tapşırıqlar varsa, Celery Beat-i də üçüncü bir terminalda işə salmalısınız:

```bash
celery -A config.celery_app beat --loglevel=info
```

### Windows istifadəçiləri üçün

#### Method 1: Batch Script (Sadə)

```cmd
run_server.bat
```

#### Method 2: PowerShell Script (Təfərrüatlı)

```powershell
.\run_server.ps1
```

#### Method 3: Manual (Əl ilə)

```cmd
# 1. Virtual environment activate et
venv\\Scripts\\activate

# 2. Dependencies yoxla/quraşdır  
pip install -r requirements.txt

# 3. Server başlat
python manage.py runserver 127.0.0.1:8000
```

### Linux/Mac istifadəçiləri üçün

```bash
# 1. Virtual environment activate et
source venv/bin/activate

# 2. Dependencies quraşdır
pip install -r requirements.txt

# 3. Server başlat
python manage.py runserver 127.0.0.1:8000
```

## 🌐 Giriş URL-ləri

Ana server başladıqdan sonra browser-də açın:

- **Ana Səhifə**: <http://127.0.0.1:8001/>
- **Admin Panel**: <http://127.0.0.1:8001/admin/>
- **İnteraktiv Dashboard**: <http://127.0.0.1:8001/interactive-dashboard/>
- **Təqvim**: <http://127.0.0.1:8001/teqvim/>
- **Bildirişlər**: <http://127.0.0.1:8001/bildirisler/>
- **Hesabatlar**: <http://127.0.0.1:8001/hesabatlar/>

## 📋 Əsas Modullar

### ✅ Tamamlanmış Features

1. **Notification System** - Real-time bildiriş mərkəzi
2. **Reporting Hub** - PDF/Excel/CSV hesabat generasiyası  
3. **Calendar Module** - FullCalendar.js ilə interaktiv təqvim
4. **Interactive Dashboard** - Chart.js ilə analytics
5. **Modern UI/UX** - Bootstrap 5 və responsive design
6. **RBAC System** - Role-based access control
7. **Audit Logging** - Comprehensive activity tracking
8. **Cache Optimization** - Redis-based performance

### 🔧 Technical Stack

- **Backend**: Django 5.2.3
- **Frontend**: Bootstrap 5, Chart.js, FullCalendar.js
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Cache**: Redis
- **Task Queue**: Celery
- **PDF Generation**: ReportLab
- **Authentication**: Django Auth + Custom

## 🛠️ Troubleshooting

### Problem: ImportError reportlab

```cmd
pip install reportlab
```

### Problem: Virtual Environment

```cmd
# Windows
venv\\Scripts\\activate

# Linux/Mac  
source venv/bin/activate
```

### Problem: Port məşğul

```cmd
# Başqa port istifadə edin
python manage.py runserver 127.0.0.1:8001
```

### Problem: Database

```cmd
# Migration-ları run edin
python manage.py migrate
```

## 📝 Development

### Test üçün

```cmd
python manage.py test
```

### Superuser yaratmaq

```cmd
python manage.py createsuperuser
```

### Dependencies yeniləmək

```cmd
pip install -r requirements.txt
```

## 🔒 Production Deployment

Production üçün aşağıdakı settings-ləri dəyişin:

- `DEBUG = False`
- `ALLOWED_HOSTS` təyin edin
- PostgreSQL/MySQL istifadə edin  
- HTTPS konfiqurə edin
- Static files nginx ilə serve edin

## License

---

**🎉 Q360 Performance Management System - Ready to Use! 🎉**
